from file import load_config, get_filepath_with_bundle_fallback


class Config:
    """
    Static class for loading and retrieving configuration values
    """

    user_config: dict = None  # User-defined configuration file, if provided

    @staticmethod
    def load(filepath: str):
        """
        Load the specified filepath as a user-defined configuration file. User
        configuration values are preferred over default configuration values
        when present.
        """
        Config.user_config = load_config(filepath)

    @staticmethod
    def get(attr_dot_string: str) -> [str, None]:
        """
        Get the configuration value specified by the dot-string. For example,
        Config.get("a.b.c") is similar to config_dictionary['a']['b']['c'].
        This function will retrieve the config value from user-specific config
        first, if available, and then fall back to default config values.
        :param attr_dot_string: a dot-delimited set of config dictionary keys
        :return: the desired configuration value
        """
        attrs = attr_dot_string.split('.')
        try:  # check user config first
            c = Config.user_config
            for attr in attrs:
                if c is None or attr not in c:
                    raise AttributeError
                c = c.get(attr)
        except AttributeError:  # fallback to default config
            try:
                c = CONFIG_TEMPLATE
                for attr in attrs:
                    if c is None or attr not in c:
                        raise AttributeError
                    c = c.get(attr)
            except AttributeError:
                return None
        return c

    @staticmethod
    def get_filepath(attr_dot_string: str) -> [str, None]:
        """
        Similar to Config.get(), but includes additional special handling for
        filepath config settings. This method retrieves the absolute filepath
        to the requested resource, checking for local assets first before
        falling back to bundled default assets.
        :param attr_dot_string: a dot-delimited set of config dictionary keys
        :return: the desired configuration value as an absolute filepath string
        """
        val = Config.get(attr_dot_string)
        if val is not None:
            val = get_filepath_with_bundle_fallback(val)
        return val


# Default filename used to generate a config file
CONFIG_FILENAME = 'card-config.json'

# Default configuration values
CONFIG_TEMPLATE = {
    "template": {
        "canvas": {
            "w": 822,
            "h": 1122
        },
        "metadata": {
            "level": {
                "label": {
                    "x": 649,
                    "y": 97,
                    "w": 120,
                    "h": 48
                }
            },
            "range": {
                "label": {
                    "x": 97,
                    "y": 203,
                    "w": 275,
                    "h": 49
                },
                "value": {
                    "x": 378,
                    "y": 205,
                    "w": 216,
                    "h": 45
                }
            },
            "duration": {
                "label": {
                    "x": 97,
                    "y": 267,
                    "w": 275,
                    "h": 49
                },
                "value": {
                    "x": 378,
                    "y": 269,
                    "w": 216,
                    "h": 45
                }
            },
            "cast_time": {
                "label": {
                    "x": 97,
                    "y": 332,
                    "w": 275,
                    "h": 49
                },
                "value": {
                    "x": 378,
                    "y": 334,
                    "w": 216,
                    "h": 45
                }
            },
            "material_cost": {
                "label": {
                    "x": 505,
                    "y": 398,
                    "w": 100,
                    "h": 36
                }
            }
        },
        "title": {
            "x": 201,
            "y": 80,
            "w": 416,
            "h": 82
        },
        "rules": {
            "x": 92,
            "y": 610,
            "w": 644,
            "h": 432
        },
        "colors": {
            "black": "#000000",
            "grey": "#BFBFBF"
        },
        "fonts": {
            "title": "resources/fonts/RINGM___.TTF",
            "main": "resources/fonts/MPLANTIN.ttf",
            "main_bold": "resources/fonts/MPLANTI1.ttf",
            "main_italic": "resources/fonts/MPLANTI3.ttf"
        },
        "bars": {
            "top": {
                "x": 127,
                "y": 75,
                "w": 620,
                "h": 91
            },
            "mid": {
                "x": 73,
                "y": 516,
                "w": 674,
                "h": 77
            }
        },
        "icons": {
            "school": {
                "cx": 127,
                "cy": 127,
                "radius": 57
            },
            "concentration": {
                "x": 320,
                "y": 265,
                "img": "resources/images/shared/concentration.png"
            },
            "verbal": {
                "x": 229,
                "y": 422,
                "img": "resources/images/shared/verbal.png"
            },
            "somatic": {
                "x": 348,
                "y": 419,
                "img": "resources/images/shared/somatic.png"
            },
            "material": {
                "x": 456,
                "y": 416,
                "img": "resources/images/shared/material.png"
            },
            "ritual": {
                "x": 97,
                "y": 402,
                "img": "resources/images/shared/ritual.png"
            },
            "combined_cast_icons_bg": {
                "x": 97,
                "y": 402,
                "img": "resources/images/shared/cast-icons.png"
            }
        },
        "class_list": {
            "x": 602,
            "y": 178,
            "w": 130,
            "h": 334,
            "marker": {
                "w": 8,
                "h_pct": 0.74,
                "y_pad_pct": 0.07
            }
        }
    },
    "general": {
        "classes": [
            "Bard",
            "Cleric",
            "Druid",
            "Paladin",
            "Ranger",
            "Sorcerer",
            "Warlock",
            "Wizard"
        ],
        "prevent_large_rule_text": True,
        "output_directory": "output"
    },
    "school": {
        "abjuration": {
            "bg_color": "#6DC3D3",
            "fg_color": "#000000",
            "img": "resources/images/abjuration/icon.png"
        },
        "conjuration": {
            "bg_color": "#59326C",
            "fg_color": "#FFFFFF",
            "img": "resources/images/conjuration/icon.png"
        },
        "divination": {
            "bg_color": "#D7CB42",
            "fg_color": "#000000",
            "img": "resources/images/divination/icon.png"
        },
        "enchantment": {
            "bg_color": "#B34485",
            "fg_color": "#FFFFFF",
            "img": "resources/images/enchantment/icon.png"
        },
        "evocation": {
            "bg_color": "#377C54",
            "fg_color": "#FFFFFF",
            "img": "resources/images/evocation/icon.png"
        },
        "illusion": {
            "bg_color": "#393F7D",
            "fg_color": "#FFFFFF",
            "img": "resources/images/illusion/icon.png"
        },
        "necromancy": {
            "bg_color": "#804539",
            "fg_color": "#FFFFFF",
            "img": "resources/images/necromancy/icon.png"
        },
        "transmutation": {
            "bg_color": "#7EBF5D",
            "fg_color": "#000000",
            "img": "resources/images/transmutation/icon.png"
        }
    }
}
