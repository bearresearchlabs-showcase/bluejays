#!/usr/bin/env python3
"""
Load all db-1 through db-16 schemas and data into Vercel/Neon PostgreSQL.

Uses POSTGRES_URL or POSTGRES_URL_NON_POOLING (Neon recommends non-pooling for migrations).
Creates separate databases db1, db2, ... db16 in the Neon project.

Usage:
  # Set POSTGRES_URL from Vercel/Neon (or .env)
  export POSTGRES_URL="postgresql://user:pass@host/neondb?sslmode=require"
  python scripts/load_all_to_vercel_postgres.py

  # Load specific databases only
  python scripts/load_all_to_vercel_postgres.py 1 2 3
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qs

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "scripts"))

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("ERROR: psycopg2 required. Run: pip install psycopg2-binary")
    sys.exit(1)

def convert_schema_for_postgres(sql: str) -> str:
    """Apply PostgreSQL-specific handling (schema is already PostgreSQL-only)."""
    # Skip GIST indexes on TEXT columns (PostgreSQL needs GEOGRAPHY or gist_trgm_ops)
    sql = re.sub(
        r'CREATE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?\w+\s+ON\s+\w+\s+USING\s+GIST\s*\(\s*\w+\s*\)',
        '-- GIST index skipped (TEXT has no GIST opclass)',
        sql,
        flags=re.IGNORECASE,
    )
    return sql


def get_connection_url() -> str:
    url = os.environ.get('POSTGRES_URL_NON_POOLING') or os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    if not url:
        print("ERROR: Set POSTGRES_URL or POSTGRES_URL_NON_POOLING (from Vercel/Neon integration)")
        sys.exit(1)
    return url


def conn_for_database(base_url: str, db_name: str):
    """Return connection params for a specific database."""
    parsed = urlparse(base_url)
    path = f'/{db_name}'
    if parsed.query:
        new_url = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))
    else:
        new_url = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, '', parsed.fragment))
    return psycopg2.connect(new_url)


def get_db_dir(db_num: int) -> Path:
    """Resolve db-N directory (source/db-N or db-N at root)."""
    for base in [BASE / 'source', BASE]:
        d = base / f'db-{db_num}'
        if d.exists():
            return d
    return BASE / 'source' / f'db-{db_num}'


def get_schema_files(db_dir: Path, db_num: int) -> list[Path]:
    """Return ordered list of schema SQL files to load."""
    data_dir = db_dir / 'data'
    if not data_dir.exists():
        return []
    # DB-specific schema order (schema.sql is canonical, PostgreSQL-only)
    if db_num == 6:
        candidates = [
            'schema.sql',
            'schema_extensions.sql',
            'insurance_schema.sql',
            'nexrad_satellite_schema.sql',
        ]
    elif db_num == 4:
        candidates = ['schema.sql', 'schema_models.sql']
    else:
        candidates = ['schema.sql'] if (data_dir / 'schema.sql').exists() else []
    files = []
    for name in candidates:
        p = data_dir / name
        if p.exists():
            files.append(p)
    if not files and (data_dir / 'schema.sql').exists():
        files = [data_dir / 'schema.sql']
    return files


def get_data_file(db_dir: Path, db_num: int) -> Path | None:
    """Return primary data file to load: prefer data_large >= 1GB, else data.sql."""
    from db_paths import get_data_dir, get_primary_data_path
    data_dir = get_data_dir(db_dir)
    primary = get_primary_data_path(data_dir)
    if primary:
        return primary[1]
    # db-10, db-14: source data has malformed VALUES; use deliverable data if available
    if db_num in (10, 14):
        deliverable_data = db_dir / 'deliverable' / 'data' / 'data.sql'
        if deliverable_data.exists():
            return deliverable_data
    return None


def split_statements(content: str) -> list[str]:
    """Split SQL by semicolons, respecting strings and parens."""
    statements = []
    buf = []
    paren_depth = 0
    in_string = False
    string_char = None
    for i, char in enumerate(content):
        buf.append(char)
        if char in ("'", '"') and not (len(buf) > 1 and buf[-2] == '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
        if not in_string:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ';' and paren_depth == 0:
                stmt = ''.join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
    if buf:
        stmt = ''.join(buf).strip()
        if stmt:
            statements.append(stmt)
    return statements


def load_schema(conn, schema_files: list[Path], enable_postgis: bool) -> tuple[bool, str]:
    """Load schema files into connection."""
    cur = conn.cursor()
    if enable_postgis:
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        except Exception:
            pass
    for f in schema_files:
        with open(f) as fp:
            sql_content = fp.read()
        sql_content = convert_schema_for_postgres(sql_content)
        sql_content = re.sub(r'VARCHAR\s*\(\s*16777216\s*\)', 'VARCHAR(10485760)', sql_content, flags=re.IGNORECASE)
        sql_content = re.sub(r'VARCHAR\s*\(\s*65535\s*\)', 'VARCHAR(65535)', sql_content, flags=re.IGNORECASE)
        for stmt in split_statements(sql_content):
            stmt = stmt.strip()
            if not stmt:
                continue
            # Strip leading comment lines (but keep SQL that has leading comments)
            lines = stmt.split('\n')
            while lines and (not lines[0].strip() or lines[0].strip().startswith('--')):
                lines.pop(0)
            stmt = '\n'.join(lines).strip()
            if not stmt:
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    cur.close()
                    return False, str(e)[:200]
    cur.close()
    return True, "OK"


# Fix malformed INSERT column lists (concatenated without commas) in source data
_DATA_COLUMN_FIXES: dict[str, str] = {
    'first_namelast_namephone_numberemailaddress_1address_2citystatezipcountrycommentsperson_id': 'first_name, last_name, phone_number, email, address_1, address_2, city, state, zip, country, comments, person_id',
    'usernamepasswordperson_idbalancedeletedhide_from_switch_user': 'username, password, person_id, balance, deleted, hide_from_switch_user',
    'employee_idlocation_id': 'employee_id, location_id',
    'namecategorydescriptioncost_priceunit_priceitem_idallow_alt_descriptionis_serializedoverride_default_taxis_servicedeleted': 'name, category, description, cost_price, unit_price, item_id, allow_alt_description, is_serialized, override_default_tax, is_service, deleted',
    'retailer_idretailer_nameretailer_typewebsite_urlheadquarters_cityheadquarters_stateheadquarters_zipmarket_coveragefounded_yearemployee_count': 'retailer_id, retailer_name, retailer_type, website_url, headquarters_city, headquarters_state, headquarters_zip, market_coverage, founded_year, employee_count',
    'store_idretailer_idstore_namestore_numberstore_addressstore_citystore_statestore_zipstore_countystore_latitudestore_longitudestore_typestore_size_sqftopening_datestore_status': 'store_id, retailer_id, store_name, store_number, store_address, store_city, store_state, store_zip, store_county, store_latitude, store_longitude, store_type, store_size_sqft, opening_date, store_status',
    'product_idskuupcproduct_namebrandmanufacturermodel_numbercategorysubcategoryproduct_descriptionweight_lbscoloris_active': 'product_id, sku, upc, product_name, brand, manufacturer, model_number, category, subcategory, product_description, weight_lbs, color, is_active',
    'provider_idprovider_nameprovider_display_nameapi_base_urlpricing_api_endpointdocumentation_urldata_sourceupdate_frequencydata_quality_score': 'provider_id, provider_name, provider_display_name, api_base_url, pricing_api_endpoint, documentation_url, data_source, update_frequency, data_quality_score',
    'region_idprovider_idregion_coderegion_nameregion_display_namecountry_codecontinenttimezoneis_activelaunch_datedata_center_countavailability_zones_count': 'region_id, provider_id, region_code, region_name, region_display_name, country_code, continent, timezone, is_active, launch_date, data_center_count, availability_zones_count',
    'inventory_idproduct_idstore_idstock_levelstock_statusavailable_quantitylast_checked_atdata_sourceconfidence_score': 'inventory_id, product_id, store_id, stock_level, stock_status, available_quantity, last_checked_at, data_source, confidence_score',
    'pricing_idproduct_idretailer_idstore_idcurrent_priceoriginal_pricesale_pricediscount_percentageprice_effective_dateprice_expiry_dateprice_typeprice_sourceprice_confidence_scoreis_online_price': 'pricing_id, product_id, retailer_id, store_id, current_price, original_price, sale_price, discount_percentage, price_effective_date, price_expiry_date, price_type, price_source, price_confidence_score, is_online_price',
    'deal_idproduct_idretailer_idstore_iddeal_typediscount_percentagediscount_amountdeal_priceoriginal_pricedeal_start_datedeal_end_datedeal_statusdeal_descriptiondeal_sourceis_online_deal': 'deal_id, product_id, retailer_id, store_id, deal_type, discount_percentage, discount_amount, deal_price, original_price, deal_start_date, deal_end_date, deal_status, deal_description, deal_source, is_online_deal',
    'census_idnaics_codeindustry_categorymonthyearretail_sales_amountinventory_amountstore_countemployment_countsales_change_percentinventory_change_percentdata_source': 'census_id, naics_code, industry_category, month, year, retail_sales_amount, inventory_amount, store_count, employment_count, sales_change_percent, inventory_change_percent, data_source',
    'bls_idseries_idproduct_categoryperiodyearprice_index_valuepercent_changepercent_change_year_agobase_periodindex_typedata_source': 'bls_id, series_id, product_category, period, year, price_index_value, percent_change, percent_change_year_ago, base_period, index_type, data_source',
    'market_idmarket_namemarket_typemarket_codepopulationmedian_incomemarket_sizestate_codecounty_namedata_source': 'market_id, market_name, market_type, market_code, population, median_income, market_size, state_code, county_name, data_source',
}


def fix_data_values(content: str) -> str:
    """Fix malformed VALUES (numberCURRENT_TIMESTAMP, numberFALSE, etc.)."""
    content = re.sub(r'(\d+)CURRENT_TIMESTAMP', r'\1, CURRENT_TIMESTAMP', content)
    content = re.sub(r'(\d+\.?\d*)FALSE\b', r'\1, FALSE', content)
    content = re.sub(r'(\d+\.?\d*)TRUE\b', r'\1, TRUE', content)
    content = re.sub(r'(\d+\.?\d*)TRUE(\d)\b', r'\1, TRUE, \2', content)  # 10.0TRUE0 -> 10.0, TRUE, 0 (db-14)
    content = re.sub(r'(\d+\.?\d*)FALSE(\d)\b', r'\1, FALSE, \2', content)
    content = re.sub(r'NULLNULL', 'NULL, NULL', content)
    return content


def fix_data_values_db5(content: str) -> str:
    """Fix db-5 specific malformed VALUES."""
    # phppos_employees: 3 values -> 6 (add balance, deleted, hide_from_switch_user)
    content = re.sub(
        r"\(username, password, person_id, balance, deleted, hide_from_switch_user\) VALUES\s*\n\s*\('([^']+)', '([^']+)', (\d+)\)",
        r"(username, password, person_id, balance, deleted, hide_from_switch_user) VALUES\n('\1', '\2', \3, 0, 0, 0)",
        content,
    )
    # phppos_employees_locations: (11) -> (1, 1) (employee 1, location 1)
    content = re.sub(
        r"\(employee_id, location_id\) VALUES \(11\)",
        r"(employee_id, location_id) VALUES (1, 1)",
        content,
    )
    # phppos_items: 4 values -> 11. ('Electric', 'Fuel', 'EV charging', 00100000) -> full row
    content = re.sub(
        r"\('Electric', 'Fuel', 'EV charging', 00100000\)",
        "('Electric', 'Fuel', 'EV charging', 0, 0, 100000, 0, 0, 0, 0, 0)",
        content,
    )
    content = re.sub(
        r"\('CNG', 'Fuel', 'Compressed natural gas', 00200000\)",
        "('CNG', 'Fuel', 'Compressed natural gas', 0, 0, 200000, 0, 0, 0, 0, 0)",
        content,
    )
    content = re.sub(
        r"\('LNG', 'Fuel', 'Liquefied natural gas', 00300000\)",
        "('LNG', 'Fuel', 'Liquefied natural gas', 0, 0, 300000, 0, 0, 0, 0, 0)",
        content,
    )
    content = re.sub(
        r"\('BD', 'Fuel', 'Biodiesel', 00400000\)",
        "('BD', 'Fuel', 'Biodiesel', 0, 0, 400000, 0, 0, 0, 0, 0)",
        content,
    )
    content = re.sub(
        r"\('E85', 'Fuel', 'Ethanol blend', 00500000\)",
        "('E85', 'Fuel', 'Ethanol blend', 0, 0, 500000, 0, 0, 0, 0, 0)",
        content,
    )
    return content


def fix_data_column_lists(content: str) -> str:
    """Fix malformed INSERT column lists (concatenated without commas)."""
    for bad, good in _DATA_COLUMN_FIXES.items():
        content = content.replace(f'({bad})', f'({good})')
    # Fix phppos_locations long column list
    loc_cols = 'location_idnameaddressphonefaxemailreceive_stock_alertstock_alert_emailtimezonemailchimp_api_keyenable_credit_card_processingmerchant_idmerchant_passworddefault_tax_1_ratedefault_tax_1_namedefault_tax_2_ratedefault_tax_2_namedefault_tax_2_cumulativedefault_tax_3_ratedefault_tax_3_namedefault_tax_4_ratedefault_tax_4_namedefault_tax_5_ratedefault_tax_5_namedeleted'
    loc_fixed = 'location_id, name, address, phone, fax, email, receive_stock_alert, stock_alert_email, timezone, mailchimp_api_key, enable_credit_card_processing, merchant_id, merchant_password, default_tax_1_rate, default_tax_1_name, default_tax_2_rate, default_tax_2_name, default_tax_2_cumulative, default_tax_3_rate, default_tax_3_name, default_tax_4_rate, default_tax_4_name, default_tax_5_rate, default_tax_5_name, deleted'
    content = content.replace(f'({loc_cols})', f'({loc_fixed})')
    content = fix_data_values(content)
    content = fix_data_values_db5(content)
    return content


def load_data(conn, data_file: Path) -> tuple[bool, str]:
    """Load data.sql into connection."""
    if not data_file.exists():
        return True, "No data file"
    cur = conn.cursor()
    with open(data_file) as f:
        content = f.read()
    content = fix_data_column_lists(content)
    statements = [s.strip() for s in split_statements(content) if s.strip()]
    errs = []
    for stmt in statements:
        try:
            cur.execute(stmt)
        except Exception as e:
            msg = str(e).lower()
            if 'duplicate key' not in msg and 'already exists' not in msg:
                errs.append(str(e)[:120])
    cur.close()
    if errs and len(errs) > len(statements) * 0.5:
        return False, '; '.join(errs[:3])
    return True, f"Loaded {len(statements)} statements"


def main():
    # Load .env if present
    env_file = BASE / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    url = get_connection_url()
    db_ids = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(1, 17))

    print("Connecting to Neon/Vercel Postgres...")
    admin_conn = psycopg2.connect(url)
    admin_conn.autocommit = True

    results = []
    for n in db_ids:
        db_name = f'db{n}'
        db_dir = get_db_dir(n)
        schema_files = get_schema_files(db_dir, n)
        data_file = get_data_file(db_dir, n)

        if not schema_files:
            print(f"  db-{n}: SKIP (no schema)")
            results.append((n, 'SKIP', 'No schema'))
            continue

        print(f"  db-{n}: ", end='', flush=True)
        try:
            cur = admin_conn.cursor()
            cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
            if cur.fetchone():
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                    (db_name,),
                )
                cur.execute(f'DROP DATABASE "{db_name}"')
            cur.execute(f'CREATE DATABASE "{db_name}"')
            cur.close()
        except Exception as e:
            print(f"CREATE DB failed: {e}")
            results.append((n, 'FAIL', str(e)))
            continue

        try:
            conn = conn_for_database(url, db_name)
            conn.autocommit = True
        except Exception as e:
            print(f"Connect failed: {e}")
            results.append((n, 'FAIL', str(e)))
            continue

        def _needs_postgis():
            for f in schema_files:
                c = open(f).read().upper()
                if 'GEOGRAPHY' in c or 'GEOMETRY' in c:
                    return True
            return False
        enable_postgis = _needs_postgis()
        ok, msg = load_schema(conn, schema_files, enable_postgis)
        if not ok:
            conn.close()
            print(f"Schema failed: {msg}")
            results.append((n, 'FAIL', msg))
            continue

        if data_file:
            ok, msg = load_data(conn, data_file)
            if not ok:
                conn.close()
                print(f"OK (schema only, data skipped: {msg[:60]}...)")
                results.append((n, 'OK', f"Data skipped: {msg[:80]}"))
                continue

        conn.close()
        print("OK")
        results.append((n, 'OK', ''))

    admin_conn.close()
    print("\nDone.")
    passed = sum(1 for _, s, _ in results if s == 'OK')
    print(f"Loaded {passed}/{len(results)} databases")


if __name__ == '__main__':
    main()
