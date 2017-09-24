# !/bin/env/python

import wx
import os
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class SMTPConfigPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        bagSizer = wx.GridBagSizer(5, 5)

        emailSenderLabel = wx.StaticText(self, label="Sender Email:")
        emailSenderPassLabel = wx.StaticText(self, label="Sender Pass:")
        emailSMTPServerLabel = wx.StaticText(self, label="SMTP Server:")
        emailSMTPPortLabel = wx.StaticText(self, label="SMTP Port:")

        emailSenderTxt = wx.TextCtrl(self, size=(300, -1))
        emailSenderPassTxt = wx.TextCtrl(self, size=(300, -1), style=wx.TE_PASSWORD)
        emailSMTPServerTxt = wx.TextCtrl(self, size=(300, -1))
        emailSMTPPortTxt = wx.TextCtrl(self, size=(300, -1))

        self.domainComboBox = wx.CheckBox(self, -1, 'Domain Account', (50, 255))
        self.domainComboBox.SetValue(False)

        bagSizer.Add(emailSenderLabel, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(emailSenderTxt, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.Add(emailSenderPassLabel, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(emailSenderPassTxt, pos=(1, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.Add(emailSMTPServerLabel, pos=(2, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(emailSMTPServerTxt, pos=(2, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.Add(emailSMTPPortLabel, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(emailSMTPPortTxt, pos=(3, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.Add(self.domainComboBox, pos=(4, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        closeButton = wx.Button(self, label="OK")
        self.Bind(wx.EVT_BUTTON, self.OnCloseClicked, closeButton)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(closeButton, 1, wx.ALL | wx.RIGHT, 5)

        bagSizer.Add(sizer, pos=(5, 1), flag=wx.RIGHT, border=5)

        self.SetSizer(bagSizer)
        bagSizer.Fit(self)

    def OnCloseClicked(self, event):
        self.GetParent().Close()


class SMTPConfigFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="SMTP Configuration Parameters")
        panel = SMTPConfigPanel(self)
        ico = wx.Icon(self.createIconPath('conf.png'), wx.BITMAP_TYPE_ANY)
        self.SetIcon(ico)
        self.Centre()
        self.SetSize(wx.Size(400, 250))
        self.SetMinSize(wx.Size(400, 250))
        self.SetMaxSize(wx.Size(400, 250))
        self.Show()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = SMTPConfigFrame()
    frame.Show()
    app.MainLoop()