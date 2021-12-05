from __future__ import annotations
from bs4 import BeautifulSoup, element
from webhelper import get_web_content, get_plans_web_content, get_workouts_web_content
from typing import Dict
from workout import ZWorkoutFile
from parsersettings import ParserSettings

class WorkoutPlan():
    def __init__(self, workouts_data) -> None:
        self.workouts = [] 
        for workout in workouts_data:
            self.workouts.append(ZWorkoutFile(workout))
            
    def save(self, export_dir):
        for workout in self.workouts:
            workout.save(export_dir); 

class WorkoutPlansCollection():
    def __init__(self, plans_data) -> None:
        self.plans = [] 
        for data in plans_data:
            card_classes = data.find('div', class_='card-sports').i['class']
            self.valid = ParserSettings.is_valid_sport_type(card_classes) 
            self.url = data.find('a', class_='button')['href']

            if not self.valid: 
                print(f"Couldn't parse {self.url} because some of the {card_classes} sports are not suppored yet") 
            else: 
                workout_data = 
                self.plans.append(WorkoutPlan(data))
            
    def save(self, export_dir):
        for plan in self.plans: 
            plan.save(export_dir)
