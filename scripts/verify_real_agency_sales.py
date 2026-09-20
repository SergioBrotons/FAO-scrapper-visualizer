import json

with open('data/exports/geneva_agencies_master.json', 'r', encoding='utf-8') as f:
    agencies = json.load(f)

print(f"Total agencies: {len(agencies)}")
total_props = sum(len(a.get('sold_properties', [])) for a in agencies)
print(f"Total sold properties: {total_props}")

bad_prec = 0
bad_addr = 0
water_pts = 0

for a in agencies:
    for p in a.get('sold_properties', []):
        if p.get('address_precision') not in ['EXACT_STREET_NUMBER', 'STREET_ONLY', 'ZONE_QUARTIER']:
            bad_prec += 1
        if 'Avenue ou Chemin' in p.get('address', ''):
            bad_addr += 1
        # In lake check: Cologny coast is ~ lon 6.175 at lat 46.225
        if 46.220 < p['lat'] < 46.260 and p['lon'] < 6.170 and p['commune'] in ['Cologny', 'Collonge-Bellerive', 'Vandœuvres']:
            water_pts += 1

print(f"Invalid precision fields: {bad_prec}")
print(f"Dummy address occurrences: {bad_addr}")
print(f"Potential water points for Cologny/Rive Gauche: {water_pts}")

ev = next((a for a in agencies if 'Engel' in a.get('name', '')), None)
if ev:
    print(f"\nAgency: {ev['name']}")
    print(f"Sold properties count: {len(ev.get('sold_properties', []))}")
    for p in ev.get('sold_properties', [])[:5]:
        print(f" - {p['typology']} | {p['address']} | {p['address_precision']} | {p['address_clarification']} | Lat: {p['lat']}, Lon: {p['lon']}")

print("\nVerification completed successfully!")
