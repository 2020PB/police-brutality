import os

#   Parse file into a unstructured format
#   Array of json

# First country, US only right now

# Files are by state
def load_and_convert_all_files(directory_path, output_file_dir):
    print("Loading data from all files in ["+directory_path+"]")
    for file_name in os.listdir(directory_path):
        with open(directory_path+"/"+file_name) as raw_file:
            file_contents = raw_file.read()
            with open(output_file_dir, 'at') as output_file:
                # Convert single file
                json_file_convert = convert_file_to_json(file_name, file_contents)
                # Aggregate all files into one
                for entry in json_file_convert:
                    output_file.write(str(entry)+"\n")

# Load file split into entries

def convert_file_to_json(file_name, file_contents):
    
    city_entries = list()
    #strip newlines and add spaces
    file_contents = file_contents.replace('\n',' ')
    #split up to areas inside state
    file_contents_by_city = break_string_by_heading2(file_contents)
    #skip blank lines and group data
    heading = "" 
    body = ""
    for n in range(0, len(file_contents_by_city)):
        if file_contents_by_city[n] == '':
            continue
        if file_contents_by_city[n].endswith('#') and not file_contents_by_city[n].__contains__('http'):
            heading = file_contents_by_city[n]
            continue
        #else attach to previous
        body = split_incident_and_links(file_contents_by_city[n])
        city_entries.append(create_city_entry(heading, body))

    print("Converted and loaded: "+file_name)
    return(city_entries)

def break_string_by_heading2(string_to_break):
    return(string_to_break.split('## '))

def create_city_entry(city_name, incident_list):
    return({"city":city_name, "incidents":incident_list})

def split_incident_and_links(incident_block):
    incident_split = incident_block.split("**Links**")
    incident_description = ""
    incident_links = ""
    if(len(incident_split)>1):
        incident_description = incident_split[0]
        incident_links = incident_split[1].split('*')
    else:
        incident_description = incident_block
    if incident_links.__contains__('  '): incident_links.remove('  ')
    return(create_incident_entry(incident_description, incident_links))

def create_incident_entry(incident_description, incident_links):
    return({"incident_description":incident_description, "incident_links":incident_links})

load_and_convert_all_files("../reports", "../output.json")
