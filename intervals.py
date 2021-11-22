from __future__ import annotations
import xml.etree.ElementTree as ET 
from interfaces import *


class ParseHelper: 
    def parse_interval(row : str) -> ZSteadyState: 
        if 'free ride' in row: return ZFreeRide.parse(row) #10min free ride 
        if 'from' in row and 'to' in row: return ZRangedInterval.parse(row) #1min from 50 to 90% FTP
        if 'x' in row: return ZIntervalsT.parse(row) #10x 3min @ 100% FTP, 1min @ 55% FTP
        return ZSteadyState.parse(row) #3min @ 100rpmm, 95% FTP
    
    def parse_cadence(row: str) -> int:
        if 'rpm,' not in row: return -1, row 
        cadence, rest = row.split('rpm,')
        return int(cadence), rest 

    def parse_power(row: str) -> int:
        power = row 
        if '%' in power: power, _ = power.split('%')
        return float(power)/100

    def parse_duration(row: str) -> int: 
        seconds = 0 
        if 'hr' in row: 
            hr, row = row.split('hr') 
            seconds += int(hr) * 3600 
        if 'min' in row: 
            min, row = row.split('min')
            seconds += int(min) * 60 
        if 'sec' in row: 
            sec, _ = row.split('sec')
            seconds += int(sec)
        return seconds


class ZSteadyState(Parsable, XMLWritable): 
    def parse(row : str) -> ZSteadyState:
        duration, row = [r.strip() for r in row.split('@')]
        duration = ParseHelper.parse_duration(duration)
        cadence, row = ParseHelper.parse_cadence(row)
        return ZSteadyState(duration, ParseHelper.parse_power(row), cadence)

    def __init__(self, duration, power, cadence = -1) -> None:
        self.duration = duration 
        self.power = power 
        self.cadence = cadence 

    def __repr__(self) -> str:
        return f'SteadyState (duration: {self.duration} power: {self.power} cadence: {self.cadence}'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'SteadyState')
        interval.set('Duration', str(self.duration))
        interval.set('Power', str(self.power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))
        return interval 

class ZRangedInterval(ZSteadyState): 
    def parse(row : str) -> ZRangedInterval:                 
        duration, row = row.split('from')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split('@')
            cadence, _ = ParseHelper.parse_cadence(cadence)
        duration = ParseHelper.parse_duration(duration)

        from_power, to_power = [ParseHelper.parse_power(p) for p in row.split('to')]
        if from_power < to_power: return ZWarmup(duration, from_power, to_power, cadence)
        
        else: return ZCooldown(duration, from_power, to_power, cadence)

    def __init__(self, duration, from_power, to_power, cadence = -1) -> None:
        self.duration = duration 
        self.from_power = from_power 
        self.to_power = to_power 
        self.cadence = cadence

    def __repr__(self) -> str:
        return f'{self.get_name()} (duration: {self.duration} from_power: {self.from_power} to_power: {self.to_power} cadence: {self.cadence})'

    def get_name(self) -> str: 
        return "ZRangedInterval"

    def write(self, root: ET.Element) -> ET.Element:
        name = self.get_name()#'Warmup' if self.from_power < self.to_power else 'Cooldown'
        interval = ET.SubElement(root, name)
        interval.set('Duration', str(self.duration))
        interval.set('PowerLow', str(self.from_power))
        interval.set("PowerHigh", str(self.to_power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))

class ZWarmup(ZRangedInterval): 
    def get_name(self) -> str:
        return "Warmup"

class ZCooldown(ZRangedInterval): 
    def get_name(self) -> str:
        return "Cooldown"

class ZIntervalsT(ZSteadyState): 
    def parse(row : str) -> ZIntervalsT: 
        number, rest =  row.split('x')
        first_interval, second_interval = [ZSteadyState.parse(r) for r in rest.split(',')]
        return ZIntervalsT(number, first_interval, second_interval)

    def __init__(self, number, first_interval : ZSteadyState, second_interval : ZSteadyState) -> None:
        self.number = number
        self.first_interval = first_interval 
        self.second_interval = second_interval 

    def __repr__(self) -> str:
        return f'IntervalT ({self.number} x {self.first_interval}, {self.second_interval})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'IntervalsT')
        interval.set('Repeat', str(self.number))
        interval.set('OnDuration', str(self.first_interval.duration))
        interval.set('OffDuration', str(self.second_interval.duration))
        interval.set("OnPower", str(self.first_interval.power))
        interval.set('OffPower', str(self.second_interval.power))
        interval.set('Cadence', str(self.first_interval.cadence))
        interval.set("CadenceResting", str(self.second_interval.cadence))
        pass 

class ZFreeRide(ZSteadyState): 
    def parse(row : str) -> ZFreeRide: 
        duration, _ = row.split('free ride')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split("@")
            cadence = ParseHelper.parse_cadence(cadence)
        duration = ParseHelper.parse_duration(duration)
        return ZFreeRide(duration, cadence)
        
    def __init__(self, duration, cadence = -1, flat_road = 1) -> None:
        self.duration = duration
        self.cadence = cadence
        self.flat_road = flat_road

    def __repr__(self) -> str:
        return f'ZFreeRide (duration: {self.duration} cadence: {self.cadence})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'FreeRide')
        interval.set('Duration', str(self.duration))
        interval.set('FlatRoad', str(self.flat_road))
        if self.cadence > 0: interval.set("Cadence", str(self.cadence))
        pass 
