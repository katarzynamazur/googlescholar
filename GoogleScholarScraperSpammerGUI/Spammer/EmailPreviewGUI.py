# !/bin/env/python
import wx
import wx.html
import os
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


class EmailPreviewPanel(wx.Panel):
    def __init__(self, parent, msgBody):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        html = wx.html.HtmlWindow(self)
        html.SetPage(msgBody)

        closeButton = wx.Button(self, label="OK")
        self.Bind(wx.EVT_BUTTON, self.OnCloseClicked, closeButton)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(html, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(closeButton, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)


    def OnCloseClicked(self, event):
        self.GetParent().Close()


class EmailPreviewFrame(wx.Frame):
    def __init__(self, msgBody):
        wx.Frame.__init__(self, None, title="Final Email")
        panel = EmailPreviewPanel(self, msgBody)
        ico = wx.Icon(self.createIconPath('mail.png'), wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)
        self.SetSize(wx.Size(750, 600))
        self.SetMinSize(wx.Size(750, 600))
        self.Centre()
        self.Show()

    def createIconPath(self, resourceName):
        tmp = os.path.split(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(tmp[0], 'Data', 'icons', resourceName)
        return path

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = EmailPreviewFrame('')
    app.MainLoop()