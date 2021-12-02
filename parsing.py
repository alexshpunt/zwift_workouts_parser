from __future__ import annotations
from bs4 import BeautifulSoup, element
from webhelper import get_web_content, get_plans_web_content, get_workout_web_content
from typing import Dict
from workout import ZWorkout, ZWorkoutFile

class ParserSettings():
    def is_valid_sport_type(class_value):
        return len([s for s in class_value if 'bike' in s]) > 0

class Workout():
    def __init__(self, workout) -> None:
        self.directory, self.filename = (None, None)
        breadcrumbs = workout.select_one('div.breadcrumbs')
        sport_type = breadcrumbs.find('h4')['class']

        self.valid = ParserSettings.is_valid_sport_type(sport_type)
        if not self.valid: return 
        
        try: 
            breadcrumbs = [item.string.strip() for item in breadcrumbs] 
        except Exception as e: 
            #Sometimes if @ is contained in the breadcrumbs, it might be obfuscated with Cloudflare, so 
            # it's not really possible to deobfuscate it back. This is why we just ignore it.  
            self.valid = False
            return 

        breadcrumbs = [b for b in breadcrumbs if len(b) > 0 and b != '»' and b != 'Workouts']
        self.filename = breadcrumbs.pop(-1)
        self.directory = '/'.join(breadcrumbs)

        try:
            self.file = ZWorkoutFile(workout)
        except Exception as e:
            self.exception = e 
            self.valid = False 
        
    def __repr__(self) -> str:
        return f"{self.directory}/{self.filename}" if self.valid else 'Invalid Workout'
        
    def save(self, export_dir):
        if not self.valid: return 

class WorkoutPlan():
    def __init__(self, plan) -> None:
        card_classes = plan.find('div', class_='card-sports').i['class']
        self.valid = ParserSettings.is_valid_sport_type(card_classes) 
        self.url = plan.find('a', class_='button')['href']
        self.workouts = [] 

        if not self.valid: return 

        workouts_data = get_workout_web_content(self.url)
        for workout in workouts_data:
            self.workouts.append(Workout(workout))
            
    def save(self, export_dir):
        for workout in self.workouts:
            workout.save(export_dir); 

class WorkoutPlansCollection():
    def __init__(self, url) -> None:
        self.plans = [] 
        plans_data = get_plans_web_content(url);  
        for data in plans_data:
            self.plans.append(WorkoutPlan(data))
            
    def save(self, export_dir):
        for plan in self.plans: 
            plan.save(export_dir)

class PlanParser():
    pass 

class WorkoutsParser():
    pass 


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
