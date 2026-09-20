"""
Sync all data from CSV and JSON exports into the SQLite database.
Ensures data/state/state.sqlite and data/fao_transactions.db are 100% up-to-date and queryable.
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path

def sync_database(db_path: str):
    print(f"\n--- Synchronizing SQLite Database: {db_path} ---")
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # 1. Load CSV (6,951 property transactions)
    csv_path = 'data/exports/geneva_property_transactions.csv'
    print(f"Loading {csv_path}...")
    df_txs = pd.read_csv(csv_path)
    print(f"Loaded {len(df_txs)} transactions.")
    
    # Write transactions table
    df_txs.to_sql('transactions', conn, if_exists='replace', index=False)
    
    # Create indexes for high-speed querying
    c = conn.cursor()
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_commune ON transactions(commune);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_parcel ON transactions(parcel_number);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(notice_date);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_price ON transactions(price_chf);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(property_type);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tx_source ON transactions(source_category);")
    
    # 2. Load Agencies (83 agencies)
    agencies_path = 'data/exports/geneva_agencies_master.json'
    print(f"Loading {agencies_path}...")
    with open(agencies_path, 'r', encoding='utf-8') as f:
        agencies = json.load(f)
        
    agencies_rows = []
    sold_props_rows = []
    
    for a in agencies:
        ag_row = {
            'id': a.get('id'),
            'name': a.get('name'),
            'rank': a.get('rank'),
            'cytria_score': a.get('cytria_score'),
            'headquarters_address': a.get('headquarters_address'),
            'headquarters_commune': a.get('headquarters_commune'),
            'lat': a.get('lat'),
            'lon': a.get('lon'),
            'radius_meters': a.get('radius_meters'),
            'primary_territory': a.get('primary_territory'),
            'top_communes': json.dumps(a.get('top_communes', []), ensure_ascii=False),
            'rating': a.get('rating'),
            'reviews_count': a.get('reviews_count'),
            'sold_24m_count': a.get('sold_24m_count'),
            'sold_volume_chf_m': a.get('sold_volume_chf_m'),
            'median_price_chf': a.get('median_price_chf'),
            'median_house_chf': a.get('median_house_chf'),
            'median_apartment_chf': a.get('median_apartment_chf'),
            'discount_rate_est': a.get('discount_rate_est'),
            'website': a.get('website'),
            'phone': a.get('phone'),
            'fao_direct_count': a.get('fao_direct_count', 0),
            'agents_count': len(a.get('agents', []))
        }
        agencies_rows.append(ag_row)
        
        for p in a.get('sold_properties', []):
            sp_row = {
                'agency_id': a.get('id'),
                'agency_name': a.get('name'),
                'fao_id': p.get('fao_id'),
                'date': p.get('date'),
                'expected_fao_date': p.get('expected_fao_date'),
                'typology': p.get('typology'),
                'commune': p.get('commune'),
                'address': p.get('address'),
                'address_precision': p.get('address_precision'),
                'address_clarification': p.get('address_clarification'),
                'price_chf': p.get('price_chf'),
                'lat': p.get('lat'),
                'lon': p.get('lon'),
                'reconciliation_level': p.get('reconciliation_level'),
                'agent_name': p.get('agent_name'),
                'publishing_delay_days': p.get('publishing_delay_days')
            }
            sold_props_rows.append(sp_row)
            
    df_ag = pd.DataFrame(agencies_rows)
    df_ag.to_sql('agencies', conn, if_exists='replace', index=False)
    c.execute("CREATE INDEX IF NOT EXISTS idx_ag_id ON agencies(id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ag_rank ON agencies(rank);")
    
    df_sp = pd.DataFrame(sold_props_rows)
    df_sp.to_sql('agency_sold_properties', conn, if_exists='replace', index=False)
    c.execute("CREATE INDEX IF NOT EXISTS idx_sp_agency ON agency_sold_properties(agency_id);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sp_fao ON agency_sold_properties(fao_id);")
    
    # 3. Load Brokers (96 brokers)
    brokers_path = 'data/exports/geneva_brokers_master.json'
    if Path(brokers_path).exists():
        print(f"Loading {brokers_path}...")
        with open(brokers_path, 'r', encoding='utf-8') as f:
            brokers = json.load(f)
        brokers_rows = []
        for b in brokers:
            b_row = {
                'name': b.get('name'),
                'role': b.get('role'),
                'agency_id': b.get('agency_id'),
                'agency_name': b.get('agency_name'),
                'rank': b.get('rank'),
                'cytria_score': b.get('cytria_score'),
                'deals_count': b.get('deals_count'),
                'specialty': b.get('specialty'),
                'top_communes': json.dumps(b.get('top_communes', []), ensure_ascii=False),
                'rating': b.get('rating'),
                'linkedin_profile_url': b.get('linkedin_profile_url')
            }
            brokers_rows.append(b_row)
        df_br = pd.DataFrame(brokers_rows)
        df_br.to_sql('brokers', conn, if_exists='replace', index=False)
        c.execute("CREATE INDEX IF NOT EXISTS idx_br_agency ON brokers(agency_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_br_name ON brokers(name);")
        
    conn.commit()
    
    # Summary
    print("\nDatabase synchronization completed successfully:")
    for tbl in ['transactions', 'agencies', 'agency_sold_properties', 'brokers']:
        cnt = c.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
        print(f" - Table '{tbl}': {cnt:,} records")
        
    conn.close()

if __name__ == '__main__':
    # Sync both the config pipeline DB and the root DB
    sync_database('data/state/state.sqlite')
    sync_database('data/fao_transactions.db')
