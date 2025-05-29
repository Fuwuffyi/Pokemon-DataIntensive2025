import logging
from bs4 import BeautifulSoup
import pandas as pd

# Data from https://pokemondb.net/type/dual
def parse_type_chart(html_content: str) -> pd.DataFrame:
    soup = BeautifulSoup(html_content)
    table = soup.find('table', class_='type-table')
    if table is None:
        raise ValueError("No table found with class 'type-table'.")
    tbody = table.find('tbody')
    if not tbody:
        raise ValueError("No <tbody> in the table.")
    rows = tbody.find_all('tr')
    if len(rows) < 2:
        raise ValueError("Table doesn't have enough rows.")
    # HEADER: first <tr> has the attack-type icons (skip the first two <th>s: label + "PKMN")
    header_ths = rows[0].find_all('th')[2:]
    attack_types = []
    for th in header_ths:
        a = th.find('a')
        # title="Fire" etc.
        name = a['title'] if a and a.has_attr('title') else th.get_text(strip=True)
        attack_types.append(name)
    records = []
    # DEFENSE ROWS: any <tr data-type1> entry
    for row in rows[1:]:
        if not row.has_attr('data-type1'):
            continue
        # Extract defense types
        links = row.find('th').find_all('a', class_='type-cell')
        # map “—” (type-null) to None
        defs = []
        for a in links:
            txt = a.get_text(strip=True)
            if txt == '—' or a.has_attr('class') and 'type-null' in a['class']:
                defs.append(None)
            else:
                defs.append(a['title'] if a.has_attr('title') else txt)
        # pad to two
        if len(defs) == 1:
            d1, d2 = defs[0], None
        else:
            d1, d2 = defs[:2]
        # Skip if both defenses are None or identical
        if d1 is None or d1 == d2:
            continue
        # Effectiveness cells: skip the first <td> which is "PKMN" count
        tds = row.find_all('td')[1:]
        if len(tds) != len(attack_types):
            continue
        # Parse each multiplier
        for atk, cell in zip(attack_types, tds):
            txt = cell.get_text(strip=True)
            if txt == '':
                multiplier = 1.0
            else:
                # normalize fractions
                norm = (txt.replace('½', '0.5')
                           .replace('¼', '0.25')
                           .replace('¾', '0.75'))
                try:
                    multiplier = float(norm)
                except ValueError:
                    # fallback on CSS class
                    code = next((c for c in cell.get('class', []) if c.startswith('type-fx-')), None)
                    mult_map = {
                        'type-fx-0': 0.0,
                        'type-fx-25': 0.25,
                        'type-fx-50': 0.5,
                        'type-fx-100': 1.0,
                        'type-fx-200': 2.0,
                        'type-fx-400': 4.0
                    }
                    multiplier = mult_map.get(code, 1.0)
            records.append({
                'attack': atk,
                'defense1': d1,
                'defense2': d2,
                'multiplier': multiplier
            })
    df = pd.DataFrame.from_records(records)
    return df

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_html_file>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        df = parse_type_chart(content)
        print(df.head())
        output = path.rsplit('.', 1)[0] + '_parsed.csv'
        df.to_csv(output, index=False)
        print(f"Data exported to {output}")
    except Exception as ex:
        print(f"Error: {ex}")
