__author__ = 'hammer'
"""
CONFIG:
List of known Associations, Game Types and Roles
"""
assns = ['WFTDA', 'MRDA', 'Other']
types = ['Champs', 'Playoff', 'Sanc', 'Reg', 'Other']
ref_roles = ['THR', 'CHR', 'HR', 'IPR', 'JR', 'OPR', 'RALT']
nso_family = {}
nso_family['ch'] = ['CHNSO']
nso_family['pt'] = ['PT', 'PW', 'IWB', 'OWB']
nso_family['st'] = ['JT', 'SO', 'SK']
nso_family['pm'] = ['PBM', 'PBT', 'LT']
#nso_family_pt = ['PT', 'PW', 'IWB', 'OWB']
#nso_family_st = ['JT', 'SO', 'SK']
#nso_family_pm = ['PBM', 'PBT', 'LT']
nso_roles = ['THNSO'] + nso_family['ch'] + nso_family['pt'] + nso_family['st'] + nso_family['pm'] + ['HNSO', 'NALT']

roles = ref_roles + nso_roles
