import os.path
import re
from math import floor
from typing import List

from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image

from file import get_abs_path
from spell import Spell
from config import Config


def generate_spell_card(spell: Spell, out_dir: str):
    """
    Generate a single spell card and save it to the specified output directory
    :param spell: The spell for which to generate a spell card image
    :param out_dir: The desired output directory
    """
    try:
        with make_canvas() as img:
            apply_template(img, spell)
            add_title(img, spell)
            add_level(img, spell)
            add_rules(img, spell)
            fn = ''.join(c for c in spell.name if (c.isalnum() or c in '._- '))
            fpath = get_abs_path(os.path.join(out_dir, f'{fn}.png'))
            img.save(filename=fpath)
    except Exception as e:
        print('Unexpected error attempting to generate card for '
              f'{spell.name} spell: {repr(e)}')
        raise SystemExit(e)

def draw_bars(canvas: Image, school: str):
    """
    Draw the colored horizontal bars that are part of each spell card background
    :param canvas: The in-progress spell card image
    :param school: The spell school for this spell. The color of the bars is
        based on the configuration file values for this spell school.
    """
    with Drawing() as draw:
        with Color(Config.get(f'school.{school}.bg_color')) as c:
            draw.stroke_color = c
            draw.fill_color = c
            for pos in ['top', 'mid']:
                draw.rectangle(left=Config.get(f'template.bars.{pos}.x'),
                               top=Config.get(f'template.bars.{pos}.y'),
                               width=Config.get(f'template.bars.{pos}.w'),
                               height=Config.get(f'template.bars.{pos}.h'))
            draw(canvas)


def draw_school_icon(canvas: Image, school: str):
    """
    Draw the spell school icon at the upper-left corner of the spell card
    :param canvas: The in-progress spell card image
    :param school: The spell school for this spell. The icon to use is based on
        the configuration file values for this spell school.
    """
    school_icon = Image(filename=Config.get_filepath(f'school.{school}.img'))
    cx = Config.get('template.icons.school.cx')
    cy = Config.get('template.icons.school.cy')
    radius = Config.get('template.icons.school.radius')
    with Drawing() as draw:
        with Color('black') as c:
            draw.stroke_color = c
            draw.fill_color = c
            draw.circle(origin=(cx, cy),
                        perimeter=(cx - radius, cy))
            draw(canvas)
    canvas.composite(image=school_icon,
                     left=cx - floor(school_icon.width / 2),
                     top=cy - floor(school_icon.height / 2))


def draw_spell_indicators(canvas: Image, spell: Spell):
    """
    Given a Spell, draws the appropriate indicator icons for that spell
    onto the spell card, including verbal, somatic, material, ritual, and
    concentration indicator icons.
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    img_path = Config.get_filepath('template.icons.combined_cast_icons_bg.img')
    cast_icons = Image(filename=img_path)
    canvas.composite(image=cast_icons,
                     left=Config.get('template.icons.combined_cast_icons_bg.x'),
                     top=Config.get('template.icons.combined_cast_icons_bg.y'))

    for ind in ['concentration', 'verbal', 'somatic', 'material', 'ritual']:
        if spell[ind]:
            img_attr_key = f'img_{ind}'
            if not hasattr(draw_spell_indicators, img_attr_key):
                img_path = Config.get_filepath(f'template.icons.{ind}.img')
                setattr(draw_spell_indicators, img_attr_key,
                        Image(filename=img_path))
            canvas.composite(image=getattr(draw_spell_indicators, img_attr_key),
                             left=Config.get(f'template.icons.{ind}.x'),
                             top=Config.get(f'template.icons.{ind}.y'))

    if hasattr(spell, 'material_cost'):
        cost_font = Font(path=Config.get_filepath('template.fonts.main'))
        cost_position = Config.get('template.metadata.material_cost.label')
        cost_text = spell.material_cost
        if spell.material_consumed:
            cost_text += '*'
        canvas.caption(text=cost_text,
                       left=cost_position['x'],
                       top=cost_position['y'],
                       width=cost_position['w'],
                       height=cost_position['h'],
                       font=cost_font,
                       gravity='south_west')


def write_spell_params(canvas: Image, spell: Spell):
    """
    Draws the text describing the spell range, cast time, and duration onto the
    spell card image.
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    label_font = Font(path=Config.get_filepath('template.fonts.main'))
    value_font = Font(path=Config.get_filepath('template.fonts.main_bold'))
    labels = {
        'range': 'Range',
        'cast_time': 'Casting Time',
        'duration': 'Duration'
    }
    for param in ['range', 'cast_time', 'duration']:
        canvas.caption(text=labels[param],
                       left=Config.get(f'template.metadata.{param}.label.x'),
                       top=Config.get(f'template.metadata.{param}.label.y'),
                       width=Config.get(f'template.metadata.{param}.label.w'),
                       height=Config.get(f'template.metadata.{param}.label.h'),
                       font=label_font,
                       gravity="west")
        canvas.caption(text=spell[param],
                       left=Config.get(f'template.metadata.{param}.value.x'),
                       top=Config.get(f'template.metadata.{param}.value.y'),
                       width=Config.get(f'template.metadata.{param}.value.w'),
                       height=Config.get(f'template.metadata.{param}.value.h'),
                       font=value_font,
                       gravity="west")

