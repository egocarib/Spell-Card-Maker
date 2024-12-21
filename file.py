import os
import sys
import csv
import json
import yaml

from spell import Spell


def load_config(filepath: str) -> dict:
    """
    Loads spell card configuration from a user-specified file
    :param filepath: The path to a JSON file to read configuration from.
    :return: A JSON configuration object.
    """
    filepath = get_abs_path(filepath)
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'r') as f:
                settings = json.load(f)
                return settings
        except Exception as e:
            print(f'Error attempting to read {filepath}: {repr(e)}')
            raise SystemExit(e)
    else:
        print(f'Invalid configuration filepath: {filepath}')
        raise SystemExit()

def load_spells_from_file(filename: str) -> dict[str, Spell]:
    """
    Loads spell data from the specified file. Can be CSV or a YAML format.
    :param filename: The name of the file to read from
    :return: A dictionary of spell data that was read from the file
    """
    fnl = filename.lower()
    if fnl.endswith('.yaml') or fnl.endswith('.yml'):
        return load_spells_from_yaml(get_abs_path(filename))
    else:
        return load_spells_from_csv(get_abs_path(filename))

def load_spells_from_csv(abs_filepath: str) -> dict[str, Spell]:
    """
    Loads spell data from the specified CSV file.
    :param abs_filepath: The absolute path to the file to read from
    :return: A dictionary of spell data that was read from the file
    """
    spells = {}
    try:
        with open(abs_filepath, 'r', newline='', encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            for row_data in reader:
                spell = Spell()
                spell.from_csv_dict(row_data)
                spells[spell.name] = spell
    except Exception as e:
        print(f'Unexpected error reading the CSV input file: {repr(e)}')
        raise SystemExit(e)
    return spells

def load_spells_from_yaml(abs_filepath: str) -> dict[str, Spell]:
    """
    Loads spell data from the specified YAML file.
    :param abs_filepath: The absolute path to the file to read from
    :return: A dictionary of spell data that was read from the file
    """
    try:
        with open(abs_filepath, 'r', newline='', encoding='UTF-8') as f:
            spell_dicts = yaml.safe_load(f)
    except Exception as e:
        print(f'Unexpected error reading the YAML input file: {repr(e)}')
        raise SystemExit(e)
    if not isinstance(spell_dicts, dict):
        print(f'Unexpected format of the YAML input file')
        raise SystemExit()
    spells = {}
    for spell_name, entry in spell_dicts.items():
        spell = Spell()
        spell.from_yaml_dict(spell_name, entry)
        spells[spell_name] = spell
    return spells

def get_abs_path(filepath: str):
    """
    Returns the absolute path string for the provided filepath.
    """
    if os.path.isabs(filepath):
        return filepath
    else:
        cwd = os.getcwd()
        return os.path.join(cwd, filepath)

def get_filepath_with_bundle_fallback(filepath: str):
    """
    Given a target relative path, returns the path to the corresponding existing
    file on the filesystem, first checking the current working directory for
    user-supplied custom files, then falling back to bundled default assets if
    no such file is found in the working directory.
    :param filepath: relative path to the requested file
    :return: absolute path the existing target file
    :raises FileNotFoundError: if no existing file is found in either location
    """
    # First, attempt to retrieve file from current working directory
    # This allows user to override files with their own custom versions
    fp = os.path.join(os.getcwd(), filepath)
    if os.path.exists(fp):
        return fp

    # If that didn't work, try to retrieve the file from our bundled assets
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS  # pyinstaller temporary exe bundle directory
        fp = os.path.join(bundle_dir, filepath)
        if os.path.exists(fp):
            return fp

    # Raise error. In executable mode, this should only ever occur if the user
    # supplies custom filepaths in a configuration json, but hasn't supplied the
    # new file(s) that they specified there.
    raise FileNotFoundError(f'Required asset file not found: "{filepath}"')
