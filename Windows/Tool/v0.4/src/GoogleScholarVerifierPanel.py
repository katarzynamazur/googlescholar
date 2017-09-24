#!/bin/env/python

import wx
import os
import re
import time
import urllib2
import urlparse
from socket import timeout
from threading import Thread
from wx.lib.pubsub import pub

import mechanize
from bs4 import BeautifulSoup

from GoogleScholarDatabase import GoogleScholarDatabase

EMAIL_COMBINATIONS = 11

class VerifierBot(Thread):
    def __init__(self, filename, email_start_number):
        super(VerifierBot, self).__init__()

        self.EMAIL_COMBINATIONS = 11
        self.GMAIL_IMPORT = './csvs/authors_emails_gmail_import'

        self.filename = filename
        self.email_start_number = email_start_number

    def __findEmailInText(self, email):
        return re.compile(r'\b({0})\b'.format(email), flags=re.IGNORECASE).search

    def __getGoogleSearchResultsLinks(self, google_query):
        try:
            # preapre and set up the browser
            browser = mechanize.Browser()
            browser.set_handle_robots(False)
            browser.set_handle_equiv(False)
            browser.addheaders = [('User-agent', 'Mozilla/5.0')]
            browser.open('http://www.google.com/')
            # do the query
            browser.select_form(name='f')
            browser.form['q'] = google_query
            data = browser.submit()
            soup = BeautifulSoup(data.read())
            # google search links
            google_links = []
            info = "[INFORMATION] Querying Google about author email: %s\n\n" % google_query
            wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
            for a in soup.select('.r a'):
                queryres = urlparse.parse_qs(urlparse.urlparse(a['href']).query)
                if 'q' in queryres:
                    link = urlparse.parse_qs(urlparse.urlparse(a['href']).query)['q'][0]
                    # get links only with http or https at the beginning
                    if link.startswith("http://") or link.startswith("https://"):
                        # omit direct pdf links, since we can not read them easily
                        if not link.endswith("pdf"):
                            google_links.append(link)
            return google_links
        except Exception:
            return None

    def __downloadPage(self, url):
        try:
            content = urllib2.urlopen(url, timeout=10).read()
            return str(content)
        except urllib2.HTTPError, error:
            info = ('[ERROR] HTTPError: ' + str(error.code) + '\n\n')
            wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
        except urllib2.URLError, error:
            info = ('[ERROR] URLError: ' + str(error.reason) + '\n\n')
            wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
        except timeout:
            info = '[ERROR] Time-Out!\n\n'
            wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
        except Exception:
            info = '[ERROR] Generic exception\n\n'
            wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))

    def __checkIfEmailIsFound(self, email):
        # get all google links available after querying
        #  google about that email (only first results page)
        google_links = self.__getGoogleSearchResultsLinks(email)
        # if we found some links
        if google_links is not None:
            # for every link
            for link in google_links:
                # simply download the page
                content = self.__downloadPage(link)
                if content is not None:
                    info = "Downloading the %s page, looking for an email %s ... \n\n" % (link, email)
                    wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
                    # and check if there is an email, if so
                    result = self.__findEmailInText(email)(content)
                    if result is not None:
                        # return it
                        info = "[INFORMATION] E-mail is found!\n\n"
                        wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
                        return email
        # email is not found
        info = '[INFORMATION] E-mail not found!\n\n'
        wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
        return None

    def __readIthEmailSetFromFile(self, i):
        """
        reads the email database and returns 10
        emails for the ith person
        """
        with open(self.filename) as f:
            all_lines = [line.rstrip() for line in f]
        i = i * self.EMAIL_COMBINATIONS
        return all_lines[i:(i + self.EMAIL_COMBINATIONS)]

    def checkHowManyEmailsWeHave(self):
        """
        simply counts how many people we have in our
        email database, 1 person = 10 email combinations
        """
        with open(self.filename) as f:
            all_lines = [line.rstrip() for line in f]
        return (len(all_lines) / self.EMAIL_COMBINATIONS)


    def __addResearcher2Database(self, email):
        data = email.split()
        db = GoogleScholarDatabase('researchers.sql')
        db.createResearchersTable()
        db.insertResearcher(data[1], data[2], data[0], data[3], data[-1].replace('_', ' ').title())

    def run(self):
        emails_count = self.checkHowManyEmailsWeHave()
        for i in range(self.email_start_number, emails_count):
            info = "Information (e-mail being processed: %d/%d)" % (i+1, emails_count)
            wx.CallAfter(pub.sendMessage, 'updateInfoLabel', text=('1',info))
            emails_set = self.__readIthEmailSetFromFile(i)
            # check the whole email dataset for just one person
            for email in emails_set:
                emailonly = email.split()[0]
                found = self.__checkIfEmailIsFound(emailonly)
                if found is not None:
                    self.__addResearcher2Database(email)
                    break
            if i != emails_count -1:
                # sleep a while, since we are not spammers (not yet :D)
                info = "[INFORMATION] Let me take a 5 minutes long nap before I start searching again ...\n\n"
                wx.CallAfter(pub.sendMessage, 'updateVerifyingInfo', text=('1',info))
            # if we check the whole email set for one person, just update progress
            wx.CallAfter(pub.sendMessage, 'updateVerifyingProgress', msg=('1',None))
            # we wont sleep if it is not necessary ^^
            if i != emails_count :
                # for a while, 5 minutes sleep - 5 minutes equals 300 seconds
                time.sleep(300)
        # we have checked all the email sets, so we can enable verify button
        #wx.CallAfter(pub.sendMessage, 'enableButtons', val=('1',True))


class VerifierPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.email_start_number = 0
        self.InitGUI()

    def InitGUI(self):

        self.count = 0
        max = 10000000

        dbFilenameLabel = wx.StaticText(self, label="Emails Database File:")
        emailStartNumberLabel = wx.StaticText(self, label="Email Start Number")
        self.infoLabel = wx.StaticText(self, label="Information")

        self.dbFilename = wx.TextCtrl(self, style=wx.TE_READONLY)

        self.chooseFileButton = wx.Button(self, label="Browse")
        self.Bind(wx.EVT_BUTTON, self.OnChooseFileButtonClicked, self.chooseFileButton)
        self.verifyButton = wx.Button(self, label="Verify")
        self.Bind(wx.EVT_BUTTON, self.OnVerifyButtonClicked, self.verifyButton)

        self.email_start_number_spin = wx.SpinCtrl(self, value="0")
        self.email_start_number_spin.SetRange(0, max)
        self.email_start_number_spin.SetValue(0)
        self.email_start_number_spin.Bind(wx.EVT_SPINCTRL, self.OnEmailStartNumberSpin)

        self.progressBar = wx.Gauge(self, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)

        self.infoText = wx.TextCtrl(self, size=(-1, 250), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(dbFilenameLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(20, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.dbFilename, 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.chooseFileButton, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(emailStartNumberLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(30, 15)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.email_start_number_spin, 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.verifyButton, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.infoLabel, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.infoText, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.progressBar, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        pub.subscribe(self.updateVerifyingInfo, 'updateVerifyingInfo')
        pub.subscribe(self.updateVerifyingProgress, 'updateVerifyingProgress')
        pub.subscribe(self.enableButtons, 'enableButtons')
        pub.subscribe(self.updateInfoLabel, 'updateInfoLabel')

        self.SetSizer(mainSizer)

    def OnChooseFileButtonClicked(self, event):

        def checkHowManyEmailsWeHave(filename, EMAIL_COMBINATIONS):
            with open(filename) as f:
                all_lines = [line.rstrip() for line in f]
            return (len(all_lines) / EMAIL_COMBINATIONS)

        wildcard = "Txt file (*.txt)|*.txt|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
        dialog.SetDirectory("./dbs")
        if dialog.ShowModal() == wx.ID_OK:
            self.dbFilename.SetValue(dialog.GetPath())
            emails_count = checkHowManyEmailsWeHave(dialog.GetPath(), EMAIL_COMBINATIONS)
        dialog.Destroy()

        info = "Information (e-mail being processed: 0/%d)" % (emails_count)
        self.infoLabel.SetLabel(info)

    def OnVerifyButtonClicked(self, event):
        wx.CallAfter(pub.sendMessage, 'enableButtons', val=('1',False))
        self.infoText.SetValue("")

        if self.dbFilename.GetValue().strip() == "":
            msg = "Give the emails database file!"
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.sendMessage, 'enableButtons', val=('1',True))
        else:
            vb = VerifierBot(self.dbFilename.GetValue().strip(), self.email_start_number)
            emails_count = vb.checkHowManyEmailsWeHave()

            if emails_count <= self.email_start_number :
                msg = "You don't have %s emails in your file!" % (self.email_start_number+1)
                wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
                wx.CallAfter(pub.sendMessage, 'enableButtons', val=('1',True))
            else:
                self.progressBar.SetRange(emails_count - self.email_start_number)
                vb.start()

    def OnEmailStartNumberSpin(self, event):
        self.email_start_number = self.email_start_number_spin.GetValue()

    def enableButtons(self, val):
        if val[1]:
            self.verifyButton.Enable()
            self.chooseFileButton.Enable()

        else:
            self.verifyButton.Disable()
            self.chooseFileButton.Disable()

    def updateVerifyingInfo(self, text):
        self.infoText.AppendText(str(text[1]))

    def updateVerifyingProgress(self, msg=None):
        self.count += 1
        if self.count > self.progressBar.GetRange() - 1:
            self.progressBar.SetValue(self.count)
            msg = "All Emails Verified!"
            wx.MessageBox(msg, 'Done', wx.OK | wx.ICON_INFORMATION)
            self.CleanUpGUI()
            wx.CallAfter(pub.sendMessage, 'enableButtons', val=('1',True))
        self.progressBar.SetValue(self.count)

    def updateInfoLabel(self, text):
        self.infoLabel.SetLabel(str(text[1]))

    def CleanUpGUI(self):
        self.count = 0
        self.email_start_number = 0
        self.dbFilename.SetValue("")
        self.infoText.SetValue("")
        self.email_start_number_spin.SetValue(0)
        self.infoLabel.SetLabel("Information")
        self.progressBar.SetValue(0)


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Email Verifier")
        panel = VerifierPanel(self)
        #ico = wx.Icon('./icons/check.png', wx.BITMAP_TYPE_PNG)
        #self.SetIcon(ico)
        self.SetSize(wx.Size(500, 450))
        self.SetMaxSize(wx.Size(500, 450))
        self.Centre()
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame()
    app.MainLoop()
