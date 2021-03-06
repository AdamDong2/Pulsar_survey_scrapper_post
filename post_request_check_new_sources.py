import requests
import lxml.html as lh
import pandas as pd
import csv
import numpy as np
import sys
import multiprocessing as mp
import shlex,subprocess
import re
import os
import shutil
class my_confirmed_sources:
    def __init__(self,source_no='',ra='',dec='',dm='',survey_search_results_atnf=[],survey_search_results_natnf=[],chime_candidates=[]):
        self.source_no=source_no
        self.ra=ra
        self.dec=dec
        self.dm=dm
        self.survey_search_results_atnf=survey_search_results_atnf
        self.survey_search_results_natnf=survey_search_results_natnf
        self.chime_candidates = chime_candidates
def convert_to_hoursminsec(ra,dec):
    hours_ra = ra/15
    minutes_ra = (hours_ra-int(hours_ra))*60
    seconds_ra = (minutes_ra-int(minutes_ra))*60
    minutes_dec = (dec-int(dec))*60
    seconds_dec = (minutes_dec-int(minutes_dec))*60
    return str(int(hours_ra))+':'+str(int(minutes_ra))+':'+str(float(seconds_ra)),str(int(dec))+':'+str(int(minutes_dec))+':'+str(float(seconds_dec))    
    
def convert_to_deg(HHMMSSra,DDMMSSdec):
        
    ra = np.array(HHMMSSra.split(':',3)).astype(np.float)
    
    dec = np.array(DDMMSSdec.split(':',3)).astype(np.float)
    rhh=ra[0]
    rmm=ra[1]
    ddd=dec[0]
    dmm=dec[1]
    if len(ra)==3:
        rss=ra[2]
    else:
        rss=0
    if len(dec)==3:
        dss=dec[2]
    else:
        dss=0
    ra_deg = (float(rhh)+float(rmm)/60+float(rss)/3600)*(360/24)
    dec_deg = float(ddd)+float(dmm)/60+float(dss)/3600
    return ra_deg,dec_deg

