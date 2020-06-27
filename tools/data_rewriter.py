import random
import string

import data_builder
from data_builder import critical_exit

unknown_location_acronym = 'tbd'

# https://gist.github.com/rogerallen/1583593
us_state_to_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Washington DC': 'DC',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
    'Unknown Location': unknown_location_acronym,
}

def random_chars(count):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(count))

def gen_id(row):
    state = row['state']
    state_abbrev = us_state_to_abbrev[state].lower()
    city = row['city']
    city_abbrev = city.replace(' ', '').replace('.', '').lower()
    if len(city_abbrev) == 0:
        if state_abbrev == unknown_location_acronym:
            city_abbrev = unknown_location_acronym
        elif state_abbrev == 'dc':
            city_abbrev = 'dc'
        else:
            critical_exit("invalid city abbreviation, exiting")

    # id_line = f'id: {state_abbrev}-{city_abbrev}-{city_index}'
    return f"{state_abbrev}-{city_abbrev}-{random_chars(4)}"

def rewrite_data(data):
    state_to_rows = {}
    for row in data:
        state = row["state"]
        if state not in state_to_rows:
            state_to_rows[state] = []
        state_to_rows[state].append(row)
    
    for state, data_rows in state_to_rows.items():
        out_path = f"{data_builder.md_dir}/{state}.md"
        # We don't need to sort `data_rows` because we read these in the order of the markdown files
        new_md_text = gen_md_from_rows(state, data_rows)
        with open(out_path, "wb") as fout:
            fout.write(new_md_text.encode("utf-8"))

row_format = '''### {name} | {date_text}

{description}

tags: {tags_md}

id: {id}

**Links**

{links_md}

'''

def markdown_link(link_obj):
    url = link_obj["url"]
    text = link_obj["text"]
    if len(text) == 0:
        return url
    return f"[{text}]({url})"

def gen_md_from_rows(state, rows):
    city = ''
    lines = []
    for row in rows:
        if row["city"] and row["city"] != city:
            # new city, let everyone know
            lines.append(f'## {row["city"]}\n')
            city = row["city"]
        
        # convert links list to a links string
        links_md = '\n'.join('* ' + markdown_link(it) for it in row["links_v2"])
        row["links_md"] = links_md

        # convert tags from a list to a string
        row["tags_md"] = ', '.join(row["tags"])

        # Create this row's markdown
        lines.append(row_format.format(**row))
    
    return '\n'.join(lines)

def validate_ids_unique(data):
    seen = set()
    for row in data:
        row_id = row["id"]
        if row_id in seen:
            print(row)
            critical_exit(f"Duplicate id found {row_id}")
        else:
            seen.add(row_id)

def add_missing_ids():
    data = data_builder.read_all_data()

    for row in data:
        if "id" not in row or len(row["id"]) == 0:
            row["id"] = gen_id(row)
            print("Added id: " + row["id"])
        if "name" not in row:
            print(row)
            critical_exit("this row is broken with no name? (missing ###):")

    validate_ids_unique(data)

    rewrite_data(data)



if __name__ == "__main__":
    add_missing_ids()
