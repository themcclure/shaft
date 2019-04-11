"""Module for the Official class and utilities to house all the information in an official's officiating history document

Theory is to keep all the raw data in summary form, and add the weighted values as well, that way either set of data can be used.
Possibly ALL the weighting models can be applied on input and just used as needed?
"""
__author__ = 'hammer'

from itertools import filterfalse
from functools import reduce
from operator import attrgetter, methodcaller

# TODO: OPTIONAL: introspect certain information... such as "how many years they've been officiating sanctioned play"
# TODO: OPTIONAL: FUTURE: keep track (and a count) of the distinct tournament names as a guide to how well travelled they are


# CONFIG:
# list of known Associations, Game Types and Roles
from . import config
assns = config.assns
types = config.types
roles = config.roles

class Official:
    """The basic official object.
    Contains data about that official, and the set of games they've worked.
    It contains:
        a list of games officiated:
            note that secondary positions officiated count here
        the processed weighting in each role (and NSO family), including secondary positions
    """

    def __init__(self, name):
        # basic stats/info about the official
        self.name = name
        self.refcert = 0
        self.nsocert = 0
        self.games = []
        self.game_tally = 0
        self.ref_tally = 0
        self.nso_tally = 0
        self.weighting = {}
        self.qualified_games = {}

    def __repr__(self):
        return "<name: %r, refcert %d, nsocert: %d, games %d>" % (self.name, self.refcert, self.nsocert, self.game_tally)

    def add_game(self, game):
        """
        Adds a game to the tally. If it's a primary position game, update Ref, NSO and total tallies
        Note that secondary and tertiary positions don't count for total counts
        :param game: Game object
        :return: None
        """
        self.games.append(game)
        if game.primacy == 1:
            self.game_tally += 1
            if game.role in config.ref_roles:
                self.ref_tally += 1
            elif game.role in config.nso_roles:
                self.nso_tally += 1

    def get_games(self, role, primary_only=False):
        """
        Returns a list of games of the role(s) queried
        :param role: string of the role name, or a list of strings
        :param primary_only: boolean. If yes, then return only primary roles otherwise return primary and secondary roles
        :return: list of matching Games
        """
        if not isinstance(role, list):
                role = [role]
        if primary_only:
            return list(filter(lambda x: attrgetter('role')(x) in role, list(filter(lambda x: attrgetter('primacy')(x) == 1, self.games))))
        else:
            return list(filter(lambda x: attrgetter('role')(x) in role, self.games))

    def apply_weight_models(self, models):
        """
        Take in a list of WeightModels and process each, adding the result under the model name (rounding off to 2 decimal places)
        :param models: list of WeightModels to be applied to the Official
        """
        for model in models:
            self.weighting[model.name] = {}
            self.qualified_games[model.name] = {}

            # iterate through each role for processing
            for r in roles:
                # lambda magic to reduce through the list of games in that role, and apply weight, and sum the weights
                self.weighting[model.name][r] = round(reduce(lambda a,b: a + model.weight(b), self.get_games(r), 0), 2)
                self.qualified_games[model.name][r] = reduce(lambda a,b: a + model.qualify(b), self.get_games(r), 0)

            # CH and H count as the same role, but H doesn't get a CH bonus, so they should be added to the CH slot
            self.weighting[model.name]['CHR'] += self.weighting[model.name]['HR']
            self.qualified_games[model.name]['CHR'] += self.qualified_games[model.name]['HR']
            self.weighting[model.name]['CHNSO'] += self.weighting[model.name]['HNSO']
            self.qualified_games[model.name]['CHNSO'] += self.qualified_games[model.name]['HNSO']

            # add in the weighting for each NSO family
            for f in config.nso_family:
                self.weighting[model.name][f] = 0
                self.qualified_games[model.name][f] = 0
                for r in config.nso_family[f]:
                    self.weighting[model.name][f] += self.weighting[model.name][r]
                    self.qualified_games[model.name][f] += self.qualified_games[model.name][r]
                self.weighting[model.name][f] = round(self.weighting[model.name][f], 2)

    def get_weight(self, role, model):
        """
        Primarily for sorting purposes, this returns the weighted value for the selected role from the named weight model
        :param role: role to be queried
        :param model: model to be used
        :return: weighting
        """
        wgt = self.weighting[model][role]
        if wgt > 0:
            return wgt
        else:
            return None

    def get_summary(self, model):
        """
        Gets the summary of the entire Official and returns a list, most notably for printing
        :param model: weighting model to use
        :return: list of all the relevant attributes and scores in the order they're listed in the config file
        """
        summary = [self.name, self.refcert, self.nsocert, self.game_tally]
        for r in roles:
            summary.append(self.weighting[model][r])
        return summary

    # TODO: FUTURE: put this in config as a dict of header/attribute pairs so dict.keys() gets the header row and dict.values() & getattr returns the values row
    def get_summary_header(self):
        """
        Gets the header line for the summary of the entire Official, most notably for printing
        :return: list of all the relevant header labels in the order they're listed in the config file
        """
        basic = ['Name', 'Ref Cert', 'NSO Cert', 'Total Games']
        return basic + roles

    def get_role_summary(self, role, model):
        """
        Gets the summary of the named role for the Official and returns a list, most notably for printing
        :param role: selected role
        :param model: weighting model to use
        :return: list of all the relevant attributes and scores in the order they're listed in the config file
        """
        if role in config.ref_roles:
            summary = [self.name, self.refcert, self.weighting[model][role], self.qualified_games[model][role]]
        else:
            summary = [self.name, self.nsocert, self.weighting[model][role], self.qualified_games[model][role]]
        return summary

    # TODO: FUTURE: put this in config as a dict of header/attribute pairs so dict.keys() gets the header row and dict.values() & getattr returns the values row
    def get_role_header(self):
        """
        Gets the header line for the role view of the Official, most notably for printing
        :return: list of all the relevant header labels in the order they're listed in the config file
        """
        return ['Name', 'Cert', 'Weighted Value', 'Qualified Games']


