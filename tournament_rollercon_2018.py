import shaft
import datetime


# sample weightings
weights = list()
# weights = shaft.create_weights()
# weights[2].secondary_weight = 0.9
# weights[2].tertiary_weight = 0.1

# TH weighting model
w = shaft.WeightModel('rollercon_2018_model')
w.wgt['WFTDA']['Champs'] = 1.0
w.wgt['WFTDA']['Playoff'] = 1.0
w.wgt['WFTDA']['Sanc'] = 0.75
w.wgt['WFTDA']['Reg'] = 0.5
w.wgt['WFTDA']['Other'] = 0.25
w.wgt['MRDA']['Champs'] = 1.0
w.wgt['MRDA']['Playoff'] = 1.0
w.wgt['MRDA']['Sanc'] = 0.75
w.wgt['MRDA']['Reg'] = 0.5
w.wgt['MRDA']['Other'] = 0.25
w.wgt['JRDA']['Champs'] = 1.0
w.wgt['JRDA']['Playoff'] = 1.0
w.wgt['JRDA']['Sanc'] = 0.75
w.wgt['JRDA']['Reg'] = 0.5
w.wgt['JRDA']['Other'] = 0.25
w.decay = [1.0, 0.9, 0.5, 0.3, 0.1]

weights.append(w)


# set the freeze date of the applications
# TODO: FUTURE: currently just a single date for each applicant, make it able to be unique per applicant (probably as part of processing a file of applicants
# this is the date applications were initially assessed and downloaded, so everyone should be held against that date so I don't have to download more recent ones all the time
# freezeDate = datetime.date(2016,5,9)
freezeDate = datetime.date.today()

dir_path = '/Volumes/GoogleDrive/My Drive/Derby/Rollercon 2018/'
dir_name = 'Officials Game Histories'
# dir_name = 'test'
# dir_path = '/Volumes/GoogleDrive/My Drive/Derby/Rollercon 2018/Officials Game Histories/'
# dir_name = '2018 Versions'
o, rejects = shaft.load_files_from_dir(dir_path + dir_name, freezeDate)

for i in o:
    i.apply_weight_models(weights)

if __name__ == '__main__':
    print("Running")
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

    filename_base = dir_path + dir_name + '/_' + dir_name
    for w in weights:
        shaft.create_results(filename_base + '-' + w.name + '.xlsx', o, w)

    # write out a file of all the rejected files (and why)
    shaft.create_rejects(filename_base + '-rejects.xlsx', rejects)
