# !/bin/env/python

import wx
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class EmailByKeywordSelectionDialog(wx.Dialog):
    def __init__(self, keywordsList):
        wx.Dialog.__init__(self, None, title="Select E-mail Addresses by Keyword")

        keywordLabel = wx.StaticText(self, label="Keyword")
        selectLabel = wx.StaticText(self, label="Select")

        self.keywordComboBox = wx.ComboBox(self, 500, '...', (50, 150), (320, -1), keywordsList,
                                           wx.CB_DROPDOWN)
        self.keywordComboBox.SetSelection(0)

        selectionList = ['All', 'All used', 'All unused']
        self.selectionComboBox = wx.ComboBox(self, 500, '...', (50, 150), (320, -1), selectionList,
                                             wx.CB_DROPDOWN)
        self.selectionComboBox.SetSelection(0)

        okButton = wx.Button(self, label="OK")
        self.Bind(wx.EVT_BUTTON, self.onClose, okButton)

        bagSizer = wx.GridBagSizer(5, 5)
        bagSizer.Add(keywordLabel, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.keywordComboBox, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(selectLabel, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.selectionComboBox, pos=(1, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(okButton, 1, wx.ALL | wx.RIGHT, 5)
        bagSizer.Add(sizer, pos=(2, 1), flag=wx.RIGHT, border=5)

        self.SetSizer(bagSizer)
        bagSizer.Fit(self)


    def onClose(self, event):
        self.Close()