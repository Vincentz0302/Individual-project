import wx
import wx.media
import os
global plot_x
global plot_y
global state_box_row
global video_x
global video_y
video_x = 1
video_y = 1
plot_x = 9
plot_y = 6
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
        loadButton = fileMenu.Append(wx.NewId(), "&Load Videos  (MPEG4, MPG supported)", "")
        menuBar.Append(fileMenu, "&File")
        parent.SetMenuBar(menuBar)
        
        # video player related
        #self.loadButton = wx.Button(self, -1, "Load File")
        self.playButton = wx.Button(self, -1, "Play")
        self.pauseButton = wx.Button(self, -1, "Pause")
        self.stopButton = wx.Button(self, -1, "Stop")
        self.exportButton = wx.Button(self, -1, "Export")
        #self.importButton = wx.Button(self, -1, "Import")
        self.previewButton = wx.Button(self, -1, "Preview")
        self.showCurPosButton = wx.Button(self, -1, "Show Pos")
        slider = wx.Slider(self, -1, 0, 0, 0, size=wx.Size(400, -1))
        self.slider = slider

        self.st_size = wx.StaticText(self, -1, size=(1,-1))
        self.st_len  = wx.StaticText(self, -1, size=(1,-1))
        self.st_pos  = wx.StaticText(self, -1, size=(1,-1))








        # matplotlib related
        self.addQuantileButton = wx.Button(self, -1, "Add quantile")
        self.addStateButton = wx.Button(self, -1, "Add State")
        self.removeQuantileButton = wx.Button(self, -1, "Remove Quantile")
        #self.removeStateButton = wx.Button(self, -1, "Remove State")
        self.interpolateButton = wx.Button(self, -1, "Inter1d")
        
        
        # 1 lower section 2 upper section 3 state 4 color
        self.textField1 = wx.TextCtrl(self)
        self.textField2 = wx.TextCtrl(self)
        self.textField3 = wx.TextCtrl(self)
        self.textField4 = wx.TextCtrl(self)
        self.textField5 = wx.TextCtrl(self)
        self.stateCheckBox = []




        self.sizer = wx.GridBagSizer(5,5)
        self.sizer.Add(self.loadButton, (3,1))
        self.sizer.Add(self.playButton, (4,1))
        self.sizer.Add(self.pauseButton, (5,1))
        self.sizer.Add(self.stopButton, (6,1))
        self.sizer.Add(self.exportButton, (7,1))
        #self.sizer.Add(self.importButton, (8,1))
        self.sizer.Add(self.previewButton, (8,1))
        self.sizer.Add(self.showCurPosButton, (9,1))
        self.sizer.Add(self.slider,(2,1),span=(1,5))
        self.sizer.Add(self.st_size, (3, 2))
        self.sizer.Add(self.st_len,  (4, 2))
        self.sizer.Add(self.st_pos,  (5, 2))
        self.sizer.Add(self.mc, (1,1),span=(1,5))  # for .avi .mpg video files

        
        
        self.sizer.Add(self.addQuantileButton,(plot_x,plot_y))
        self.sizer.Add(self.removeQuantileButton,(plot_x,plot_y+1))
        self.sizer.Add(self.addStateButton,(plot_x,plot_y+2))
        #self.sizer.Add(self.removeStateButton,(plot_x,plot_y+3))
        self.sizer.Add(self.interpolateButton, (plot_x, plot_y+3))
        
        #set size to display the video
        self.sizer.Add(wx.StaticText(self, -1, 'lower', size=(100,20)), (plot_x+1,plot_y))
        self.sizer.Add(wx.StaticText(self, -1, 'upper', size=(100,20)),(plot_x+1,plot_y+1))
        self.sizer.Add(wx.StaticText(self, -1, 'description', size=(100,20)), (plot_x+1,plot_y+2))
        self.sizer.Add(wx.StaticText(self, -1, 'color', size=(100,20)), (plot_x+1,plot_y+3))
        self.sizer.Add(wx.StaticText(self, -1, 'state', size=(100,20)), (plot_x+1,plot_y+4))
        
        self.sizer.Add(self.textField1,(plot_x+2,plot_y))
        self.sizer.Add(self.textField2,(plot_x+2,plot_y+1))
        self.sizer.Add(self.textField3,(plot_x+2,plot_y+2))
        self.sizer.Add(self.textField4,(plot_x+2,plot_y+3))
        self.sizer.Add(self.textField5,(plot_x+2,plot_y+4))
        
        self.SetSizerAndFit(self.sizer)
        self.Layout()
    def add_check_box(self, state):
        self.stateCheckBox.append(wx.CheckBox(self, -1, state))
        current = len(self.stateCheckBox) - 1
        self.sizer.Add(self.stateCheckBox[current],(plot_x+3+current/state_box_row, plot_y+current%state_box_row))
        self.Layout()



    def onClose(self, event):
        self.Destroy()


if __name__=='__main__':
    
    app = wx.App(False)
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "Video Annotation Tool", size = (1280, 720))
    # call the derived class
    MainView(frame, -1)
    frame.Show(1)
    app.MainLoop()