"""
Business Logic Layer — Recommendation Engine.

A lightweight content-based recommender tuned for Cameroonian travel data.
It scores each destination by matching user preference tags and history to
local categories, then prioritizes higher-rated options that fit the user's
budget tier.
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

    def _budget_penalty(self, destination: Dict[str, Any], max_budget: Optional[float]) -> int:
        if max_budget is None:
            return 0
        avg_cost = destination.get("avg_cost_per_day") or 0
        if avg_cost <= max_budget:
            return 0
        if avg_cost <= max_budget * 1.2:
            return 2
        return 5

    def _category_score(self, destination: Dict[str, Any], preference_set: set[str]) -> int:
        category = (destination.get("category") or "").lower()
        tags = {str(tag).lower() for tag in destination.get("tags", [])}

        category_map = {
            "food": {"food", "gastronomy", "restaurant", "boukarou", "fish market", "market"},
            "culture": {"culture", "history", "museum", "monument", "chiefdom", "chefferie"},
            "nature": {"nature", "adventure", "park", "ecotourism", "waterfall", "beach"},
            "nightlife": {"nightlife", "lounge", "cabaret"},
        }

        score = 0
        for name, keywords in category_map.items():
            if name in preference_set or any(keyword in tags for keyword in keywords):
                if category == name:
                    score += 4
                elif any(keyword in tags for keyword in keywords):
                    score += 2
        return score

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
        for destination in self.destinations:
            tags = {str(t).lower() for t in destination.get("tags", [])}

            direct_match_score = len(tags & preference_set) * 3
            history_score = sum(history_weights.get(t, 0) for t in tags)
            category_score = self._category_score(destination, preference_set)
            rating_score = int((destination.get("rating") or 0) * 2)
            budget_penalty = self._budget_penalty(destination, max_budget)
            score = direct_match_score + history_score + category_score + rating_score - budget_penalty

            if destination["id"] in already_planned:
                score -= 2

            if score > 0:
                scored.append((score, destination))

        if not scored:
            fallback = sorted(self.destinations, key=lambda d: (d.get("avg_cost_per_day", 0), -(d.get("rating") or 0)))
            return fallback[:limit]

        scored.sort(key=lambda pair: (-pair[0], pair[1].get("name", "")))
        return [dest for _, dest in scored[:limit]]
