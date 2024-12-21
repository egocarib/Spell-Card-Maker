import argparse
import json
import os

from cardmaker import generate_spell_card
from config import CONFIG_FILENAME, CONFIG_TEMPLATE, Config
from file import load_spells_from_file
from progbar import ProgressBar

# TODO: Consider options to optimize image creation. For example, cache
#       template for each school before starting a large batch. Cache Color or
#       Font objects, if possible. Consider writing text in a different way
#       than caption() - caption seems to be the thing that is taking the
#       longest for card generation.

USAGE_MAIN = '%(prog)s [-h] (generate | make_config) ...'
USAGE_GENERATE = '%(prog)s ' \
    'generate [-h] INPUT_FILE [-o OUTPUT_DIR] [-s SINGLE_SPELL] [-c CONFIG]'
USAGE_MAKE_CONFIG = '%(prog)s make_config [-h] [-o]'


def generate(args):
    """
    Generate spell card(s) based on the provided command-line arguments
    :param args: command-line arguments for the `generate` command
    """
    # load configuration
    if args.config:
        Config.load(args.config)

    # load spells
    spells = load_spells_from_file(args.input_file)
    if len(spells) == 0:
        print('No spells could be loaded from the provided input file. '
              'Is the file formatted correctly?')
        return

    # set up output directory
    out_dir = args.output_dir
    if out_dir is None:
        out_dir = Config.get('general.output_directory')
    os.makedirs(out_dir, exist_ok=True)

    if args.single_spell:
        # generate a single spell card based on input
        if args.single_spell in spells:
            target_spell = args.single_spell
        elif args.single_spell.title() in spells:
            target_spell = args.single_spell.title()
        elif args.single_spell.lower() in spells:
            target_spell = args.single_spell.lower()
        else:
            print(f'Spell "{args.single_spell}" is not defined in the provided'
                  f'input file ({args.input_file}).')
            return
        print(f'generating {target_spell}...')
        generate_spell_card(spells[target_spell], out_dir)
        print('COMPLETE!')
    else:
        # generate all spell cards and show progress bar
        progbar = ProgressBar(max_items=len(spells))
        for spell_name, spell in spells.items():
            progbar.draw_and_increment(f'generating {spell_name}...')
            generate_spell_card(spell, out_dir)
        progbar.message_and_exit('COMPLETE!')


def make_config(args):
    """
    Generate a default configuration file
    :param args: command-line arguments for the `make_config` command
    :return:
    """
    out_file = os.path.join(os.getcwd(), CONFIG_FILENAME)
    # print(f'will try to output to {out_file}')  # TODO: debug - delete
    if os.path.isfile(out_file) and not args.overwrite:
        print(f'The file "{CONFIG_FILENAME}" already exists. '
              'You must specify the -o option to overwrite it.')
    else:
        with open(out_file, 'w') as f:
            json.dump(CONFIG_TEMPLATE, f, indent=4)


# define main program command
parser = argparse.ArgumentParser(
    description='Spell Card Generator - 5E compatible',
    usage=USAGE_MAIN,
    formatter_class=argparse.RawTextHelpFormatter
)
subparsers = parser.add_subparsers(required=True)

# define the "generate" sub-command
gen_parser = subparsers.add_parser(
    name='generate',
    description='Generates spell cards for all data in the provided input file.',
    formatter_class=argparse.RawTextHelpFormatter,
    usage=USAGE_GENERATE,
    help=f'usage: {USAGE_GENERATE}\n'
         'generates spell cards for all data in the provided input file'
)
gen_parser.add_argument(
    'input_file',
    help='input file with spell details (required)'
)
gen_parser.add_argument(
    '-c', '--config',
    help='config file to use when generating spell cards'
)
gen_parser.add_argument(
    '-s', '--single_spell',
    help='generate a single card for the spell with this name'
)
gen_parser.add_argument(
    '-o', '--output_dir',
    help='name of directory in which to output generated spell card images'
)
gen_parser.set_defaults(func=generate)

# define the "make_config" sub-command
config_parser = subparsers.add_parser(
    name='make_config',
    description='Creates a default config file that can '
                'be used to customize spell card generation.',
    usage=USAGE_MAKE_CONFIG,
    help=f'usage: {USAGE_MAKE_CONFIG}\n'
         'creates a default config file that can '
         'be used to customize spell card generation'
)
config_parser.add_argument(
    '-o', '--overwrite',
    action='store_true',
    help=f'if specified, any existing {CONFIG_FILENAME} file will be overwritten.'
)
config_parser.set_defaults(func=make_config)


# Parse arguments and run the utility
prog_args = parser.parse_args()
prog_args.func(prog_args)
