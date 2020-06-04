import csv
import glob
import json
import os
import re
import copy

from dateutil.parser import parse


src_dir = os.path.relpath(os.path.dirname(__file__))
md_dir = os.path.join(src_dir, '..', 'reports')
out_dir = os.path.join(src_dir, 'data_build')
combined_fpath = os.path.join(out_dir, "all-locations.md")
csv_fpath = os.path.join(out_dir, 'all-locations.csv')
json_fpath = os.path.join(out_dir, 'all-locations.json')

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
        return line.strip(), '', ''
    date_text = parts[1].strip()

    try:
        date_found = date_regex.search(date_text).group()
        date = parse(date_found).strftime('%Y-%m-%d')
    except (ValueError, AttributeError) as err:
        print(f"Failed date parse '{parts[1]}': {err}")
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
    clean_entry = {"links": [], "state": state, "edit_at": source_link}
    entry = clean_entry.copy()
    last_entry = entry

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
            # we already built an entry up, put it in, clean up
            # if "state" not in entry:
            #   entry["state"] = last_entry["state"]
            if state == 'Unknown Location':
                entry["city"] = ''
            if state == 'Washington DC':
                entry["city"] = 'DC'
            if "city" not in entry:
                entry["city"] = last_entry["city"]
            # print(entry)
            last_entry = entry
            yield entry
            entry = copy.deepcopy(clean_entry)
            entry["city"] = last_entry["city"]

        # remove the prefix
        line = line[len(starts_with):]

        # if starts_with == '#':
        #   entry["state"] = line.strip()
        if starts_with == '##':
            entry["city"] = line.strip()
        if starts_with == '###':
            name, date, date_text = title_to_name_date(line.strip())
            # print(name, date)
            entry["name"] = name
            entry["date"] = date
            entry["date_text"] = date_text
        if starts_with == '*':
            link = url_regex.search(line)
            if link:
                entry["links"].append(link.group())
            else:
                print(f"Failed link parse '{line}'")

    if entry and entry["links"]:
        yield entry


def process_md_texts(md_texts):
    data = []
    for state, text in md_texts.items():
        for entry in parse_state(state, text):
            # print(entry)
            data.append(entry)
    return data

md_header = '''
GENERATED FILE, PLEASE MAKE EDITS ON MASTER AT https://github.com/2020PB/police-brutality/

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
        "data": data,
    }
    with open(target_path, 'w') as f:
        json.dump(data_with_meta, f)
    print(f"Written .json data to {target_path}")


if __name__ == '__main__':
    md_texts = read_all_md_files(md_dir)
    data = process_md_texts(md_texts)

    to_merged_md_file(md_texts, combined_fpath)
    to_csv_file(data, csv_fpath)
    to_json_file(data, json_fpath)

    print("Done!")
