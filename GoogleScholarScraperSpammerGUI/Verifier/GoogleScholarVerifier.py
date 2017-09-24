# !/bin/env/python

import wx
import os
from wx.lib.pubsub import pub

from VerifierBot import VerifierBot


EMAIL_COMBINATIONS = 11


class VerifierPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.email_start_number = 0

        self.InitGUI()
        self.InitListeners()

    def InitGUI(self):

        self.count = 0
        max = 10000000

        dbFilenameLabel = wx.StaticText(self, label="Emails Database File")
        emailStartNumberLabel = wx.StaticText(self, label="Email Start Number")
        self.infoLabel = wx.StaticText(self, label="Information")

        bagSizer = wx.GridBagSizer(15, 10)

        self.dbFilename = wx.TextCtrl(self, size=(340, -1), style=wx.TE_READONLY)

        self.chooseFileButton = wx.Button(self, label="Browse")
        self.Bind(wx.EVT_BUTTON, self.OnChooseFileButtonClicked, self.chooseFileButton)
        self.verifyButton = wx.Button(self, label="Verify")
        self.Bind(wx.EVT_BUTTON, self.OnVerifyButtonClicked, self.verifyButton)

        self.emailStartNumberSpin = wx.SpinCtrl(self, size=(340, -1), value="0")
        self.emailStartNumberSpin.SetRange(0, max)
        self.emailStartNumberSpin.SetValue(0)
        self.emailStartNumberSpin.Bind(wx.EVT_SPINCTRL, self.OnEmailStartNumberSpin)

        self.progressBar = wx.Gauge(self, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)

        self.infoText = wx.TextCtrl(self, size=(300, 270), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        clearAllButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('clear.png'), wx.BITMAP_TYPE_ANY),
                                         (0, 0), (20, 20))
        clearAllButton.SetToolTip(wx.ToolTip("Clear all"))
        clearAllButton.Bind(wx.EVT_LEFT_DOWN, self.OnClearAllButtonClicked)

        bagSizer.Add(dbFilenameLabel, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.dbFilename, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.chooseFileButton, pos=(0, 2), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(emailStartNumberLabel, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.emailStartNumberSpin, pos=(1, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.verifyButton, pos=(1, 2), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)

        bagSizer.Add(self.infoLabel, pos=(2, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        bagSizer.Add(self.infoText, pos=(3, 0), span=(1, 3), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)
        bagSizer.Add(self.progressBar, pos=(4, 0), span=(1, 3), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(clearAllButton, 0, wx.ALL | wx.RIGHT, 5)

        bagSizer.Add(sizer, pos=(5, 0), span=(1, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=5)

        bagSizer.AddGrowableRow(3)
        bagSizer.AddGrowableCol(0)

        self.SetSizer(bagSizer)

    def InitListeners(self):

        pub.Publisher.subscribe(self.updateVerifyingInfo, 'updateVerifyingInfo')
        pub.Publisher.subscribe(self.updateVerifyingProgress, 'updateVerifyingProgress')
        pub.Publisher.subscribe(self.enableGUIElements, 'enableGUIElements')
        pub.Publisher.subscribe(self.updateInfoLabel, 'updateInfoLabel')


    def OnClearAllButtonClicked(self, event):
        if self.verifyButton.IsEnabled():
            self.count = 0
            self.email_start_number = 0
            self.dbFilename.SetValue("")
            self.infoText.SetValue("")
            self.emailStartNumberSpin.SetValue(0)
            self.infoLabel.SetLabel("Information")
            self.progressBar.SetValue(0)

    def OnChooseFileButtonClicked(self, event):

        def checkHowManyEmailsWeHave(filename, EMAIL_COMBINATIONS):
            with open(filename) as f:
                all_lines = [line.rstrip() for line in f]
            return (len(all_lines) / EMAIL_COMBINATIONS)

        wildcard = "Txt file (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
        dialog.SetDirectory(self.createDBDirPath())
        if dialog.ShowModal() == wx.ID_OK:
            self.dbFilename.SetValue(dialog.GetPath())
            emails_count = checkHowManyEmailsWeHave(dialog.GetPath(), EMAIL_COMBINATIONS)
            info = "Information (e-mail being processed: 0/%d)" % (emails_count)
            self.infoLabel.SetLabel(info)
        dialog.Destroy()

    def OnVerifyButtonClicked(self, event):
        wx.CallAfter(pub.Publisher.sendMessage, 'enableGUIElements', False)
        self.infoText.SetValue("")

        if self.dbFilename.GetValue().strip() == "":
            msg = "Give the emails database file!"
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableGUIElements', True)
        else:
            vb = VerifierBot(self.dbFilename.GetValue().strip(), self.email_start_number)
            emails_count = vb.checkHowManyEmailsWeHave()

            if emails_count <= self.email_start_number:
                msg = "You don't have %s emails in your file!" % (self.email_start_number + 1)
                wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
                wx.CallAfter(pub.Publisher.sendMessage, 'enableGUIElements', True)
            else:
                self.progressBar.SetRange(emails_count - self.email_start_number)
                vb.start()

    def OnEmailStartNumberSpin(self, event):
        self.email_start_number = self.emailStartNumberSpin.GetValue()

    def enableGUIElements(self, val):
        if val.data:
            self.verifyButton.Enable()
            self.chooseFileButton.Enable()
            self.emailStartNumberSpin.Enable()

        else:
            self.verifyButton.Disable()
            self.chooseFileButton.Disable()
            self.emailStartNumberSpin.Disable()

    def updateVerifyingInfo(self, text):
        self.infoText.AppendText(str(text.data))

    def updateVerifyingProgress(self, msg=None):
        self.count += 1
        if self.count > self.progressBar.GetRange() - 1:
            self.progressBar.SetValue(self.count)
            msg = "All Emails Verified!"
            wx.MessageBox(msg, 'Done', wx.OK | wx.ICON_INFORMATION)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableGUIElements', True)
        self.progressBar.SetValue(self.count)
        self.emailStartNumberSpin.SetValue(self.emailStartNumberSpin.GetValue() + 1)

    def updateInfoLabel(self, text):
        self.infoLabel.SetLabel(str(text.data))


    def createDBDirPath(self):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'dbs')
        return path

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Email Verifier")
        panel = VerifierPanel(self)
        ico = wx.Icon(self.createIconPath('check.png'), wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)
        self.SetSize(wx.Size(580, 550))
        self.SetMinSize(wx.Size(580, 550))
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
