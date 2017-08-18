"""
Loading an Official's game history, using one of several methods:
 1/ from a file (Excel export)
 2/ from a directory of Excel exports
 2/ from google sheet live (FUTURE)
 3/ from tournament application sheet (FUTURE)
"""
__author__ = 'hammer'

from shaft import Official
from shaft import Game

import re
import os
import datetime
from dateutil import relativedelta
from openpyxl import load_workbook
from openpyxl import utils
from openpyxl import Workbook

import config
assns = config.assns
types = config.types
roles = config.roles


# TODO: FUTURE: add in live google sheet parsing
# TODO: FUTURE: add in parsing of tournament applicaton sheets (raw or baked)
# TODO: FUTURE: OPTIONAL: iterate through a file to generate the list of officials


def normalize_cert(cert_string):
    """
    Takes the cert string from the history, which is a freeform field, and normalizes it to 1-5 or a blank for uncertified
    :param cert_string: string taken directly from the history sheet
    :return: None, or 1-5
    """
    if cert_string is None:
        return 0
    # if it's already a number, return an int (if it's < 1 or greater than 5, return None)
    elif isinstance(cert_string, float) or isinstance(cert_string, int):
        if (cert_string < 1) or (cert_string > 5):
            return 0
        else:
            return int(cert_string)
    # if it's a string with numbers in it, return the first one
    numbers = re.findall(r'\d+', cert_string)
    if numbers:
        return int(numbers[0])
    else:
        # there are no numbers in the cell, look for someone spelling out the numbers:
        if cert_string.upper() == 'ONE':
            return 1
        elif cert_string.upper() == 'TWO':
            return 2
        elif cert_string.upper() == 'THREE':
            return 3
        elif cert_string.upper() == 'FOUR':
            return 4
        elif cert_string.upper() == 'FIVE':
            return 5
        else:
            # there are no valid numbers in the string
            return 0


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
        elif 'Instructions' not in workbook.get_sheet_names():
            # this is a new history doc it's been modified to delete the instructions tab (a no no)
            return None
        elif workbook['Instructions']['A1'].value == 'Loading...':
            # found one instance where the Instructions tab was showing "loading" - at the moment this will only happen on the new sheets
            return 2
        elif 'Last Revised 2015' in workbook['Instructions']['A104'].value:
            return 2
        elif 'Last Revised 2016' in workbook['Instructions']['A104'].value:
            return 3
        elif 'Last Revised 2017-01-05' in workbook['Instructions']['A104'].value:
            return 4
        else:
            return None
    elif 'WFTDA Summary' in workbook.get_sheet_names():
        return 1
    else:
        return None


def load_file(filename, freezeDate=datetime.date.today()):
    """
    Loads an official's history document from an exported Excel file and returns it as a raw Official object
    :param filename: file location of the excel file
    :param freezeDate: the date to measure the age of games
    :return: Official object
    """
    wb = load_workbook(filename, data_only=True, read_only=True)
    ver = get_version(wb)
    if ver == 1:
        # TODO: OPTIONAL: support the old version of the history doc
        print "**** OLD History Doc found: %s" % filename
        return None
    elif (ver == 2) or (ver == 3) or (ver == 4):
        # extract the official's name
        name = wb['Summary']['C4'].value
        if name is None or name == '' or name == '-':
            # fall back to real name
            name = wb['Summary']['C3'].value
        # create official object, and fill in metadata
        off = Official(unicode(name))
        off.refcert = normalize_cert(wb['Summary']['C7'].value)
        off.nsocert = normalize_cert(wb['Summary']['C8'].value)

        # go through each game in the Game History tab
        history = wb['Game History']
        # TODO: OPTIONAL: Should be made into a function to go through the Other tab... maybe primacy 3, so easily filtered?
        # TODO: OPTIONAL: like, (date, assn, type, role, secondary_role) = process_row(entry) - that way the Other tab can be processed just fine
        for entry in history.rows:
            # skip entirely blank lines
            if len(entry) == 0:
                continue
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

            # calculate the age (in whole years), relative to the freezeDate / today
            # skipping over games that happen in the "future"
            date = date.date()
            if date > freezeDate:
                continue
            age = relativedelta.relativedelta(freezeDate, date).years

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

            # extract the primary role/position (secondary position is handled below)
            role = entry[8].value
            # skip over rows with no position listed
            if role is None:
                continue
            # remove padding whitespace so it can be found in the list of real roles
            role = role.strip()
            # skip positions abbreviations that don't actually exist
            if role not in roles:
                continue

            # extract the secondary role/position (secondary position is handled below)
            secondary = entry[9].value
            # remove padding whitespace so it can be found in the list of real roles
            if secondary is not None:
                secondary = secondary.strip()

            # create the primary game
            off.add_game(Game(assn, type, role, age, 1, date))

            # create the secondary game
            secondary_game = Game(assn, type, secondary, age, 2, date)
            if secondary_game.primacy is not None:
                off.add_game(secondary_game)

        return off

    # no supported version found
    return None


