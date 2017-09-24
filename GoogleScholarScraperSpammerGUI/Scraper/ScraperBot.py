# !/bin/env/python

from threading import Thread
import urllib2
import re
import copy
import os
from wx.lib.pubsub import pub
import wx

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding("utf8")

"""
@info Works with Google Scholar in 2015
Last check: 14.07.2015
"""


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

        self.EMAIL_FILE = self.createEmailFilePath()

    def createEmailFilePath(self):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'dbs', 'authors_emails')
        return path

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
            wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)
        except urllib2.URLError, error:
            info = ('URLError = ' + str(error.reason) + '\n')
            wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)
        except Exception:
            info = 'Generic exception\n'
            wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)

    def __makeBasicURL(self, label):
        baseurl = "http://scholar.google.pl/citations?view_op=search_authors&hl=pl&mauthors=label:%s" % (label)
        return baseurl


    def __makeSoupFirstPage(self, label):
        info = "Getting the 1 Google Scholar page ...\n"
        wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)
        baseurl = self.__makeBasicURL(label)
        content = self.__downloadPage(baseurl)
        soup = BeautifulSoup(content)
        return soup


    def __makeSoup(self, baseurl, num):
        info = "Getting the %s Google Scholar page ...\n" % num
        wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)

        if num == self.pages + 1:
            info = "\n[INFORMATION] All emails scrapped!\n"
            wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)

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
            wx.CallAfter(pub.Publisher.sendMessage, 'updateScrapingInfo', info)
            wx.CallAfter(pub.Publisher.sendMessage, 'enableScrapButton', True)
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
                    f.write(email + ' ' + author.firstname + ' ' + author.lastname + ' ' + str(
                        author.citations) + ' ' + label + '\n')
