import pandas as pd
import requests
import json
from rich.console import Console
from rich import print

console = Console()

STATUS_CODE_JSON = 'scripts/status-codes.json'
OVERWRITE_JSON = False
FIELDS_WITH_LINKS = {
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


# Get unique links from all fields
all_links = set()
for file, field_list in FIELDS_WITH_LINKS.items():
    df = pd.read_csv(file)
    for col in field_list:
        for links in df[col].dropna().unique():
            for link in links.split(';'):
                all_links.add(link)


# TEST: Ensure all multivalued links are correctly parsed
assert not any([';' in link for link in all_links])

print(f'Number of unique links: {len(all_links)}')


# DETERMINE STATUS CODES

# Decide whether to continue where we left off or run script fresh
if OVERWRITE_JSON:
    url_status_codes = {}
else:
    with open(STATUS_CODE_JSON) as f:
        url_status_codes = json.load(f)

# Find status code for all links
for i, link in enumerate(list(all_links)):
    if link not in url_status_codes:
        code = requests.get(link).status_code
        url_status_codes[link] = code

        if code == 200:
            print(f'[green]\t{i}\t{code}\t{link}[/green]')
        else:
            print(f'[red]\t{i}\t{code}\t{link}[/red]')

    # Update status code JSON periodically
    if i % 100 == 0:
        with open(STATUS_CODE_JSON, 'w') as f:
            json.dump(url_status_codes, f, indent=4)

# Write final status code JSON
with open(STATUS_CODE_JSON, 'w') as f:
    json.dump(url_status_codes, f, indent=4)

# Print results summary
print('Error URLs:')
for url, status_code in url_status_codes.items():
    if status_code != 200:
        print(f'\t{url}')
