import json
from pathlib import Path

path = Path('app/data/db.json')
data = json.loads(path.read_text(encoding='utf-8'))

mapping = {
    'Yaoundé Food Trail': '/images/destinations/yaounde-food-trail.svg',
    'National Museum of Yaoundé': '/images/destinations/national-museum-yaounde.svg',
    'Waza National Park': '/images/destinations/waza-national-park.svg',
    'Kribi Beachfront': '/images/destinations/kribi-beachfront.svg',
    'Lobé Waterfalls': '/images/destinations/lobe-waterfalls.svg',
    'Douala Night Market': '/images/destinations/douala-night-market.svg',
    'Limbe Botanical Gardens': '/images/destinations/limbe-botanical-gardens.svg',
    'Ekom Nkam Waterfalls': '/images/destinations/ekom-nkam-waterfalls.svg',
    'Bafoussam Chiefdom Route': '/images/destinations/bafoussam-chiefdom-route.svg',
    'Buea Mountain Loop': '/images/destinations/buea-mountain-loop.svg',
    'Mfoundi Market Circuit': '/images/destinations/mfoundi-market-circuit.svg',
    'Bamenda Highlands': '/images/destinations/bamenda-highlands.svg',
}

for destination in data.get('destinations', []):
    name = destination.get('name')
    if name in mapping:
        destination['media'] = {
            'main': mapping[name],
            'secondary': [mapping[name]],
        }

path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
