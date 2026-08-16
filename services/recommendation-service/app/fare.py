"""
Transport fare estimation between two destinations.

Bafoussam's urban transport (moto-taxi and shared taxi) is priced
informally and negotiated by distance rather than metered — there's no
official published tariff table to scrape. Calibrated here against a
well-known real in-town reference trip (Hôtel des Finances → l'agence de
transport à l'entrée de la ville, ≈2 km): taxi tops out around 200-250
FCFA for that ride, moto-taxi around 400-500 FCFA. Contrary to what one
might assume, moto-taxi runs noticeably *more* expensive per kilometre
than shared taxi in Bafoussam, not cheaper — the pricing below reflects
that local reality rather than a generic assumption.

This module turns that real baseline into a distance-aware estimate using
the great-circle (Haversine) distance between two destinations' real
coordinates, so every place in the catalog gets a plausible, consistent
fare rather than a hand-typed number per pair. It's explicitly an
estimate — the UI and docs say so — not a scraped official price list.
"""

import math
from dataclasses import dataclass

# Calibrated so a typical ~2 km in-town hop (e.g. Hôtel des Finances →
# l'agence à l'entrée de la ville) lands in the 200-250 FCFA range for a
# taxi and 400-500 FCFA for a moto-taxi, as reported on the ground.
PRICING = {
    "moto": {"base_fcfa": 150, "per_km_fcfa": 150, "minimum_fcfa": 300},
    "taxi": {"base_fcfa": 100, "per_km_fcfa": 55, "minimum_fcfa": 150},
}

# Rough average urban travel speed used only to estimate trip duration for
# display purposes (accounts for traffic, unpaved sections, stops).
AVERAGE_SPEED_KMH = {"moto": 28, "taxi": 22}


@dataclass
class FareResult:
    distance_km: float
    duration_min: int
    price_fcfa: int
    price_label: str
    note: str


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return earth_radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def estimate_fare(lat1: float, lon1: float, lat2: float, lon2: float, mode: str) -> FareResult:
    if mode not in PRICING:
        raise ValueError(f"Unknown transport mode: {mode}")

    # City streets rarely run in a straight line — pad the great-circle
    # distance a bit to approximate real road distance.
    straight_line_km = haversine_km(lat1, lon1, lat2, lon2)
    road_km = round(straight_line_km * 1.3, 2)

    tariff = PRICING[mode]
    raw_price = tariff["base_fcfa"] + road_km * tariff["per_km_fcfa"]
    price = max(tariff["minimum_fcfa"], round(raw_price / 50) * 50)  # round to nearest 50 FCFA

    duration_min = max(3, round((road_km / AVERAGE_SPEED_KMH[mode]) * 60))

    label = "Gratuit" if price == 0 else f"{price:,.0f} FCFA".replace(",", " ")

    return FareResult(
        distance_km=road_km,
        duration_min=duration_min,
        price_fcfa=int(price),
        price_label=label,
        note=(
            "Estimation basée sur la distance réelle entre les deux lieux "
            f"({'moto-taxi' if mode == 'moto' else 'taxi'}, tarif négocié sur place — "
            "prix non contractuel)."
        ),
    )
