import csv
import glob
import json
import os
import re
import copy

from dateutil.parser import parse
from datetime import datetime, timezone

# `or '.'` because when you're in the same directory as this code
# `ValueError: no path specified` gets thrown by `relpath` with empty input
src_dir = os.path.relpath(os.path.dirname(__file__) or ".")
possible_tags_path = os.path.join(src_dir, "..", "docs/possible_tags.md")
md_dir = os.path.join(src_dir, "..", "reports")
out_dir = os.path.join(src_dir, "data_build")
combined_fpath = os.path.join(out_dir, "all-locations.md")
csv_fpath_v1 = os.path.join(out_dir, "all-locations.csv")
json_fpath_v1 = os.path.join(out_dir, "all-locations.json")
json_fpath_v2 = os.path.join(out_dir, "all-locations-v2.json")
readme_fpath = os.path.join(out_dir, "README.md")

if not os.path.exists(out_dir):
    os.mkdir(out_dir)

date_regex = re.compile(
    r"(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
    r"Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|"
    r"Dec(ember)?)\s+\d{1,2}"
)

url_regex = re.compile(
    r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))" r"([\w\-\.,@?^=%&amp;:/~\+#\!]*[\w\-\@?^=%&amp;/~\+#\!])?"
)

# Regex is used to ensure that lat/long is both in a valid format has has 6-7 decimal places (or is an exact 90/180) to improve data quality on the backend
LAT_REGEX = re.compile(r"^\(?([-+]?(?:[1-8]?\d(?:\.\d{5,7})|90(?:\.0+)?)),")
LONG_REGEX = re.compile(r".*,\s*([-+]?(?:180(?:\.0+)?|(?:(?:1[0-7]\d)|(?:[1-9]?\d))(?:\.\d{5,7})))\)?$")


def critical_exit(msg):
    print(f"---CRITICAL FAILURE {msg}")
    exit(2)


def title_to_name_date(line):
    parts = line.split("|")
    if len(parts) != 2:
        raise ValueError(f"Failed title_to_name_date. Expected 2 parts, separated by '|'. Got: {line}")

    name = parts[0].strip()
    if len(name) == 0:
        raise ValueError(f"Failed name parse: missing name for {line}")

    date_text = parts[1].strip()

    if date_text in ("Date Unknown", "Unknown Date"):
        return name, "", "Unknown Date"

    date_search = date_regex.search(date_text)
    date_found = date_text.lower().replace("(believed to be)", "").strip()
    if date_search:
        date_found = date_search.group()
        if "202" not in date_text:
            date_found += ", 2020"

    date = parse(date_found).strftime("%Y-%m-%d")
    new_date_text = date
    if "believed" in date_text.lower():
        new_date_text = f"(Believed to be) {date}"
    return name, date, new_date_text


def read_all_md_files(base_dir):
    md_texts = {}
    for md_file in glob.glob(base_dir + "/*.md"):
        print(f"Reading '{os.path.basename(md_file)}'")
        with open(md_file, "rb") as fin:
            fname = os.path.basename(md_file)
            state_name = fname.replace(".md", "")
            md_texts[state_name] = fin.read().decode("utf-8")
    print(f"Got {len(md_texts)} locations")
    return md_texts


def finalize_entry(entry):
    entry["description"] = entry["description"].strip()
    return entry


def find_md_link_or_url(text):
    """
    find_md_link_or_url('ab[cd](ef)xy') returns:
        ('abcdxy', 'ef')

    All the text goes into the text, and the URL as well.
    """
    start = (0,)
    open_sq = (1,)
    closed_sq = (2,)
    open_curve = (3,)
    closed_curve = (4,)
    state = start
    text_content = ""
    link_url = ""
    for ch in text:
        if state == start:
            if ch == "[":
                state = open_sq
            else:
                text_content += ch
        elif state == open_sq:
            if ch == "]":
                state = closed_sq
            else:
                text_content += ch
        elif state == closed_sq:
            if ch == "(":
                state = open_curve
            else:
                text_content += ch
        elif state == open_curve:
            if ch == ")":
                state = closed_curve
            else:
                link_url += ch
        elif state == closed_curve:
            text_content += ch

    if len(link_url) == 0:
        # no markdown link found, consider it all one url
        link_url = text_content
        text_content = ""

    return text_content.strip(), link_url.strip()


def _format_lat_or_long(val: str) -> None:
    return val.strip("+")


def validate_geo(geo_body_raw: str) -> str:
    geo_body = geo_body_raw.strip()
    if geo_body == "":
        return ""

    try:
        parsed_lat = _format_lat_or_long(LAT_REGEX.match(geo_body).group(1))
        parsed_long = _format_lat_or_long(LONG_REGEX.match(geo_body).group(1))
        if not parsed_lat and not parsed_long:
            raise ValueError(f"Could not parse geolocation: {geo_body}")
        return f"{parsed_lat}, {parsed_long}"
    except AttributeError:
        raise ValueError(f"Could not parse geolocation: {geo_body}")


def parse_state(state, text):
    source_link = f"https://github.com/2020PB/police-brutality/blob/main/reports/{state}.md"
    city = ""
    if state == "Washington DC":
        city = "DC"
    if state == "Unknown Location":
        city = ""

    clean_entry = {
        "links": [],
        "links_v2": [],
        "state": state,
        "edit_at": source_link,
        "city": city,
        "description": "",
        "tags": [],
        "geolocation": "",
    }
    entry = copy.deepcopy(clean_entry)

    for line in text.splitlines():
        line = line.strip()

        # if len(line) < 2:
        #     continue

        starts_with = ""
        for char in line:
            if char in ("*", "#", "-"):
                starts_with += char
            else:
                break

        if entry["links"] and "#" in starts_with:
            # We found a new city name so we must finish this `entry`
            # and start a fresh new one
            # Let the outer loop have this completed entry
            yield finalize_entry(entry)

            # Start a new entry
            entry = copy.deepcopy(clean_entry)
            # If we already parsed a city, keep it in there
            entry["city"] = city

        # remove the prefix
        line = line[len(starts_with) :].strip()

        if starts_with == "##":
            city = line
            entry["city"] = city
        elif starts_with == "###":
            name, date, date_text = title_to_name_date(line)
            # print(name, date)
            entry["name"] = name
            entry["date"] = date
            entry["date_text"] = date_text
        elif starts_with == "*":
            link_text, link_url = find_md_link_or_url(line)
            if link_url:
                entry["links"].append(link_url)
                entry["links_v2"].append(
                    {
                        "url": link_url,
                        "text": link_text,
                    }
                )
            else:
                print("Data build failed, exiting")
                critical_exit(f"Failed link parse '{line}' in state '{state}'")
        elif starts_with == "**":
            # **links** line
            pass
        else:
            # Text without a markdown marker, this might be the description or metadata
            id_prefix = "id:"
            tags_prefix = "tags:"
            lat_long_prefix = "geolocation:"
            if line.startswith(id_prefix):
                entry["id"] = line[len(id_prefix) :].strip()
            elif line.startswith(tags_prefix):
                spacey_tags = line[len(tags_prefix) :].split(",")
                entry["tags"] = [tag.strip() for tag in spacey_tags]
            elif line.startswith(lat_long_prefix):
                entry["geolocation"] = validate_geo(line[len(lat_long_prefix) :].lstrip())
                pass
            else:
                # Add a line to the description, but make sure there are no extra
                # new lines surrounding it.
                # entry["description"] = (entry["description"] + '\n' + line).strip()
                # We want to allow as many newlines as are already in the middle of the description
                # but not allow any extra newlines in the end or beginning. The only way
                # to do that right now is right before we `yield`
                entry["description"] += line + "\n"

    if entry and entry["links"]:
        yield finalize_entry(entry)
    else:
        raise ValueError(f"Failed links parse: missing links for {entry}")


def process_md_texts(md_texts):
    data = []
    for state, text in md_texts.items():
        for entry in parse_state(state, text):
            data.append(entry)
    return data


updated_at = datetime.now(timezone.utc).isoformat()

md_header = f"""
GENERATED FILE, PLEASE MAKE EDITS ON MASTER AT https://github.com/2020PB/police-brutality/

UPDATED AT: {updated_at}

"""

md_out_format = """
# {location}

{text}

"""


def to_merged_md_file(md_texts, target_path):
    with open(target_path, "wb") as fout:
        fout.write(md_header.encode("utf-8"))
        for location, text in sorted(md_texts.items()):
            out_text = md_out_format.format(location=location, text=text)
            fout.write(out_text.encode("utf-8"))
    print(f"Written merged .md data to {target_path}")


def to_csv_file_v1(data, target_path):
    max_link_count = max(len(it["links"]) for it in data)
    flat_data = []
    for row in data:
        # just write it but instead of a list of links
        # put each link in its own column
        flat_row = row.copy()
        links = flat_row["links"]
        del flat_row["links"]
        for i in range(max_link_count):
            url = ""
            if i < len(links):
                url = links[i]
            flat_row[f"Link {i + 1}"] = url
        flat_data.append(flat_row)

    with open(target_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, flat_data[0].keys())
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"Written .csv data to {target_path}")


