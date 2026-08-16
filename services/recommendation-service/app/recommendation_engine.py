"""
Business logic — Recommendation Engine.

Unchanged in spirit from the monolith version: scores each destination by
overlap with the user's preference tags plus tags implied by their
itinerary history. The only difference is *where* preferences and history
come from now — both arrive over the network from user-service and
itinerary-service (see app/clients.py) instead of a local JSON read.
"""

from typing import Any, Dict, List, Optional


class RecommendationEngine:
    def __init__(self, destinations: List[Dict[str, Any]]):
        self.destinations = destinations

    def _history_tag_weights(self, user_itineraries: List[Dict[str, Any]]) -> Dict[str, int]:
        dest_by_id = {d["id"]: d for d in self.destinations}
        weights: Dict[str, int] = {}
        for itinerary in user_itineraries:
            dest = dest_by_id.get(itinerary.get("destination_id"))
            if not dest:
                continue
            for tag in dest.get("tags", []):
                weights[tag.lower()] = weights.get(tag.lower(), 0) + 1
        return weights

    def recommend(
        self,
        preferences: List[str],
        user_itineraries: Optional[List[Dict[str, Any]]] = None,
        max_budget: Optional[float] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        user_itineraries = user_itineraries or []
        preference_set = {p.lower() for p in preferences}
        history_weights = self._history_tag_weights(user_itineraries)
        already_planned = {i.get("destination_id") for i in user_itineraries}

        scored: List[tuple] = []
        for dest in self.destinations:
            tags = {t.lower() for t in dest.get("tags", [])}

            direct_match_score = len(tags & preference_set) * 3
            history_score = sum(history_weights.get(t, 0) for t in tags)
            score = direct_match_score + history_score

            if max_budget is not None and dest.get("avg_cost_per_day", 0) > max_budget:
                score -= 5

            if dest["id"] in already_planned:
                score -= 2

            if score > 0:
                scored.append((score, dest))

        if not scored:
            fallback = sorted(self.destinations, key=lambda d: d.get("avg_cost_per_day", 0))
            return fallback[:limit]

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [dest for _, dest in scored[:limit]]
