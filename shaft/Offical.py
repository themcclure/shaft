"""
Module for the Offical class and utilities to house all the information in an official's officiating history document

Theory is to keep all the raw data in summary form, and add the weighted values as well, that way either set of data can be used.
Possibly ALL the weighting models can be applied on input and just used as needed?
"""
__author__ = 'hammer'


class Official:
    def __init__(self):
        # basic stats/info about the official
        name = None
        refcert = 0
        nsocert = 0

        # WFTDA info
        chr = None

        # MRDA info
        # TODO: add MRDA info

        # Other info
        # TODO: add other info, possibly separating out juniors? Probably new format only
