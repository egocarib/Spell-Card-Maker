from typing import List


class Spell:
    """
    All of the data that defines a single spell, such as the spell name, level,
    school, and rules text.
    """
    name: str                # Spell name
    level: int               # Spell level (0 indicates a cantrip)
    rules: str               # Spell description / rules text
    school: str              # School associated with spell, such as "Illusion"
    classes: List[str]       # Classes that have this spell on their spell list
    cast_time: str           # Cast time, such as "1 Action"
    range: str               # Range of the spell, such as "60 Feet"
    duration: str            # Duration of the spell, such as "1 Minute"
    concentration: bool      # True if this spell requires concentration
    ritual: bool             # True if this spell can be cast as a ritual
    verbal: bool             # True if this spell has a verbal component
    somatic: bool            # True if this spell has a somatic component
    material: bool           # True if this spell has a material component
    material_costly: bool    # True if the material component has a cost
    material_consumed: bool  # True if the material component is consumed
    material_text: str       # Description of the material component
    material_cost: str       # Cost of the material component, such as "100gp"
    source: str              # The rulebook or other source text for this spell

    @staticmethod
    def csv_headers():
        """
        Headers that should be used when outputting spells to a CSV file. The
        same headers are expected when reading from a spell CSV definition file.
        :return: the list of CSV headers
        """
        return ['level', 'name', 'school', 'classes', 'range', 'cast_time',
                'duration', 'concentration', 'ritual', 'verbal', 'somatic',
                'material', 'material_costly', 'material_consumed',
                'material_text', 'material_cost', 'rules', 'source']

    def to_csv_dict(self):
        """
        Converts a Spell object to a simple flattened dictionary that can be
        output as an individual row in a CSV file.
        :return: a dictionary object that can be written to a CSV row
        """
        return {
            'level': str(getattr(self, 'level', -1)),
            'name': getattr(self, 'name', 'Unknown'),
            'school': getattr(self, 'school', 'Unknown'),
            'classes': ', '.join(getattr(self, 'classes', [])),
            'range': getattr(self, 'range', ''),
            'cast_time': getattr(self, 'cast_time', ''),
            'duration': getattr(self, 'duration', ''),
            'concentration': 'yes' if getattr(self, 'concentration', False) else 'no',
            'ritual': 'yes' if getattr(self, 'ritual', False) else 'no',
            'verbal': 'yes' if getattr(self, 'verbal', False) else 'no',
            'somatic': 'yes' if getattr(self, 'somatic', False) else 'no',
            'material': 'yes' if getattr(self, 'material', False) else 'no',
            'material_costly': 'yes' if getattr(self, 'material_costly', False) else 'no',
            'material_consumed': 'yes' if getattr(self, 'material_consumed', False) else 'no',
            'material_text': getattr(self, 'material_text', ''),
            'material_cost': getattr(self, 'material_cost', ''),
            'rules': getattr(self, 'rules', ''),
            'source': getattr(self, 'source', '')
        }

    def from_csv_dict(self, csv_row):
        """
        Populates this Spell object from the provided CSV row dictionary.
        """
        self.level = int(csv_row['level'])
        self.name = csv_row['name']
        self.school = csv_row['school']
        self.classes = csv_row['classes'].split(', ')
        self.range = csv_row['range']
        self.cast_time = csv_row['cast_time']
        self.duration = csv_row['duration']
        self.concentration = True if csv_row['concentration'] == 'yes' else False
        self.ritual = True if csv_row['ritual'] == 'yes' else False
        self.verbal = True if csv_row['verbal'] == 'yes' else False
        self.somatic = True if csv_row['somatic'] == 'yes' else False
        self.material = True if csv_row['material'] == 'yes' else False
        self.material_costly = True if csv_row['material_costly'] == 'yes' else False
        self.material_consumed = True if csv_row['material_consumed'] == 'yes' else False
        if self.material:
            self.material_text = csv_row['material_text']
            if len(csv_row['material_cost']) > 0:
                self.material_cost = csv_row['material_cost']
        self.rules = csv_row['rules']
        self.source = csv_row['source']

    class YamlRulesText:
        """
        A simple wrapper class around the str data type to allow consistent
        formatting of spell rules text when dumping spells to a YAML output file
        """
        content: str
        def __init__(self, content):
            self.content = content
        def __repr__(self):
            return self.content
        def __str__(self):
            return self.content

    def to_yaml_dict(self) -> dict:
        """
        Converts a Spell object to a simple flattened dictionary that can be
        output as an individual entry in a YAML output file. Note that the
        "name" attribute is intentionally excluded from this dictionary, because
        the name is used as a key for this data in the YAML output.
        :return: a dictionary object that can be written as a YAML entry
        """
        result = {
            'level': getattr(self, 'level', -1),
            'school': getattr(self, 'school', 'Unknown'),
            'classes': ', '.join(getattr(self, 'classes', [])),
            'range': getattr(self, 'range', ''),
            'cast_time': getattr(self, 'cast_time', ''),
            'duration': getattr(self, 'duration', ''),
            'concentration': getattr(self, 'concentration', False),
            'ritual': getattr(self, 'ritual', False),
            'verbal': getattr(self, 'verbal', False),
            'somatic': getattr(self, 'somatic', False),
            'material': getattr(self, 'material', False),
            'material_costly': getattr(self, 'material_costly', False),
            'material_consumed': getattr(self, 'material_consumed', False),
            'rules': self.YamlRulesText(getattr(self, 'rules', '')),
            'source': getattr(self, 'source', '')
        }
        if hasattr(self, 'material_text'):
            result['material_text'] = self.material_text
        if hasattr(self, 'material_cost'):
            result['material_cost'] = self.material_cost
        return result

    def from_yaml_dict(self, spell_name: str, entry: dict):
        """
        Populates this Spell object from the provided spell_name and YAML entry.
        """
        self.level = entry['level'] if 'level' in entry else -1
        self.name = spell_name
        self.school = entry['school'] if 'school' in entry else 'Unknown'
        self.classes = entry['classes'].split(', ') if 'classes' in entry else 'Unknown'
        self.range = entry['range'] if 'range' in entry else 'Unknown'
        self.cast_time = entry['cast_time'] if 'cast_time' in entry else 'Unknown'
        self.duration = entry['duration'] if 'duration' in entry else 'Unknown'
        self.concentration = entry['concentration'] if 'concentration' in entry else False
        self.ritual = entry['ritual'] if 'ritual' in entry else False
        self.verbal = entry['verbal'] if 'verbal' in entry else False
        self.somatic = entry['somatic'] if 'somatic' in entry else False
        self.material = entry['material'] if 'material' in entry else False
        self.material_costly = entry['material_costly'] if 'material_costly' in entry else False
        self.material_consumed = entry['material_consumed'] if 'material_consumed' in entry else False
        if self.material:
            self.material_text = entry['material_text'] if 'material_text' in entry else ''
            if 'material_cost' in entry and len(entry['material_cost']) > 0:
                self.material_cost = entry['material_cost']
        self.rules = entry['rules'] if 'rules' in entry else ''
        self.source = entry['source'] if 'source' in entry else ''

    def __getitem__(self, key):
        """
        Simple Spell object getter that defaults missing attributes to "None"
        """
        return getattr(self, key, None)
