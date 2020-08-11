# Pulsar_survey_scrapper_post
This python script queries http://hosting.astro.cornell.edu/~deneva/tabscr/tabscr.php.
The usage of this file is 
python post_request_check_new_sources.py filename ra_dec_tol(deg) dm_tol

This script will accept both csv and .npz files. However they must be formatted in a specific way. The CSV file in this git repository is an example of the format
each line in the CSV file needs to be 

candidate_name,ra(HHMMSS),dec(DDMMSS),DM

where the candidate name is any name you assign to the location you are checking for.

for the npz file, the load format should be

my_new_sources = np.load(filename,allow_pickle=1)['data'].tolist()

where every element in the my_new_sources list is a dictionary of 
{candidate_name:[ra(HHMMSS),dec(HHMMSS),DM]}

again, an example of this is placed in this repository
