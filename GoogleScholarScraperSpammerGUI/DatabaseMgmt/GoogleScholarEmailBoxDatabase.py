#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sqlite
import os
import sys


def createDBPath(resourceName):
    tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(tmp[0], 'Databases', resourceName)
    return path


class ScholarEmail():
    def __init__(self, emailSender, emailRecipient, emailSubject, emailContent, dateSent):
        self.emailSender = emailSender
        self.emailRecipient = emailRecipient
        self.emailSubject = emailSubject
        self.emailContent = emailContent
        self.dateSent = dateSent

    def __repr__(self):
        return 'FROM: %s TO: %s SUBJECT: "%s" DATE SENT: %s' % (
            self.emailSender, self.emailRecipient, self.emailSubject, self.dateSent)

    def __str__(self):
        return 'FROM: %s TO: %s SUBJECT: "%s" DATE SENT: %s' % (
            self.emailSender, self.emailRecipient, self.emailSubject, self.dateSent)


class GoogleScholarEmailBoxDatabase:
    def __init__(self, dbname):
        self.dbname = dbname


    def createEmailBoxTable(self):
        connection = sqlite.connect(self.dbname)
        try:
            with connection:
                cursor = connection.cursor()
                sql = '''\
                    CREATE TABLE IF NOT EXISTS EmailBox (
                        ID INTEGER PRIMARY KEY NOT NULL,
                        EMAIL_SENDER TEXT,
                        EMAIL_RECEIVER TEXT,
                        EMAIL_SUBJECT TEXT,
                        EMAIL_CONTENT TEXT,
                        DATE_SENT TEXT)
                '''
                cursor.execute(sql)
        finally:
            connection.close()

    def insertEmail(self, emailSender, emailRecipient, emailSubject, emailContent, dateSent):
        connection = sqlite.connect(self.dbname, check_same_thread=False)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "INSERT INTO EmailBox (email_sender, email_receiver, email_subject, email_content, date_sent) VALUES (?, ?, ?, ?, ?)"
                try:
                    cursor.execute(sql, (emailSender, emailRecipient, emailSubject, emailContent, dateSent))
                except sqlite.ProgrammingError:
                    pass
        finally:
            connection.close()

    def getSentEmails(self):
        emails = []
        connection = sqlite.connect(self.dbname, check_same_thread=False)
        try:
            with connection:
                cursor = connection.cursor()
                sql = "SELECT EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_SUBJECT, EMAIL_CONTENT, DATE_SENT FROM EmailBox"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    emails.append(ScholarEmail(row[0], row[1], row[2], row[3], row[4]))
        finally:
            connection.close()
        return emails

    def getNumberOfAllEmails(self):
        emails = self.getSentEmails()
        return len(emails)

    def checkIfEmailWasUsed(self, email):
        mails = self.getSentEmails()
        for mail in mails:
            if mail.emailRecipient == email:
                return True
        return False


if __name__ == "__main__":

    db = GoogleScholarEmailBoxDatabase(createDBPath('mailbox_sent_emails.sql'))
    emails = db.getSentEmails()

    sys.stdout.write('-' * 80)
    print ""
    for email in emails:
        print email
    sys.stdout.write('-' * 80)
    print ""