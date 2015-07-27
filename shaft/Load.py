"""
Loading an individual Official's game history, using one of several methods:
 1/ from a file
 2/ from google sheet live (FUTURE)
 3/ from tournament application sheet (FUTURE)
"""
__author__ = 'hammer'

from shaft import Official
from shaft import Game

import re
import datetime
from openpyxl import load_workbook
from openpyxl import utils
from openpyxl import Workbook

import config
assns = config.assns
types = config.types
roles = config.roles

# TODO: add in live google sheet parsing
# TODO: add in parsing of tournament applicaton sheets (raw or baked)


def normalizeCert(certString):
    """
    Takes the cert string from the history, which is a freeform field, and normalizes it to 1-5 or a blank for uncertified
    :param certString: string taken directly from the history sheet
    :return: None, or 1-5
    """
    if certString is None:
        return None
    # if it's already a number, return an int (if it's < 1 or greater than 5, return None)
    elif isinstance(certString, float) or isinstance(certString, int):
        if (certString < 1) or (certString > 5):
            return None
        else:
            return int(certString)
    # if it's a string with numbers in it, return the first one
    numbers = re.findall(r'\d+', certString)
    if numbers:
        return(int(numbers[0]))
    else:
        # there are no numbers in the cell, look for someone spelling out the numbers:
        if certString.upper() == 'ONE':
            return 1
        elif certString.upper() == 'TWO':
            return 2
        elif certString.upper() == 'THREE':
            return 3
        elif certString.upper() == 'FOUR':
            return 4
        elif certString.upper() == 'FIVE':
            return 5
        else:
            # there are no valid numbers in the string
            return None


def get_version(workbook):
    """
    Check the info tabs and make a determination about which version of the officiating history document is being used.
    Different versions keep information in different places
    :param workbook: the loaded workbook
    :return: integer with the version number, or None for unknown version
    """
    if 'Summary' in workbook.get_sheet_names():
        if 'WFTDA Referee' in workbook.get_sheet_names() or 'WFTDA NSO' in workbook.get_sheet_names():
            # this is an old history doc but it's been modified to change the WFTDA Summary tab name
            return None
        elif workbook['Instructions']['A1'].value == 'Loading...':
            # found one instance where the Instructions tab was showing "loading" - at the moment this will only happen on the new sheets
            return 2
        elif 'Last Revised 2015' in workbook['Instructions']['A104'].value:
            return 2
        else:
            return None
    elif 'WFTDA Summary' in workbook.get_sheet_names():
        return 1
    else:
        return None


def load_file(filename):
    """
    Loads an official's history document from an exported Excel file and returns it as a raw Official object
    :param filename: file location of the excel file
    :return: Official object
    """
    wb = load_workbook(filename, data_only=True, read_only=True)
    ver = get_version(wb)
    if ver == 1:
        # TODO: support the old version of the history doc
        pass
    elif ver == 2:
        # TODO: support the new version of the history doc
        # extract the official's name
        name = wb['Summary']['C4'].value
        if name is None or name == '':
            # fall back to real name
            name = wb['Summary']['C3'].value
        # create official object, and fill in metadata
        off = Official(name)
        off.refcert = (wb['Summary']['C7'].value)
        off.nsocert = (wb['Summary']['C8'].value)

        # go through each game in the Game History tab
        history = wb['Game History']
        # TODO: Should be made into a function to go throught he Other tab
        for entry in history.rows:
            date = entry[0].value
            # the top 3 rows are headers and there might be blank lines, so skip over lines without dates:
            if not isinstance(date, datetime.date):
                if isinstance(date, float):
                    try:
                        date = utils.datetime.from_excel(date)
                    except:
                        continue
                else:
                    continue
            # dateRange = getDateWeight(date,freezeDate)
            # dateWeight = weightArray['age'][dateRange]
            assn = entry[6].value
            if assn:
                assn = assn.strip()
            # if we don't recognize the association, use 'Other'
            if assn not in assns:
                assn = 'Other'

            type = entry[7].value
            # remove entries with no game type entered
            if type is None:
                continue
            else:
                type = type.strip()
                # normalize types in ALL CAPS
                type = type.capitalize()

            # skip over records that have an invalid type listed
            if type not in types:
                continue

            # main position counts for weighted score
            posn = entry[8].value
            # skip over rows with no position listed
            if posn is None:
                continue
            # remove padding whitespace so it can be found in the list of real roles
            posn = posn.strip()
            # skip positions abbreviations that don't actually exist
            if posn not in roles:
                continue

            # TODO: handle the second position

            # create the game
            off.games.append(Game(assn,type,posn))

        return(off)
    else:
        # no supported version found
        return None


# TODO: iterate through a list of some kind


# Some nifty bits of code:
"""Run this to load a file:
import shaft
o,w = shaft.filtertest()
mh = shaft.load_file('/Users/mcclure/PycharmProjects/local_crewenator/history/Mike Hammer - Game History.xlsx')
mh.weighting

import shaft ; o,w = shaft.filtertest() ; mh = shaft.load_file('/Users/mcclure/PycharmProjects/local_crewenator/history/Mike Hammer - Game History.xlsx') ; mh ; mh.apply_weight_models(w); mh.weighting
"""