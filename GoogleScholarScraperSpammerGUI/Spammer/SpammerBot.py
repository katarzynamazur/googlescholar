#!/bin/env/python

import wx
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket
import time
from threading import Thread
from wx.lib.pubsub import pub

from DatabaseMgmt.GoogleScholarEmailBoxDatabase import ScholarEmail


class SpammerBot(Thread):
    def __init__(self):
        super(SpammerBot, self).__init__()

    def __getCurrDateTime(self):
        return str(time.strftime("%Y-%m-%d %H:%M"))

    def __buildMessage2Send(self):


        msgContent = "<html>\n\t<head></head>\n\t\t<body>\n\t\t\t"
        msgContent += ("Dear %s %s, <br/><br/> %s <br/>" % (
            self.emailRecipientFirstname, self.emailRecipientLastname, self.emailContent))
        msgContent += "\n\t\t</body>\n\t</html>"
        msg = MIMEMultipart('alternative')

        try:
            text = MIMEText(msgContent.encode('utf-8'), 'html')
        except UnicodeEncodeError:
            text = MIMEText('<html><head></head><body></body></html>', 'html')

        msg['To'] = email.utils.formataddr(
            ('%s %s' % (self.emailRecipientFirstname, self.emailRecipientLastname), self.emailRecipientMail))
        msg['From'] = email.utils.formataddr(('Annales UMCS Informatica', self.emailSender))
        msg['Messsage-Id'] = email.utils.make_msgid('Annales UMCS Informatica')
        msg['Reply-to'] = email.utils.formataddr(('Annales UMCS Informatica', self.emailSender))
        msg['Date'] = email.utils.formatdate(localtime=1)
        msg['Subject'] = self.emailSubject
        msg.attach(text)

        return msg.as_string()


    def setData(self, emailSender, emailPass, emailRecipientMail, smtpServer, smtpPort, emailSubject, emailContent,
                isDomainAccount):
        self.emailSender = emailSender
        self.emailPass = emailPass
        self.smtpServer = smtpServer
        self.smtpPort = smtpPort
        self.emailSubject = emailSubject
        self.emailContent = emailContent
        self.emailRecipientMail = emailRecipientMail[2]
        self.emailRecipientFirstname = emailRecipientMail[0]
        self.emailRecipientLastname = emailRecipientMail[1]
        self.isDomainAccount = isDomainAccount

    def run(self):
        message = self.__buildMessage2Send()
        try:
            server = None

            if self.isDomainAccount:

                server = smtplib.SMTP_SSL(self.smtpServer, self.smtpPort)
                server.esmtp_features['auth'] = 'LOGIN PLAIN'
                server.login(self.emailSender.split('@')[0], self.emailPass)
                server.sendmail(self.emailSender, self.emailRecipientMail, message)

            else:

                server = smtplib.SMTP_SSL(self.smtpServer, self.smtpPort)
                server.login(self.emailSender, self.emailPass)
                server.sendmail(self.emailSender, self.emailRecipientMail, message)

            wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.updateProgress', None)
            wx.CallAfter(pub.Publisher.sendMessage, 'SpammerPanel.saveEmail',
                         ScholarEmail(self.emailSender, self.emailRecipientMail,
                                      self.emailSubject, self.emailContent,
                                      self.__getCurrDateTime()))
        except socket.error as e:
            msg = ("Could not connect to " + self.smtpServer + ":" + str(self.smtpPort) + " - is it listening / up?")
            wx.MessageBox(msg, 'Connection Error', wx.OK | wx.ICON_ERROR)
            print msg

        except smtplib.SMTPServerDisconnected:
            msg = "smtplib.SMTPServerDisconnected"
            print msg
            wx.MessageBox(msg, 'SMTP Server Disconnected', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPResponseException, e:
            msg = "smtplib.SMTPResponseException"
            print msg + str(e.smtp_code) + " " + str(e.smtp_error)
            wx.MessageBox(msg, 'SMTP Response Exception', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPSenderRefused:
            msg = "smtplib.SMTPSenderRefused"
            print msg
            wx.MessageBox(msg, 'SMTP Sender Refused', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPRecipientsRefused:
            msg = "smtplib.SMTPSenderRefused"
            print msg
            wx.MessageBox(msg, 'SMTP Sender Refused', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPDataError:
            msg = "smtplib.SMTPSenderRefused"
            print msg
            wx.MessageBox(msg, 'SMTP Sender Refused', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPConnectError:
            msg = "smtplib.SMTPConnectError"
            print msg
            wx.MessageBox(msg, 'SMTP Connect Error', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPHeloError:
            msg = "smtplib.SMTPHeloError"
            print msg
            wx.MessageBox(msg, 'SMTP Helo Error', wx.OK | wx.ICON_ERROR)

        except smtplib.SMTPAuthenticationError:
            msg = "smtplib.SMTPAuthenticationError"
            print msg
            wx.MessageBox(msg, 'SMTP Authentication Error', wx.OK | wx.ICON_ERROR)

        except Exception, e:
            msg = "Unknown error"
            print msg
            wx.MessageBox(msg, 'Unknown Error', wx.OK | wx.ICON_ERROR)
        finally:
            if server != None:
                server.quit()