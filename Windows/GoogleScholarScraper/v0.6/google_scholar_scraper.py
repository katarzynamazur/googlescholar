# !/usr/bin/env python
# -*- coding: utf-8 -*-

#title           :google_scholar_scrapper.py
#description     :gets the information from google scholar site: authors names, affiliations and citation numbers
#author          :kasiula
#date            :21-03-2015
#version         :0.6
#usage           :google_scrapper.py -c [number of citations needed] -l [label] -p [how many pages I should search]
#notes           :

import mechanize
import argparse
import urlparse
from bs4 import BeautifulSoup
import urllib2
import re
import sys
import copy
import os

reload(sys)
sys.setdefaultencoding("utf8")

EMAIL_COMBINATIONS = 11
EMAIL_FILE = 'authors_emails'
GMAIL_IMPORT = 'authors_emails_gmail_import'


class GoogleScholarAuthorInfo():
    def __init__(self, firstname, lastname, affiliation, citations, emails_list):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.affiliation = affiliation
        self.citations = citations
        self.emails_list = copy.deepcopy(emails_list)

    def __repr__(self):
        return '(%s %s, %s, %s)' % (self.firstname, self.lastname, self.affiliation, self.citations)

    def __str__(self):
        return '(%s %s, %s, %s)' % (self.firstname, self.lastname, self.affiliation, self.citations)


def printWelcomeHeader():
    n = 80
    for i in range(0, n): sys.stdout.write('-')
    print "\n\t\tSimple Google Scholar Scraper / Spammer Script"
    print "\t\t\tCopyright (c) 2015 Katarzyna Mazur"
    for i in range(0, n): sys.stdout.write('-')
    print ''


def printWelcomeMsg(pages, label, citations):
    print "\nKindly please be patient, I'm digging out through %s pages to find emails of \nGoogle Scholar Researchers associated with '%s'," \
          "\nwho have number of citations less or equal to %s ... \nThis may take a while ... \n" \
          % (pages, label, citations)


def printGoodbyeMsg(label):
    print "\nDone! Please check the 'authors_details_%s.csv' (Gmail import file) for authors emails details. Bye! :)\n" % label


def parseScriptArguments():
    parser = argparse.ArgumentParser(description='Script gathers information about Google Scholar Researchers.')
    parser.add_argument('-c', help='number of citations', type=int, required=True)
    parser.add_argument('-l', help='Google Scholar label', required=True)
    parser.add_argument('-p', help='number of pages I should dig out', type=int, required=True)
    parser.add_argument('-e', help='email number I should look for', type=int, required=True)
    args = parser.parse_args()
    return args.c, args.l.replace(' ', '_'), args.p, args.e


def findEmailInText(email):
    return re.compile(r'\b({0})\b'.format(email), flags=re.IGNORECASE).search


def createFilename(base, label, citations, extension):
    return base + "_" + label + "_" + str(citations) + "." + extension


def createPossibleEmails(firstname, lastname, email):
    emailend = '@%s' % email
    emails = []
    # we have just 'EMAIL_COMBINATIONS' email combinations
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


def splitFirstnameLastname(lastname_firstname, makelower):
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


def downloadPage(url):
    try:
        content = urllib2.urlopen(url).read()
        return content
    except urllib2.HTTPError, error:
        print ('HTTPError = ' + str(error.code))
    except urllib2.URLError, error:
        print ('URLError = ' + str(error.reason))
    except Exception:
        print 'Generic exception'


def makeBasicURL(label):
    baseurl = "http://scholar.google.pl/citations?view_op=search_authors&hl=pl&mauthors=label:%s" % (label)
    return baseurl


def makeSoupFirstPage(label):
    print  "Getting the 1 Google Scholar page ..."
    baseurl = makeBasicURL(label)
    content = downloadPage(baseurl)
    soup = BeautifulSoup(content)
    return soup


def makeSoup(baseurl, num):
    print  "Getting the %s Google Scholar page ..." % num
    content = downloadPage(baseurl)
    soup = BeautifulSoup(content)
    return soup


def getNextPageID(soup):
    try:
        buttons = soup.findAll("button", {"onclick": True})
        button = buttons[-1]
        texttochop = str(button['onclick'])
        start = 'x3d'
        end = '__8J'
        result = re.search('.*%s(.*)%s' % (start, end), texttochop).group(1)
        return result
    except AttributeError:
        print "\n[INFORMATION] I could not find the ID of the next page, so I'm quitting"
        print "[INFORMATION] crawling through Google Scholar Pages!"
        print "[INFORMATION] Hint: maybe this is the last available page?"
        return None


def getThemAll(label, count):
    soups = []
    counter = 10
    j = 1
    # build soup for the very first url
    soup = makeSoupFirstPage(label)
    basicurl = makeBasicURL(label)
    # append first page soup to the soups list
    soups.append(soup)
    # get soups for 'count' next pages
    for i in range(0, count):
        # get the ID of the next page
        nextID = getNextPageID(soup)
        if nextID is not None:
            #  build next url
            nexturl = basicurl + "&after_author=" + nextID + "__8J&astart=" + str(counter)
            # make a soup
            soup = makeSoup(nexturl, (j + 1))
            # add soup to the soups list
            soups.append(soup)
            counter += 10
            j += 1
        else:
            break
    return soups


