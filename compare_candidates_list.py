import numpy as np
import sys
import os
from os import path
import matplotlib.pyplot as plt
import csv
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy import uncertainty as unc
import pyne2001
'''
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
    my_ra=data['new_source_ra']
    my_dec=data['new_source_dec']
    my_filter = (my_dec<72.8)
    my_dec = my_dec[my_filter]
    my_ra = my_ra[my_filter]
    #print({data['new_source_cluster_no'][0]:(average_ra,average_dec,average_dm)})
    my_dict.update({data['new_source_cluster_no'][0]:(average_ra,average_dec,average_dm)})
    print(my_dict)
'''
def header_localized(folder,confidence=90):
    files = os.listdir(folder)
    ra=[]
    dec=[]
    ra_unc = []
    dec_unc = []
    coord = []
    file = []
    dm=[]
    for my_file in files:
        if '.pkl' in my_file:
            results = np.load(path.join(folder,my_file),allow_pickle=1)['results'][confidence]
            dm.append(np.load(path.join(folder,my_file),allow_pickle=1)['dm'])
            ra.append(results[0])
            ra_unc.append(results[1])
            dec.append(results[2])
            dec_unc.append(results[3])
            file.append(my_file)
    coord = SkyCoord(ra,dec,unit=(u.deg,u.deg))            
    return coord,ra_unc,dec_unc,dm,file

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

def readSN(filename='SNCat.csv'):
    name=[]
    ra=[]
    dec=[]
    D = []
    blank_name=[]
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile,quotechar='"', delimiter=',')
        for row_num,row in enumerate(spamreader):
            if row_num>0:
                if not(row[4].strip()==''):
                    name.append(row[0])
                    ra.append(row[3].split(',')[0])
                    dec.append(row[4].split(',')[0])
                    if row[5]=='':
                        row[5]=99999
                    D.append(float(row[5]))
                else:
                    blank_name.append(row[0])
        coord = SkyCoord(ra,dec,unit=(u.hourangle, u.deg))
    return coord,name,D

def compare_sources(compare,compare_dms,compare_name,mine,ra_tol,dec_tol,my_dm,fn,dm_tol=1000*1e-3,dist_ne2001=True):
    for j,item in enumerate(mine):
        ra=item.ra.degree
        dec=item.dec.degree
        glon = item.galactic.l.degree
        glat = item.galactic.b.degree
        dm=my_dm[j]
        if dist_ne2001:
            #print(glon)
            #print(glat)
            #print(dm)
            dm,lowlim=pyne2001.get_dist(glon,glat,dm)
            
            #convert to Mpc
            dm=dm*1e-3
            print(dm)
        compare_ra = compare.ra.degree
        compare_dec = compare.dec.degree
        if isinstance(ra_tol,list):
            ura = ra_tol[j]
            udec = dec_tol[j]
        else:
            ura = ra_tol
            udec = dec_tol
        ra_bool = ((ra-ura)<compare_ra)&((ra+ura)>compare_ra)
        dec_bool = ((dec-udec)<compare_dec)&((dec+udec)>compare_dec)
        
        if compare_dms==-1|lowlim:
            i=(ra_bool*dec_bool==True)
            if np.sum(ra_bool&dec_bool):
                print(str(fn[j])+' might be (ra,dec match) '+str(np.array(compare_name)[i]))
        else:
            dm_bool = ((dm-dm_tol)<np.array(compare_dms))&((dm+dm_tol)>np.array(compare_dms))
            i=(ra_bool*dm_bool*dec_bool==True)
            if np.sum(ra_bool&dec_bool&dm_bool):
                print(str(fn[j])+' might be (ra,dec,dm match) '+str(np.array(compare_name)[i]))

#coord,dm,name=read_fast_sources()
my_coord,ra_unc,dec_unc,my_dm,file =header_localized('cluster_localize')
coord,name,dist=readSN()
compare_sources(coord,dist,name,my_coord,ra_unc,dec_unc,my_dm,fn=file)


'''
plt.scatter(ra,dec,c=dm)
plt.colorbar()
plt.show()
'''

