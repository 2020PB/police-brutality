import os
import re
import csv
import subprocess
import glob

from dateutil.parser import parse

src_dir = os.path.relpath(os.path.dirname(__file__))
md_dir = os.path.join(src_dir, '..', 'reports')

def title_to_name_date(line):
  parts = line.split('|')
  name = parts[0].strip()
  if len(parts) == 1:
    return line.strip(), '', ''
  date_text = parts[1].strip()
  try:
    date = parse(date_text).strftime('%Y-%m-%d')
  except ValueError:
    print(f"Failed date parse '{date_text}'")
    date = ''
  return name, date, date_text

md_texts = {}
for md_file in glob.glob(md_dir + '/*.md'):
  print(md_file)

  with open(md_file, 'rb') as fin:
    fname = os.path.basename(md_file)
    state_name = fname.replace('.md', '')
    md_texts[state_name] = fin.read().decode('utf-8')

combined_fpath = os.path.join(src_dir, '..', "all-locations.md")
csv_fpath = os.path.join(src_dir, '..', 'all-locations-parsed.csv')

with open(combined_fpath, 'wb') as fout:
  for location, text in sorted(md_texts.items()):
    out_text = '# ' + location + '\n\n' + text + '\n\n\n\n'
    fout.write(out_text.encode('utf-8'))

print(f"Got {len(md_texts)} locations")

def parse_state(state, text):
  entry = {"links": [], "state": state}
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
      #print(entry)
      last_entry = entry
      yield entry
      entry = {"links": [], "state": state}
    
    # remove the prefix
    line = line[len(starts_with):]

    # if starts_with == '#':
    #   entry["state"] = line.strip()
    if starts_with == '##':
      entry["city"] = line.strip()
    if starts_with == '###':
      name, date, date_text = title_to_name_date(line.strip())
      #print(name, date)
      entry["name"] = name
      entry["date"] = date
      entry["date_text"] = date_text
    if starts_with == '*':
      entry["links"].append(line.strip())
  
  if entry and entry["links"]:
    yield entry

def process_md_texts(md_texts):
  data = []
  for state, text in md_texts.items():
    for entry in parse_state(state, text):
      #print(entry)
      data.append(entry)
  return data

data = process_md_texts(md_texts)
max_link_count = max(len(it["links"]) for it in data)
print(f"max_link_count {max_link_count}")

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

with open(csv_fpath, 'w', newline='', encoding='utf-8') as fout:
  writer = csv.DictWriter(fout, flat_data[0].keys())
  writer.writeheader()
  writer.writerows(flat_data)

print("done")

