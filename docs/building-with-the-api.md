The [structured dataset](https://github.com/2020PB/police-brutality/tree/data_build) is built by a [script](https://github.com/2020PB/police-brutality/tree/master/tools) that processes the data every time a change is made. This allows sites to ingest the data and build new front ends.

# Built with the dataset

* http://www.2020protesters.com/ - 
* https://policebrutality.netlify.app/ - list of events you can visually see per state, per city, and link to the specific incident.
* https://onebadapple.org/ - Mega list of events.
* https://bread.codes/PoliceBrutality/ - Timeline of police brutality events.
* https://too-many-incidents.netlify.app/ - see the incidents as cards, sort by date, and location.
* https://frontend-1750f.web.app/ - map of incidents with links.
* https://maminian.github.io/brutality-map/ - map of incidents with links.
* https://2020policebrutality.netlify.app/ - click on a state to see the links visually.
* https://datastudio.google.com/s/oFSSsjw2kAY - a dashboard with stats on a state and city level.
* http://api.policebrutality.io/v1/videos - a REST API that points to backed up video files. Managed at https://github.com/nickatnight/policebrutality.io
* https://github.com/2020PB/police-brutality/tree/master/tools/downloader - a tool to back up videos from this database to your local computer.
* https://codepen.io/949mac/pen/abdOggV - an example of using the API with jQuery

# How to start building your own front end

What will you build?

* Go to https://github.com/2020PB/police-brutality/tree/data_build
* Choose which API you'd like to consume from a markdown, CSV or JSON file.
* Most folks should [use the JSON file](https://raw.githubusercontent.com/2020PB/police-brutality/data_build/all-locations.json)
* You can also use the [846 API](https://github.com/949mac/846-backend) if you need lat-long-geo information from [here](https://api.846policebrutality.com/api/incidents), or direct links to video evidence from [here](https://api.846policebrutality.com/api/incidents?include=evidence)
