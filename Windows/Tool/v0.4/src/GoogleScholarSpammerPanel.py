#!/bin/env/python

import wx
import os
import string
import smtplib
import socket
from threading import Thread
from wx.lib.pubsub import pub


class SpammerBot(Thread):
    def __init__(self, emailSubject, emailContent, recipient):
        super(SpammerBot, self).__init__()
        self.myEmail = "katarzyna.mazur@poczta.umcs.lublin.pl"
        self.myEmailPass = "tibby89emade"
        self.smtp = "zeus.umcs.lublin.pl"
        self.port = 465
        self.emailSubject = emailSubject
        self.emailContent = emailContent
        self.recipient = recipient


    def BuildMessage2Send(self):
        msgContent = "Dear %s %s, \n\n%s\n" % (
            self.recipient[0], self.recipient[1], self.emailContent)

        msgBody = string.join((
                                  "From: %s" % self.myEmail,
                                  "To: %s" % self.recipient[2],
                                  "Subject: %s" % self.emailSubject,
                                  "",
                                  msgContent
                              ), "\r\n")
        return msgBody

    def run(self):
        message = self.BuildMessage2Send()
        try:
            server = None
            server = smtplib.SMTP_SSL(self.smtp, self.port)
            server.login(self.myEmail, self.myEmailPass)
            server.sendmail(self.myEmail, self.recipient[2], message)
            wx.CallAfter(pub.sendMessage, 'updateProgress', msg=('1',None))
        except socket.error as e:
            msg = ("Could not connect to " + self.smtp + ":" + str(self.port) + " - is it listening / up?")
            wx.MessageBox(msg, 'Connection Error', wx.OK | wx.ICON_ERROR)
        except:
            msg = "Unknown error"
            wx.MessageBox(msg, 'Unknown Error', wx.OK | wx.ICON_ERROR)
        finally:
            if server != None:
                server.quit()
        return message


