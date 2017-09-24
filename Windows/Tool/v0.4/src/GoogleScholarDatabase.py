#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sqlite
import os
import sys

class GoogleScholarResearcher:
    def __init__(self, firstname, lastname, email, citations, keyword):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email
        self.citations = citations
        self.keyword = keyword

    def __repr__(self):
        return '(%s %s [%s], Citations: %s, Keyword: %s)' % (
        self.firstname, self.lastname, self.email, self.citations, self.keyword)

    def __str__(self):
        return '(%s %s [%s], Citations: %s, Keyword: %s)' % (
        self.firstname, self.lastname, self.email, self.citations, self.keyword)


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
                        KEYWORD TEXT)
                '''
                cursor.execute(sql)
        finally:
            connection.close()

    def insertResearcher(self, firstname, lastname, email, citations, keyword):
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "INSERT INTO Researchers (firstname, lastname, email, citations, keyword) VALUES (?, ?, ?, ?, ?)"
                try :
                    cursor.execute(sql, (firstname, lastname, email, citations, keyword))
                except sqlite.ProgrammingError:
                    pass
        finally:
            connection.close()

    def getAllResearchers(self):
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
        finally:
            connection.close()
        return researchers

    def getResearcherByID(self, ID):
        ID = str(ID)
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE id=?"
                cursor.execute(sql, ID)
                row = cursor.fetchone()
                return GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4])
        finally:
            connection.close()

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

    def getResearchersByCitationsEqual(self, citations):
        citations = str(citations)
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE citations=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
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
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE citations<=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
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
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE citations>=?"
                cursor.execute(sql, (citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
        finally:
            connection.close()
        return researchers

    def getResearchersByKeyword(self, keyword):
        researchers = []
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE keyword=?"
                cursor.execute(sql, (keyword,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
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
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE keyword=? AND citations=?"
                cursor.execute(sql, (keyword,citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
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
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE keyword=? AND citations<=?"
                cursor.execute(sql, (keyword,citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
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
                sql = "SELECT firstname, lastname, email, citations, keyword FROM Researchers WHERE keyword=? AND citations>=?"
                cursor.execute(sql, (keyword,citations,))
                rows = cursor.fetchall()
                for row in rows:
                    researchers.append(GoogleScholarResearcher(row[0], row[1], row[2], row[3], row[4]))
        finally:
            connection.close()
        return researchers

    def __checkIfFileExists(self, filename):
        return os.path.isfile(filename) and os.path.exists(filename)

    def createGmailImportFile(self):
        filename = "./csvs/gmail_import_all.csv"
        researchers = self.getAllResearchers()
        if not self.__checkIfFileExists(filename):
            with open(filename, "wa") as f:
                f.write(
                    'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional '
                    'Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,'
                    'Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,'
                    'Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,'
                    'E-mail 1 - Type,E-mail 1 - Value\n')

        for researcher in researchers :
            with open(filename, "a") as f:
                try :
                    f.write("%s %s,%s,,%s,,,,,,,,,,,,,,,,,,,,,,,%s ::: * My Contacts,* Home,%s\n" % (researcher.firstname, researcher.lastname,
                                                                                                 researcher.firstname, researcher.lastname,
                                                                                                 researcher.keyword, researcher.email))
                except UnicodeEncodeError:
                    pass

    def createGmailImportFileByKeyword(self, keyword):
        filename = "./csvs/gmail_import_%s.csv" % keyword
        researchers = self.getResearchersByKeyword(keyword)
        if not self.__checkIfFileExists(filename):
            with open(filename, "wa") as f:
                f.write(
                    'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional '
                    'Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,'
                    'Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,'
                    'Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,'
                    'E-mail 1 - Type,E-mail 1 - Value\n')

        for researcher in researchers :
            with open(filename, "a") as f:
                try:
                    f.write("%s %s,%s,,%s,,,,,,,,,,,,,,,,,,,,,,,%s ::: * My Contacts,* Home,%s\n" % (researcher.firstname, researcher.lastname,
                                                                                                 researcher.firstname, researcher.lastname,
                                                                                                 researcher.keyword, researcher.email))
                except UnicodeEncodeError:
                    pass

if __name__ == "__main__":

    db = GoogleScholarDatabase('researchers.sql')
    researchers = db.getAllResearchers()

    sys.stdout.write('-' * 80)
    print ""
    for researcher in researchers :
        print researcher
    sys.stdout.write('-' * 80)
    print ""

    #db.createGmailImportFile()

