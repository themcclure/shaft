import shaft
import datetime
from itertools import ifilter, ifilterfalse
from operator import attrgetter, methodcaller


# sample weightings
weights = shaft.create_weights()
weights[2].secondary_weight = 0.9

# set the freeze date of the applications
# TODO: currently just a single date for each applicant, make it able to be unique per applicant (probably as part of processing a file of applicants
#freezeDate = datetime.date(2015,6,1)
freezeDate = datetime.date.today()

#mh = shaft.load_file('sample/Mike Hammer - Game History - new with future.xlsx')
#mh.apply_weight_models(w)

#o = shaft.load_files_from_dir('sample', freezeDate)
o = shaft.load_files_from_dir('champs', freezeDate)
for i in o:
    i.apply_weight_models(weights)

if __name__ == '__main__':
    print "Running"
    for i in o:
        print i
        #print "strict:"
        #print i.weighting['wstrict']
        #print "std/vanilla:"
        #print i.weighting['std']
        #print "full (all the bells and whistles):"
        #print i.weighting['full']

    print "ref roles:"
    for r in shaft.ref_roles:
        print r
        print shaft.sort_by_role(o, r, 'full')

    print "NSO roles:"
    for r in shaft.nso_roles:
        print r
        print shaft.sort_by_role(o, r, 'full')

    filename_base = 'test'
    for w in weights:
        shaft.create_results(filename_base + '-' + w.name + '.xlsx', o, w.name)