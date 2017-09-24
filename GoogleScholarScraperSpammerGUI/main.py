#!/bin/env/python

import wx
import os

from Scraper.GoogleScholarScraper import ScraperPanel
from Spammer.GoogleScholarSpammer import SpammerPanel
from Verifier.GoogleScholarVerifier import VerifierPanel


class SuperAwesomeTool(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
        wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
        )

        il = wx.ImageList(35, 35)
        scholarTab = il.Add(wx.Bitmap(self.createIconPath('scholar.png'), wx.BITMAP_TYPE_PNG))
        spammerTab = il.Add(wx.Bitmap(self.createIconPath('mail.png'), wx.BITMAP_TYPE_PNG))
        verifierTab = il.Add(wx.Bitmap(self.createIconPath('check.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        tabOne = ScraperPanel(self)
        self.AddPage(tabOne, "Google Scholar Scraper")
        self.SetPageImage(0, scholarTab)

        tabTwo = VerifierPanel(self)
        self.AddPage(tabTwo, "Google Scholar Verifier")
        self.SetPageImage(1, verifierTab)

        tabThree = SpammerPanel(self)
        self.AddPage(tabThree, "Google Scholar Spammer")
        self.SetPageImage(2, spammerTab)

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], tmp[1], 'Data', 'icons', resourceName)
        return path


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Super Awesome Google Scholar Scraper / Spammer Tool",
                          size=(650, 650)
        )
        panel = wx.Panel(self, -1, style=wx.BORDER_RAISED)

        notebook = SuperAwesomeTool(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        ico = wx.Icon(self.createIconPath('googlescholar.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Centre()
        self.Show()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], tmp[1], 'Data', 'icons', resourceName)
        return path


    def OnCloseFrame(self, event):
        dialog = wx.MessageDialog(self, message="Are you sure you want to quit?", caption="Exit", style=wx.YES_NO,
                                  pos=wx.DefaultPosition)
        response = dialog.ShowModal()

        if (response == wx.ID_YES):
            self.Destroy()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
