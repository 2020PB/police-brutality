#!/usr/bin/env python3

"""This parses data from markdown files in reports directory."""

import re
from os import listdir
from os.path import isfile, join

# Set to True to enable print summary lines for each incident
# False will just display totals by state
show_summaries = False

# Vars, defaults should be fine
path = 'reports'
files = [f for f in listdir(path) if isfile(join(path, f))]
summary = dict()
total = 0
search_term = re.compile('^### .*$')  # Needs to match summary line format.

# Parse data out of markdown files
for f in files:
    state = f.strip('.md')
    state_count = 0
    with open(f'{path}/{f}') as f:
        content = f.read().splitlines()
        matches = list(filter(search_term.match, content))
        if matches:
            total += len(matches)  # Add to total
            summary[state] = list() # store by state
            for match in matches:
                if len(match) > 0:
                    summary[state].append(match.strip('### '))

def print_summaries(lines):
    """Used to optionally print summary lines"""
    for line in lines:
        print(f'    {line}')
    print('-------------')
    
# Display results
print(f'Total Number of Incidents: {total}')
for k in sorted(summary.keys()):
    state_total = len(summary[k])
    print(f'  {k}: {state_total} incidents')

    # Uncomment below for summary of each incidenta
    if show_summaries is True:
        print_summaries(summary[k])
