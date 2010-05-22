#!/usr/bin/env python

# =============================================================
# Script for parsing new posts from all groups in the database
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


from settings import *

from raw.models import Group


if __name__ == '__main__':
    for group in Group.objects.all():
        group.parse_new()
