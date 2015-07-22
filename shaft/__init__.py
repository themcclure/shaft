"""Module to process and rank officials by experience.

We have several parts:
- load an official from an exported Excel file (old and new formats accepted)
- load an official from live google sheets (not implemented)
- summarise a list of officials from a given directory
- standard options for processing
- process tournament application sheets (not implemented)
"""
__author__ = 'hammer'

#TODO: OO the whole lot
#TODO: modularise the whole lot. options baby, options
#TODO: standardise a few different weighting models

from shaft.Offical import Official
from shaft.Offical import History
from shaft.Offical import filtertest


if __name__ == '__main__':
    print "Damn right"
