import helper as Helper
from workout import ZWorkoutFile

def get_plans_web_content(url): return Helper.get_filtered_web_content(url, 'div', 'card')
def get_workouts_web_content(url): return Helper.get_filtered_web_content(url, 'article', 'workout')

class Parser:
    def __init__(self, export_dir, *urls) -> None:
        self.export_dir = export_dir
        for url in urls: 
            print(url)
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
        for plan_data in plans_data:
            card_sports = plan_data.find('div', class_='card-sports')
            if not card_sports: return False 

            card_classes = card_sports.i['class']
            valid = ParserSettings.is_valid_sport_type(card_classes) 
            url = plan_data.find('a', class_='button')['href']

            if not valid: 
                print(f"Couldn't parse {url} because some of the {card_classes} sports are not suppored yet") 
                return False 

            self.try_parse_workout(url)
            print(f"Parsed plan: {url}")
        return True 

    def try_parse_workout(self, url):
        workouts_data = get_workouts_web_content(url) 
        if not workouts_data: 
            print(f"Coulnd't get workout data by {url} for unknown reason.")
            return False 

        for workout_data in workouts_data: 
            ZWorkoutFile(workout_data).save(self.export_dir)
        return True 