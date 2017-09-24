# !/bin/env/python
import re
import wx
import wx.richtext
import os
from wx.lib.pubsub import pub

from DatabaseMgmt.GoogleScholarEmailBoxDatabase import GoogleScholarEmailBoxDatabase
from DatabaseMgmt.GoogleScholarResearchersDatabase import GoogleScholarDatabase
from Spammer.EmailAddressChooserDialog import EmailAddressChooserDialog
from Spammer.EmailPreviewGUI import EmailPreviewFrame
from Spammer.SMTPConfigGUI import SMTPConfigFrame
from Spammer.SpammerBot import SpammerBot
from Spammer.TextFormattingDialog import EmailFormattingDialog


class SpammerPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.InitGUI()
        self.InitListeners()

    def InitGUI(self):

        self.count = 0
        self.chosenResearchers = []
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        emailSubjectLabel = wx.StaticText(self, label="Email Subject:")
        emailContentLabel = wx.StaticText(self, label="Email Content:")

        self.emailSubject = wx.TextCtrl(self)
        self.emailContent = wx.richtext.RichTextCtrl(self, size=(-1, 300), style=wx.TE_MULTILINE | wx.PROCESS_ENTER)

        self.progressBar = wx.Gauge(self, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)

        configSMTPButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('conf.png'), wx.BITMAP_TYPE_ANY),
                                           (0, 0), (20, 20))
        configSMTPButton.SetToolTip(wx.ToolTip("SMTP Configuration Parameters"))
        configSMTPButton.Bind(wx.EVT_LEFT_DOWN, self.OnConfigureSMTPButtonClicked)

        formatTextButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('format.png'), wx.BITMAP_TYPE_ANY),
                                           (0, 0), (20, 20))
        formatTextButton.SetToolTip(wx.ToolTip("E-mail Text Formatting"))
        formatTextButton.Bind(wx.EVT_LEFT_DOWN, self.OnFormatTextButtonClicked)

        chooseEmailsButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('db.png'), wx.BITMAP_TYPE_ANY),
                                             (0, 0), (20, 20))
        chooseEmailsButton.SetToolTip(wx.ToolTip("Choose e-mail addresses"))
        chooseEmailsButton.Bind(wx.EVT_LEFT_DOWN, self.OnChooseEmailsButtonClicked)

        previewEmailsButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('prev.png'), wx.BITMAP_TYPE_ANY),
                                              (0, 0), (20, 20))
        previewEmailsButton.SetToolTip(wx.ToolTip("Preview e-mail"))
        previewEmailsButton.Bind(wx.EVT_LEFT_DOWN, self.OnPreviewButtonClicked)

        sendEmailsButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('letter.png'), wx.BITMAP_TYPE_ANY),
                                           (0, 0), (30, 30))
        sendEmailsButton.SetToolTip(wx.ToolTip("Send e-mail(s)"))
        sendEmailsButton.Bind(wx.EVT_LEFT_DOWN, self.OnSendButtonClicked)

        clearAllButton = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('clear.png'), wx.BITMAP_TYPE_ANY),
                                         (0, 0), (20, 20))
        clearAllButton.SetToolTip(wx.ToolTip("Clear all"))
        clearAllButton.Bind(wx.EVT_LEFT_DOWN, self.OnClearAllButtonClicked)

        loadEmailTemplateButton = wx.StaticBitmap(self, -1,
                                                  wx.Bitmap(self.createIconPath('notepad.png'), wx.BITMAP_TYPE_ANY),
                                                  (0, 0), (20, 20))
        loadEmailTemplateButton.SetToolTip(wx.ToolTip("Load E-mail Template"))
        loadEmailTemplateButton.Bind(wx.EVT_LEFT_DOWN, self.OnEmailTemplateButtonClicked)

        self.emailContent.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPressed)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailSubjectLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(35, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.emailSubject, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailContentLabel, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.emailContent, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.progressBar, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(configSMTPButton, 0, wx.ALL | wx.RIGHT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sendEmailsButton, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(chooseEmailsButton, 0, wx.ALL | wx.RIGHT, 5)
        sizer.Add(previewEmailsButton, 0, wx.ALL | wx.RIGHT, 5)
        sizer.Add(clearAllButton, 0, wx.ALL | wx.RIGHT, 5)
        sizer.Add(formatTextButton, 0, wx.ALL | wx.RIGHT, 5)
        sizer.Add(loadEmailTemplateButton, 0, wx.ALL | wx.RIGHT, 5)
        sizer.Add(configSMTPButton, 0, wx.ALL | wx.RIGHT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)

    def InitListeners(self):

        pub.Publisher.subscribe(self.updateProgress, 'SpammerPanel.updateProgress')
        pub.Publisher.subscribe(self.saveEmail, 'SpammerPanel.saveEmail')
        pub.Publisher.subscribe(self.OnBoldText, 'SpammerPanel.OnBoldText')
        pub.Publisher.subscribe(self.OnItalicText, 'SpammerPanel.OnItalicText')
        pub.Publisher.subscribe(self.OnUnderlineText, 'SpammerPanel.OnUnderlineText')
        pub.Publisher.subscribe(self.OnURLText, 'SpammerPanel.OnURLText')

    def OnEnterPressed(self, event):

        ip = self.emailContent.GetInsertionPoint()
        self.emailContent.SetInsertionPoint(ip - 1)
        self.emailContent.WriteText("<br>")
        self.emailContent.SetInsertionPoint(ip + 4)

    def OnBoldText(self, arg=None):

        selStart, selEnd = self.emailContent.GetSelection()

        if (selStart != -2 and selEnd != -2) or (selStart != -2 or selEnd != -2):
            if not self.emailContent.IsSelectionBold():
                self.emailContent.SetInsertionPoint(selStart)
                self.emailContent.WriteText("<b>")
                self.emailContent.SetInsertionPoint(selEnd + 3)
                self.emailContent.WriteText("</b>")
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd + 7))
                self.emailContent.ApplyBoldToSelection()
            else:
                selectedText = self.emailContent.GetStringSelection()
                modifiedText = selectedText.replace('<b>', '')
                modifiedText = modifiedText.replace('</b>', '')
                self.emailContent.Replace(selStart, selEnd, modifiedText)
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd - 7))
        else:
            self.emailContent.WriteText("<b></b>")
            self.emailContent.SetInsertionPointEnd()

    def OnItalicText(self, arg=None):

        selStart, selEnd = self.emailContent.GetSelection()

        if (selStart != -2 and selEnd != -2) or (selStart != -2 or selEnd != -2):
            if not self.emailContent.IsSelectionItalics():
                self.emailContent.SetInsertionPoint(selStart)
                self.emailContent.WriteText("<i>")
                self.emailContent.SetInsertionPoint(selEnd + 3)
                self.emailContent.WriteText("</i>")
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd + 7))
                self.emailContent.ApplyItalicToSelection()
            else:
                selectedText = self.emailContent.GetStringSelection()
                modifiedText = selectedText.replace('<i>', '')
                modifiedText = modifiedText.replace('</i>', '')
                self.emailContent.Replace(selStart, selEnd, modifiedText)
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd - 7))
        else:
            self.emailContent.WriteText("<i></i>")
            self.emailContent.SetInsertionPointEnd()

    def OnUnderlineText(self, arg=None):

        selStart, selEnd = self.emailContent.GetSelection()

        if (selStart != -2 and selEnd != -2) or (selStart != -2 or selEnd != -2):
            if not self.emailContent.IsSelectionUnderlined():
                self.emailContent.SetInsertionPoint(selStart)
                self.emailContent.WriteText("<u>")
                self.emailContent.SetInsertionPoint(selEnd + 3)
                self.emailContent.WriteText("</u>")
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd + 7))
                self.emailContent.ApplyUnderlineToSelection()
            else:
                selectedText = self.emailContent.GetStringSelection()
                modifiedText = selectedText.replace('<u>', '')
                modifiedText = modifiedText.replace('</u>', '')
                self.emailContent.Replace(selStart, selEnd, modifiedText)
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd - 7))
        else:
            self.emailContent.WriteText("<u></u>")
            self.emailContent.SetInsertionPointEnd()

    def OnURLText(self, arg=None):

        selStart, selEnd = self.emailContent.GetSelection()

        if (selStart != -2 and selEnd != -2) or (selStart != -2 or selEnd != -2):

            selText = self.emailContent.GetStringSelection()
            selTextLen = len(selText)

            if selText.find("<a href=") == -1:

                self.emailContent.Remove(selStart, selEnd)

                textToInsert = "<a href=\"" + selText + "\">" + selText + "</a>"
                textToInsertLen = len(textToInsert)

                self.emailContent.SetInsertionPoint(selStart)
                self.emailContent.WriteText(textToInsert)
                self.emailContent.SetInsertionPoint(selEnd + textToInsertLen)
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd + selTextLen + 15))

            else:
                selectedText = self.emailContent.GetStringSelection()
                result = re.search('%s(.*)%s' % (">", "<"), selectedText).group(1)
                self.emailContent.Replace(selStart, selEnd, result)
                self.emailContent.SetSelectionRange(wx.richtext.RichTextRange(selStart, selEnd - selTextLen))

        else:
            self.emailContent.WriteText("<a href=\"\"></a>")
            self.emailContent.SetInsertionPointEnd()

    def OnConfigureSMTPButtonClicked(self, event):

        frame = SMTPConfigFrame()
        frame.Show()

    def OnFormatTextButtonClicked(self, event):
        dialog = EmailFormattingDialog(self.emailContent)
        dialog.ShowModal()

    def OnChooseEmailsButtonClicked(self, event):

        dialog = EmailAddressChooserDialog(self.chosenResearchers)
        dialog.ShowModal()
        self.chosenResearchers = dialog.chosenResearchers[:]

    def OnPreviewButtonClicked(self, event):

        msgContent = "<br>Dear John Doe, <br><br>%s <br>" % self.emailContent.GetValue()

        msgContent = msgContent.replace('\n\r', '<br><br>')
        msgContent = msgContent.replace('\r\n', '<br><br>')
        msgContent = msgContent.replace('\n', '<br><br>')
        msgContent = msgContent.replace('\r', '<br><br>')

        msgBody = "<html><head></head><body> "
        msgBody += ("From: %s <br>" % "ai@umcs.pl")
        msgBody += ("To: %s <br>" % "test@gmail.com")
        msgBody += ("Subject: %s <br><br>" % self.emailSubject.GetValue())
        msgBody += (msgContent)
        msgBody += "</body></html>"

        frame = EmailPreviewFrame(msgBody)
        frame.Show()

    def OnSendButtonClicked(self, event):

        if len(self.chosenResearchers) == 0:
            msg = "Choose emails to send!"
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)

        else:
            dlg = wx.MessageDialog(None, 'Are you sure you want\nto send those e-mails?', 'Send it 4 sure?',
                                   wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:

                self.progressBar.SetRange(len(self.chosenResearchers))

                for i in range(0, len(self.chosenResearchers)):
                    sb = SpammerBot()
                    sb.setData("ai@poczta.umcs.lublin.pl", "XXXXXXXX",
                               self.chosenResearchers[i], "zeus.umcs.lublin.pl", 465,
                               self.emailSubject.GetValue(), self.emailContent.GetValue(), False)
                    sb.start()

            dlg.Destroy()

    def OnClearAllButtonClicked(self, event):
        self.CleanUpGUI()

    def OnEmailTemplateButtonClicked(self, event):
        wildcard = "Txt file (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, message="Choose a file", wildcard=wildcard, defaultDir=os.getcwd(), defaultFile="",
                               style=wx.OPEN)
        dialog.SetDirectory(self.createEmailsTemplateDirPath())
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            with open(path) as f:
                all_lines = [line.rstrip() for line in f]
            content = ""
            for line in all_lines:
                content += str(line + "\n")
            self.emailContent.SetValue(content.encode('utf-8'))
        dialog.Destroy()

    def CleanUpGUI(self):
        self.count = 0
        self.emailSubject.SetValue('')
        self.emailContent.SetValue('')
        self.emailContent.SetInsertionPoint(0)
        self.progressBar.SetValue(0)
        self.chosenResearchers[:] = []

    def updateProgress(self, msg=None):
        self.count += 1
        if self.count > self.progressBar.GetRange() - 1:
            self.progressBar.SetValue(self.count)
            msg = "All Emails Sent!"
            wx.MessageBox(msg, 'Done', wx.OK | wx.ICON_INFORMATION)
            self.progressBar.SetValue(0)
            self.chosenResearchers[:] = []
        else:
            self.progressBar.SetValue(self.count)

    def saveEmail(self, emailData):
        emailDB = GoogleScholarEmailBoxDatabase(self.createDBPath('mailbox_sent_emails.sql'))
        emailDB.createEmailBoxTable()
        emailDB.insertEmail(str(emailData.data.emailSender), str(emailData.data.emailRecipient),
                            str(emailData.data.emailSubject), str(emailData.data.emailContent),
                            str(emailData.data.dateSent))

        researchersDB = GoogleScholarDatabase(self.createDBPath('researchers.sql'))
        researchersDB.createResearchersTable()
        researchersDB.updateEmailUsage(1, str(emailData.data.emailRecipient))

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path

    def createCSVDirPath(self):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'csvs')
        return path

    def createDBPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Databases', resourceName)
        return path

    def createEmailsTemplateDirPath(self):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'email_template')
        return path


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Spammer")

        panel = SpammerPanel(self)

        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        ico = wx.Icon(self.createIconPath('gmail.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.SetSize(wx.Size(495, 530))
        self.SetMinSize(wx.Size(495, 530))
        self.Centre()
        self.Show()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path

    def OnCloseFrame(self, event):
        dialog = wx.MessageDialog(self, message="Are you sure you want to quit?", caption="Exit", style=wx.YES_NO,
                                  pos=wx.DefaultPosition)
        response = dialog.ShowModal()

        if (response == wx.ID_YES):
            self.Destroy()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