def query_psrcat(ra,dec,dm,ra_tol=5,dec_tol=5,dm_tol=10):
    """Summary or Description of the Function

    Parameters:
    ra (str): ra position (hh:mm:ss)
    dec(str): dec position (dd:mm:ss)
    dm (str): dm (m/cm^3)

    Returns:
    results(str): String containing the if the pulsar was found or not
    """
    #4 minutes per degree
    ra_deg,dec_deg = convert_to_deg(ra,dec)
    dm=float(dm)
    ra_deg_min=ra_deg-ra_tol
    ra_deg_max=ra_deg+ra_tol
    dec_deg_min = dec_deg-dec_tol
    dec_deg_max = dec_deg+dec_tol
    #find the min and max's
    ra_min,dec_min = convert_to_hoursminsec(ra_deg-ra_tol,dec_deg-dec_tol)
    ra_max,dec_max = convert_to_hoursminsec(ra_deg+ra_tol,dec_deg+dec_tol)
    dm_min = dm-dm_tol
    dm_max= dm+dm_tol
    #search psrcat
    dm_str = 'DM<'+str(dm_max)+ ' && ' +'DM>'+str(dm_min)
    ra_str = 'RAJD<'+str(ra_deg_max)+' && '+'RAJD>'+str(ra_deg_min)
    dec_str = 'DecJD<'+str(dec_deg_max)+' && '+'DecJD>'+str(dec_deg_min)

    command = './psrcat_tar/psrcat -db_file ./psrcat_tar/psrcat.db -c "name dm RAJ DECJ" -l '+'"'+dm_str+' && '+ra_str+' && '+dec_str+'"'
    args=shlex.split(command)
    psrcat_results = subprocess.Popen(args,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
    results,error = psrcat_results.communicate()
    results=results.decode('ascii')
    #hacky way to find the last string
    start = results.find("1")
    end = len(results)-len('------------------------------------------------------------------------------------------------------------------------------')-3
    results = results[start:end]
    return results 
def CheckChimeCandidates(ra,dec,dm,dm_tol=10,ra_tol=10,dec_tol=10,CandidateCSV='chime_galactic_sources.csv'):
    """Summary or Description of the Function

    Parameters:
    ra (str): ra position (hh:mm:ss)
    dec(str): dec position (dd:mm:ss)
    dm (str): dm (m/cm^3)
    CandidateCSV (str): filepath to CandidateCSV file

    Returns:
    results(str): String containing the if the pulsar was found or not
    """
    matched_sources={}
    ra,dec = convert_to_deg(ra,dec)
    dm=float(dm)
    with open (CandidateCSV,'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader:
            chime_ra = float(row[1])
            chime_dec = float(row[2])
            chime_dm =float(row[3])
            matched =(ra<(chime_ra+ra_tol)) & (ra>(chime_ra-ra_tol)) & (dec<(chime_dec+dec_tol)) & (dec>(chime_dec-dec_tol)) & (dm<(chime_dm+dm_tol)) & (dm>(chime_dm-dm_tol))
            if matched:
                matched_sources.update({float(row[0]):[chime_ra,chime_dec,chime_dm]})
    return matched_sources



def sort_other(my_request):
    request_return=my_request.content
    doc= lh.fromstring(request_return)
    table_elements=doc.xpath('//td')
    counter=0
    tables_start=False
    non_ATNF_results=[]
    for item in table_elements:
        element = item.text_content()
        if element == 'Pulsar name':
            tables_start=False
        elif element == 'Period (ms)':
            tables_start=True

        elif (tables_start)&(element!='DM (pc/cc)'):
            if counter==0:
                #print('Pulsar Name: '+element)
                pulsar_name=element
                counter=counter+1
            elif counter==1:
                #print('Period: '+element)
                period=element
                counter=counter+1
            elif counter==2:
                #print('DM: '+element)
                dm=element
                counter=0
                non_ATNF_results.append([pulsar_name,period,dm])
    return non_ATNF_results

def mp_query(source,my_new_sources,ra_dec_tol,dm_tol):
    ra=my_new_sources[source][0]
    dec=my_new_sources[source][1]
    dm=my_new_sources[source][2]
    my_request_params ={'RA' : ra, 'DEC': dec, 'POSTOL':ra_dec_tol,'DM':dm,'DMTOL':dm_tol}
    url = 'http://hosting.astro.cornell.edu/~deneva/tabscr/tabscr.php'
    my_request = requests.post(url,data=my_request_params)
    #atnf_results=sort_ATNF(my_request)
    atnf_results = query_psrcat(ra,dec,dm,dm_tol=float(dm_tol),ra_tol=float(ra_dec_tol),dec_tol=float(ra_dec_tol))
    non_atnf_results =sort_other(my_request)
    chime_candidates = CheckChimeCandidates(ra,dec,dm,dm_tol=float(dm_tol),ra_tol=float(ra_dec_tol),dec_tol=float(ra_dec_tol),CandidateCSV='chime_galactic_sources.csv')
    source_results = my_confirmed_sources(source_no=source,ra=ra,dec=dec,dm=dm,survey_search_results_atnf=atnf_results,survey_search_results_natnf=non_atnf_results,chime_candidates = chime_candidates)
    return source_results

def load_new_sources(filename,ra_dec_tol,dm_tol):
    '''This function will plot all the new confirmed sources'''
    lets_go=False
    if 'csv' in filename:
        with open(filename) as csv_file:
            my_new_sources={}
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                new_item = {row[0]:np.array([row[1],row[2],row[3]])}
                my_new_sources.update(new_item)
        lets_go=True
    elif 'npz' in filename:        
        print('loading new sources')
        my_new_sources = np.load(filename,allow_pickle=1)['data'].tolist()
        print(my_new_sources)
        lets_go=True
    else:
        print('please ensure the extension is correct, this python script only takes .csv and .npz files')
    if lets_go:
        pool=mp.Pool(100)
        my_associated_sources=pool.starmap(mp_query, [(source,my_new_sources,ra_dec_tol,dm_tol) for source in my_new_sources])
        np.save('my_associated_sources',my_associated_sources)
        pool.close()
        print_new_sources(my_associated_sources)
        
def print_new_sources(my_associated_sources):
    new_sources=[]
    for item in my_associated_sources:
        if (len(item.survey_search_results_atnf)==0) & (len(item.survey_search_results_natnf)==0) & (len(item.chime_candidates)==0):
            print('NEW source found!!')
            print('*********************')
            print('ra:'+str(item.ra)+' dec:'+str(item.dec)+' dm:'+str(item.dm)+' source number:'+str(item.source_no))
            print('*********************\n')
            new_sources.append({item.source_no:[item.ra,item.dec,item.dm]})
        else:        
            print('ra:'+str(item.ra)+' dec:'+str(item.dec)+' dm:'+str(item.dm)+' soruce number:'+str(item.source_no))
            print('ATNF results')
            print(item.survey_search_results_atnf)
            print('Other results')
            print(item.survey_search_results_natnf)
            print('Chime source')
            print(item.chime_candidates)
            print('\n')
    print('\n\n New sources')
    for item in new_sources:
        print(item)
    root='200215_2pts_repeaters/'
    root_folders = os.listdir(root)
    for item in new_sources:
        for folder in root_folders:
            if 'C'+str(list(item.keys())[0])+'_' in folder:
                shutil.copytree(root+folder,'200215_new_repeater/'+folder)



if __name__=="__main__":
    filename=sys.argv[1]
    ra_dec_tol = sys.argv[2]
    dm_tol = sys.argv[3]
    load_new_sources(filename,ra_dec_tol,dm_tol)


