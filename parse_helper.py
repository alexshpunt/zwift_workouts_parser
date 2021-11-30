from __future__ import annotations
from bs4 import BeautifulSoup, element

class ParseHelper: 
    def convert_to_string(data):
        output = [] 
        if isinstance(data, element.NavigableString): return data.string
        for content in data.contents:
            if isinstance(content, str): output.append(content)
            else: output.extend([ParseHelper.convert_to_string(c) for c in content.contents])
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