def make_canvas() -> Image:
    """
    Creates a blank image canvas to be used for drawing a spell card.
    :return: an Image object
    """
    return Image(width=Config.get('template.canvas.w'),
                 height=Config.get('template.canvas.h'),
                 background=Color('white'))

def apply_template(canvas: Image, spell: Spell):
    """
    Given a Spell, draws most of the iconography onto the spell card, and some
    of the basic metadata text, such as duration, cast time, and range. This
    function essentially draws all of the spell card except for the spell name,
    level, and rules text.
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    school = spell.school.lower()
    classes = spell.classes
    # School-specific images
    draw_bars(canvas, school)
    draw_school_icon(canvas, school)
    add_class_list(canvas, school, classes)
    write_spell_params(canvas, spell)
    draw_spell_indicators(canvas, spell)

def add_class_list(canvas: Image, school: str, classes: List[str]):
    """
    Draws the list of classes on the upper-right side of the spell card, and
    highlights the classes that have this spell on their class spell list.
    :param canvas: The in-progress spell card image
    :param school: The spell school for this spell. The highlight color used for
        class names is based on the config file values for this spell school.
    :param classes: The list of classes to highlight because this spell is on
        their class spell list.
    """
    # Draw default greyed-out class list to start
    canvas.composite(image=default_class_list_bg(),
                     left=Config.get('template.class_list.x'),
                     top=Config.get('template.class_list.y'))

    # Iterate through all possible classes, adding school-colored indicators
    # for each class that has this spell in their class spell list
    with Color(Config.get(f'school.{school}.bg_color')) as school_color:
        font = Font(path=Config.get_filepath('template.fonts.main'),
                color=school_color,
                stroke_color=school_color,
                stroke_width=0.05)
        class_ct = len(Config.get('general.classes'))
        line_height = floor(Config.get('template.class_list.h') / class_ct)
        for i in range(class_ct):
            cls = Config.get('general.classes')[i]
            if cls not in classes:
                continue

            # Draw "active" class name in the color of this school
            #print(f"drawing active classname {cls} at left={dl} top={dt} wid={dw} hei={dh}")
            offset = line_height * i
            class_x = Config.get('template.class_list.x')
            class_y = Config.get('template.class_list.y') + offset
            class_w = Config.get('template.class_list.w')
            with Color('#FFFFFF') as color_white:
                with Drawing() as draw:
                    draw.stroke_color = color_white
                    draw.fill_color = color_white
                    draw.rectangle(left=class_x, top=class_y,
                                   width=class_w, height=line_height)
                    draw(canvas)
            canvas.caption(text=cls,
                           left=class_x,
                           top=class_y,
                           width=class_w,
                           height=line_height,
                           font=font,
                           gravity='east')

            # Draw rectangle indicator to right of class name using same color
            with Drawing() as draw:
                draw.stroke_color = school_color
                draw.fill_color = school_color
                extra_offset = line_height \
                    * Config.get('template.class_list.marker.y_pad_pct')
                right_margin = Config.get('template.bars.top.x') \
                    + Config.get('template.bars.top.w')
                bar_w = Config.get('template.class_list.marker.w')
                bar_h = line_height \
                        * Config.get('template.class_list.marker.h_pct')
                bar_x = right_margin - bar_w
                bar_y = class_y + extra_offset
                draw.rectangle(left=bar_x, top=bar_y, width=bar_w, height=bar_h)
                draw(canvas)

def default_class_list_bg() -> Image:
    """
    Creates, caches, and returns a greyed-out version of the class list shown at
    the top right side of each spell card. This image is drawn onto the card as
    a starting point, and then specific classes are highlighted in color on top
    of this background image.
    :return: The default greyed-out class list background image
    """
    if hasattr(default_class_list_bg, "cached_img"):
        return default_class_list_bg.cached_img
    bg = Image(width=Config.get('template.class_list.w'),
               height=Config.get('template.class_list.h'))
    with Color(Config.get('template.colors.grey')) as bg_color:
        grey_font = Font(path=Config.get_filepath('template.fonts.main'),
                         color=bg_color)
                         # ,
                         # stroke_color=bg_color,
                         # stroke_width=0.05)
        class_ct = len(Config.get('general.classes'))
        line_height = floor(Config.get('template.class_list.h') / class_ct)
        for i in range(class_ct):
            offset = line_height * i
            bg.caption(text=Config.get('general.classes')[i],
                       left=0,
                       top=offset,
                       width=Config.get('template.class_list.w'),
                       height=line_height,
                       font=grey_font,
                       gravity='east')
    default_class_list_bg.cached_img = bg
    return bg


def add_title(canvas: Image, spell: Spell):
    """
    Draws the title of the spell card, which is the text of the spell's name
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    spell_school = spell.school.lower()
    title_font_color = Config.get(f'school.{spell_school}.fg_color')
    title_font = Font(path=Config.get_filepath('template.fonts.title'),
                      color=Color(title_font_color))
    canvas.caption(text=spell.name,
                   left=Config.get('template.title.x'),
                   top=Config.get('template.title.y'),
                   width=Config.get('template.title.w'),
                   height=Config.get('template.title.h'),
                   font=title_font,
                   gravity='west')

