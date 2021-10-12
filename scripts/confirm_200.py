import pandas as pd
import requests
import json
from rich.console import Console
from rich import print

console = Console()

# Select all the fields with links
fields_with_links = {
    "annotations.csv": [
        'id', 'book_id', 'annotation_region', 'page_iiif'
    ],
    "references.csv": [
        'id', 'book_id', 'interventions'
    ],
    "library.csv": [
        'id', 'collected_work_uri', 'catalog_uri'
    ],
    "insertions.csv": [
        'book_id', 'image_iiif'
    ]
}

# TEST: Confirm this is all of the fields with links:
for file, field_list in fields_with_links.items():
    df = pd.read_csv(file)
    for col in df.columns:
        if df[col].astype(str).str.contains('http').any() and col not in field_list:
            print(f'WARNING. Missing field in {file}: {col}')

# Get unique links from all fields
all_links = set()
for file, field_list in fields_with_links.items():
    df = pd.read_csv(file)
    for col in field_list:
        for links in df[col].dropna().unique():
            for link in links.split(';'):
                all_links.add(link)


# TEST: Ensure all multivalued links are correctly parsed
assert not any([';' in link for link in all_links])

# Print summary
print(f'Number of unique links: {len(all_links)}')

# Find status code for all links
url_status_codes = {}
for i, link in enumerate(list(all_links)):
    code = requests.get(link).status_code
    url_status_codes[link] = code
    if code == 200:
        print(f'[green]\t{i}\t{code}\t{link}[/green]')
    else:
        print(f'[red]\t{i}\t{code}\t{link}[/red]')

with open('scripts/status-codes.json', 'w') as f:
    json.dump(url_status_codes, f, indent=4)
