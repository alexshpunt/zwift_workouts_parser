import json
from xml.etree.ElementTree import parse 
with open('settings.json') as f: 
    settings = json.load(f)
    
urls = [] 
if 'urls' in settings: 
    urls.extend(settings['urls'])

export_dir = settings['exportDir']
plans_url = settings['plansUrl'] 
from parsing import parse_plans
parse_plans(plans_url, export_dir)

import sys 
if __name__ == '__main__': 
    print(sys.argv)