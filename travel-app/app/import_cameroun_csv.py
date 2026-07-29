import csv
import json
from pathlib import Path

csv_path = Path(r'g:\distributed_systems_and_cloud_computing\cameroun_centre_ouest.csv')
db_path = Path(r'g:\distributed_systems_and_cloud_computing\travel-app\app\data\db.json')

with csv_path.open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))

with db_path.open(encoding='utf-8') as f:
    data = json.load(f)

existing_names = {d['name'].lower() for d in data.get('destinations', []) if isinstance(d, dict) and d.get('name')}

for idx, row in enumerate(rows, start=1):
    name = (row.get('nom') or '').strip()
    if not name or name.lower() in existing_names:
        continue
    raw_type = (row.get('type') or '').strip().lower()
    region = (row.get('region') or '').strip()
    departement = (row.get('departement') or '').strip()
    note = (row.get('note') or '').strip()
    tags = []
    if 'ville' in raw_type or 'chef-lieu' in raw_type:
        tags.append('city')
    if 'quartier' in raw_type:
        tags.append('neighborhood')
    if 'site' in raw_type or 'touristique' in raw_type:
        tags.append('tourism')
    if 'culture' in raw_type or 'musée' in raw_type or 'religieux' in raw_type:
        tags.append('culture')
    if 'nature' in raw_type or 'aire' in raw_type or 'faune' in raw_type or 'chute' in raw_type:
        tags.append('nature')
    if 'marché' in raw_type:
        tags.append('market')
    if 'transport' in raw_type or 'infrastructure' in raw_type:
        tags.append('infrastructure')
    if 'sport' in raw_type:
        tags.append('sport')
    if not tags:
        tags.append('local')
    if region:
        tags.append(region.lower())
    if departement:
        tags.append(departement.lower())

    data['destinations'].append({
        'id': f'dest-cm-{idx:03d}',
        'name': name,
        'country': 'Cameroon',
        'tags': tags,
        'climate': 'tropical',
        'avg_cost_per_day': 25000.0,
        'price_range_xaf': '10,000-40,000',
        'description': note or f'{name} in {departement or region or "Centre"}',
        'best_season': 'Year-round',
        'category': 'local',
        'latitude': float(row['latitude']) if row.get('latitude') else None,
        'longitude': float(row['longitude']) if row.get('longitude') else None,
        'rating': 4.3,
        'budget_tier': 'budget',
    })
    existing_names.add(name.lower())

with db_path.open('w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'Imported {len(data["destinations"])} destinations')
