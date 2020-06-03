# Compile the reports from all over into easily-accessible databases in SqLite, JSON, and CSV
# Create 3 files: reports.[json|csv|db], one for each format
#
# From the reports, scrape the state, city, title, date, description and links for each incident
#	Each markdown file is named for the state it represents. H2 is the city. H3 is formatted as: /(title) ?\| ?(date)/
# The unformatted line below the title is the description
# Links are separated in an unordered list
#
# Not all columns in the database have to be filled. For example, some incidents have occurred in unknown locations, hence the name of the file.
import os, sys, pathlib, subprocess, bs4, copy, sqlite3, json

# Assume this file exists at the root of the project
# Normalize the path to this file, then extract the directory tree and move into it
path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(path)

# Get a list of all the states reporting incidents by listing the directory 'reports'
# Each file name fills the state column in the database, except for 'Unknown Location.md' which should fill null
states = os.listdir("reports")

# Extract the contents of each file into an object ('data')
data = {}

# Input html from report file. Output a row of data as an object containing city, title, description, date, links
# Parse html with beautifulsoup4 to easily search through objects
def extract_incidents(html):
	data = []
	html = bs4.BeautifulSoup(html.stdout, "html.parser")

	struct = {
		"city": None,
		"title": None,
		"description": [],
		"date": None,
		"links": []
	}

	element = html.h2
	while (element != None):
		if (element.name == "h2"):# city
			struct["city"] = element.string
		elif (element.name == "h3"):# incident title | date
			n = element.string.split(" | ")
			if len(n) == 2:
				title, date = n
			elif len(n) == 1:
				title = n[0]
				date = None
			else:
				title = None; date = None
			struct["title"] = title
			struct["date"] = date

			struct["description"] = []# reset with new incident
			struct["links"] = []
		elif (element.name == "p" and not element.contents[0].name == "strong" and element.string != None):# description
			if type(struct["description"]) == list:
				struct["description"].append(element.string)
			elif type(struct["description"]) == str:
				struct["description"] += element.string
		elif (element.name == "ul"):# links
			struct["description"] = '\n'.join(struct["description"])

			for l in element.children:
				if l.string != '\n':
					struct["links"].append(l.string)

			data.append(copy.copy(struct))

		element = element.next_sibling

	return data

# Convert messy markdown documents into simple html, which can be easily manipulated
for s in states:
	state = pathlib.PurePath(s).stem# get the file name without the extension. Files cannot be trusted to have .md extension
	html = subprocess.run(["perl", "Markdown.pl", f"reports/{s}"], capture_output=True, encoding="utf-8")

	data[state] = extract_incidents(html)

#https://www.sqlitetutorial.net/sqlite-tutorial/sqlite-export-csv/

# Store collected data into the database formats
sql = sqlite3.connect("reports.db")
cursor = sql.cursor()
cursor.execute("""
	DROP TABLE IF EXISTS incidents;
""")
cursor.execute("""
	CREATE TABLE IF NOT EXISTS incidents (
		state TEXT,
		city TEXT,
		title TEXT NOT NULL,
		date TEXT,
		description TEXT,
		links TEXT
	);
""")

for state in data:
	for incident in data[state]:
		try:
			cursor.execute("""
					INSERT INTO incidents
					VALUES (?, ?, ?, ?, ?, ?);
				""",
				(state,
				incident["city"],
				incident["title"],
				incident["date"],
				incident["description"],
				json.dumps(incident["links"]))
			)
		except:
			print(state, incident)

sql.commit()
sql.close()