#!/bin/env/python

from wx.lib.pubsub import pub
import wx
import os

from ScraperBot import ScraperBot


class ScraperPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.keyword = ""
        self.citations_start = 0
        self.citations_stop = 0
        self.pages = 0

        self.InitGUI()
        self.InitListeners()

    def InitGUI(self):
        max = 10000000

        bagSizer = wx.GridBagSizer(15, 10)

        citationsLabel = wx.StaticText(self, label="Citations:")
        keywordLabel = wx.StaticText(self, label="Keyword:")
        pagesLabel = wx.StaticText(self, label="Pages:")
        infoLabel = wx.StaticText(self, label="Information")

        self.citations_start_spin = wx.SpinCtrl(self, size=(230, -1), value="0")
        self.citations_start_spin.SetRange(0, max)
        self.citations_start_spin.SetValue(0)
        self.citations_start_spin.Bind(wx.EVT_SPINCTRL, self.OnCitationsStartSpin)

        self.citations_stop_spin = wx.SpinCtrl(self, size=(230, -1), value="0")
        self.citations_stop_spin.SetRange(0, max)
        self.citations_stop_spin.SetValue(0)
        self.citations_stop_spin.Bind(wx.EVT_SPINCTRL, self.OnCitationsStopSpin)

        self.pages_spin = wx.SpinCtrl(self, size=(490, -1), value="0")
        self.pages_spin.SetRange(0, max)
        self.pages_spin.SetValue(0)
        self.pages_spin.Bind(wx.EVT_SPINCTRL, self.OnPagesSpin)

        self.keywordText = wx.TextCtrl(self, size=(490, -1))
        self.infoText = wx.TextCtrl(self, size=(300, 280), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.scraperButton = wx.Button(self, label="Scrap Emails")
        self.Bind(wx.EVT_BUTTON, self.OnScraperButtonClicked, self.scraperButton)

        clearAllButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('clear.png'), wx.BITMAP_TYPE_ANY),
                                         (0, 0), (20, 20))
        clearAllButton.SetToolTip(wx.ToolTip("Clear all"))
        clearAllButton.Bind(wx.EVT_LEFT_DOWN, self.OnClearAllButtonClicked)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.scraperButton, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(clearAllButton, 0, wx.ALL | wx.RIGHT, 5)

        bagSizer.Add(citationsLabel, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.citations_start_spin, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(wx.StaticText(self, label="-"), pos=(0, 2), border=5)
        bagSizer.Add(self.citations_stop_spin, pos=(0, 3), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(keywordLabel, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.keywordText, pos=(1, 1), span=(1, 3), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(pagesLabel, pos=(2, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.pages_spin, pos=(2, 1), span=(1, 3), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(infoLabel, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(self.infoText, pos=(4, 0), span=(1, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.Add(sizer, pos=(5, 0), span=(1, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.AddGrowableRow(4)
        bagSizer.AddGrowableCol(0)

        self.SetSizer(bagSizer)

    def InitListeners(self):

        pub.Publisher.subscribe(self.updateScrapingInfo, 'updateScrapingInfo')
        pub.Publisher.subscribe(self.enableScrapButton, 'enableScrapButton')

    def OnCitationsStartSpin(self, event):
        self.citations_start = self.citations_start_spin.GetValue()

    def OnCitationsStopSpin(self, event):
        self.citations_stop = self.citations_stop_spin.GetValue()

    def OnPagesSpin(self, event):
        self.pages = self.pages_spin.GetValue()

    def OnScraperButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', False)
        self.infoText.SetValue("")
        self.keyword = self.keywordText.GetValue().strip().replace(' ', '_').title()

        if self.citations_stop == 0:
            msg = "Please give the maximum citation number."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)
        elif self.keyword == "":
            msg = "Please give the keyword."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)
        elif self.pages == 0:
            msg = "Please give the number of pages to dig out."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)
        else:
            s = ScraperBot(self.citations_start, self.citations_stop, self.keyword, self.pages)
            if not s.checkIfFileExists():
                s.start()
            else:
                msg = "I've already found researchers with given criteria, so" \
                      " emails file is already created (please check the './Data/dbs' directory)."
                wx.MessageBox(msg, 'Information', wx.OK | wx.ICON_INFORMATION)
                wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)

    def OnClearAllButtonClicked(self, event):
        if self.scraperButton.IsEnabled():
            self.citations_start = 0
            self.citations_stop = 0
            self.keyword = ""
            self.citations_start_spin.SetValue(0)
            self.citations_stop_spin.SetValue(0)
            self.pages_spin.SetValue(0)
            self.keywordText.SetValue("")
            self.infoText.SetValue("")

    def enableScrapButton(self, val):
        if val.data:
            self.scraperButton.Enable()
        else:
            self.scraperButton.Disable()

    def updateScrapingInfo(self, text):
        self.infoText.AppendText(str(text.data))

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Scraper")
        panel = ScraperPanel(self)
        ico = wx.Icon(self.createIconPath('scholar.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.SetSize(wx.Size(585, 545))
        self.SetMinSize(wx.Size(585, 545))
        self.Centre()
        self.Show()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
