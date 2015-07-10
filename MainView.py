import wx
import wx.media
import os

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
global plot_x
global plot_y
global state_box_row
global video_x
global video_y
video_x = 1
video_y = 1
plot_x = 1
plot_y = 1
state_box_row = 5
class MainView(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
        try:
            self.mc = wx.media.MediaCtrl(self, size = (400, 300),style=wx.SIMPLE_BORDER)
        except NotImplementedError:
            self.Destroy()
            raise
        

        self.previewImage = []
        
        
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        self.loadButton = fileMenu.Append(wx.NewId(), "&Load Videos  (MPEG4, MPG supported)", "")
        self.exportButton = fileMenu.Append(wx.NewId(), "&Export landmark   (CSV format)", "")
        self.importButton = fileMenu.Append(wx.NewId(), "&Import annotation file    (CSV format)")
        menuBar.Append(fileMenu, "&File")
        parent.SetMenuBar(menuBar)
        
        # video player related
        #self.loadButton = wx.Button(self, -1, "Load File")
        self.playButton = wx.Button(self, -1, "Play")
        #self.pauseButton = wx.Button(self, -1, "Pause")
        self.stopButton = wx.Button(self, -1, "Stop")
        #self.exportButton = wx.Button(self, -1, "Export")
        #self.importButton = wx.Button(self, -1, "Import")
        slider = wx.Slider(self, -1, 0, 0, 0, size=wx.Size(400, -1))
        self.slider = slider


        
        #Operations on upper right
        self.op_notebook = wx.Notebook(self, size = (810, 310))
        self.op_notebook.SetPosition((410, 5))
        
        # video related information panel
        self.infoPanel = wx.Panel(self.op_notebook, -1, size = (800, 340))
        self.op_notebook.AddPage(self.infoPanel, "vid info")
        self.previewButton = wx.Button(self.infoPanel, -1, "Preview", pos = (5,5))
        self.showCurPosButton = wx.Button(self.infoPanel, -1, "Show Pos", pos = (105, 5))
        self.st_size = wx.StaticText(self.infoPanel, -1, size=(1,-1), pos = (605,5))
        self.st_len  = wx.StaticText(self.infoPanel, -1, size=(1,-1), pos = (605, 30))
        self.st_pos  = wx.StaticText(self.infoPanel, -1, size=(1,-1), pos = (605, 55))
        self.volumeSlider = wx.Slider(self.infoPanel, -1, 0, 0, 0, size=(400, -1), pos =(5,55) )
        self.audioOff = wx.CheckBox(self.infoPanel, -1, "Audio off", pos = (500, 55))

        self.annotationPanel = wx.Panel(self.op_notebook, -1, size = (800, 340))
        self.op_notebook.AddPage(self.annotationPanel, "annotate")
        self.addQuantileButton = wx.Button(self.annotationPanel, -1, "Add quantile")
        self.addStateButton = wx.Button(self.annotationPanel, -1, "Add State")
        self.removeQuantileButton = wx.Button(self.annotationPanel, -1, "Del Quantile")
        self.removeStateButton = wx.Button(self.annotationPanel, -1, "Remove State")
        self.interpolateButton = wx.Button(self.annotationPanel, -1, "Inter1d")
        # 1 lower section 2 upper section 3 state 4 color
        self.textField1 = wx.TextCtrl(self.annotationPanel)
        self.textField2 = wx.TextCtrl(self.annotationPanel)
        self.textField3 = wx.TextCtrl(self.annotationPanel)
        self.textField4 = wx.TextCtrl(self.annotationPanel)
        self.textField5 = wx.TextCtrl(self.annotationPanel)

        self.sizer = wx.GridBagSizer(5,5)
        self.sizer.Add(self.addQuantileButton,(plot_x,plot_y))
        self.sizer.Add(self.removeQuantileButton,(plot_x,plot_y+1))
        self.sizer.Add(self.addStateButton,(plot_x,plot_y+2))
        self.sizer.Add(self.removeStateButton,(plot_x,plot_y+3))
        self.sizer.Add(self.interpolateButton, (plot_x, plot_y+4))
        
        



        self.sizer.Add(wx.StaticText(self.annotationPanel, -1, label = 'lower', size=(100,20)), (plot_x+1,plot_y))
        self.sizer.Add(wx.StaticText(self.annotationPanel, -1, label = 'upper', size=(100,20)),(plot_x+1,plot_y+1))
        self.sizer.Add(wx.StaticText(self.annotationPanel, -1, label = 'description', size=(100,20)), (plot_x+1,plot_y+2))
        self.sizer.Add(wx.StaticText(self.annotationPanel, -1, label = 'color', size=(100,20)), (plot_x+1,plot_y+3))
        self.sizer.Add(wx.StaticText(self.annotationPanel, -1, label = 'state', size=(100,20)), (plot_x+1,plot_y+4))
        
        self.sizer.Add(self.textField1,(plot_x+2,plot_y))
        self.sizer.Add(self.textField2,(plot_x+2,plot_y+1))
        self.sizer.Add(self.textField3,(plot_x+2,plot_y+2))
        self.sizer.Add(self.textField4,(plot_x+2,plot_y+3))
        self.sizer.Add(self.textField5,(plot_x+2,plot_y+4))


        self.plot_notebook = wx.Notebook(self, size = (1270, 390))
        self.plot_notebook.SetPosition((5, 340))
        self.annotationPanel.SetSizerAndFit(self.sizer)
        self.annotationPanel.Layout()
        # matplotlib related
        
        
        
        
        self.valencePanel = wx.Panel(self.plot_notebook, -1, size = (1260, 360))
        self.plot_notebook.AddPage(self.valencePanel, "Valence")
        self.arousalPanel = wx.Panel(self.plot_notebook, -1, size = (1260, 360))
        self.plot_notebook.AddPage(self.arousalPanel, "Arousal")


        #self.plotPanel.SetBackgroundColour("white")
        

        
        

        self.stateCheckBox = []

        # video player is 400 width and 300 height at (5,5) in pixels
        self.mc.SetPosition((5,5))
        # slider for the video player is 400 width at (5, 305) in pixels
        self.slider.SetPosition((5, 305))
        # start position for bottons of video control
        x = 5
        y = 330
        x_offset = 90
        y_offset = 15
        self.playButton.SetPosition((x, y))
        self.stopButton.SetPosition((x+x_offset, y))

        #self.sizer.Add(self.loadButton, (3,1))
        #self.sizer.Add(self.playButton, (4,1))
        #self.sizer.Add(self.pauseButton, (5,1))
        #self.sizer.Add(self.stopButton, (6,1))
        #self.sizer.Add(self.exportButton, (7,1))
        #self.sizer.Add(self.importButton, (8,1))
        #self.sizer.Add(self.previewButton, (8,1))
        #self.sizer.Add(self.showCurPosButton, (9,1))
        #self.sizer.Add(self.slider,(2,1),span=(1,5))
        #self.sizer.Add(self.st_size, (3, 2))
        #self.sizer.Add(self.st_len,  (4, 2))
        #self.sizer.Add(self.st_pos,  (5, 2))
        #self.sizer.Add(self.mc, (1,1),span=(1,5))  # for .avi .mpg video files

        
        
    def add_check_box(self, state):
        self.stateCheckBox.append(wx.CheckBox(self.annotationPanel, -1, state))
        current = len(self.stateCheckBox) - 1
        self.sizer.Add(self.stateCheckBox[current],(plot_x+4+current/state_box_row, plot_y+current%state_box_row))
        self.annotationPanel.Layout()




if __name__=='__main__':
    
    app = wx.App(False)
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "Video Annotation Tool", size = (1280, 750))

    
    
    # call the derived class
    m = MainView(frame, -1)
    
    fig = plt.figure(0, figsize=(16, 4.5), dpi=80)
    
    canvas = FigureCanvasWxAgg(m.valencePanel, -1, fig)
    
    fig = plt.figure(0, figsize=(16, 4.5), dpi=80)
    
    canvas = FigureCanvasWxAgg(m.arousalPanel, -1, fig)
    
    frame.Show(1)
    app.MainLoop()