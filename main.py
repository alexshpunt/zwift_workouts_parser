import json 
with open('options.json') as f: 
    options = json.load(f)
    
urls = [] 
if 'urls' in options: 
    urls.extend(options['urls'])

from parsing import save_workout
for url in urls: 
    save_workout(url)