class Game:
    """
    Each official will have a history made up of many games
    Note:
        Age is the the number of whole years since the reference date (freezeDate)
        Primacy is 1 for games worked in the primary position, 2 for secondary positions
    """
    def __init__(self, assn, gtype, role, age, primacy, date=None, event=None):
        # default "error" values
        self.assn = None
        self.type = None
        self.role = None
        self.age = None
        self.date = None
        self.primacy = None
        self.event = None

        # if all the inputs are valid, then populate the data
        if (assn in assns) and (gtype in types) and (role in roles) and (age >= 0) and (primacy >= 1):
            self.assn = assn
            self.type = gtype
            self.role = role
            self.age = age
            self.date = date
            self.primacy = primacy
            self.event = event

    def __repr__(self):
        return "<Assn %s, Role %s>" % (self.assn, self.role)


class WeightModel:
    """This is a weighting model to weight each Game in an Official's history.
    The model describes weight factors that will be applied to each game.
    Each model will have a unique name what will be attached to the Official object so that multiple weighting models can
    be applied and then queried individually to provide a comparison
    Current factors that can be weighted:
        - Association (WFTDA, etc)
        - Type of game (Sanc, Reg, etc)
        - Primary or Secondary role (optional scale down factor for secondary roles)
        - Age of game (relative to today or otherwise configured freezeDate
        - Crew Head role bonus
    """
    def __init__(self, name, ch_uplift=1.2):
        self.wgt = {}
        self.name = name
        self.ch_uplift = ch_uplift
        self.secondary_weight = 1
        self.tertiary_weight = 1
        self.decay = [1]
        for assn in assns:
            if assn not in self.wgt.keys():
                self.wgt[assn] = {}
            for gtype in types:
                self.wgt[assn][gtype] = 1

    def __repr__(self):
        return "<Weight model %s>" % self.name

    def weight(self, game):
        """
        Takes a Game and produces a weighted value for that game, based on the weighting model
        :param game: Game object
        :return: real number value
        """
        if game.assn not in self.wgt.keys():
            return 0
        if game.type not in self.wgt[game.assn].keys():
            return 0

        # apply the basic weighing of the game and association from the model
        wgt = self.wgt[game.assn][game.type]

        # apply the scaling for secondary roles
        if game.primacy == 2:
            wgt = wgt * self.secondary_weight

        # apply the scaling for tertiary roles (ie Other tab games)
        if game.primacy == 3:
            wgt = wgt * self.tertiary_weight

        # apply the age decay
        if game.age < len(self.decay):
            wgt = wgt * self.decay[game.age]
        else:
            wgt = wgt * self.decay[-1]

        # apply the CH uplift
        if game.role in ['CHR', 'CHNSO']:
            wgt = wgt * self.ch_uplift

        return wgt

    def qualify(self, game):
        """
        Takes a Game and produces a qualified value for that game, based on the weighting model
        as to whether the game should be included in the minimums or not.
        Based on the assumption that if there is a weighting entry for the association/type/age that is greater than 0,
        then the game counts as a qualified game
        Also, that if games have a primacy other than 1, the game des not qualify
        :param game: Game object
        :return: integer number value (1 or 0)
        """
        if game.assn not in self.wgt.keys():
            return 0
        if game.type not in self.wgt[game.assn].keys():
            return 0

        if game.primacy > 1:
            return 0

        # figure out the age decay
        if game.age < len(self.decay):
            decay = self.decay[game.age]
        else:
            decay = self.decay[-1]
        if decay <= 0:
            return 0

        if self.wgt[game.assn][game.type] > 0:
            return 1
        else:
            return 0