def getFullAuthorsInfo(soup):
    authors = []
    divs = soup.findAll("div", {"class": "gsc_1usr_text"})
    for div in divs:
        names = div.findAll("h3", {"class": "gsc_1usr_name"})
        affs = div.findAll("div", {"class": "gsc_1usr_aff"})
        cits = div.findAll("div", {"class": "gsc_1usr_cby"})
        mails = div.findAll("div", {"class": "gsc_1usr_eml"})
        # omit people not verified (without verified email address)
        if len(mails) > 0:
            # omit people without affiliation
            if len(affs) > 0:
                # split lastname and firstname
                firstname, lastname = splitFirstnameLastname(names[0].findAll('a')[0].contents[0].encode('utf-8'), True)
                # create 10 email combinations
                mails = createPossibleEmails(firstname, lastname, (mails[0].text.encode('utf-8').split()[-1]))[:]
                # if person have some citations
                if len(cits) > 0:
                    authors.append(GoogleScholarAuthorInfo(firstname, lastname,
                                                           affs[0].text.encode('utf-8'),
                                                           int(cits[0].text.encode('utf-8').split()[2]),
                                                           mails))
                # if person does not have citations
                else:
                    authors.append(GoogleScholarAuthorInfo(firstname, lastname,
                                                           affs[0].text.encode('utf-8'),
                                                           0, mails))
    return authors


def getGoogleSearchResultsLinks(google_query):
    try:
        # preapre and set tup the browser
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
        print "\n[INFORMATION] Querying Google about author email: %s" % google_query
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


def checkIfEmailIsFound(email):
    # get all google links available after querying
    #  google about that email (only first results page)
    google_links = getGoogleSearchResultsLinks(email)
    # if we found some links
    if google_links is not None:
        # for every link
        for link in google_links:
            # simply download the page
            content = downloadPage(link)
            if content is not None:
                print "Downloading the %s page, looking for an email %s ... " % (link, email)
                # and check if there is an email, if so
                result = findEmailInText(email)(content)
                if result is not None:
                    # return it
                    print "\n[INFORMATION] E-mail is found!"
                    return email
    # email is not found
    print '\n[INFORMATION] E-mail not found!'
    return None


def buildAuthorsInfoList(soups):
    authors_list = []
    for soup in soups:
        authors = getFullAuthorsInfo(soup)
        for author in authors:
            authors_list.append(author)
    return authors_list


def getAuthorsWithCitations(authors, citations):
    authors_list = []
    for author in authors:
        if citations >= author.citations:
            authors_list.append(author)
    return authors_list


def checkIfFileExists(filename):
    return os.path.isfile(filename) and os.path.exists(filename)


def writeOutPossibleEmails2File(authors_list, label, citations):
    """
    creates a simple email database for authors
    from the list
    """
    emails_file = createFilename(EMAIL_FILE, label, citations, "txt")
    with open(emails_file, 'w') as f:
        for author in authors_list:
            for email in author.emails_list:
                f.write(email + ' ' + author.firstname + ' ' + author.lastname + '\n')


def readIthEmailSetFromFile(label, i, citations):
    """
    reads the email database and returns 10
    emails for the ith person
    """
    emails_file = createFilename(EMAIL_FILE, label, citations, "txt")
    with open(emails_file) as f:
        all_lines = [line.rstrip() for line in f]
    i = i * EMAIL_COMBINATIONS
    return all_lines[i:(i + EMAIL_COMBINATIONS)]


def checkHowManyEmailsWeHave(label, citations):
    """
    simply counts how many people we have in our
    email database, 1 person = 10 email combinations
    """
    emails_file = createFilename(EMAIL_FILE, label, citations, "txt")
    with open(emails_file) as f:
        all_lines = [line.rstrip() for line in f]
    return len(all_lines) / EMAIL_COMBINATIONS


def writeGmailImportFile(email, label, citations):
    importfile = createFilename(GMAIL_IMPORT, label, citations, "csv")
    data = email.split()
    # file does not exist, so simply create it
    if not checkIfFileExists(importfile):
        with open(importfile, "w") as f:
            f.write(
                'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional '
                'Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,'
                'Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,'
                'Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,'
                'E-mail 1 - Type,E-mail 1 - Value\n')

    with open(importfile, "a") as f:
        f.write("%s %s,%s,,%s,,,,,,,,,,,,,,,,,,,,,,,%s ::: * My Contacts,* Home,%s\n" % (data[1], data[2], data[1], data[2], label.replace('_', ' ').title(), data[0]))


def createGmailImportFile(label, i, citations):
    emails_file = createFilename(EMAIL_FILE, label, citations, "txt")
    emails_count = checkHowManyEmailsWeHave(label, citations)
    if emails_count < i:
        print "\n[ERROR] I could not find the %s email in your %s file, " \
              "since you do not have enough emails!" % (i, emails_file)
    else:
        emails_set = readIthEmailSetFromFile(label, i, citations)
        for email in emails_set:
            emailonly = email.split()[0]
            found = checkIfEmailIsFound(emailonly)
            if found is not None:
                writeGmailImportFile(email, label, citations)
                return True
    return False

if __name__ == "__main__":
    try:
        printWelcomeHeader()
        citations, label, pages, email_number = parseScriptArguments()
        printWelcomeMsg(pages + 1, label.replace('_', ' '), citations)
        emails_file = createFilename(EMAIL_FILE, label, citations, "txt")

        if not checkIfFileExists(emails_file):
            soups = getThemAll(label, pages)
            authors = buildAuthorsInfoList(soups)
            authors = getAuthorsWithCitations(authors, citations)
            writeOutPossibleEmails2File(authors, label, citations)

        createGmailImportFile(label, email_number, citations)
        printGoodbyeMsg(label)
    except:
        raw_input()
    finally:
        raw_input()

