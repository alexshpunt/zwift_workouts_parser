from webhelper import get_filtered_web_content 
from parsing import WorkoutPlan, WorkoutPlansCollection

def get_plans_web_content(url): return get_filtered_web_content(url, 'div', 'card')
def get_workouts_web_content(url): return get_filtered_web_content(url, 'article', 'workout')

class Parser:
    def __init__(self, export_dir, *urls) -> None:
        for url in urls: 
            parser = self.get_parser(url) 
            if not parser: print(f"Couldn't find a parser for {url} hence skipping it.")
            else: parser.save(export_dir) 
    
    def get_parser(self, url):
        plans = get_plans_web_content(url); 
        if plans: return WorkoutPlansCollection(plans)

        workouts = get_workouts_web_content(url) 
        if workouts: return WorkoutPlan(workouts)

        return None 