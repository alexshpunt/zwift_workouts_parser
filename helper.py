from bs4 import BeautifulSoup, element
import unicodedata
import re

def convert_to_string(data):
    output = [] 
    if isinstance(data, element.NavigableString): return data.string
    for content in data.contents:
        if isinstance(content, str): output.append(content)
        else: output.extend([convert_to_string(c) for c in content.contents])
    return "".join(output)

def parse_cadence(row: str) -> int:
    keyword = 'rpm'

    if keyword not in row: return -1, row 
    if ',' in row: keyword += ','

    cadence, rest = row.split(keyword)
    if '/' in cadence: cadence = sum([int(c) for c in cadence.split('/')])/2 
    return int(cadence), rest 

def parse_power(row: str) -> int:
    power = row 
    if '%' in power: power, _ = power.split('%')
    if 'W' in power: power, _ = power.split('W')
    return float(power)/100

def parse_duration(row: str) -> int: 
    import re 
    prog = re.compile('^\d+$')
    seconds = 0 
    if 'hr' in row: 
        hr, row = row.split('hr') 
        seconds += int(hr) * 3600 
    if 'min' in row: 
        min, row = row.split('min')
        min = "".join(re.findall('\d+', min)) #Add this to all the time values
        seconds += int(min) * 60 
    if 'sec' in row: 
        sec, _ = row.split('sec')
        seconds += int(sec)
    return seconds

def is_valid_sport_type(class_value):
    return len([s for s in class_value if 'bike' in s]) > 0

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def get_web_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Vivaldi/4.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    import ssl, certifi, urllib.request
    req = urllib.request.Request(url, headers=headers)
    context = ssl.create_default_context(cafile=certifi.where())
    response = urllib.request.urlopen(req, context=context)
    return response.read().decode('utf-8')

def get_filtered_web_content(url, tag, tag_class):
    content = get_web_content(url)

    soup = BeautifulSoup(content, features='html.parser')
    return soup.find_all(tag, class_ = tag_class)