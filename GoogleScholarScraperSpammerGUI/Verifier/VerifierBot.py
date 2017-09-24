# !/bin/env/python

import wx
import os
import re
import time
import urllib2
import urlparse
import datetime
from socket import timeout
from threading import Thread
from wx.lib.pubsub import pub

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import mechanize
from bs4 import BeautifulSoup

from DatabaseMgmt.GoogleScholarResearchersDatabase import GoogleScholarDatabase


class VerifierBot(Thread):
    def __init__(self, filename, email_start_number):
        super(VerifierBot, self).__init__()

        self.EMAIL_COMBINATIONS = 11

        self.filename = filename
        self.email_start_number = email_start_number

    def __findEmailInText(self, email):
        try:
            return re.compile(r'\b({0})\b'.format(email), flags=re.IGNORECASE).search
        except Exception:
            return None

    def __getCurrentDateTime(self):
        return datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")


    def __prepareInfMsg(self, inf_content, inf_type):

        if len(inf_type) == 0:
            return ("[%s] %s\n") % (self.__getCurrentDateTime(), inf_content)
        else:
            return ("[%s] %s\n") % (inf_type, inf_content)

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
            info = self.__prepareInfMsg("Querying Google about author email: %s\n\n" % google_query, "INFORMATION")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)

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
            info = self.__prepareInfMsg("HTTPError: %s\n\n" % str(error.code), "ERROR")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
            return None
        except urllib2.URLError, error:
            info = self.__prepareInfMsg("URLError: %s\n\n" % str(error.reason), "ERROR")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
            return None
        except timeout:
            info = self.__prepareInfMsg("Time-Out! \n\n", "ERROR")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
            return None
        except Exception:
            info = self.__prepareInfMsg("Generic exception \n\n", "ERROR")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
            return None

    def __checkIfEmailIsFound(self, email):
        try:
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
                        info = self.__prepareInfMsg(
                            "Downloading the %s page, looking for an email %s ... \n\n" % (link, email), "")
                        wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
                        # and check if there is an email, if so
                        result = self.__findEmailInText(email)(content)

                        if result is not None:
                            # return it
                            info = self.__prepareInfMsg("E-mail is found! \n\n", "INFORMATION")
                            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
                            return email

            # email is not found
            info = self.__prepareInfMsg("E-mail not found! \n\n", "INFORMATION")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
            return None

        except Exception:
            # email is not found
            info = self.__prepareInfMsg("Exception: E-mail not found! \n\n", "INFORMATION")
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)
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
        db = GoogleScholarDatabase(self.createDBPath('researchers.sql'))
        db.createResearchersTable()
        if not db.emailAlreadyInDB(email):
            db.insertResearcher(data[1], data[2], data[0], data[3], data[-1].replace('_', ' ').title())

    def run(self):
        emails_count = self.checkHowManyEmailsWeHave()

        for i in range(self.email_start_number, emails_count):

            info = "Information (e-mail being processed: %d/%d)" % (i + 1, emails_count)
            wx.CallAfter(pub.Publisher.sendMessage, 'updateInfoLabel', info)
            emails_set = self.__readIthEmailSetFromFile(i)
            # check the whole email dataset for just one person

            for email in emails_set:
                emailonly = email.split()[0]
                found = self.__checkIfEmailIsFound(emailonly)
                if found is not None:
                    self.__addResearcher2Database(email)
                    break

            if i != emails_count - 1:
                # sleep a while, since we are not spammers (not yet :D)
                info = self.__prepareInfMsg("Let me take a 5 minutes long nap before I start searching again ...\n\n",
                                            "INFORMATION")
                wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingInfo', info)

            # if we check the whole email set for one person, just update progress
            wx.CallAfter(pub.Publisher.sendMessage, 'updateVerifyingProgress', None)

            # we wont sleep if it is not necessary ^^
            if i != emails_count:
                # for a while, 5 minutes sleep - 5 minutes equals 300 seconds
                # for now on, sleep a little longer, let's say, about 10 minutes
                time.sleep(600)

    def createDBPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Databases', resourceName)
        return path

#----------------------------------------------------------------------
if __name__ == "__main__":
    pass