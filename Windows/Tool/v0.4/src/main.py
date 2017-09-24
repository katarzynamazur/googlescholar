#!/bin/env/python

import wx

from GoogleScholarScraperPanel import ScraperPanel
from GoogleScholarSpammerPanel import SpammerPanel
from GoogleScholarVerifierPanel import VerifierPanel

class SuperAwesomeTool(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
        wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
        )

        #il = wx.ImageList(35, 35)
        #scholarTab = il.Add(wx.Bitmap('./icons/scholar.png', wx.BITMAP_TYPE_PNG))
        #spammerTab = il.Add(wx.Bitmap('./icons/mail.png', wx.BITMAP_TYPE_PNG))
        #veryfierTab = il.Add(wx.Bitmap('./icons/check.png', wx.BITMAP_TYPE_PNG))
        #self.AssignImageList(il)

        tabOne = ScraperPanel(self)
        self.AddPage(tabOne, "Google Scholar Scraper")
        #self.SetPageImage(0, scholarTab)

        tabTwo = VerifierPanel(self)
        self.AddPage(tabTwo, "Google Scholar Verifier")
        #self.SetPageImage(1, veryfierTab)

        tabThree = SpammerPanel(self)
        self.AddPage(tabThree, "Google Scholar Spammer")
        #self.SetPageImage(2, spammerTab)


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Super Awesome Google Scholar Scraper / Spammer Tool",
                          size=(600, 500)
        )
        panel = wx.Panel(self)

        notebook = SuperAwesomeTool(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        ico = wx.Icon('./icons/googlescholar.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Centre()
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
