from __future__ import annotations
from bs4 import BeautifulSoup, element
from webhelper import get_web_content
from typing import Dict
from workout import ZWorkout, ZWorkoutFile

def is_valid_sport_type(class_value):
    return len([s for s in class_value if 'bike' in s]) > 0

def get_meta_data(workout: element.Tag):
    invalid_meta_data = (None, None)
    breadcrumbs = workout.select_one('div.breadcrumbs')
    header = breadcrumbs.find('h4')
    sport_type = header['class']
    if not is_valid_sport_type(sport_type): return invalid_meta_data 
    try: 
        breadcrumbs = [item.string.strip() for item in workout.select_one('div.breadcrumbs')] 
    except Exception as e: 
        #Sometimes if @ is contained in the breadcrumbs, it might be obfuscated with Cloudflare, so 
        # it's not really possible to deobfuscate it back. This is why we just ignore it.  
        return invalid_meta_data 
    breadcrumbs = [item for item in breadcrumbs if len(item) > 0 and item != '»' and item != 'Workouts']
    filename = breadcrumbs.pop(-1)
    directory = '/'.join(breadcrumbs)
    return directory, filename

def get_workout_data(url):
    content = get_web_content(url)
    soup = BeautifulSoup(content, features='html.parser')
    workouts = soup.find_all('article', class_ = 'workout')
    return workouts

def save_plan(plan_url, export_dir): 
    workouts = get_workout_data(plan_url)
    from tqdm import tqdm

    for workout in workouts:
        save_workout(workout, export_dir)

def save_workout(workout, export_dir): 
    directory, filename = get_meta_data(workout)
    if not directory or not filename: return #We can't really parse it, if there is some issue with the meta data
    try:
        text = ZWorkoutFile.parse(workout, filename)
    except Exception as e:
        print(f"Skipping {directory}/{filename} because of {e}")
        return
    print(f'Parsed {directory}/{filename}')
    from utility import slugify
    directory = f"{export_dir}/{slugify(directory)}"

    from os import path, makedirs
    if not path.isdir(directory): makedirs(directory)

    with open(f"{directory}/{slugify(filename, True)}.zwo", 'wb') as f: 
        f.write(text)

def parse_plans(url, export_dir): 
    content = get_web_content(url)
    soup = BeautifulSoup(content, features='html.parser')
    plans = soup.find_all('div', class_ = 'card')
    for plan in plans: 
        card_classes = plan.find('div', class_='card-sports').i['class']
        if not is_valid_sport_type(card_classes): continue
        plan_url = plan.find('a', class_='button')['href']
        save_plan(plan_url, export_dir)