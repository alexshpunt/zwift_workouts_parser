import argparse  
from zparser import Parser 

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description="Parses Zwift workouts from www.whatsonzwift.com")
    parser.add_argument('urls', metavar='URLs', type=str, nargs="+", help="an URL of the workout to parse")
    parser.add_argument("--output",  nargs="?", help="output directory of the parsed workouts")
    args = vars(parser.parse_args()) 
    
    if 'urls' in args and args['urls']: 
        urls = args['urls'] 
        export_dir = args['output'] if 'output' in args and args['output'] else 'export/'
        Parser(export_dir, *urls)