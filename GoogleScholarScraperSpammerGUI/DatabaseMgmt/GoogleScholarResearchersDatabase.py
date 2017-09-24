# !/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sqlite
import os
import sys


def createDBPath(resourceName):
    tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(tmp[0], 'Databases', resourceName)
    return path


def createCSVPath(resourceName):
    tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(tmp[0], 'Data', 'csvs', resourceName)
    return path


class GoogleScholarResearcher:
    def __init__(self, firstname, lastname, email, citations, keyword, used_before=0):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email
        self.citations = citations
        self.keyword = keyword
        self.used_before = used_before

    def __repr__(self):
        return '%s %s [%s], Citations: %s, Keyword: %s %s' % (
            self.firstname, self.lastname, self.email, self.citations, self.keyword, str(self.used_before))

    def __str__(self):
        return '%s %s [%s], Citations: %s, Keyword: %s %s' % (
            self.firstname, self.lastname, self.email, self.citations, self.keyword, str(self.used_before))


class GoogleScholarDatabase:
    def __init__(self, dbname):
        self.dbname = dbname

    def createResearchersTable(self):
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = '''\
                    CREATE TABLE IF NOT EXISTS Researchers (
                        ID INTEGER PRIMARY KEY NOT NULL,
                        FIRSTNAME TEXT,
                        LASTNAME TEXT,
                        EMAIL TEXT,
                        CITATIONS INTEGER,
                        KEYWORD TEXT,
                        USED_BEFORE INTEGER)
                '''
                cursor.execute(sql)
        finally:
            connection.close()

    ###################################################################################################################################

    def insertResearcher(self, firstname, lastname, email, citations, keyword):
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "INSERT INTO Researchers (FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE) VALUES (?, ?, ?, ?, ?, ?)"
                try:
                    cursor.execute(sql, (firstname, lastname, email, citations, keyword, 0))
                except sqlite.ProgrammingError:
                    pass
        finally:
            connection.close()

    ###################################################################################################################################

    def emailAlreadyInDB(self, email):
        emails = self.getEmails()
        if email.split()[0] in emails:
            return True
        else:
            return False

    ###################################################################################################################################

    def updateEmailUsage(self, value, email):
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = ''' \
                        UPDATE Researchers
                        SET USED_BEFORE=?
                        WHERE
                        EMAIL=?;
                      '''
                try:
                    cursor.execute(sql, (value, email))
                except sqlite.DatabaseError, dbe:
                    print dbe
        finally:
            connection.close()

    ###################################################################################################################################

    def getAllResearchers(self):
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers"
                cursor.execute(sql)
                for (firstname, lastname, email, citations, keyword, used_before, ) in cursor:
                    researchers.append(
                        GoogleScholarResearcher(firstname, lastname, email, citations, keyword, used_before))
        finally:
            connection.close()
        return researchers

    def getNumberOfAllResearchers(self):
        researchers = self.getAllResearchers()
        return len(researchers)

    def getResearcherByID(self, ID):
        ID = str(ID)
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE ID=?"
                cursor.execute(sql, ID)
                row = cursor.fetchone()
                return GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5])
        finally:
            connection.close()

    def getResearchersByCitationsEqual(self, citations):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE CITATIONS=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByCitationsLessEqual(self, citations):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE CITATIONS<=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByCitationsGreaterEqual(self, citations):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE CITATIONS>=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByKeyword(self, keyword):
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE KEYWORD=?"
                cursor.execute(sql, (keyword,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers


    def getResearchersByKeywordAndCitationsEqual(self, citations, keyword):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE KEYWORD=? AND CITATIONS=?"
                cursor.execute(sql, (keyword, citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByKeywordAndCitationsLessEqual(self, citations, keyword):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE KEYWORD=? AND CITATIONS<=?"
                cursor.execute(sql, (keyword, citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByKeywordAndCitationsGreaterEqual(self, citations, keyword):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE KEYWORD=? AND CITATIONS>=?"
                cursor.execute(sql, (keyword, citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers

    def getResearchersByEmailCountryCode(self, countrycode=None):
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT FIRSTNAME, LASTNAME, EMAIL, CITATIONS, KEYWORD, USED_BEFORE FROM Researchers WHERE EMAIL LIKE ?"

                # format is like anything@sth.uk, anything@sth.de, anything@sth.us, anything@sth.se, anything@sth.no, ...
                # depends on given country code, if country code is no, we look for anything@oslo..no
                format = '%.'
                format = format + countrycode

                cursor.execute(sql, (format,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4], row[5]))
        finally:
            connection.close()
        return researchers


    def getEmailCountryCodes(self):
        countryCodes = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT EMAIL FROM Researchers"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    countryCode = str(row[0]).split('.')[-1]
                    if countryCode not in countryCodes and \
                                    countryCode != 'edu' and \
                                    countryCode != 'com' and \
                                    countryCode != 'org' and \
                                    countryCode != 'net' and \
                                    countryCode != 'gov' and \
                                    countryCode != 'digital':
                        countryCodes.append(countryCode.lower())
        finally:
            connection.close()
        countryCodes.sort()
        return countryCodes

    def getKeywords(self):
        keywords = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT DISTINCT KEYWORD FROM Researchers"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    keywords.append(str(row[0]))
        finally:
            connection.close()
        return keywords


    def getEmails(self):
        emails = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT EMAIL FROM Researchers"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    emails.append(str(row[0]))
        finally:
            connection.close()
        return emails

    ###################################################################################################################################

    def deleteResearcherByID(self, ID):
        ID = str(ID)
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "DELETE FROM Researchers WHERE id=?"
                cursor.execute(sql, ID)
        finally:
            connection.close()

    ###################################################################################################################################

    def __checkIfFileExists(self, filename):
        return os.path.isfile(filename) and os.path.exists(filename)

    ###################################################################################################################################

    def createGmailImportFile(self):
        filename = createCSVPath('gmail_import_all.csv')
        researchers = self.getAllResearchers()
        if not self.__checkIfFileExists(filename):
            with open(filename, "wa") as f:
                f.write(
                    'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional '
                    'Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,'
                    'Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,'
                    'Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,'
                    'E-mail 1 - Type,E-mail 1 - Value\n')

        for researcher in researchers:
            with open(filename, "a") as f:
                try:
                    f.write("%s %s,%s,,%s,,,,,,,,,,,,,,,,,,,,,,,%s ::: * My Contacts,* Home,%s\n" % (
                        researcher.firstname, researcher.lastname,
                        researcher.firstname, researcher.lastname,
                        researcher.keyword, researcher.email))
                except UnicodeEncodeError:
                    pass

    def createGmailImportFileByKeyword(self, keyword):
        filename = createCSVPath('gmail_import_%s.csv' % keyword)
        researchers = self.getResearchersByKeyword(keyword)
        if not self.__checkIfFileExists(filename):
            with open(filename, "wa") as f:
                f.write(
                    'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional '
                    'Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,'
                    'Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,'
                    'Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,'
                    'E-mail 1 - Type,E-mail 1 - Value\n')

        for researcher in researchers:
            with open(filename, "a") as f:
                try:
                    f.write("%s %s,%s,,%s,,,,,,,,,,,,,,,,,,,,,,,%s ::: * My Contacts,* Home,%s\n" % (
                        researcher.firstname, researcher.lastname,
                        researcher.firstname, researcher.lastname,
                        researcher.keyword, researcher.email))
                except UnicodeEncodeError:
                    pass

                    ##################################################################################################################################


if __name__ == "__main__":

    db = GoogleScholarDatabase(createDBPath('researchers.sql'))
    researchers = db.getAllResearchers()

    sys.stdout.write('-' * 80)
    print ""
    for researcher in researchers:
        print researcher
    sys.stdout.write('-' * 80)
    print ""

    keywords = db.getKeywords()
    # print keywords
    for keyword in keywords:
        r = db.getResearchersByKeyword(keyword)
        print "Keyword '%s' has " % keyword + str(len(r)) + " email(s) verified."

    print "\nVerified so far (in total): " + str(len(researchers))

