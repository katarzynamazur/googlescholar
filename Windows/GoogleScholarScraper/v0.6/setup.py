from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True,"includes":["bs4","mechanize"]}},
    console = [{'script': "google_scholar_scraper.py", "icon_resources": [(1, "googlescholar.ico")]}],
    zipfile = None
)
