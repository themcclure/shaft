import shaft
import datetime
# from itertools import ifilter, ifilterfalse
# from operator import attrgetter, methodcaller


# sample weightings
weights = list()
# weights = shaft.create_weights()
# weights[2].secondary_weight = 0.9
# weights[2].tertiary_weight = 0.1

# TH weighting model - WFTDA full, MRDA/Other lower
w = shaft.WeightModel('cc2017_model')
w.wgt['WFTDA']['Champs'] = 1.20
w.wgt['WFTDA']['Playoff'] = 1.20
w.wgt['WFTDA']['Sanc'] = 1.0
w.wgt['WFTDA']['Reg'] = 0.8
w.wgt['WFTDA']['Other'] = 0.4
w.wgt['MRDA']['Champs'] = 0.4
w.wgt['MRDA']['Playoff'] = 0.4
w.wgt['MRDA']['Sanc'] = 0.4
w.wgt['MRDA']['Reg'] = 0.4
w.wgt['MRDA']['Other'] = 0.3
w.decay = [1.0, 0.9, 0.5, 0.3, 0.1]
del(w.wgt['Other'])
weights.append(w)


# set the freeze date of the applications
# TODO: FUTURE: currently just a single date for each applicant, make it able to be unique per applicant (probably as part of processing a file of applicants
# this is the date applications were initially assessed and downloaded, so everyone should be held against that date so I don't have to download more recent ones all the time
# freezeDate = datetime.date.today()
freezeDate = datetime.date(2017, 1, 1)

# production ENV
dir_path = '/Users/mcclure/Google Drive/TOSP/2016/2016 Selections/'
dir_name = 'Applicant History Docs'
# Diva's data set:
# dir_name = 'Copy of Applicant History Docs'

# test ENV (uncomment to run on test data)
# dir_path = '/Users/mcclure/Google Drive/Crewenator/CC2017/'
# dir_name = 'Docs Test'

# load the officials information from the exported excel files
o, rejects = shaft.load_files_from_dir(dir_path + dir_name, freezeDate)


if __name__ == '__main__':
    print("Running")
    for i in o:
        print(i)
        # print("strict:")
        # print(i.weighting['wstrict'])
        # print("std/vanilla:")
        # print(i.weighting['std'])
        # print("full (all the bells and whistles):")
        # print(i.weighting['full'])

    filename_base = dir_path + dir_name + '/_' + dir_name
    shaft.create_raw_results(filename_base + '-Raw_Dump.xlsx', o, w)
