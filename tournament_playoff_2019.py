import shaft
import datetime
from pathlib import Path
# from itertools import ifilter, ifilterfalse
# from operator import attrgetter, methodcaller


# sample weightings
weights = list()
# weights = shaft.create_weights()

# playoff count weighting
# w2 = shaft.WeightModel('playoff_count_2_years', ch_uplift=1.0)
# w2.wgt['WFTDA']['Champs'] = 0
# w2.wgt['WFTDA']['Playoff'] = 1
# w2.wgt['WFTDA']['Sanc'] = 0
# w2.wgt['WFTDA']['Reg'] = 0
# w2.wgt['WFTDA']['Other'] = 0
# w2.wgt['MRDA']['Champs'] = 0
# w2.wgt['MRDA']['Playoff'] = 1
# w2.wgt['MRDA']['Sanc'] = 0
# w2.wgt['MRDA']['Reg'] = 0
# w2.wgt['MRDA']['Other'] = 0
# del(w2.wgt['Other'])
# w2.decay = [1.0, 1.0, 0]
# weights.append(w2)

# champs count weighting
# w2 = shaft.WeightModel('champs_count_2_years', ch_uplift=1.0)
# w2.wgt['WFTDA']['Champs'] = 1
# w2.wgt['WFTDA']['Playoff'] = 0
# w2.wgt['WFTDA']['Sanc'] = 0
# w2.wgt['WFTDA']['Reg'] = 0
# w2.wgt['WFTDA']['Other'] = 0
# w2.wgt['MRDA']['Champs'] = 1
# w2.wgt['MRDA']['Playoff'] = 0
# w2.wgt['MRDA']['Sanc'] = 0
# w2.wgt['MRDA']['Reg'] = 0
# w2.wgt['MRDA']['Other'] = 0
# del(w2.wgt['Other'])
# w2.decay = [1.0, 1.0, 0]
# weights.append(w2)

# sanc+reg count weighting
w2 = shaft.WeightModel('wftda_sanc_reg_mrda_sanc_jrda_sanc_count_2_years', ch_uplift=1.0)
w2.wgt['WFTDA']['Champs'] = 1
w2.wgt['WFTDA']['Playoff'] = 1
w2.wgt['WFTDA']['Sanc'] = 1
w2.wgt['WFTDA']['Reg'] = 1
w2.wgt['WFTDA']['Other'] = 0
w2.wgt['MRDA']['Champs'] = 1
w2.wgt['MRDA']['Playoff'] = 1
w2.wgt['MRDA']['Sanc'] = 1
w2.wgt['MRDA']['Reg'] = 0
w2.wgt['MRDA']['Other'] = 0
w2.wgt['JRDA']['Champs'] = 1
w2.wgt['JRDA']['Playoff'] = 1
w2.wgt['JRDA']['Sanc'] = 1
w2.wgt['JRDA']['Reg'] = 0
w2.wgt['JRDA']['Other'] = 0
del(w2.wgt['Other'])
w2.decay = [1.0, 1.0, 0]
weights.append(w2)


# JRDA count weighting
# w2 = shaft.WeightModel('jrda_sanc_count_2_years', ch_uplift=1.0)
# w2.wgt['JRDA']['Champs'] = 1
# w2.wgt['JRDA']['Playoff'] = 1
# w2.wgt['JRDA']['Sanc'] = 1
# w2.wgt['JRDA']['Reg'] = 0
# w2.wgt['JRDA']['Other'] = 0
# del(w2.wgt['WFTDA'])
# del(w2.wgt['MRDA'])
# del(w2.wgt['Other'])
# w2.decay = [1.0, 1.0, 0]
# weights.append(w2)


# set the freeze date of the applications
# TODO: FUTURE: currently just a single date for each applicant, make it able to be unique per applicant (probably as part of processing a file of applicants
# freezeDate = datetime.date.today()
# this is the date applications were initially assessed and downloaded, so everyone should be held against that date so I don't have to download more recent ones all the time
# freezeDate = datetime.date(2017,5,8)
# freezeDate = datetime.date(2018, 5, 12)
freezeDate = datetime.date(2019, 5, 6)

dir_path = Path('/Volumes/GoogleDrive/My Drive/TOSP/2019')
# dir_name = '2019 - Games Histories TOSP'  # Test folder
dir_name = 'Exported Games History Docs'  # Prod folder
wdir = dir_path / dir_name
o, rejects = shaft.load_files_from_dir(wdir, freezeDate)
events = list()

for i in o:
    i.apply_weight_models(weights)
    for g in i.games:
        if g.event:
            events.append([i.name, g.date.year, g.event, g.type, g.role])


if __name__ == '__main__':
    print("Running")
    now = datetime.datetime.now()
    debug = False

    for i in o:
        print(i)
        # print("strict:")
        # print(i.weighting['wstrict'])
        # print("std/vanilla:")
        # print(i.weighting['std'])
        # print("full (all the bells and whistles):")
        # print(i.weighting['full'])

    # This is for debugging
    if debug:
        print("ref roles:")
        for r in shaft.ref_roles:
            print(r)
            print(shaft.sort_by_role(o, r, 'full'))

        print("NSO roles:")
        for r in shaft.nso_roles:
            print(r)
            print(shaft.sort_by_role(o, r, 'full'))

    for w in weights:
        shaft.create_results(wdir / f"_{dir_name}-{w.name}.xlsx", o, w)

    # write out a file of all the rejected files (and why)
    # shaft.create_rejects(filename_base + '-rejects.xlsx', rejects)

    # generate unique list of events attended by each person in the list
    events = [list(y) for y in set(tuple(y) for y in events)]
    shaft.create_events(wdir / f"_{dir_name}-events.xlsx", events)

    print(f"Runtime is {datetime.datetime.now() - now}s")