def add_level(canvas: Image, spell: Spell):
    """
    Draws the text noting the level of the spell at the top of the spell card,
    next to the spell name.
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    spell_school = spell.school.lower()
    lvl_font_color = Config.get(f'school.{spell_school}.fg_color')
    lvl_font = Font(path=Config.get_filepath('template.fonts.main_bold'),
                    color=Color(lvl_font_color))
    canvas.caption(text=f'Lv {spell.level}',
                   left=Config.get('template.metadata.level.label.x'),
                   top=Config.get('template.metadata.level.label.y'),
                   width=Config.get('template.metadata.level.label.w'),
                   height=Config.get('template.metadata.level.label.h'),
                   font=lvl_font,
                   gravity='west')


def add_rules(canvas: Image, spell: Spell):
    """
    Draws the spell rules text on the bottom half of the spell card.

    Note:
    This function currently uses the Image.caption() method to draw this text,
    which automatically determines the correct font size to use so that the
    text can fit into the allotted space. However, the Image.caption() method
    is somewhat slow, so it would be worthwhile to try and investigate other
    methods of drawing text on the card for the future. Other methods of text
    drawing could also potentially allow us to support formatted text - such as
    bold text - which would be a nice feature that is currently missing.
    :param canvas: The in-progress spell card image
    :param spell: The Spell object that holds metadata about this spell
    """
    rules_font = Font(path=Config.get_filepath('template.fonts.main'))
    pad_rules = Config.get('general.prevent_large_rule_text')
    rule_text = get_padded_rules(spell) if pad_rules else spell.rules
    rule_text = replace_problematic_chars(rule_text)
    canvas.caption(text=rule_text,
                   left=Config.get('template.rules.x'),
                   top=Config.get('template.rules.y'),
                   width=Config.get('template.rules.w'),
                   height=Config.get('template.rules.h'),
                   font=rules_font,
                   gravity='north_west')

def replace_problematic_chars(txt: str) -> str:
    """
    Some higher-range unicode characters don't seem to render - perhaps this is
    an issue with the font we are using for rules text? Fix them here.
    """
    return txt.replace('−', '-')  # U+2212 (mathematical minus sign)

def get_padded_rules(spell: Spell) -> str:
    """
    Very simplistic function to approximately pad rules text with a few extra
    lines, used to avoid having the font size get too huge for spells with
    only a sentence or two of rules text.
    """
    rules_text = spell.rules
    rough_block_size = len(rules_text)
    for _ in re.findall(r'\n\n', rules_text):
        rough_block_size += 30  # empty line roughly 30 chars worth of space
    while rough_block_size < 240:
        rough_block_size += 30
        rules_text += '\n'
    return rules_text
