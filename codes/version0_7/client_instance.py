'''
Created on 24 Jul 2014

@author: ehsan
'''
import pyalveo

API_KEY = 'SMysEekachrdyGfiheGs'
API_URL = 'https://app.alveo.edu.au/'
CACHE_DIR = 'wrassp_cache'

client = pyalveo.Client(api_key=API_KEY, api_url=API_URL, 
                         use_cache=True, update_cache=True)