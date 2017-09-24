#!/bin/env/python

import wx
from GoogleScholarScraperPanel import ScraperPanel
from GoogleScholarSpammerPanel import SpammerPanel
from GoogleScholarDatabase import GoogleScholarDatabase

class SuperAwesomeTool(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        il = wx.ImageList(16,16)
        scholarTab = il.Add(wx.Bitmap('./icons/scholar.ico', wx.BITMAP_TYPE_ICO))
        spammerTab = il.Add(wx.Bitmap('./icons/gmail.ico', wx.BITMAP_TYPE_ICO))
        self.AssignImageList(il)

        tabOne = ScraperPanel(self)
        self.AddPage(tabOne, "Google Scholar Scraper")
        self.SetPageImage(0, scholarTab)

        tabTwo = SpammerPanel(self)
        self.AddPage(tabTwo, "Google Scholar Spammer")
        self.SetPageImage(1, spammerTab)
        
    #     self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
    #     self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
    #
    # def OnPageChanged(self, event):
    #     old = event.GetOldSelection()
    #     new = event.GetSelection()
    #     sel = self.GetSelection()
    #     print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
    #     event.Skip()
    #
    # def OnPageChanging(self, event):
    #     old = event.GetOldSelection()
    #     new = event.GetSelection()
    #     sel = self.GetSelection()
    #     print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
    #     event.Skip()


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 
                          "Super Awesome Google Scholar Scraper / Spammer Tool",
                          size=(500,500)
                          )
        panel = wx.Panel(self)
        
        notebook = SuperAwesomeTool(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
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
