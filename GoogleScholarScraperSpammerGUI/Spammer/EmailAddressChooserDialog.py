# !/bin/env/python

import wx
import os
import copy
from wx.lib.pubsub import pub
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from DatabaseMgmt.GoogleScholarEmailBoxDatabase import GoogleScholarEmailBoxDatabase
from DatabaseMgmt.GoogleScholarResearchersDatabase import GoogleScholarDatabase
from Spammer.EmailByKeywordSelectionDialog import EmailByKeywordSelectionDialog
from Spammer.EmailByCountryCodeSelectionDialog import EmailByCountryCodeSelectionDialog


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnCheckItem)

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    def OnCheckItem(self, data, flag):
        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnHandleSelection', (data, flag))


class EmailAddressChooserDialog(wx.Dialog):
    def __init__(self, chosenResearchers=None):
        wx.Dialog.__init__(self, None, title="Choose E-mail Addresses")

        self.InitDBs()
        self.InitGUI()
        self.InitListeners()


    def InitGUI(self):

        self.chosenResearchers = []
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # self.searcher = wx.TextCtrl(self)

        leftPanel = wx.Panel(self, -1)
        rightPanel = wx.Panel(self, -1)

        selectButton = wx.Button(leftPanel, -1, 'Select ...', size=(100, -1))
        selectAllButton = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        deselectAllButton = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))

        self.infoLabel = wx.StaticText(self, label='Selected E-mails: 0, All E-mails: %s' % str(
            self.researchersDB.getNumberOfAllResearchers()))
        infoIcon = wx.StaticBitmap(self, -1, wx.Bitmap(self.createIconPath('stats.png'), wx.BITMAP_TYPE_ANY), (0, 0),
                                   (20, 20))
        infoIcon.SetToolTip(wx.ToolTip("Number of Selected Emails"))

        infoSizer = wx.BoxSizer(wx.HORIZONTAL)
        infoSizer.Add(infoIcon, 0, wx.ALL | wx.LEFT, 5)
        infoSizer.Add(self.infoLabel, 0, wx.ALL | wx.LEFT, 5)

        self.list = CheckListCtrl(self)

        self.Bind(wx.EVT_BUTTON, self.OnSelect, id=selectButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=selectAllButton.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=deselectAllButton.GetId())
        # self.Bind(wx.EVT_TEXT, self.OnKeyPress, id=self.searcher.GetId())

        rightPanelSizer = wx.BoxSizer(wx.VERTICAL)
        leftPanelSizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        rows = self.PrepareDataForSelection()
        self.myRowDict = {}
        i = 0
        self.list.InsertColumn(0, 'Firstname')
        self.list.InsertColumn(1, 'Lastname')
        self.list.InsertColumn(2, 'Email', width=200)
        self.list.InsertColumn(3, 'Used Before', width=80)
        self.list.InsertColumn(4, 'Keyword', width=200)
        self.list.InsertColumn(5, 'Citations', width=70)
        for row in rows:
            index = self.list.InsertStringItem(sys.maxint, row[0])
            self.list.SetStringItem(index, 1, row[1])
            self.list.SetStringItem(index, 2, row[2])
            self.list.SetStringItem(index, 3, row[3])
            self.list.SetStringItem(index, 4, row[4])
            self.list.SetStringItem(index, 5, row[5])
            self.myRowDict[i] = row
            i += 1

        leftPanelSizer.Add(selectButton, 0, wx.TOP, 5)
        leftPanelSizer.Add(selectAllButton)
        leftPanelSizer.Add(deselectAllButton)

        leftPanel.SetSizer(leftPanelSizer)

        rightPanelSizer.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        rightPanel.SetSizer(rightPanelSizer)

        hbox.Add(rightPanel, 1, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(leftPanel, 0, wx.EXPAND)
        hbox.Add((3, -1))

        bottomPanel = wx.BoxSizer(wx.VERTICAL)
        bottomPanel.Add(wx.StaticText(self), 0, wx.EXPAND)
        # bottomPanel.Add(self.searcher, 0, wx.EXPAND)

        mainSizer.Add(hbox, 1, wx.EXPAND)
        mainSizer.Add(bottomPanel, 0, wx.EXPAND)
        mainSizer.Add(infoSizer, 0, wx.EXPAND)

        self.SetSizer(mainSizer)
        self.SetSize(wx.Size(800, 400))
        self.SetMinSize(wx.Size(800, 400))

    def InitListeners(self):

        pub.Publisher.subscribe(self.OnHandleSelection, 'EmailAddressChooserDialog.OnHandleSelection')
        pub.Publisher.subscribe(self.OnUpdateInfo, 'EmailAddressChooserDialog.OnUpdateInfo')

    def InitDBs(self):

        self.researchersDB = GoogleScholarDatabase(self.createDBPath('researchers.sql'))
        self.emailDB = GoogleScholarEmailBoxDatabase(self.createDBPath('mailbox_sent_emails.sql'))

    def PrepareDataForSelection(self):

        rows = []
        researchers = self.researchersDB.getAllResearchers()
        for researcher in researchers:
            if researcher.used_before == 1:
                rows.append(
                    (str(researcher.firstname), str(researcher.lastname), str(researcher.email), 'Yes',
                     str(researcher.keyword), str(researcher.citations)))
            elif researcher.used_before == 0:
                rows.append((str(researcher.firstname), str(researcher.lastname), str(researcher.email), 'No',
                             str(researcher.keyword), str(researcher.citations)))

        return rows


    def OnHandleSelection(self, data):
        id = data.data[0]
        value = data.data[1]

        firstname = self.list.GetItem(id, 0).GetText()
        lastname = self.list.GetItem(id, 1).GetText()
        email = self.list.GetItem(id, 2).GetText()
        citation = self.list.GetItem(id, 5).GetText()

        rt = (str(firstname), str(lastname), str(email))

        if value:
            if rt not in self.chosenResearchers:
                self.chosenResearchers.append(rt)
        else:
            if rt in self.chosenResearchers:
                self.chosenResearchers.remove(rt)

        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnUpdateInfo', str(self.CountSelected()))

    def OnUpdateInfo(self, arg):
        self.infoLabel.SetLabel(
            'Selected E-mails: %s, All E-mails: %s' % (arg.data, str(self.researchersDB.getNumberOfAllResearchers())))


    def CountSelected(self):
        selected = 0
        num = self.list.GetItemCount()
        for i in range(num):
            if self.list.IsChecked(i):
                selected += 1
        return selected


    def OnSelect(self, event):

        class SelectDialog(wx.Dialog):

            def __init__(self, list=None):
                wx.Dialog.__init__(self, None, title="Select ...")
                mainSizer = wx.BoxSizer(wx.VERTICAL)
                self.selected = -1
                selectionList = ['...', 'By Keyword', 'By Country Code']
                self.choices = wx.ComboBox(self, 500, '...', (50, 150), (320, -1), selectionList, wx.CB_DROPDOWN)
                self.choices.SetSelection(0)

                self.choices.Bind(wx.EVT_COMBOBOX, self.OnSelection)

                bagSizer = wx.GridBagSizer(5, 5)
                bagSizer.Add(self.choices, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
                self.SetSizer(bagSizer)
                bagSizer.Fit(self)

            def OnSelection(self, event):
                self.selected = self.choices.GetSelection()
                self.Close()

        dialog = SelectDialog()
        dialog.ShowModal()

        if dialog.selected == 1:
            self.OnSelectByKeyword(None)
        elif dialog.selected == 2:
            self.OnSelectByCountryCode(None)

    def OnSelectByCountryCode(self, event):
        countryCodes = self.researchersDB.getEmailCountryCodes()
        dialog = EmailByCountryCodeSelectionDialog(countryCodes)
        dialog.ShowModal()

        num = self.list.GetItemCount()
        countryCode = dialog.countryCodesComboBox.GetValue()
        selection = dialog.selectionComboBox.GetValue()

        if selection == 'All':
            for i in range(num):
                if self.myRowDict[i][2].split('.')[-1] == countryCode:
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))
        elif selection == 'All used':
            for i in range(num):
                if self.myRowDict[i][2].split('.')[-1] == countryCode and self.myRowDict[i][3] == 'Yes':
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))
        elif selection == 'All unused':
            for i in range(num):
                if self.myRowDict[i][2].split('.')[-1] == countryCode and self.myRowDict[i][3] == 'No':
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))

        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnUpdateInfo', str(self.CountSelected()))


    def OnSelectByKeyword(self, event):
        keywordsList = self.researchersDB.getKeywords()
        dialog = EmailByKeywordSelectionDialog(keywordsList)
        dialog.ShowModal()

        num = self.list.GetItemCount()
        keyword = dialog.keywordComboBox.GetValue()
        selection = dialog.selectionComboBox.GetValue()

        if selection == 'All':
            for i in range(num):
                if self.myRowDict[i][4] == keyword:
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))
        elif selection == 'All used':
            for i in range(num):
                if self.myRowDict[i][4] == keyword and self.myRowDict[i][3] == 'Yes':
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))
        elif selection == 'All unused':
            for i in range(num):
                if self.myRowDict[i][4] == keyword and self.myRowDict[i][3] == 'No':
                    self.list.CheckItem(i)
                    self.chosenResearchers.append(
                        (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))

        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnUpdateInfo', str(self.CountSelected()))


    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)
            self.chosenResearchers.append(
                (str(self.myRowDict[i][0]), str(self.myRowDict[i][1]), str(self.myRowDict[i][2])))
        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnUpdateInfo', str(num))

    def OnDeselectAll(self, event):
        self.chosenResearchers[:] = []
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)
        wx.CallAfter(pub.Publisher.sendMessage, 'EmailAddressChooserDialog.OnUpdateInfo', str(0))


    def OnKeyPress(self, event):
        searched = self.searcher.GetValue()
        print searched

        # listcopy = self.list[:]
        # self.list.DeleteAllItems()
        #
        # num = self.list.GetItemCount()
        #
        # for i in range(num):
        #     if searched in self.list.GetItem(i):
        #         print self.list.GetItem()
        #
        # for i in range (num) :
        #     if str(self.myRowDict[i][2]) == searched :
        #         print "FOUND! " + str(self.myRowDict[i][2])
        #
        #

        # self.list.DeleteAllItems()
        #
        # for i in range(num):
        # if searched in tmplist[i]:
        #         self.list.InsertItem(tmplist[i])

        # tmplist = []
        # num = self.list.GetItemCount()
        # for i in range(num):
        #     tmplist.append(self.list.GetItem())
        # self.list.DeleteAllItems()

    def createDBPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Databases', resourceName)
        return path


    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path