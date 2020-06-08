import csv
import glob
import json
import os
import re
import copy

from dateutil.parser import parse
from datetime import datetime, timezone


src_dir = os.path.relpath(os.path.dirname(__file__))
md_dir = os.path.join(src_dir, '..', 'reports')
out_dir = os.path.join(src_dir, 'data_build')
combined_fpath = os.path.join(out_dir, "all-locations.md")
csv_fpath = os.path.join(out_dir, 'all-locations.csv')
json_fpath = os.path.join(out_dir, 'all-locations.json')
readme_fpath = os.path.join(out_dir, 'README.md')

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

date_regex = re.compile(
    r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
    r"Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|"
    r"Dec(ember)?)\s+\d{1,2}")

url_regex = re.compile(
    r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))"
    r"([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?")


def title_to_name_date(line):
    parts = line.split('|')
    name = parts[0].strip()
    if len(parts) == 1:
        print(f"Failed date parse: missing date for {line}")
        return line.strip(), '', ''
    if len(name) == 0:
        print(f"Failed name parse: missing name for {line}")
    date_text = parts[1].strip()

    try:
        date_found = date_regex.search(date_text).group()
        date = parse(date_found).strftime('%Y-%m-%d')
    except (ValueError, AttributeError) as err:
        print(f"Failed date format parse for title '{name}' and date '{date_text}': {err}")
        date = ''
    return name, date, date_text


def read_all_md_files(base_dir):
    md_texts = {}
    for md_file in glob.glob(base_dir + '/*.md'):
        print(f"Reading '{os.path.basename(md_file)}'")
        with open(md_file, 'rb') as fin:
            fname = os.path.basename(md_file)
            state_name = fname.replace('.md', '')
            md_texts[state_name] = fin.read().decode('utf-8')
    print(f"Got {len(md_texts)} locations")
    return md_texts


def parse_state(state, text):
    source_link = f"https://github.com/2020PB/police-brutality/blob/master/reports/{state}.md"
    city = ''
    if state == 'Washington DC':
        city = 'DC'
    if state == 'Unknown Location':
        city = ''

    clean_entry = {
        "links": [],
        "state": state,
        "edit_at": source_link,
        "city": city,
    }
    entry = copy.deepcopy(clean_entry)

    for line in text.splitlines():
        line = line.strip()
        if len(line) < 2:
            continue

        starts_with = ''
        for char in line:
            if char in ('*', '#', '-'):
                starts_with += char
            else:
                break

        if entry["links"] and '#' in starts_with:
            # We found a new city name so we must finish this `entry`
            # and start a fresh new one
            # Let the outer loop have this completed entry
            yield entry

            # Start a new entry
            entry = copy.deepcopy(clean_entry)
            # If we already parsed a city, keep it in there
            entry["city"] = city

        # remove the prefix
        line = line[len(starts_with):].strip()

        if starts_with == '##':
            city = line
            entry["city"] = city
        elif starts_with == '###':
            name, date, date_text = title_to_name_date(line)
            # print(name, date)
            entry["name"] = name
            entry["date"] = date
            entry["date_text"] = date_text
        elif starts_with == '*':
            link = url_regex.search(line)
            if link:
                entry["links"].append(link.group())
            else:
                print(f"Failed link parse '{line}'")
        else:
            # Text without a markdown marker, this might be the description or metadata
            id_prefix = 'id: '
            if line.startswith(id_prefix):
                entry["id"] = line[len(id_prefix):].strip()

    if entry and entry["links"]:
        yield entry
    else:
        print(f"Failed links parse: missing links for {entry}")


def process_md_texts(md_texts):
    data = []
    for state, text in md_texts.items():
        for entry in parse_state(state, text):
            data.append(entry)
    return data

updated_at = datetime.now(timezone.utc).isoformat()

md_header = f'''
GENERATED FILE, PLEASE MAKE EDITS ON MASTER AT https://github.com/2020PB/police-brutality/

UPDATED AT: {updated_at}

'''

md_out_format = '''
# {location}

{text}

'''


def to_merged_md_file(md_texts, target_path):
    with open(target_path, 'wb') as fout:
        fout.write(md_header.encode("utf-8"))
        for location, text in sorted(md_texts.items()):
            out_text = md_out_format.format(location=location, text=text)
            fout.write(out_text.encode('utf-8'))
    print(f"Written merged .md data to {target_path}")


def to_csv_file(data, target_path):
    max_link_count = max(len(it["links"]) for it in data)
    flat_data = []
    for row in data:
        # just write it but instead of a list of links
        # put each link in its own column
        flat_row = row.copy()
        links = flat_row["links"]
        del flat_row["links"]
        for i in range(max_link_count):
            url = ''
            if i < len(links):
                url = links[i]
            flat_row[f"Link {i + 1}"] = url
        flat_data.append(flat_row)

    with open(target_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, flat_data[0].keys())
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"Written .csv data to {target_path}")


def to_json_file(data, target_path):
    data_with_meta = {
        "edit_at": "https://github.com/2020PB/police-brutality",
        "help": "ask @ubershmekel on twitter",
        "updated_at": updated_at,
        "data": data
    }
    with open(target_path, 'w') as f:
        json.dump(data_with_meta, f)
    print(f"Written .json data to {target_path}")


readme_text ='''
# /r/2020PoliceBrutality/ dataset

This repository exists to accumulate and contextualize evidence of police brutality during the 2020 George Floyd protests.

Our goal in doing this is to assist journalists, politicians, prosecutors, activists and concerned citizens who can use the evidence accumulated here for political campaigns, news reporting, public education and prosecution of criminal police officers.

* This branch is just the files generated by parsing the markdown for ease of building other sites.
* For example your webapp can query and display data from https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json
* For more info see https://github.com/2020PB/police-brutality
* These data files are generated by https://github.com/2020PB/police-brutality/tree/master/tools

# THESE FILES ARE GENERATED - DO NOT EDIT (including this readme)

# THESE FILES ARE GENERATED - DO NOT EDIT (including this readme)

* Please edit the `.md` files on the `master` branch at https://github.com/2020PB/police-brutality
* Also notice each data row has a `edit_at` link so you can find the source data for every entry.

'''

def to_readme(target_path):
    with open(target_path, 'w') as f:
        f.write(readme_text)


if __name__ == '__main__':
    md_texts = read_all_md_files(md_dir)
    data = process_md_texts(md_texts)

    to_merged_md_file(md_texts, combined_fpath)
    to_csv_file(data, csv_fpath)
    to_json_file(data, json_fpath)
    to_readme(readme_fpath)

    print("Done!")
