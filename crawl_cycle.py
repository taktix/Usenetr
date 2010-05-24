#!/usr/bin/env python

# =============================================================
# Script for parsing new posts from all groups in the database
# this script cycles endlessly with a small delay in between cycles
# =============================================================


if __name__ == '__main__':
    import sys
    import os

    #python magic to add the current directory to the pythonpath
    sys.path.append(os.getcwd())

    # ==========================================================
    # Setup django environment 
    # ==========================================================
    if not os.environ.has_key('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    # ==========================================================
    # Done setting up django environment

import time
from settings import *

from raw.models import Group

INTERVAL = 120.0 #2 minutes
if __name__ == '__main__':
    
    while(True):
        start = time.time()
        for group in Group.objects.all():
            group.parse_new()
            
        end = time.time()
        duration = end - start
        
        if duration < INTERVAL:
            print 'too soon, sleeping: %s secs' % INTERVAL-duration
            time.sleep(INTERVAL-duration)