class SpammerPanel(wx.Panel):
    def __init__(self, parent):

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.filename = ""
        self.emails = 0
        self.content = ""

        self.InitGUI()

    def InitGUI(self):

        max = 10000000
        self.count = 0

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        emailsFileLabel = wx.StaticText(self, label="Emails (CSV) File:")
        emailsNumberLabel = wx.StaticText(self, label="Number of Emails:")
        emailSubjectLabel = wx.StaticText(self, label="Email Subject:")
        emailContentLabel = wx.StaticText(self, label="Email Content:")

        self.emailsFilename = wx.TextCtrl(self, wx.TE_READONLY)
        self.emailsFilename.SetEditable(False)
        self.emailSubject = wx.TextCtrl(self)
        self.emailContent = wx.TextCtrl(self, size=(-1, 150), style=wx.TE_MULTILINE)

        chooseFileButton = wx.Button(self, label="Browse")
        self.Bind(wx.EVT_BUTTON, self.OnChooseFileButtonClicked, chooseFileButton)
        self.sendMeButton = wx.Button(self, size=(200, -1), label="Send %s emails" % self.emails)
        self.Bind(wx.EVT_BUTTON, self.OnSendMeButtonClicked, self.sendMeButton)
        checkEmailButton = wx.Button(self, size=(200, -1), label="Check Final Email")
        self.Bind(wx.EVT_BUTTON, self.OnCheckEmailClicked, checkEmailButton)

        self.progressBar = wx.Gauge(self, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)

        self.emailsSpin = wx.SpinCtrl(self, value="0")
        self.emailsSpin.SetRange(0, max)
        self.emailsSpin.SetValue(0)
        self.emailsSpin.Bind(wx.EVT_SPINCTRL, self.OnEmailsSpin)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailsFileLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(20, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.emailsFilename, 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(chooseFileButton, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailsNumberLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(15, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.emailsSpin, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailSubjectLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(35, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.emailSubject, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailContentLabel, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.emailContent, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sendMeButton, 1, wx.ALL | wx.CENTER, 5)
        sizer.Add(checkEmailButton, 1, wx.ALL | wx.CENTER, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.progressBar, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        pub.subscribe(self.updateProgress, 'updateProgress')

        self.SetSizer(mainSizer)


    def OnEmailsSpin(self, event):
        self.emails = self.emailsSpin.GetValue()
        self.sendMeButton.SetLabel("Send %s emails" % self.emails)

    def OnChooseFileButtonClicked(self, event):

        self.CleanUpGUI()

        wildcard = "CSV file (*.csv)|*.csv|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
        dialog.SetDirectory("./csvs")
        if dialog.ShowModal() == wx.ID_OK:
            self.emailsFilename.SetValue(dialog.GetPath())
        dialog.Destroy()


    def OnCheckEmailClicked(self, event):
        msgContent = "\nDear John Doe, \n\n%s\n" % self.emailContent.GetValue()

        msgBody = string.join((
                                  "From: %s" % "katarzyna.mazur@poczta.umcs.lublin.pl",
                                  "To: %s" % "test@gmail.com",
                                  "Subject: %s" % self.emailSubject.GetValue(),
                                  "",
                                  msgContent
                              ), "\r\n")

        class EmailTextPanel(wx.Panel):
            def __init__(self, parent):
                wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
                self.emailText = wx.TextCtrl(self, style=wx.TE_MULTILINE)
                self.emailText.SetValue(msgBody)
                self.emailText.SetEditable(False)
                closeButton = wx.Button(self, label="OK")
                self.Bind(wx.EVT_BUTTON, self.OnCloseClicked, closeButton)

                mainSizer = wx.BoxSizer(wx.VERTICAL)

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(self.emailText, 1, wx.ALL | wx.EXPAND, 5)
                mainSizer.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
                sizer.Add(closeButton, 0, wx.ALL | wx.EXPAND, 5)
                mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

                self.SetSizer(mainSizer)

            def OnCloseClicked(self, event):
                self.GetParent().Close()


        class EmailTextFrame(wx.Frame):
            def __init__(self):
                wx.Frame.__init__(self, None, title="Final Email")
                panel = EmailTextPanel(self)
                ico = wx.Icon('./icons/gmail.ico', wx.BITMAP_TYPE_ICO)
                self.SetIcon(ico)
                self.Centre()

        frame = EmailTextFrame()
        frame.Show()

    def OnSendMeButtonClicked(self, event):

        if self.emails == 0 or self.emailsFilename.GetValue() == "":

            msg = "Choose CSV file and number of emails to send!"
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)

        else:
            recipientsList = self.BuildRecipientsList(self.emailsFilename.GetValue())[:self.emails]
            self.progressBar.SetRange(len(recipientsList))

            if self.emails > len(recipientsList):
                msg = "You don't have %s emails in your CSV file!" % self.emails
                wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            else:
                for i in range(0, self.emails):
                    sb = SpammerBot(self.emailSubject.GetValue(), self.emailContent.GetValue(), recipientsList[i])
                    sb.start()

    def ReadCSVFile(self, filename):
        with open(filename) as f:
            content = f.readlines()[1:]
        return content

    def BuildRecipientsList(self, filename):
        recipientsList = []
        content = self.ReadCSVFile(filename)
        for person in content:
            info = person.split(',')
            recipientsList.append((info[1], info[3], info[-1].strip()))
        return recipientsList

    def CleanUpGUI(self):
        self.count = 0
        self.emails = 0
        self.emailsFilename.SetValue('')
        self.emailSubject.SetValue('')
        self.emailContent.SetValue('')
        self.progressBar.SetValue(0)
        self.emailsSpin.SetValue(0)
        self.sendMeButton.SetLabel("Send %s emails" % self.emails)

    def updateProgress(self, msg=None):
        self.count += 1
        if self.count > self.progressBar.GetRange() - 1:
            self.progressBar.SetValue(self.count)
            msg = "All Emails Sent!"
            wx.MessageBox(msg, 'Done', wx.OK | wx.ICON_INFORMATION)
            self.CleanUpGUI()
        self.progressBar.SetValue(self.count)


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Spammer")
        panel = SpammerPanel(self)
        ico = wx.Icon('./icons/gmail.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.SetSize(wx.Size(500, 450))
        self.SetMaxSize(wx.Size(500, 450))
        self.Centre()
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