# NOTES: Some very clever functions:
# returns an array of games where the official a[1]'s role was OPR
# list(ifilter(lambda x: attrgetter('role')(x) == 'OPR', a[1].games))
# this could be one way to calculate weighting function results, using reduce, but instead of add, using
# whatever function is there to apply the weight model:
# reduce(lambda x,y: x+y, ifilter(lambda x: attrgetter('role')(x) == 'OPR', a[1].games))
"""Line to load the test data:
import shaft ; o,w = shaft.filtertest()
"""


# searching, filtering and sorting example data:
def filtertest():
    a1 = Official('a')
    a1.refcert = 1
    a1.nsocert = 1
    a1.games.append(Game('WFTDA', 'Playoff', 'CHR', 0, 1))
    a1.games.append(Game('WFTDA', 'Sanc', 'IPR', 0, 1))
    a1.games.append(Game('WFTDA', 'Other', 'IPR', 0, 1))
    a2 = Official('c')
    a2.refcert = 0
    a2.nsocert= 0
    a2.games.append(Game('WFTDA', 'Playoff', 'OPR', 0, 1))
    a2.games.append(Game('WFTDA', 'Other', 'OPR', 0, 1))
    a2.games.append(Game('WFTDA', 'Reg', 'OPR', 0, 1))
    a2.games.append(Game('MRDA', 'Sanc', 'JR', 0, 1))
    a3 = Official('d')
    a3.refcert = 2
    a3.nsocert = 0
    a3.games.append(Game('WFTDA', 'Sanc', 'JR',0,1))
    a4 = Official('b')
    a4.refcert = 2
    a4.nsocert = 0
    a5 = Official('e')
    a5.refcert = 0
    a5.nsocert = 1
    a = [a1, a2, a3, a4, a5]
    print(f"A = {a}")
    print("filtering refcert > 0:")
    f = filter(lambda x: attrgetter('refcert')(x) > 0, a)
    for i in f: print(i)
    print("filtered ones (simpler):")
    f = filterfalse(lambda x: attrgetter('refcert')(x) > 0, a)
    for i in f: print(i)
    print("sorting by refcert:")
    print(sorted(a, key=attrgetter('refcert', 'name'), reverse=True))
    print("filtering refcert > 0, and sorted:")
    f = filter(lambda x: attrgetter('refcert')(x) > 0, a)
    print(sorted(f, key=attrgetter('refcert', 'name'), reverse=True))
    print("filtering refcert > 0, and sorted desc by refcert and asc by name:")
    f = filter(lambda x: attrgetter('refcert')(x) > 0, a)
    print(sorted(sorted(f, key=attrgetter('name')), key=attrgetter('refcert'), reverse=True))

    # returns the test officials array, after running the filter code
    return a

