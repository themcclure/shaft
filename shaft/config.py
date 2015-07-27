__author__ = 'hammer'

# CONFIG:
# list of known Associations, Game Types and Roles
assns = ['WFTDA', 'MRDA', 'Other']
types = ['Champs', 'Playoff', 'Sanc', 'Reg', 'Other']
#roles = ['CHR', 'HR', 'IPR', 'JR', 'OPR', 'JT', 'OWB', 'SK']
ref_roles = ['THR', 'CHR', 'HR', 'IPR', 'JR', 'OPR', 'RALT']
nso_family_st = ['JT', 'SO', 'SK']
nso_family_pm = ['PBM', 'PBT', 'LT']
nso_family_pt = ['PT', 'PW', 'IWB', 'OWB']
nso_roles = ['THNSO', 'CHNSO', 'NALT'] + nso_family_st + nso_family_pm + nso_family_pt

roles = ref_roles + nso_roles
