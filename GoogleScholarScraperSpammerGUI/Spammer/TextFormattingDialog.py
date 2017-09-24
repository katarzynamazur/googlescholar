#!/bin/env/python
import wx
import os
from wx.lib.pubsub import pub


class EmailFormattingDialog(wx.Dialog):
    def __init__(self, text):
        wx.Dialog.__init__(self, None, title="E-mail Formatting Options")

        boldTextButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('bold.png'), wx.BITMAP_TYPE_ANY),
                                         (0, 0), (20, 20))
        boldTextButton.SetToolTip(wx.ToolTip("Bold"))
        boldTextButton.Bind(wx.EVT_LEFT_DOWN, self.OnBoldTextButtonClicked)

        italicTextButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('italic.png'), wx.BITMAP_TYPE_ANY),
                                           (0, 0), (20, 20))
        italicTextButton.SetToolTip(wx.ToolTip("Italic"))
        italicTextButton.Bind(wx.EVT_LEFT_DOWN, self.OnItalicTextButtonClicked)

        underlineTextButton = wx.StaticBitmap(self, -1,
                                              wx.Bitmap(self.createIconPath('underline.png'), wx.BITMAP_TYPE_ANY),
                                              (0, 0), (20, 20))
        underlineTextButton.SetToolTip(wx.ToolTip("Underline"))
        underlineTextButton.Bind(wx.EVT_LEFT_DOWN, self.OnUnderlineTextButtonClicked)

        insertURLButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('url.png'), wx.BITMAP_TYPE_ANY),
                                          (0, 0), (20, 20))
        insertURLButton.SetToolTip(wx.ToolTip("Insert URL"))
        insertURLButton.Bind(wx.EVT_LEFT_DOWN, self.OnInsertURLButtonClicked)

        bagSizer = wx.GridBagSizer(5, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(boldTextButton, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(italicTextButton, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(underlineTextButton, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(insertURLButton, 0, wx.ALL | wx.LEFT, 5)
        bagSizer.Add(sizer, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        self.SetSizer(bagSizer)
        bagSizer.Fit(self)

    def OnBoldTextButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.OnBoldText', None)

    def OnItalicTextButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.OnItalicText', None)

    def OnUnderlineTextButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.OnUnderlineText', None)

    def OnInsertURLButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.OnURLText', None)

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path


    def onClose(self, event):
        self.Close()