from __future__ import annotations
import xml.etree.ElementTree as ET 
import helper as Helper

class ZSteadyState: 
    def __init__(self, row: str) -> None:
        duration, row = [r.strip() for r in row.split('@')]
        duration = Helper.parse_duration(duration)
        cadence, row = Helper.parse_cadence(row)
        self.duration = duration
        self.power = Helper.parse_power(row)
        self.cadence = cadence 

    def __repr__(self) -> str:
        return f'SteadyState (duration: {self.duration} power: {self.power} cadence: {self.cadence}'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'SteadyState')
        interval.set('Duration', str(self.duration))
        interval.set('Power', str(self.power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))
        return interval 

class ZRangedInterval(): 
    def __init__(self, row: str) -> None:
        duration, row = row.split('from')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split('@')
            cadence, _ = Helper.parse_cadence(cadence)
        duration = Helper.parse_duration(duration)

        from_power, to_power = [Helper.parse_power(p) for p in row.split('to')]

        self.duration = duration 
        self.from_power = from_power 
        self.to_power = to_power 
        self.cadence = cadence 
        self.name = "Warmup" if from_power < to_power else "Cooldown"  

    def __repr__(self) -> str:
        return f'{self.get_name()} (duration: {self.duration} from_power: {self.from_power} to_power: {self.to_power} cadence: {self.cadence})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, self.name)
        interval.set('Duration', str(self.duration))
        interval.set('PowerLow', str(self.from_power))
        interval.set("PowerHigh", str(self.to_power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))

class ZIntervalsT(): 
    def __init__(self, row: str): 
        number, rest =  row.split('x')
        rest = rest.replace("rpm,", 'rpm')
        first_interval, second_interval = [ZSteadyState(r) for r in rest.split(',')]
        self.nubner = number 
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

class ZFreeRide(): 
    def __init__(self, row: str): 
        duration, _ = row.split('free ride')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split("@")
            cadence = Helper.parse_cadence(cadence)
        duration = Helper.parse_duration(duration)

        self.duration = duration
        self.cadence = cadence
        self.flat_road = 1 

    def __repr__(self) -> str:
        return f'ZFreeRide (duration: {self.duration} cadence: {self.cadence})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'FreeRide')
        interval.set('Duration', str(self.duration))
        interval.set('FlatRoad', str(self.flat_road))
        if self.cadence > 0: interval.set("Cadence", str(self.cadence))
        pass 
