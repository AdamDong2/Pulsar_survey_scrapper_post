import requests
import lxml.html as lh
import pandas as pd
import csv
import numpy as np
import sys
import multiprocessing as mp
from search_param_wrapper import search_params_postprocessing

class my_confirmed_sources:
    def __init__(self,source_no='',ra='',dec='',dm='',survey_search_results_atnf=[],survey_search_results_natnf=[]):
        self.source_no=source_no
        self.ra=ra
        self.dec=dec
        self.dm=dm
        self.survey_search_results_atnf=survey_search_results_atnf
        self.survey_search_results_natnf=survey_search_results_natnf

def sort_ATNF(my_request):
    request_return=my_request.content
    my_text=my_request.text
    start_atnf_string = '\n------------------------------------------------------------------------------\n'
    end_atnf_string = '\n------------------------------------------------------------------------------</pre>'
    index_atnf_table_start = my_text.find(start_atnf_string)+len(start_atnf_string)
    index_atnf_table_end = my_text.find(end_atnf_string)
    atnf_string=str(request_return[index_atnf_table_start:index_atnf_table_end])
    atnf_string = " ".join(atnf_string.split())
    atnf_string.replace("'",'')
    reader=csv.reader(atnf_string.split('\\n'),delimiter=' ')
    atnf_results=[]
    for row in reader:
        if len(row)>1:
            for i,my_element in enumerate(row):
                if i==2:
                    pulsar_name=my_element
                elif i==5:
                    period = my_element
                elif i==6:
                    dm = my_element.replace("'","")
                    #print(dm)
            atnf_results.append([pulsar_name,period,dm])
    return atnf_results

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
                print('Pulsar Name: '+element)
                pulsar_name=element
                counter=counter+1
            elif counter==1:
                print('Period: '+element)
                period=element
                counter=counter+1
            elif counter==2:
                print('DM: '+element)
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
    atnf_results=sort_ATNF(my_request)
    non_atnf_results =sort_other(my_request)
    source_results = my_confirmed_sources(source_no=source,ra=ra,dec=dec,dm=dm,survey_search_results_atnf=atnf_results,survey_search_results_natnf=non_atnf_results)
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
        Lets_go=True
    else:
        print('please ensure the extension is correct, this python script only takes .csv and .npz files')
    if lets_go:
        pool=mp.Pool(100)
        my_associated_sources=pool.starmap(mp_query, [(source,my_new_sources,ra_dec_tol,dm_tol) for source in my_new_sources])
        np.save('my_associated_sources',my_associated_sources)
        pool.close()
        print_new_sources(my_associated_sources)

def print_new_sources(my_associated_sources):
    for item in my_associated_sources:
        if (len(item.survey_search_results_atnf)==0) & (len(item.survey_search_results_natnf)==0):
            #print(item.survey_search_results_natnf)
            print('NEW source found!!')
            print('*********************')
            print('ra:'+str(item.ra)+' dec:'+str(item.dec)+' dm:'+str(item.dm)+' cluster number:'+str(item.source_no))
            print('*********************')
        else:
            print('ra:'+str(item.ra)+' dec:'+str(item.dec)+' dm:'+str(item.dm)+' cluster number:'+str(item.source_no))
            print('ATNF results')
            print(item.survey_search_results_atnf)
            print('Other results')
            print(item.survey_search_results_natnf)

if __name__=="__main__":
    filename=sys.argv[1]
    ra_dec_tol = sys.argv[2]
    dm_tol = sys.argv[3]
    load_new_sources(filename,ra_dec_tol,dm_tol)


