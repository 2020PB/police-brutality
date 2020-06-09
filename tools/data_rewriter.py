import data_builder

def rewrite_data(data):
    print(data[0])
    print(data[0].keys())
    state_to_rows = {}
    for row in data:
        state = row["state"]
        if state not in state_to_rows:
            state_to_rows[state] = []
        state_to_rows[state].append(row)
    
    # We don't need to sort because we read these in the order of the markdown files
    #for state, data_rows in state_to_rows.items():
    #    data_rows.sort(key=lambda row: row["city"] + row["id"])

    for state, data_rows in state_to_rows.items():
        out_path = f"{data_builder.md_dir}/{state}.md"
        print(out_path)
        # links, city, description, name, date_text, id
        new_md_text = gen_md_from_rows(data_rows)
        with open(out_path, "wb") as fout:
            fout.write(new_md_text.encode("utf-8"))

row_format = '''
### {name} | {date_text}

{description}

**Links**

{links_md}
'''

def gen_md_from_rows(rows):
    city = ''
    lines = []
    for row in rows:
        if row["city"] and row["city"] != city:
            # new city, let everyone know
            lines.append(f'## {row["city"]}')
            city = row["city"]
        
        # convert links list to a links string
        links_md = '\n'.join('* ' + it for it in row["links"])
        row["links_md"] = links_md

        # Create this row's markdown
        lines.append(row_format.format(**row))
    
    return '\n'.join(lines)


if __name__ == "__main__":
    data = data_builder.read_all_data()
    rewrite_data(data)

