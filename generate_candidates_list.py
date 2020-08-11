import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import csv
from astropy import units as u
from astropy.coordinates import SkyCoord
root=sys.argv[1]

folders = os.listdir(root)
ra=np.array([])
dec=np.array([])
dm=np.array([])
my_dict={}
for folder in folders:
    path = os.path.join(root,folder)
    data_path = os.path.join(path,'data.npz')
    data = np.load(data_path,allow_pickle=1)
    ra=np.concatenate((ra,data['new_source_ra']))
    dec=np.concatenate((dec,data['new_source_dec']))
    dm=np.concatenate((dm,data['new_source_dm']))
    average_ra = np.mean(data['new_source_ra'])
    average_dec = np.mean(data['new_source_dec'])
    average_dm = np.mean(data['new_source_dm'])
    print({data['new_source_cluster_no'][0]:(average_ra,average_dec,average_dm)})
    my_dict.update({data['new_source_cluster_no'][0]:(average_ra,average_dec,average_dm)})
def read_fast_sources(filename='fast.csv'):
    name=[]
    ra=[]
    dec=[]
    dm=[]
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row_num,row in enumerate(spamreader):
            if row_num>0:
                name.append(row[0])
                ra.append(row[1])
                dec.append(row[2])
                dm.append(float(row[3]))
        coord = SkyCoord(ra,dec,unit=(u.hourangle, u.deg))
    return coord,dm,name
def compare_sources(fast,fast_dms,fast_name,mine,ra_dec_tol=5,dm_tol=5):
    for item in mine:
        ra=mine[item][0]
        dec=mine[item][1]
        dm=mine[item][2]
        for i,fast_coord in enumerate(fast):
            fast_ra = fast_coord.ra.degree
            fast_dec = fast_coord.dec.degree
            fast_dm = fast_dms[i]
            ra_bool = (ra<(fast_ra+ra_dec_tol))&(ra>(fast_ra-ra_dec_tol))
            dec_bool = (dec<(fast_dec+ra_dec_tol))&(dec>(fast_dec-ra_dec_tol))
            dm_bool = (dm<(fast_dm+dm_tol))&(dm>(fast_dm-dm_tol))
            if ra_bool&dec_bool&dm_bool:
                print(str(item)+' probably '+fast_name[i])

coord,dm,name=read_fast_sources()
compare_sources(coord,dm,name,my_dict)


'''
plt.scatter(ra,dec,c=dm)
plt.colorbar()
plt.show()
'''

