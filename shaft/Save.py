"""
Taking a list of Officials and saving the summary to an Excel sheet
"""
__author__ = 'hammer'

from shaft import Official
from shaft import Game
from Offical import sort_by_role

import re
import os
import datetime
from operator import attrgetter
from dateutil import relativedelta
from openpyxl import load_workbook
from openpyxl import utils
from openpyxl import Workbook

import config
assns = config.assns
types = config.types
roles = config.roles
ref_roles = config.ref_roles
nso_roles = config.nso_roles
nso_family = config.nso_family

def create_results(file_name, officials, model_name):
    """
    create the Excel file summarizing the officials, given the chosen weighting model
    :param file_name: the name of the file to output
    :param officials: the list of officials
    :param model_name: the name of the weighting model to use
    :return: the excel object (for now)
    """
    order = 0
    wb = Workbook()
    page1 = wb.active
    page1.title = "Applicants"

    header = officials[0].get_summary_header()
    wb['Applicants'].append(header)
    #wb['applicants'].auto_filter.ref = 'A1:BH1'

    # print summary of entire list, sorted by name
    for off in sorted(officials, key=attrgetter('name')):
        print off
        off.get_summary(model_name)
        wb['Applicants'].append(off.get_summary(model_name))

    # go through each ref role:
    for r in ref_roles:
        order += 1
        wb.create_sheet(order, r)
        wb[r].append(officials[0].get_role_header())
        for o in sort_by_role(officials, r, model_name):
            wb[r].append(o)

    # go through each nso role:
    for r in nso_roles:
        order += 1
        wb.create_sheet(order, r)
        wb[r].append(officials[0].get_role_header())
        for o in sort_by_role(officials, r, model_name):
            wb[r].append(o)

    # save the file
    wb.save(file_name)
