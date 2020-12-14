import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from astropy.coordinates import SkyCoord

folders = os.listdir(sys.argv[1])
ra=[]
dec=[]
dm=[]
for folder in folders:
    path = os.path.join(sys.argv[1],folder,'data.npz')
    d = np.load(path)
    ra.append(np.mean(d['new_source_ra']))
    dec.append(np.mean(d['new_source_dec']))
    dm.append(np.mean(d['new_source_dm']))
ra_atnf=[]
dec_atnf=[]
with open('atnf.csv') as csvfile:
    import csv
    r = csv.reader(csvfile,delimiter=',')
    for row in r:
        ra_atnf.append(float(row[1]))
        dec_atnf.append(float(row[2]))

coords_cluster = SkyCoord(ra,dec,unit='deg')
coords_atnf = SkyCoord(ra_atnf,dec_atnf,unit='deg')
gl =np.linspace(0,360,1000)
gb = np.zeros(len(gl))
galactic = SkyCoord(gl,gb,frame='galactic',unit='deg')
galactic_ra=galactic.icrs.ra
galactic_dec = galactic.icrs.dec
i = np.squeeze(np.argwhere(np.array(galactic_ra)+1>360))
print(i)
galactic_ra_1 = galactic_ra[0:i]
galactic_dec_1 = galactic_dec[0:i]
galactic_ra_2 = galactic_ra[i+1:-1]
galactic_dec_2 = galactic_dec[i+1:-1]

galactic_ra = np.append(galactic_ra_2,galactic_ra_1)
galactic_dec = np.append(galactic_dec_2,galactic_dec_1)
plt.plot(ra_atnf,dec_atnf,'.',ms=2,label='ATNF')
plt.plot(ra,dec,'.',ms=4,alpha=0.7,label='Clustering Candidates')
plt.plot(galactic_ra,galactic_dec,'k',label='Galactic Plane')
plt.legend()
plt.xlabel('RA (deg)')
plt.ylabel('Dec (deg)')
plt.title('Distribution of clustering candidates')

plt.figure()
plt.plot(coords_atnf.galactic.l,coords_atnf.galactic.b,'.',ms='2',label='ATNF')
plt.plot(coords_cluster.galactic.l,coords_cluster.galactic.b,'.',alpha=0.7,ms='4',label='Clustering Candidates')
plt.legend()
plt.xlabel('Galactic Longitude(deg)')
plt.ylabel('Galactic Lattitude(deg)')
plt.title('Distribution of clustering candidates')


plt.show()
