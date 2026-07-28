import os
import urllib.request
from pathlib import Path

out_dir = Path('public/images/destinations/real')
out_dir.mkdir(parents=True, exist_ok=True)

items = [
    ('yaounde-food-trail.jpg', 'https://source.unsplash.com/featured/1200x800/?yaounde%20food%20market,cameroon'),
    ('national-museum-yaounde.jpg', 'https://source.unsplash.com/featured/1200x800/?national%20museum%20yaounde,cameroon'),
    ('waza-national-park.jpg', 'https://source.unsplash.com/featured/1200x800/?waza%20national%20park,cameroon,wildlife'),
    ('kribi-beachfront.jpg', 'https://source.unsplash.com/featured/1200x800/?kribi%20beach,cameroon,ocean'),
    ('lobe-waterfalls.jpg', 'https://source.unsplash.com/featured/1200x800/?lobe%20waterfalls,cameroon,waterfall'),
    ('douala-night-market.jpg', 'https://source.unsplash.com/featured/1200x800/?douala%20night%20market,cameroon'),
    ('limbe-botanical-gardens.jpg', 'https://source.unsplash.com/featured/1200x800/?limbe%20botanical%20gardens,cameroon'),
    ('ekom-nkam-waterfalls.jpg', 'https://source.unsplash.com/featured/1200x800/?ekom%20nkam%20waterfalls,cameroon'),
    ('bafoussam-chiefdom-route.jpg', 'https://source.unsplash.com/featured/1200x800/?bafoussam,cameroon,traditional%20village'),
    ('buea-mountain-loop.jpg', 'https://source.unsplash.com/featured/1200x800/?buea%20mountain,cameroon,landscape'),
    ('mfoundi-market-circuit.jpg', 'https://source.unsplash.com/featured/1200x800/?mfoundi%20market,yaounde,cameroon'),
    ('bamenda-highlands.jpg', 'https://source.unsplash.com/featured/1200x800/?bamenda%20highlands,cameroon,mountain'),
]

for filename, url in items:
    path = out_dir / filename
    if path.exists():
        continue
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
        path.write_bytes(data)
        print(f'Downloaded {filename}')
    except Exception as exc:
        print(f'Failed {filename}: {exc}')
