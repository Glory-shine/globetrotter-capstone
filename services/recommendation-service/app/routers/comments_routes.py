from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.models import Comment, Destination
from app.schemas import CommentCreate, CommentOut, MyCommentOut

router = APIRouter(tags=["comments"])


def _to_out(c: Comment, current_user_id: str) -> dict:
    liked_by = c.liked_by or []
    return {
        "id": c.id,
        "destination_id": c.destination_id,
        "parent_id": c.parent_id,
        "user_id": c.user_id,
        "username": c.username,
        "text": c.text,
        "likes_count": len(liked_by),
        "liked_by_me": current_user_id in liked_by,
        "created_at": c.created_at,
        "replies": [],
    }


@router.get("/destinations/{destination_id}/comments", response_model=List[CommentOut])
def list_comments(
    destination_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns comments for a destination as a two-level tree: top-level
    reviews with their replies nested inside `replies`, newest first."""
    destination = db.get(Destination, destination_id)
    if destination is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{destination_id}' does not exist")

    all_comments = db.scalars(
        select(Comment).where(Comment.destination_id == destination_id).order_by(Comment.created_at.asc())
    ).all()

    by_id = {c.id: _to_out(c, current_user.id) for c in all_comments}
    top_level = []
    for c in all_comments:
        out = by_id[c.id]
        if c.parent_id and c.parent_id in by_id:
            by_id[c.parent_id]["replies"].append(out)
        elif not c.parent_id:
            top_level.append(out)

    top_level.sort(key=lambda c: c["created_at"], reverse=True)
    return top_level


@router.post("/destinations/{destination_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    destination_id: str,
    payload: CommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    destination = db.get(Destination, destination_id)
    if destination is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{destination_id}' does not exist")

    if payload.parent_id:
        parent = db.get(Comment, payload.parent_id)
        if parent is None or parent.destination_id != destination_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found")

    comment = Comment(
        destination_id=destination_id,
        parent_id=payload.parent_id,
        user_id=current_user.id,
        username=current_user.username or "Visiteur",
        text=payload.text.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _to_out(comment, current_user.id)


@router.get("/comments/mine", response_model=List[MyCommentOut])
def list_my_comments(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Every comment the current user has ever written, newest first, with
    enough destination context for the profile page to link straight back
    to where each one was posted."""
    my_comments = db.scalars(
        select(Comment).where(Comment.user_id == current_user.id).order_by(Comment.created_at.desc())
    ).all()

    destination_ids = {c.destination_id for c in my_comments}
    names_by_id = {
        d.id: d.name for d in db.scalars(select(Destination).where(Destination.id.in_(destination_ids))).all()
    }

    return [
        {
            "id": c.id,
            "destination_id": c.destination_id,
            "destination_name": names_by_id.get(c.destination_id, "Lieu supprimé"),
            "parent_id": c.parent_id,
            "text": c.text,
            "created_at": c.created_at,
        }
        for c in my_comments
    ]


@router.post("/comments/{comment_id}/like", response_model=CommentOut)
def toggle_like(
    comment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggles the current user's like on a comment (like if not yet
    liked, unlike if already liked)."""
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    liked_by = list(comment.liked_by or [])
    if current_user.id in liked_by:
        liked_by.remove(current_user.id)
    else:
        liked_by.append(current_user.id)
    comment.liked_by = liked_by
    db.commit()
    db.refresh(comment)
    return _to_out(comment, current_user.id)
