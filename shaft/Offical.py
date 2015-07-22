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
        return "<name: %s, refcert %d>" % (self.name, self.refcert)


# searching, filtering and sorting example code:
from itertools import ifilter
from operator import attrgetter
def filtertest():
    a1 = Official()
    a1.name = 'a'
    a1.refcert = 1
    a2 = Official()
    a2.name = 'c'
    a2.refcert = 0
    a3 = Official()
    a3.name = 'd'
    a3.refcert = 2
    a4 = Official()
    a4.name = 'b'
    a4.refcert = 2
    a = [a1, a2, a3, a4]
    print "A = ", a
    print "filtering refcert > 0:"
    rcfilter = attrgetter('refcert')
    f = ifilter(lambda x: rcfilter(x) > 0, a)
    #f = (x for x in a if attrgetter('refcert') > 0)
    for i in f: print i
    print "sorting by refcert:"
    print sorted(a, key=attrgetter('refcert', 'name'), reverse=True)
    print "filtering refcert > 0, and sorted:"
    f = ifilter(lambda x: rcfilter(x) > 0, a)
    print sorted(f, key=attrgetter('refcert', 'name'), reverse=True)
    print "filtering refcert > 0, and sorted desc by refcert and asc by name:"
    f = ifilter(lambda x: rcfilter(x) > 0, a)
    print sorted(sorted(f, key=attrgetter('name')), key=attrgetter('refcert'), reverse=True)


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