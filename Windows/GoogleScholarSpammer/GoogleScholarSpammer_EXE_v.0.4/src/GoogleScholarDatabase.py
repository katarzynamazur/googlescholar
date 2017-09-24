#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sqlite
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
                cursor.execute(sql, (firstname, lastname, email, citations, keyword))
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


if __name__ == "__main__":
    pass
    # db = GoogleScholarDatabase('test.sql')
    # db.createResearchersTable()
    # db.insertResearcher('Tibby', 'Molko', 'tibby.molko@gmail.com', 999, 'security')
    # db.insertResearcher('Tibby', 'Molko', 'tibby.molko@gmail.com', 666, 'security')
    # db.insertResearcher('Tibby', 'Molko', 'tibby.molko@gmail.com', 999, 'sec')
    # db.insertResearcher('Tibby', 'Molko', 'tibby.molko@gmail.com', 1000, 'crypto')
    #
    # rs = db.getResearchersByKeywordAndCitationsGreaterEqual(666, 'security')
    # for r in rs :
    #     print r