def load_files_from_dir(history_dir, freezeDate=datetime.date.today()):
    """
    Open the given directory and grab all the Officiating history excel files and load them
    :param history_dir: directory name
    :param freezeDate: the date to measure the age of games
    :return: list of Officials
    """
    histories = []
    rejects = []
    # get the list of history docs to process
    file_list = os.walk(history_dir).next()[2]
    # remove files that start with a . like .DS_Store and .bashrc etc
    file_list = [f for f in file_list if not f[0] == '.']

    print file_list
    for filename in file_list:
        # skip over files that begin with _ (such as output from this tool)
        if filename[0] == '_':
            continue
        # skip over filenames that aren't long enough to be real files
        elif len(filename) < 6:
            continue
        # skip files that do not end with a .xlsx
        elif filename[-5:] != '.xlsx':
            continue
        print filename
        h = load_file(history_dir + '/' + filename, freezeDate)
        if h is not None:
            histories.append(h)
        else:
            rejects.append((filename, "unsupported document version"))

    return histories, rejects


import gspread
from oauth2client.client import AccessTokenCredentials


def load_google_sheet(url, token, freezeDate=datetime.date.today()):
    """
    Loads an official's history document from a live google sheet and returns it as a raw Official object
    :param url: the URL of history doc
    :param token: the security token required
    :param freezeDate: the date to measure the age of games
    :return: Official object
    """
    access_token = "ya29.Ci8uA-oQLfvo_NIVOh6ayWiNadGSt52xcN8TUY97ywsBMrwJOFdiXr_yeTdbdXXh0A"
    refresh_token = "1/EoXmQmxwjPGsGsyxB7wJ630dLVJrrU29Ff3lcZ8aubE"
    mike_url = "https://docs.google.com/spreadsheets/d/1kG9QTdus7LbpZP-3L9fNvwQ0nVpUUXyw7m7hpKSBH-E/edit#gid=2008460745"
    aggie_url = "https://docs.google.com/spreadsheets/d/1f9do7TIC31ktgCww0Sw1kvEl7bQc6RPCMExFhfR7cso/edit#gid=1988016352"
    clobber_url = "https://docs.google.com/spreadsheets/d/1kbScLowzIzpDkKtr9eO9MvWnaGdG3V4RDzQqV_KOcso/edit#gid=1988016352"
    urls = [mike_url, aggie_url, clobber_url]
    creds = AccessTokenCredentials(access_token, 'Agent/1.0')
    gs = gspread.authorize(creds)
    wb = gs.open_by_url(urls[url])

    return wb






# Some nifty bits of code:
"""Run this to load a file:
import shaft
o,w = shaft.filtertest()
mh = shaft.load_file('/Users/mcclure/PycharmProjects/local_crewenator/history/Mike Hammer - Game History.xlsx')
mh.apply_weight_models(w)
mh.weighting

import shaft ; w = shaft.create_weights() ; mh = shaft.load_file('sample/Mike Hammer - Game History - new with future.xlsx') ; mh ; mh.apply_weight_models(w); mh.weighting['wstrict']; mh.weighting['std']
"""


"""
This from the old way of doing things - but this is the code that parses the old format:
# parses the old sheets (since ref and NSO tabs are the same, just on different sheets) and populates the gameRoleCount
def getRoleCountFromOldSheet(history, freezeDate, minPosGames, gameRoleCount, weightArray, gameCountArray):
    # have to modify the num*Games variables this way to make them effectively pass-by-reference
    numGames = 0
    numQualGames = 0

    for entry in history.rows:
        date = entry[0].value
        # the top 3 rows are headers and there might be blank lines, so skip over lines without dates:
        if not isinstance(date, datetime.date):
            if isinstance(date, float):
                date = utils.datetime.from_excel(date)
            else:
                continue

        dateRange = getDateWeight(date,freezeDate)
        dateWeight = weightArray['age'][dateRange]
        assn = 'WFTDA'
        assnWeight = weightArray['assn'][assn]

        # have to pick game type and position out of 4 columns. Only one entry can count, so we don't check for multiple
        if entry[6].value:
            posn = entry[6].value.upper()
            type = 'Playoff'
        elif entry[7].value:
            posn = entry[7].value.upper()
            type = 'Sanc'
        elif entry[8].value:
            posn = entry[8].value.upper()
            type = 'Reg'
        elif entry[9].value:
            posn = entry[9].value.upper()
            type = 'Other'
        else:
            # skip over rows with no position listed
            continue

        # remove positions with whitespace
        # TODO: found in JewJew
        posn = posn.strip()

        # convert from ALT to ALTR/ALTN
        if posn == 'ALT':
            if history.title == 'WFTDA Referee':
                posn = 'ALTR'
            else:
                posn = 'ALTN'

        typeWeight = weightArray['type'][type]


        # raw number of games
        numGames += 1

        # skip positions abbreviations that don't actually exist
        # TODO: found in Apron & Turtle
        if posn not in gameRoleCount[assn].keys():
            continue

        # assign game weighting
        gameWeight = dateWeight * assnWeight * typeWeight
        gameRoleCount[assn][posn][1] += gameWeight
        #print gameWeight

        # count of the number of games worked in a position ... but only Playoff, Sanc or Reg games that are recent or relevant
        if (type is not 'Other') and (dateRange == "recent" or dateRange == "relevant"):
            numQualGames += 1
            gameRoleCount[assn][posn][0] += 1
            if gameRoleCount[assn][posn][0] >= minPosGames:
                gameRoleCount[assn][posn][2] = True

        # if the minimum number of games is 0, then everyone should qualify for any role they've worked!
        if minPosGames == 0:
            gameRoleCount[assn][posn][2] = True

    gameCountArray[0] += numGames
    gameCountArray[1] += numQualGames

"""