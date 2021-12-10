import helper as Helper
from workout import ZWorkoutFile

def get_plans_web_content(url): return Helper.get_filtered_web_content(url, 'div', 'card')
def get_workouts_web_content(url): return Helper.get_filtered_web_content(url, 'article', 'workout')

class Parser:
    def __init__(self, export_dir, *urls) -> None:
        self.export_dir = export_dir
        for i, url in enumerate(urls): 
            print(f'Parsing url {url} ({i+1}/{len(urls)})')
            parsed = self.try_parse(url) 
            if not parsed: 
                print(f"Couldn't find a parser for {url} hence skipping it.")
                continue
    
    def try_parse(self, url):
        parsed = self.try_parse_plans(url); 
        if not parsed: 
            parsed = self.try_parse_workout(url);  
        return parsed 

    def try_parse_plans(self, url):
        plans_data = get_plans_web_content(url); 
        if not plans_data: return False;   
        any_parsed = False  
        for i, plan_data in enumerate(plans_data):
            card_sports = plan_data.find('div', class_='card-sports')
            if not card_sports: continue

            card_classes = card_sports.i['class']
            valid = Helper.is_valid_sport_type(card_classes) 
            url = plan_data.find('a', class_='button')['href']

            if not valid: 
                print(f"Couldn't parse {url} because some of the {card_classes} sports are not suppored yet") 
                continue

            print(f"Parsing plan ({i+1}/{len(plans_data)})")
            self.try_parse_workout(url)
            any_parsed = True 
        return any_parsed 

    def try_parse_workout(self, url):
        workouts_data = get_workouts_web_content(url) 
        if not workouts_data: 
            print(f"Coulnd't get workout data by {url} for unknown reason.")
            return False 

        for i, workout_data in enumerate(workouts_data): 
            print(f"- Parsing workout ({i+1}/{len(workouts_data)})")
            ZWorkoutFile(workout_data).save(self.export_dir)
        return True 