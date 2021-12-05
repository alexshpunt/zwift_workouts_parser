from webhelper import get_filtered_web_content 
from parsing import WorkoutPlan, WorkoutPlansCollection
from parsersettings import ParserSettings
from workout import ZWorkoutFile

def get_plans_web_content(url): return get_filtered_web_content(url, 'div', 'card')
def get_workouts_web_content(url): return get_filtered_web_content(url, 'article', 'workout')

class Parser:
    def __init__(self, export_dir, *urls) -> None:
        for url in urls: 
            parser = self.get_parser(url) 
            if not parser: print(f"Couldn't find a parser for {url} hence skipping it.")
            else: parser.save(export_dir) 
    
    def get_parser(self, url):
        plans = self.try_parse_plans(url); 
        if plans: return plans

        workouts = self.try_parse_workout(url);  
        if workouts: return workouts 
        return None 

    def try_parse_plans(self, url):
        plans_data = get_plans_web_content(url); 
        if not plans_data: return None   

        plans = []
        for plan_data in plans_data:
            card_classes = plan_data.find('div', class_='card-sports').i['class']
            valid = ParserSettings.is_valid_sport_type(card_classes) 
            url = plan_data.find('a', class_='button')['href']

            if not valid: 
                print(f"Couldn't parse {url} because some of the {card_classes} sports are not suppored yet") 
                return None 

            workouts = self.try_parse_workout(url)
            if workouts: plans.append(workouts) 
        return plans; 

    def try_parse_workout(self, url):
        workouts_data = get_workouts_web_content(url) 
        if not workouts_data: 
            print(f"Coulnd't get workout data by {url} for unknown reason.")
            return None 

        workouts = []
        for workout_data in workouts_data: 
            workouts.append(ZWorkoutFile(workout_data)) 
        return workouts 