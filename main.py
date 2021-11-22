from bs4 import BeautifulSoup, element
import xml.etree.ElementTree as ET 

from intervals import * 
from workout import * 

def purify_workout_data(data : element.Tag): 
    workout = []
    for row in data.find_all('div'):
        workout_set = [] 
        for content in row.contents: 
            if isinstance(content, element.Tag): workout_set.append("".join(content.contents)) 
            else: workout_set.append(content)
        workout.append("".join(workout_set))
    return workout

#move to params 
url = "https://whatsonzwift.com/workouts/gran-fondo/week-2-1-long-tempo-intervals"
# url = "https://whatsonzwift.com/workouts/mattias-thyr-unstructured-workouts/szrgwo-021-"
# url = "https://whatsonzwift.com/workouts/gcn-zero-to-hero-plan/week-1-initial-testing-7-sat-or-sun-free-ride"

#move to file 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Vivaldi/4.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

import ssl
from urllib import request
import certifi
context = ssl.create_default_context(cafile=certifi.where())
req = request.Request(url, headers=headers)
response = request.urlopen(req, context=context)
content = response.read().decode('utf-8')
soup = BeautifulSoup(content, features='html.parser')

breadcrumbs = [item.string.strip() for item in soup.select_one('div.breadcrumbs')] 
breadcrumbs = [item for item in breadcrumbs if len(item) > 0 and item != '»' and item != 'Workouts']
filename = breadcrumbs.pop(-1)
directory = 'export/' + '/'.join(breadcrumbs)

workout_data = soup.select_one('div.one-third.column.workoutlist')
pure_workout_data = purify_workout_data(workout_data) 
parsed_workout = ZWorkout.parse(pure_workout_data)

workout_overview = soup.select_one('div.overview')
workout_author = 'Zwift Workouts Parser'
workout_desc = workout_overview.next_sibling
if 'Author' in workout_overview.next_sibling.string:
    workout_author = workout_overview.next_sibling
    workout_desc = workout_author.next_sibling

if not isinstance(workout_author, str) and 'Author' in workout_author.string: 
    _, workout_author = workout_author.string.split('Author:')
workout_desc = workout_desc.get_text("\n")

workout_file = ZWorkoutFile(parsed_workout, 
                            name=filename, author=workout_author.strip(), description=workout_desc) 
data = workout_file.write()
text = ET.tostring(data)
xml_header = b'<?xml version="1.0" encoding="utf-8"?>'
pretty_text = BeautifulSoup(text, 'xml').prettify().encode('utf-8')
pretty_text = pretty_text.replace(xml_header, b'').strip()

from os import path, makedirs
if not path.isdir(directory): makedirs(directory)

from utility import slugify
with open(f"{directory}/{slugify(filename, True)}.zwo", 'wb') as f: 
    f.write(pretty_text)