def to_json_file_v1(data, target_path):
    data_with_meta = {
        "edit_at": "https://github.com/2020PB/police-brutality",
        "help": "ask @ubershmekel on twitter",
        "updated_at": updated_at,
        "data": data,
    }
    with open(target_path, "w") as f:
        json.dump(data_with_meta, f)
    print(f"Written .json data to {target_path}")


def v2_only(item):
    item = copy.deepcopy(item)
    item["links"] = item["links_v2"]
    del item["links_v2"]
    return item


def to_json_file_v2(data, target_path):
    v2_data = [v2_only(item) for item in data]
    data_with_meta = {
        "edit_at": "https://github.com/2020PB/police-brutality",
        "help": "ask @ubershmekel on twitter",
        "updated_at": updated_at,
        "data": v2_data,
    }
    with open(target_path, "w") as f:
        json.dump(data_with_meta, f)
    print(f"Written .json v2 data to {target_path}")


readme_text = """
# /r/2020PoliceBrutality/ dataset

This repository exists to accumulate and contextualize evidence of police brutality during the 2020 George Floyd protests.

Our goal in doing this is to assist journalists, politicians, prosecutors, activists and concerned individuals who can use the evidence accumulated here for political campaigns, news reporting, public education and prosecution of criminal police officers.

* This branch is just the files generated by parsing the markdown for ease of building other sites.
* For example your webapp can query and display data from https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json
* For more info see https://github.com/2020PB/police-brutality
* These data files are generated by https://github.com/2020PB/police-brutality/tree/main/tools

# THESE FILES ARE GENERATED - DO NOT EDIT (including this readme)

* Please edit the `.md` files on the `main` branch at https://github.com/2020PB/police-brutality
* Also notice each data row has a `edit_at` link so you can find the source data for every entry.

"""


def to_readme(target_path):
    with open(target_path, "w") as f:
        f.write(readme_text)


def read_all_data():
    md_texts = read_all_md_files(md_dir)
    data = process_md_texts(md_texts)
    return data


def v1_only(item):
    # Deepcopy to avoid affecting the original data
    item = copy.deepcopy(item)
    v1_keys = set(["links", "state", "city", "edit_at", "name", "date", "date_text", "id"])
    # Cache keys to avoid errors for deleting while iterating
    item_keys = list(item.keys())
    for key in item_keys:
        if key not in v1_keys:
            del item[key]
    return item


if __name__ == "__main__":
    md_texts = read_all_md_files(md_dir)
    data = process_md_texts(md_texts)
    to_merged_md_file(md_texts, combined_fpath)

    to_json_file_v2(data, json_fpath_v2)

    v1_data = [v1_only(item) for item in data]
    to_csv_file_v1(v1_data, csv_fpath_v1)
    to_json_file_v1(v1_data, json_fpath_v1)
    to_readme(readme_fpath)

    print("Done!")
