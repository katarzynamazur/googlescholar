# !/bin/env/python

import wx
import os

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Spammer.CountryCodes import CountryCodes


class EmailByCountryCodeSelectionDialog(wx.Dialog):
    def __init__(self, countryCodesList):
        wx.Dialog.__init__(self, None, title="Select E-mail Addresses by Country Code")

        countryCodeLabel = wx.StaticText(self, label="Country Code")
        selectLabel = wx.StaticText(self, label="Select")

        self.countryCodesComboBox = wx.ComboBox(self, 500, '...', (50, 150), (320, -1), countryCodesList,
                                                wx.CB_DROPDOWN)
        self.countryCodesComboBox.SetSelection(0)

        countryCodesButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('cc.png'), wx.BITMAP_TYPE_ANY),
                                             (0, 0), (20, 20))
        countryCodesButton.SetToolTip(wx.ToolTip("Check Country Codes"))
        countryCodesButton.Bind(wx.EVT_LEFT_DOWN, self.OnCountryCodesButtonClicked)

        selectionList = ['All', 'All used', 'All unused']
        self.selectionComboBox = wx.ComboBox(self, 500, '...', (50, 150), (320, -1), selectionList,
                                             wx.CB_DROPDOWN)
        self.selectionComboBox.SetSelection(0)

        okButton = wx.Button(self, label="OK")
        self.Bind(wx.EVT_BUTTON, self.onClose, okButton)

        bagSizer = wx.GridBagSizer(5, 5)
        bagSizer.Add(countryCodeLabel, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.countryCodesComboBox, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(selectLabel, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.selectionComboBox, pos=(1, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(okButton, 1, wx.ALL | wx.RIGHT, 5)
        sizer.Add(countryCodesButton, 1, wx.ALL | wx.RIGHT, 5)
        bagSizer.Add(sizer, pos=(2, 1), flag=wx.RIGHT, border=5)

        self.SetSizer(bagSizer)
        bagSizer.Fit(self)


    def onClose(self, event):
        self.Close()

    def OnCountryCodesButtonClicked(self, event):
        dia = CountryCodes(self, -1, 'Country Codes and Countries')
        dia.ShowModal()
        dia.Destroy()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path