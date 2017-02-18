"""Module to process and rank officials by experience.

We have several parts:
- load an official from an exported Excel file (old not yet accepted but new formats accepted)
- load an official from live google sheets (not implemented)
- summarise a list of officials from a given directory
- standard options for processing
- process tournament application sheets (not implemented)
- save sheet summarizing officials
"""
__author__ = 'hammer'
__version__ = 0.5

# TODO: FUTURE: OPTIONAL: add in game mimimums - currently can filter out in the spreadsheet, no need to here. Probably not until application processing is automated

# TODO: Is the Association weighting very different for NSOs? It is a different game for refs... but maybe less so for NSOs


from shaft.Offical import Official
from shaft.Offical import Game
from shaft.Offical import WeightModel
from shaft.Offical import filtertest
from shaft.Offical import create_weights
from shaft.Offical import sort_by_role
from shaft.Load import load_file
from shaft.Load import load_files_from_dir
from shaft.Save import create_results
from shaft.Save import create_raw_results
from shaft.Save import create_rejects
from shaft.config import roles, ref_roles, nso_roles, nso_family


if __name__ == '__main__':
    print "Damn right"
