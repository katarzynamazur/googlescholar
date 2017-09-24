#!/bin/env/python

from threading import Thread
import urllib2
import re
import sys
import copy
import os
from wx.lib.pubsub import pub
import wx

from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding("utf8")


class GoogleScholarAuthorInfo():
    def __init__(self, firstname, lastname, citations, emails_list):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.citations = citations
        self.emails_list = copy.deepcopy(emails_list)

    def __repr__(self):
        return '(%s %s, %s)' % (self.firstname, self.lastname, self.citations)

    def __str__(self):
        return '(%s %s, %s)' % (self.firstname, self.lastname, self.citations)


class ScraperBot(Thread):
    def __init__(self, citations_start, citations_stop, label, pages):
        super(ScraperBot, self).__init__()
        self.citations_start = citations_start
        self.citations_stop = citations_stop
        self.label = label
        self.pages = pages

        self.EMAIL_FILE = './dbs/authors_emails'

    def __createFilename(self, base, label, citations_start, citations_stop, extension):
        return base + "_" + label + "_" + str(self.pages) + "_" + str(citations_start) + "-" + str(
            citations_stop) + "." + extension

    def __createPossibleEmails(self, firstname, lastname, email):
        emailend = '@%s' % email
        emails = []
        emails.append(('%s.%s%s') % (firstname, lastname, emailend))
        emails.append(('%s.%s%s') % (lastname, firstname, emailend))
        emails.append(('%s%s%s') % (firstname, lastname, emailend))
        emails.append(('%s%s%s') % (lastname, firstname, emailend))
        emails.append(('%s_%s%s') % (firstname, lastname, emailend))
        emails.append(('%s_%s%s') % (lastname, firstname, emailend))
        emails.append(('%s.%s%s') % (firstname[0], lastname, emailend))
        emails.append(('%s%s%s') % (firstname[0], lastname, emailend))
        emails.append(('%s.%s%s') % (lastname, firstname[0], emailend))
        emails.append(('%s%s%s') % (lastname, firstname[0], emailend))
        emails.append(('%s%s') % (lastname, emailend))
        return emails

    def __splitFirstnameLastname(self, lastname_firstname, makelower):
        if makelower:
            tokens = lastname_firstname.lower().split()
        else:
            tokens = lastname_firstname.split()
        if len(tokens) == 2:
            firstname = tokens[0]
            lastname = tokens[1]
        elif len(tokens) == 3:
            firstname = tokens[0]
            lastname = tokens[2]
        else:
            firstname = tokens[0]
            lastname = tokens[-1]
        return firstname, lastname

    def __downloadPage(self, url):
        try:
            content = urllib2.urlopen(url).read()
            return str(content)
        except urllib2.HTTPError, error:
            info = ('HTTPError = ' + str(error.code) + '\n')
            wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))
        except urllib2.URLError, error:
            info = ('URLError = ' + str(error.reason) + '\n')
            wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))
        except Exception:
            info = 'Generic exception\n'
            wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))

    def __makeBasicURL(self, label):
        baseurl = "http://scholar.google.pl/citations?view_op=search_authors&hl=pl&mauthors=label:%s" % (label)
        return baseurl


    def __makeSoupFirstPage(self, label):
        info = "Getting the 1 Google Scholar page ...\n"
        wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))
        baseurl = self.__makeBasicURL(label)
        content = self.__downloadPage(baseurl)
        soup = BeautifulSoup(content)
        return soup


    def __makeSoup(self, baseurl, num):
        info = "Getting the %s Google Scholar page ...\n" % num
        wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))

        if num == self.pages + 1:
            info = "\n[INFORMATION] All emails scrapped!\n"
            wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))
            wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=True)

        content = self.__downloadPage(baseurl)
        soup = BeautifulSoup(content)
        return soup

    def __getNextPageID(self, soup):
        try:
            buttons = soup.findAll("button", {"onclick": True})
            button = buttons[-1]
            texttochop = str(button['onclick'])
            start = 'x3d'
            end = '__8J'
            result = re.search('.*%s(.*)%s' % (start, end), texttochop).group(1)
            return result
        except AttributeError:
            info = "\n[INFORMATION] I could not find the ID of the next page, so I'm quitting\n"
            info += "[INFORMATION] crawling through Google Scholar Pages!\n"
            info += "[INFORMATION] Hint: maybe this is the last available page?\n"
            wx.CallAfter(pub.sendMessage, 'updateScrapingInfo', text=('1',info))
            wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=('1',True))
            return None

    def __scrapAllPages(self, label, pages):
        soups = []
        counter = 10
        j = 1
        # build soup for the very first url
        soup = self.__makeSoupFirstPage(label)
        basicurl = self.__makeBasicURL(label)
        # append first page soup to the soups list
        soups.append(soup)
        # get soups for 'count' next pages
        for i in range(0, pages):
            # get the ID of the next page
            nextID = self.__getNextPageID(soup)
            if nextID is not None:
                #  build next url
                nexturl = basicurl + "&after_author=" + nextID + "__8J&astart=" + str(counter)
                # make a soup
                soup = self.__makeSoup(nexturl, (j + 1))
                # add soup to the soups list
                soups.append(soup)
                counter += 10
                j += 1
            else:
                break
        return soups

    def __getFullAuthorsInfo(self, soup):
        authors = []
        divs = soup.findAll("div", {"class": "gsc_1usr_text"})
        for div in divs:
            names = div.findAll("h3", {"class": "gsc_1usr_name"})
            cits = div.findAll("div", {"class": "gsc_1usr_cby"})
            mails = div.findAll("div", {"class": "gsc_1usr_eml"})
            # omit people not verified (without verified email address)
            if len(mails) > 0:
                # split lastname and firstname
                firstname, lastname = self.__splitFirstnameLastname(names[0].findAll('a')[0].contents[0], True)
                # create 10 email combinations
                mails = self.__createPossibleEmails(firstname, lastname, (mails[0].text.split()[-1]))[:]
                # if person have some citations
                if len(cits) > 0:
                    authors.append(GoogleScholarAuthorInfo(firstname, lastname, int(cits[0].text.split()[2]), mails))
                # if person does not have citations
                else:
                    authors.append(GoogleScholarAuthorInfo(firstname, lastname, 0, mails))
        return authors

    def __buildAuthorsInfoList(self, soups):
        authors_list = []
        for soup in soups:
            authors = self.__getFullAuthorsInfo(soup)
            for author in authors:
                authors_list.append(author)
        return authors_list


    def __getAuthorsWithCitations(self, authors, citations_start, citations_stop):
        authors_list = []
        for author in authors:
            if author.citations >= citations_start and author.citations <= citations_stop:
                authors_list.append(author)
        return authors_list

    def checkIfFileExists(self):
        emails_file = self.__createFilename(self.EMAIL_FILE, self.label, self.citations_start, self.citations_stop,
                                            "txt")
        return os.path.isfile(emails_file) and os.path.exists(emails_file)

    def run(self):
        """
        creates a simple email database for authors
        from the list
        """
        soups = self.__scrapAllPages(self.label, self.pages)
        authors = self.__buildAuthorsInfoList(soups)
        authors_list = self.__getAuthorsWithCitations(authors, self.citations_start, self.citations_stop)
        emails_file = self.__createFilename(self.EMAIL_FILE, self.label, self.citations_start, self.citations_stop,
                                            "txt")

        with open(emails_file, 'w') as f:
            for author in authors_list:
                for email in author.emails_list:
                    label = self.label.strip().replace(' ', '_').title()
                    f.write(email + ' ' + author.firstname + ' ' + author.lastname + ' ' + str(author.citations) + ' ' + label + '\n')


class ScraperPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.keyword = ""
        self.citations_start = 0
        self.citations_stop = 0
        self.pages = 0

        self.InitGUI()

    def InitGUI(self):
        max = 10000000

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        citationsLabel = wx.StaticText(self, label="Citations:")
        keywordLabel = wx.StaticText(self, label="Keyword:")
        pagesLabel = wx.StaticText(self, label="Pages:")
        infoLabel = wx.StaticText(self, label="Information")

        self.citations_start_spin = wx.SpinCtrl(self, value="0")
        self.citations_start_spin.SetRange(0, max)
        self.citations_start_spin.SetValue(0)
        self.citations_start_spin.Bind(wx.EVT_SPINCTRL, self.OnCitationsStartSpin)

        self.citations_stop_spin = wx.SpinCtrl(self, value="0")
        self.citations_stop_spin.SetRange(0, max)
        self.citations_stop_spin.SetValue(0)
        self.citations_stop_spin.Bind(wx.EVT_SPINCTRL, self.OnCitationsStopSpin)

        self.pages_spin = wx.SpinCtrl(self, value="0")
        self.pages_spin.SetRange(0, max)
        self.pages_spin.SetValue(0)
        self.pages_spin.Bind(wx.EVT_SPINCTRL, self.OnPagesSpin)

        self.labelText = wx.TextCtrl(self)
        self.infoText = wx.TextCtrl(self, size=(-1, 220), style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.scraperButton = wx.Button(self, label="Scrap Emails")
        self.Bind(wx.EVT_BUTTON, self.OnScraperButtonClicked, self.scraperButton)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(citationsLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(10, 10)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.citations_start_spin, 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, label="-"), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.citations_stop_spin, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(keywordLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(10, 10)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.labelText, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(pagesLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self, size=(24, 10)), 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.pages_spin, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.LEFT, 5)
        sizer.Add(self.scraperButton, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(infoLabel, 0, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.infoText, 1, wx.ALL | wx.LEFT, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        pub.subscribe(self.updateScrapingInfo, 'updateScrapingInfo')
        pub.subscribe(self.enableScrapButton, 'enableScrapButton')

        self.SetSizer(mainSizer)

    def OnCitationsStartSpin(self, event):
        self.citations_start = self.citations_start_spin.GetValue()

    def OnCitationsStopSpin(self, event):
        self.citations_stop = self.citations_stop_spin.GetValue()

    def OnPagesSpin(self, event):
        self.pages = self.pages_spin.GetValue()

    def OnScraperButtonClicked(self, event):
        wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=('1',False))
        self.infoText.SetValue("")
        self.keyword = self.labelText.GetValue().strip().replace(' ', '_').title()

        if self.citations_stop == 0:
            msg = "Please give the maximum citation number."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=('1',True))
        elif self.keyword == "":
            msg = "Please give the keyword."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=('1',True))
        elif self.pages == 0:
            msg = "Please give the number of pages to dig out."
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=('1',True))
        else:
            s = ScraperBot(self.citations_start, self.citations_stop, self.keyword, self.pages)
            if not s.checkIfFileExists():
                s.start()
            else:
                msg = "I've already found researchers with given criteria, so" \
                      " emails file is already created (please check the 'dbs' directory)."
                wx.MessageBox(msg, 'Information', wx.OK | wx.ICON_INFORMATION)
                wx.CallAfter(pub.sendMessage, 'enableScrapButton', val=True)

    def enableScrapButton(self, val):
        if val[1]:
            self.scraperButton.Enable()
        else:
            self.scraperButton.Disable()

    def updateScrapingInfo(self, text):
        self.infoText.AppendText(str(text[1]))


class DemoFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Google Scholar Scraper")
        panel = ScraperPanel(self)
        ico = wx.Icon('./icons/scholar.ico', wx.BITMAP_TYPE_ICO)
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
