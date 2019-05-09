__author__ = 'hammer'
"""
CONFIG:
List of known Associations, Game Types and Roles
"""
assns = ['WFTDA', 'MRDA', 'JRDA', 'Other']
types = ['Champs', 'Playoff', 'Sanc', 'Reg', 'Other']
ref_roles = ['THR', 'ATHR', 'CHR', 'HR', 'IPR', 'JR', 'OPR', 'ALTR']
nso_family = dict()
nso_family['ch'] = ['CHNSO']
nso_family['pt'] = ['PT', 'PLT', 'PW', 'IWB', 'OWB']
nso_family['st'] = ['JT', 'SBO', 'SK']
nso_family['pm'] = ['PBM', 'PBT', 'LT']
# nso_family_pt = ['PT', 'PW', 'IWB', 'OWB']
# nso_family_st = ['JT', 'SO', 'SK']
# nso_family_pm = ['PBM', 'PBT', 'LT']
nso_roles = ['THNSO', 'ATHNSO'] + nso_family['ch'] + nso_family['pt'] + nso_family['st'] + nso_family['pm'] + ['HNSO', 'ALTN']

roles = ref_roles + nso_roles