def create_weights():
    """
    Create the default set of weighting models
    :return: returns an list of weight models
    """
    # vanilla model, all 1s (basically a count of the number of games worked with no age decay)
    # w1 = WeightModel('std', 1)

    # strict WFTDA only, Regulation or better, standard weights and standard age decay
    w2 = WeightModel('wstrict')
    w2.wgt['WFTDA']['Champs'] = 1.25
    w2.wgt['WFTDA']['Playoff'] = 1.2
    w2.wgt['WFTDA']['Reg'] = 0.9
    w2.wgt['WFTDA']['Other'] = 0
    w2.decay = [1.0, 0.9, 0.2, 0.1]
    del(w2.wgt['MRDA'])
    del(w2.wgt['Other'])

    # w3 = WeightModel('aged')
    # w3.decay = [1.0, 0.9, 0.2, 0.1]

    # w4 = WeightModel('full')
    # w4.wgt['WFTDA']['Champs'] = 1.25
    # w4.wgt['WFTDA']['Playoff'] = 1.2
    # w4.wgt['WFTDA']['Sanc'] = 1.0
    # w4.wgt['WFTDA']['Reg'] = 0.9
    # w4.wgt['WFTDA']['Other'] = 0.1
    # w4.wgt['MRDA']['Champs'] = 1.0
    # w4.wgt['MRDA']['Playoff'] = 0.9
    # w4.wgt['MRDA']['Sanc'] = 0.7
    # w4.wgt['MRDA']['Reg'] = 0.4
    # w4.wgt['MRDA']['Other'] = 0.1
    # w4.wgt['Other']['Champs'] = 0.5
    # w4.wgt['Other']['Playoff'] = 0.5
    # w4.wgt['Other']['Sanc'] = 0.2
    # w4.wgt['Other']['Reg'] = 0.1
    # w4.wgt['Other']['Other'] = 0.01
    # w4.decay = [1.0, 0.9, 0.2, 0.1]
    #
    # w = [w1,w2,w4]
    w = [w2]

    # return weight model (array)
    return w


def sort_by_role(officials, role, weight_model, filter_zero_weight=True):
    """
    This function sorts the officials in a list, in order of their weighted value for a role, in a given model
    :param officials: list of officials
    :param role: role to be sorted by
    :param weight_model: name of the model to sort by
    :param filter_zero_weight: if the zero weight entries should be removed from the returned list
    :return: sorted list of officials data (name, cert level (ref or NSO depending on the role), weighted value, raw games in that role)
    """

    # remove the officials with no experience in the role
    inner_list = officials
    if filter_zero_weight is True:
        inner_list = filter(lambda x: methodcaller('get_weight', role, weight_model)(x) > 0, officials)

    # sort the list by weighted value
    inner_list = sorted(inner_list, key=methodcaller('get_weight', role, weight_model), reverse=True)

    # return a list of tuples containing just the information needed
    # return map(lambda z: (z.name, z.refcert if role in config.ref_roles else z.nsocert, z.weighting[weight_model][role], len(z.get_games(role))), inner_list)
    return map(lambda z: z.get_role_summary(role, weight_model), inner_list)


if __name__ == '__main__':
    # o = filtertest()
    w = create_weights()
    from . import Load
    mh = Load.load_file('../sample/MikeHammer_GameHistoryNew.xlsx')
    mh.apply_weight_models(w)
    print(mh.weighting['wstrict'])
    # print(mh.weighting['std'])
    # print(mh.weighting['aged'])
