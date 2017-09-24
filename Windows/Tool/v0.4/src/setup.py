from distutils.core import setup
import py2exe, sys, os
sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, "dll_excludes": ['w9xpopen.exe', 'MSVCP90.dll', 'mswsock.dll', 'powrprof.dll', 'MPR.dll', 'MSVCR100.dll', 'mfc90.dll'], 'compressed': True,"includes":["bs4","mechanize","wx","wx.lib.pubsub.*", "wx.lib.pubsub.core.*", 
                           "wx.lib.pubsub.core.kwargs.*"],}},
    windows = [{'script': "main.py", "icon_resources": [(1, "./icons/googlescholar.ico"), (2,"./icons/scholar.ico"), (3,"./icons/gmail.ico")]}],
    zipfile = None
)
