import re
import csv
import yaml
import requests
from typing import List

from spell import Spell


class SRD_5_Extractor:
    """
    This is a very basic example of a utility that extracts SRD spell data from
    an online source and converts it to a CSV or YAML file suitable for use with
    the Spell Card Maker utility.

    This extractor primarily uses regex and it is not perfect. The source file
    contains some inconsistencies and this extractor discards / ignores some
    content from more complex spell descriptions, such as those that include
    tables in their rules text.

    This extractor loads System Reference Document spell data from the
    public repository here: https://github.com/BTMorton/dnd-5e-srd/. Similar
    extractors could be built to load spells from another source.
    """

    spells: dict[str, Spell]
    source: str
    re_lvl_school_ritual: re.Pattern
    re_cantrip_school_ritual: re.Pattern
    re_casting_time: re.Pattern
    re_range: re.Pattern
    re_components: re.Pattern
    re_duration: re.Pattern
    re_mat_cost: re.Pattern
    re_conc_dur: re.Pattern
    re_rules_formatted: re.Pattern

    def __init__(self):
        """
        Initial setup before parsing spells, such as compiling the regex
        patterns we will use during parsing.
        """
        self.spells = dict()
        # Using the permalink to this file to avoid unanticipated future changes
        self.source = ('https://raw.githubusercontent.com/BTMorton/dnd-5e-srd'
                       '/edb6e2dcaec1edc6472f863b29ff72e45b21d8b6/json'
                       '/08%20spellcasting.json')
        self.re_lvl_school_ritual = \
            re.compile(r'\*(\d)\w\w-level (\w+)( \(ritual\))?\*')
        self.re_cantrip_school_ritual = \
            re.compile(r'\*(\w+) cantrip( \(ritual\))?\*')
        self.re_casting_time = \
            re.compile(r'\*\*Casting Time:\*\* ((?:(?!\*\*Range|\n).)+)')
        self.re_range = \
            re.compile(r'\*\*Range:\*\* ((?:(?!\*\*Component|\n).)+)')
        self.re_components = \
            re.compile(r'\*\*Components?:?\*\*:? ((?:(?!\*\*Duration|\n).)+)')
        self.re_duration = \
            re.compile(r'\*\*Duration:\*\* ([^\n]+)')
        self.re_mat_cost = \
            re.compile(r'\b(\d+(?:,\d{3})?) ?gp\b')
        self.re_conc_dur = \
            re.compile(r'\bConcentration,? up to ([^\n]+)\b')
        self.re_rules_formatted = \
            re.compile(r'(\*{1,3})([^*\n]+)\1')

    def parse_spells(self):
        """
        Parse spells from Github and save them to the "spells" attribute of this
        class.
        """
        spell_json = self.retrieve_json()
        spell_data = spell_json['Spellcasting']['Spell Descriptions']
        class_data = spell_json['Spellcasting']['Spell Lists']
        self.create_spell_dict(spell_data)
        self.add_class_info(class_data)

    def retrieve_json(self):
        """
        Retrieve the SRD spell json from BTMorton's GitHub repository
        :return: a json dictionary representation of spell data
        """
        r = requests.get(self.source)
        r.raise_for_status()
        spell_json: dict = r.json()
        if 'Spellcasting' not in spell_json:
            raise RuntimeError('Unexpected JSON format of spell source file: '
                f'missing "Spellcasting" node at {self.source}')
        if 'Spell Descriptions' not in spell_json['Spellcasting']:
            raise RuntimeError('Unexpected JSON format of spell source file: '
                f'missing "Spell Descriptions" node at {self.source}')
        if 'Spell Lists' not in spell_json['Spellcasting']:
            raise RuntimeError('Unexpected JSON format of spell source file: '
                f'missing "Spell Lists" node at {self.source}')
        return spell_json

    def create_spell_dict(self, spell_data: dict):
        """
        Create Spell objects for each spell in the json source file, adding them
        to the "spells" dictionary of this class.
        """
        for spell_name, spell_info in spell_data.items():
            spell = Spell()
            spell.name = spell_name
            spell.source = 'System Reference Document'
            spell.classes = []  # To be populated later by add_class_info()
            if 'content' not in spell_info:
                print(f'No "content" node for possible spell "{spell_name}", '
                      'this section will be skipped.')
                continue

            # Extract content array into two strings: metadata, and rules text
            content: List[str] = ['', '']
            segment: int = 0
            for txt in spell_info['content']:
                if not isinstance(txt, str):
                    if not isinstance(txt, List):
                        # Not a string or a list of strings... error
                        print('Encountered non-string node within "content" for'
                              f' spell "{spell_name}" - no additional rules'
                              ' text will be parsed.')
                        break
                    else:
                        # verify this is a list of strings. If so, it represents
                        # a bulleted list, and we'll parse it as such.
                        inner_err = False
                        for fragment in txt:
                            if not isinstance(fragment, str):
                                print('Encountered non-string node within '
                                      f'"content" for spell "{spell_name}" - no'
                                      ' additional rules text will be parsed.')
                                inner_err = True
                                break
                        if inner_err:
                            break
                        # convert list of str into a single bulleted list string
                        txt = '• ' + '\n• '.join(txt)
                        # list usually follows intro sentence. Remove one of the
                        # two line breaks we added before the list, if relevant:
                        if content[segment][-2:] == '\n\n':
                            content[segment] = content[segment][:-1]
                content[segment] += txt + '\n\n'
                if '**Duration:**' in txt:
                    segment = 1
            if segment == 0:  # did not find Duration, invalid spell definition
                print('No Duration / other metadata found for possible spell '
                      f'"{spell_name}", this section will be skipped.')
                continue

            # Process metadata for spell
            meta = content[0].strip()
            self.populate_spell_metadata(spell, meta)

            # Process rules text for spell
            rules = content[1].strip()
            self.populate_spell_rules(spell, rules)

            # Add finalized spell to dictionary
            self.spells[spell_name] = spell

    def populate_spell_rules(self, spell: Spell, rule_str: str):
        """
        Populate rules text for a spell. Currently, this simply ignores tables
        and can truncate content that appears after tables (so it won't fully
        document complex spells like Teleport). It also strips out formatting,
        namely bold and italic words.
        """
        if not hasattr(spell, 'rules'):  # some rule text may already be present
            spell.rules = ''
        spell.rules += rule_str

        # remove bold/italic formatting
        spell.rules = self.re_rules_formatted.sub(r'\2', spell.rules)

    def populate_spell_metadata(self, spell: Spell, meta_str: str):
        """
        Populates various metadata for the spell based on the passed-in metadata
        string. May also add initial content to the beginning of spell.rules -
        so that content should be preserved (ex: casting time conditionals)
        """
        # parse level, school, and ritual
        match = self.re_cantrip_school_ritual.search(meta_str)
        if match is not None:
            spell.level = 0
            spell.school = match.group(1).title()
            spell.ritual = True if match.group(2) is not None else False
        else:
            match = self.re_lvl_school_ritual.search(meta_str)
            if match is None:
                raise RuntimeError('Unexpectedly unable to parse spell level, '
                    f'school, or ritual for spell "{spell.name}". Aborting.')
            spell.level = int(match.group(1))
            spell.school = match.group(2).title().strip()
            spell.ritual = True if match.group(3) is not None else False

        # parse casting time
        match = self.re_casting_time.search(meta_str, match.end())
        if match is None:
            raise RuntimeError('Unexpectedly unable to parse spell casting time'
                f' for spell "{spell.name}". Aborting.')
        if ', which you take when ' in match.group(1):
            spell.cast_time = match.group(1).split(',')[0].title()
            spell.rules = match.group(1) + '\n\n'
        else:
            spell.cast_time = match.group(1).title().strip()
        if spell.cast_time == '1 Bonus Action':
            spell.cast_time = 'Bonus'
        elif spell.cast_time == '1 Reaction':
            spell.cast_time = 'Reaction'

        # parse range
        match = self.re_range.search(meta_str, match.end())
        if match is None:
            raise RuntimeError('Unexpectedly unable to parse spell range for'
                f' spell "{spell.name}". Aborting.')
        spell.range = match.group(1).title().strip()

        # parse components
        match = self.re_components.search(meta_str, match.end())
        if match is None:
            raise RuntimeError('Unexpectedly unable to parse spell components'
                f' for spell "{spell.name}". Aborting.')
        types = match.group(1)
        if '(' in match.group(1):
            types = match.group(1).split('(')[0]
            spell.material_text = match.group(1).split('(')[1].split(')')[0]
        spell.verbal = True if 'V' in types else False
        spell.somatic = True if 'S' in types else False
        spell.material = True if 'M' in types else False
        spell.material_costly = False
        spell.material_consumed = False
        if spell.material:
            if hasattr(spell, 'material_text'):
                cost: int = 0
                for c in self.re_mat_cost.finditer(spell.material_text):
                    cost += int(c.group(1).replace(',', ''))
                if cost > 0:
                    spell.material_costly = True
                    spell.material_cost = f'{cost}gp'
                if 'which the spell consumes' in spell.material_text:
                    spell.material_consumed = True
            else:
                spell.material_text = ''

        # parse duration
        match = self.re_duration.search(meta_str, match.end())
        if match is None:
            raise RuntimeError('Unexpectedly unable to parse spell duration for'
                f' spell "{spell.name}". Aborting.')
        conc_match = self.re_conc_dur.search(match.group(1))
        if conc_match:
            spell.concentration = True
            spell.duration = conc_match.group(1)
        else:
            spell.concentration = False
            spell.duration = match.group(1)
            if 'Instantaneous' in spell.duration:
                spell.duration = 'Instant'
        # standardize errant written numbers ("one minute" -> "1 minute")
        spell.duration.replace('one ', '1 ')

    def add_class_info(self, class_data: dict):
        """
        Populate the class list for each spell in the self.spells dictionary
        (This info is documented in a separate section of the SRD)
        :param class_data: Section of the JSON SRD that contains class spell
            lists
        """
        for class_label, class_section in class_data.items():
            class_name: str = class_label.split(' ')[0]  # ex: "Bard Spells"
            for level_label, spell_list in class_section.items():
                for spell_name in spell_list:
                    if spell_name in self.spells:
                        self.spells[spell_name].classes.append(class_name)

    @staticmethod
    def yaml_rules_presenter(dumper, data):
        """
        Enforce some consistency on yaml output by ensuring rules text always
        uses block scalar format.
        """
        return dumper.represent_scalar('tag:yaml.org,2002:str', data.content,
                                       style='>')

    def dump_yaml(self):
        """
        Save spell list to YAML formatted "spells.yaml" output file
        """
        simple_spell_dict = {}
        for spell_name, spell in self.spells.items():
            simple_spell_dict[spell_name] = spell.to_yaml_dict()
        try:
            with open('spells.yaml', 'w', newline='', encoding='UTF-8') as f:
                print('dumping spell data to yaml file...')
                yaml.add_representer(data_type=Spell.YamlRulesText,
                                     representer=self.yaml_rules_presenter)
                yaml.dump(simple_spell_dict, f, allow_unicode=True)
        except Exception as e:
            print(f'Unexpected error generating YAML output file: {repr(e)}')
            raise SystemExit(e)

    def dump_csv(self):
        """
        Save spell list to CSV formatted "spells.csv" output file
        """
        try:
            with open('spells.csv', 'w', newline='', encoding='UTF-8') as f:
                print('dumping spell data to csv file...')
                w = csv.DictWriter(f, fieldnames=Spell.csv_headers())
                w.writeheader()
                for sp_name, spell in self.spells.items():
                    w.writerow(spell.to_csv_dict())
        except Exception as e:
            print(f'Unexpected error generating CSV output file: {repr(e)}')
            raise SystemExit(e)


if __name__ == '__main__':

    # read and extract spell data from BTMorton/dnd-5e-srd GitHub repo
    extractor = SRD_5_Extractor()
    extractor.parse_spells()

    # dump spells to both YAML and CSV format
    # either format can then be ingested by the SpellCardMaker program
    extractor.dump_yaml()
    extractor.dump_csv()
