import os

import wx
import wx.lib.agw.thumbnailctrl as TC

class MyFrame(wx.Frame):
    
    def __init__(self, parent):
        
        wx.Frame.__init__(self, parent, -1, "ThumbnailCtrl Demo")
        
        panel = wx.Panel(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        thumbnail = TC.ThumbnailCtrl(panel, imagehandler=TC.NativeImageHandler)
        sizer.Add(thumbnail, 1, wx.EXPAND | wx.ALL, 10)
        
        thumbnail.ShowDir(os.getcwd())
        panel.SetSizer(sizer)


# our normal wxApp-derived class, as usual

app = wx.App(0)

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()