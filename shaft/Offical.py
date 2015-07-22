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

        # Associations
        assoc = []

        # WFTDA info
        chr = None

        # MRDA info
        # TODO: add MRDA info

        # Other info
        # TODO: add other info, possibly separating out juniors? Probably new format only

    def __repr__(self):
        return "<name: %s>" % (self.name)


# searching, filtering and sorting example code:
from itertools import ifilter
from operator import attrgetter
def filtertest():
    a1 = Official()
    a1.name = 'a'
    a1.refcert = 1
    a2 = Official()
    a2.name = 'b'
    a2.refcert = 0
    a = [a1, a2]
    f = ifilter(attrgetter('refcert') >= 0, a)
    f = (x for x in a if attrgetter('refcert') >= 0)
    for i in f: print i.name


class History:
    """
    Each official will have a history with an association. each Association recorded
    """
    def __init__(self):
        pass


class Position:
    """
    Each official will have experience in many different positions, this is the record of all their
    """