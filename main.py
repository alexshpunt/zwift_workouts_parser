import json
from xml.etree.ElementTree import parse 
with open('settings.json') as f: 
    settings = json.load(f)
    
urls = [] 
if 'urls' in settings: 
    urls.extend(settings['urls'])

export_dir = settings['exportDir']
plans_url = settings['plansUrl'] 

plans_url = "https://whatsonzwift.com/workouts/olympic-tri-prep-plan/week-1-day-2-bike"
from zparser import Parser 
Parser(export_dir, plans_url)

import sys 
if __name__ == '__main__': 
    print(sys.argv)