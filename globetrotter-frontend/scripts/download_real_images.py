import urllib.request
from pathlib import Path

out = Path('public/images/destinations/real')
out.mkdir(parents=True, exist_ok=True)

items = [
    ('yaounde-food-trail.jpg', 'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1200&q=80'),
    ('national-museum-yaounde.jpg', 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80'),
    ('waza-national-park.jpg', 'https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1200&q=80'),
    ('kribi-beachfront.jpg', 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80'),
    ('lobe-waterfalls.jpg', 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80'),
    ('douala-night-market.jpg', 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80'),
    ('limbe-botanical-gardens.jpg', 'https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&w=1200&q=80'),
    ('ekom-nkam-waterfalls.jpg', 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=80'),
    ('bafoussam-chiefdom-route.jpg', 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80'),
    ('buea-mountain-loop.jpg', 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80'),
    ('mfoundi-market-circuit.jpg', 'https://images.unsplash.com/photo-1512428813834-c702c7702b78?auto=format&fit=crop&w=1200&q=80'),
    ('bamenda-highlands.jpg', 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80'),
]

for filename, url in items:
    path = out / filename
    if path.exists():
        continue
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            path.write_bytes(response.read())
        print(f'OK {filename}')
    except Exception as exc:
        print(f'FAIL {filename}: {exc}')
