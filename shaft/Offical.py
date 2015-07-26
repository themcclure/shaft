"""Module for the Offical class and utilities to house all the information in an official's officiating history document

Theory is to keep all the raw data in summary form, and add the weighted values as well, that way either set of data can be used.
Possibly ALL the weighting models can be applied on input and just used as needed?
"""
__author__ = 'hammer'

from itertools import ifilter, ifilterfalse
from operator import attrgetter

# TODO: implement __str__() to use print to print an official straight into the spreadsheet
# TODO: implement print_role() type thing too... pity __str__() won't work for that...
# TODO: introspect certain information... such as "how many years they've been officiating sanctioned play"


# CONFIG:
# list of known Associations, Game Types and Roles
assns = ['WFTDA', 'MRDA', 'Other']
types = ['Champs', 'Playoff', 'Sanc', 'Reg', 'Other']
roles = ['CHR', 'JR', 'OPR']


class Official:
    """The basic official object.
    Contains data about that official, and the set of games they've worked.
    """
    def __init__(self):
        # basic stats/info about the official
        self.name = None
        self.refcert = 0
        self.nsocert = 0
        self.games = []

    def __repr__(self):
        return "<name: %s, refcert %d, games %d>" % (self.name, self.refcert, len(self.games))

    def get_games(self, role):
        """
        Returns a list of games of that role
        :param role: string of the role name
        :return: list of Games
        """
        return list(ifilter(lambda x: attrgetter('role')(x) == role, self.games))

    def apply_weight_models(self, models):
        """
        Take in a list of WeightModels and process each, adding the result under the model name
        :param models: list of WeightModels to be applied to the Official
        """
        for model in models:
            self.weighting[model.name] = []


class Game:
    """
    Each official will have a history made up of many games
    """
    def __init__(self, assn, type, role):
        # default values
        self.assn = 'Other'
        self.type = 'Other'
        self.role = None
        # override from constructor
        if assn in assns:
            self.assn = assn
        if type in types:
            self.type = type
        if role in roles:
            self.role = role

    def __repr__(self):
        return "<Assn %s, Role %s>" % (self.assn, self.role)


class WeightModel:
    """This is a weighting model to weight each Game in an Official's history.
    The model describes weight factors that will be applied to each game.
    Each model will have a unique name what will be attached to the Official object so that multiple weighting models can
    be applied and then queried individually to provide a comparison
    """
    ch_uplift = 1.2
    wgt = {}

    def __init__(self, name):
        self.name = name
        for assn in assns:
            if assn not in self.wgt.keys():
                self.wgt[assn] = {}
            for type in types:
                self.wgt[assn][type] = 1

    def __repr__(self):
        return "<Weight model %s>" % self.name

    def weight(self, game):
        """
        Takes a Game and produces a weighted value for that game, based on the weighting model
        :param game: Game object
        :return: real number value
        """
        wgt = self.wgt[game.assn][game.type]
        if game.role in ['CHR', 'CHNSO']:
            wgt = wgt * self.ch_uplift
        return wgt


# NOTES:
# TODO: Some very clever functions:
# returns an array of games where the official a[1]'s role was OPR
# list(ifilter(lambda x: attrgetter('role')(x) == 'OPR', a[1].games))
# this could be one way to calculate weighting function results, using reduce, but instead of add, using
# whatever function is there to apply the weight model:
# reduce(lambda x,y: x+y, ifilter(lambda x: attrgetter('role')(x) == 'OPR', a[1].games))
# TODO: serialize the weighting module for editing by humans... maybe pickle or a csv module?


# searching, filtering and sorting example data:
def filtertest():
    a1 = Official()
    a1.name = 'a'
    a1.refcert = 1
    a1.nsocert = 1
    a1.games.append(Game('WFTDA', 'Playoff', 'CHR'))
    a1.games.append(Game('WFTDA', 'Sanc', 'IPR'))
    a2 = Official()
    a2.name = 'c'
    a2.refcert = 0
    a2.nsocert= 0
    a2.games.append(Game('WFTDA', 'Playoff', 'OPR'))
    a2.games.append(Game('WFTDA', 'Other', 'OPR'))
    a2.games.append(Game('WFTDA', 'Reg', 'OPR'))
    a3 = Official()
    a3.name = 'd'
    a3.refcert = 2
    a3.nsocert = 0
    a3.games.append(Game('WFTDA', 'Sanc', 'JR'))
    a4 = Official()
    a4.name = 'b'
    a4.refcert = 2
    a4.nsocert = 0
    a5 = Official()
    a5.name = 'e'
    a5.refcert = 0
    a5.nsocert = 1
    a = [a1, a2, a3, a4, a5]
    print "A = ", a
    print "filtering refcert > 0:"
    f = ifilter(lambda x: attrgetter('refcert')(x) > 0, a)
    for i in f: print i
    print "filtered ones (simpler):"
    f = ifilterfalse(lambda x: attrgetter('refcert')(x) > 0, a)
    for i in f: print i
    print "sorting by refcert:"
    print sorted(a, key=attrgetter('refcert', 'name'), reverse=True)
    print "filtering refcert > 0, and sorted:"
    f = ifilter(lambda x: attrgetter('refcert')(x) > 0, a)
    print sorted(f, key=attrgetter('refcert', 'name'), reverse=True)
    print "filtering refcert > 0, and sorted desc by refcert and asc by name:"
    f = ifilter(lambda x: attrgetter('refcert')(x) > 0, a)
    print sorted(sorted(f, key=attrgetter('name')), key=attrgetter('refcert'), reverse=True)

    # example weight array
    w1 = WeightModel('open')
    w1.wgt['WFTDA']['Playoff'] = 1.2
    w2 = WeightModel('wstrict')
    w2.wgt['WFTDA']['Other'] = 0
    del(w2.wgt['MRDA'])

    w = [w1,w2]
    # return the same officials array, and weight array
    return a,w


if __name__ == '__main__':
    filtertest()