import wx
import cv2
import cv2.cv as cv
from MainView import *

import matplotlib
matplotlib.use('WXAgg')
from PlotController import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

class ToolController():
    def __init__(self, parent, id):
        self.plotController = []
        self.current_plotController = 0
        self.loadFlag = False
        self.mainView = MainView(parent, -1)
        self.timer = wx.Timer(self.mainView)
        self.currentVolume = 5
        self.toolbar = []

        fig1 = plt.figure(1, figsize=(16, 4.3), dpi = 80)
        fig2 = plt.figure(2, figsize=(16, 4.3), dpi = 80)
        self.valence_canvas = FigureCanvasWxAgg(self.mainView.valencePanel, -1, fig1)
        self.arousal_canvas = FigureCanvasWxAgg(self.mainView.arousalPanel, -1, fig2)
        fig1.canvas.mpl_connect('button_press_event', self.onClick)
        fig2.canvas.mpl_connect('button_press_event', self.onClick)
        #will be moved to main view
        #self.mainView.sizer.Add(self.canvas, (1,6), span=(8,5))
        # self.mainView.valencePanel.Fit()
        # self.mainView.arousalPanel.Fit()

        
        
        self.connect(parent)
        self.timer.Start(100)
        self.fps = 1
        self.previewImage = []
    
    def connect(self, parent):
        
        #binding the menu bar item
        parent.Bind(wx.EVT_MENU, self.onLoadFile, self.mainView.loadButton)
        parent.Bind(wx.EVT_MENU, self.exportToCSV, self.mainView.exportButton)
        parent.Bind(wx.EVT_MENU, self.importFromCSV, self.mainView.importButton)
        parent.Bind(wx.EVT_MENU, self.importConfigData, self.mainView.importConfigButton)
        parent.Bind(wx.EVT_MENU, self.exportConfigData, self.mainView.exportConfigButton)
        
        
        
        self.mainView.Bind(wx.EVT_BUTTON, self.onPlay, self.mainView.playButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.onStop, self.mainView.stopButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.showPreview, self.mainView.previewButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.show_current_position, self.mainView.showCurPosButton)
  
        self.mainView.Bind(wx.EVT_BUTTON, self.add_state, self.mainView.addStateButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.add_quantile_section, self.mainView.addQuantileButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.remove_quantile_section, self.mainView.removeQuantileButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.interpolate, self.mainView.interpolateButton)
        
        self.mainView.Bind(wx.EVT_SLIDER, self.onSeek, self.mainView.slider)
        self.mainView.Bind(wx.EVT_SLIDER, self.setVolume, self.mainView.volumeSlider)
        self.mainView.Bind(wx.EVT_TIMER, self.onTimer)

        self.mainView.Bind(wx.EVT_CLOSE, self.on_close)
        self.mainView.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.plotChanged)
    
        self.mainView.Bind(wx.EVT_CHECKBOX, self.setAudioOff)
    
    def setAudioOff(self, evt):
        if self.mainView.audioOff.GetValue():
            self.mainView.volumeSlider.SetValue(0)
            self.mainView.mc.SetVolume(0)
        else:
            print self.currentVolume
            self.mainView.volumeSlider.SetValue(self.currentVolume)
            self.mainView.mc.SetVolume(self.currentVolume)
    def setVolume(self, evt):
        volume = self.mainView.volumeSlider.GetValue()
        self.mainView.mc.SetVolume(volume)
        self.currentVolume = volume
        if volume == 0:
            self.mainView.audioOff.SetValue(True)
        else:
            self.mainView.audioOff.SetValue(False)

    def onPlay(self, evt):
        state = self.mainView.mc.GetState()
        #the video is in pause or stop state
        if state == 0 or state == 1:
            self.mainView.mc.Play()
            self.mainView.playButton.SetLabel("Pause")
        else:
            self.mainView.mc.Pause()
            self.mainView.playButton.SetLabel("Play")
            
    def onPause(self, evt):
        self.mainView.mc.Pause()
    def onStop(self, evt):
        self.mainView.mc.Stop()
    def onSeek(self, evt):
        offset = self.mainView.slider.GetValue()
        self.mainView.mc.Seek(offset)
    
    def onTimer(self, evt):
        offset = self.mainView.mc.Tell()
        self.mainView.slider.SetValue(offset)
        self.mainView.st_size.SetLabel('size: %s ms' % self.mainView.mc.Length())
        self.mainView.st_len.SetLabel('( %d seconds )' % (self.mainView.mc.Length()/1000))
        self.mainView.st_pos.SetLabel('position: %d frame' % (int(offset*self.fps/1000)))

    def onLoadFile(self, evt):
        dlg = wx.FileDialog(self.mainView, message="Choose a media file",
                        defaultDir=os.getcwd(), defaultFile="",
                        style=wx.OPEN | wx.CHANGE_DIR )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.doLoadFile(path)
            dlg.Destroy()




    def doLoadFile(self, path):
        if not self.mainView.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            folder, filename = os.path.split(path)
            self.cv_capture = cv2.VideoCapture(path)
            self.fps = self.cv_capture.get(cv.CV_CAP_PROP_FPS)
            self.mainView.slider.SetRange(0, self.mainView.mc.Length())
    
            self.mainView.volumeSlider.SetRange(0, 100)
            self.mainView.mc.SetVolume(self.currentVolume)
            self.mainView.volumeSlider.SetValue(self.currentVolume)
    
    
            self.doLoadPlot()


    def doLoadPlot(self):
        if self.loadFlag:
            del self.plotController
            self.plotController = []
            fig1 = plt.figure(1)
            fig2 = plt.figure(2)
            fig1.clf()
            fig2.clf()
        valence_plotController = PlotController(1, self.cv_capture.get(cv.CV_CAP_PROP_FRAME_COUNT),'')
        arousal_plotController = PlotController(2, self.cv_capture.get(cv.CV_CAP_PROP_FRAME_COUNT),'')
        #fig1 = plt.figure(0)
        self.current_plotController = 0
        self.loadFlag = True
        self.plotController.append(valence_plotController)
        self.plotController.append(arousal_plotController)
        #self.toolbar =Toolbar(self.canvas)
        #self.mainView.SetSizer(self.mainView.sizer)
        self.mainView.Layout()


    def RepresentsInt(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False



    def show_current_position(self, evt):
        if self.loadFlag:
            offset = self.mainView.mc.Tell()
            current_frame = offset*self.fps/1000
            self.plotController[self.current_plotController].showFramePos(current_frame)

    def add_quantile_section(self, evt):
        if self.loadFlag:
            raw_lower = self.mainView.textField1.GetValue().strip()
            raw_upper = self.mainView.textField2.GetValue().strip()
            raw_level = self.mainView.textField3.GetValue().strip()
            raw_color = self.mainView.textField4.GetValue().strip()

            if self.RepresentsInt(raw_lower) and self.RepresentsInt(raw_upper):
                raw_lower = int(raw_lower)
                raw_upper = int(raw_upper)
                if raw_lower < raw_upper and raw_lower >= -100 and raw_upper <= 100 and raw_color in ['blue', 'yellow', 'green', 'purple', 'red'] :
                    self.plotController[self.current_plotController].add_quantile_section(int(raw_lower),int(raw_upper), raw_level, raw_color)
            self.mainView.textField1.SetValue("")
            self.mainView.textField2.SetValue("")
            self.mainView.textField3.SetValue("")
            self.mainView.textField4.SetValue("")

    def remove_quantile_section(self,evt):
        p = self.mainView.textField1.GetValue().strip()
        if self.RepresentsInt(p):
            p = int(p)
            self.plotController[self.current_plotController].remove_quantile_section(p)
        self.mainView.textField1.SetValue("")




    def add_state(self, evt):
        _state = self.mainView.textField5.GetValue().strip()
        #there is a plot in UI, and successfully add state
        if self.loadFlag:
            if self.plotController[self.current_plotController].add_state(_state):
                self.mainView.add_check_box(_state)
                self.mainView.textField5.SetValue("")

    def show_landmark(self, current_frame, state_list):
        self.cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, current_frame)
        pos = self.cv_capture.get(cv.CV_CAP_PROP_POS_MSEC)
        self.mainView.mc.Seek(pos)
        for cb in self.mainView.stateCheckBox:
            index = self.mainView.stateCheckBox.index(cb)
            if cb.GetLabel() in state_list:
                self.mainView.stateCheckBox[index].SetValue(True)
            else:
                self.mainView.stateCheckBox[index].SetValue(False)


    def onClick(self, evt):
        print "Click"
        #self.current_plotController = self.mainView.plot_notebook.GetSelection()
        if self.loadFlag and evt.xdata and evt.ydata:
            pos = self.mainView.mc.Tell()
            self.cv_capture.set(cv.CV_CAP_PROP_POS_MSEC, pos)
            current_frame = self.cv_capture.get(cv.CV_CAP_PROP_POS_FRAMES)
            state_list = []
            audioflag = self.mainView.audioOff.GetValue()
            offset = self.cv_capture.get(cv.CV_CAP_PROP_FRAME_COUNT) * 0.002
            temp_landmark = []
            
            for landmark in self.plotController[self.current_plotController].landmark_list:
                if landmark[0] > evt.xdata - offset and landmark[0] < evt.xdata + offset and landmark[1] > evt.ydata - offset and landmark[1] < evt.ydata + offset:
                    temp_landmark = landmark
                    #print "landmark clicked!!"
                    #print landmark
                    break
            #if left click
            if evt.button == 1:
                for cb in self.mainView.stateCheckBox:
                    if cb.GetValue():
                        state_list.append(cb.GetLabel())
                #no landmark is clicked
                if not temp_landmark:
                    self.plotController[self.current_plotController].add_landmark(current_frame, evt.ydata, audioflag, state_list)
                else:
                    self.show_landmark(temp_landmark[0], temp_landmark[4])
            #if right click
            else:
                if temp_landmark:
                    self.plotController[self.current_plotController].remove_landmark(landmark)


#print self.plotController[self.current_plotController].landmark_list


    def showPreview(self, evt):
        k = 5
        if self.loadFlag:
            if self.previewImage:
                for p in self.previewImage:
                    self.previewImage.remove(p)
        
            offset = self.mainView.mc.Tell()
            k_frame = offset*self.fps/1000
            if k_frame >= 2 * k:
                k_frame = k_frame - 2 * k
            for i in range(0,5):
                self.cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, k_frame)
                ret, frame = self.cv_capture.read()
                frame = cv2.resize(frame, (144, 108))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame.shape[:2]
                bmp = wx.BitmapFromBuffer(width, height, frame)
                control = wx.StaticBitmap(self.mainView.infoPanel, -1, bmp)
                control.SetPosition((5+(144+10) * i, 100))
                self.previewImage.append(control)
                k_frame = k_frame + k
            self.cv_capture.set(cv.CV_CAP_PROP_POS_MSEC, offset)


    def interpolate(self, evt):
        self.plotController[self.current_plotController].fit_curve()


    def exportToCSV(self, evt):
        if self.loadFlag:
            dlg = wx.FileDialog(self.mainView, "Save CSV file", "", "",
                                "CSV files (*.csv)|*.csv", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            self.plotController[self.current_plotController].exportData(path, 0)
            dlg.Destroy()
            
    def exportConfigData(self, evt):
        if self.loadFlag:
            dlg = wx.FileDialog(self.mainView, "Save config file", "", "",
                                "CSV files (*.csv)|*.csv", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            self.plotController[self.current_plotController].exportConfigData(path)
            dlg.Destroy()


    def importFromCSV(self, evt):
        if self.loadFlag:
            dlg = wx.FileDialog(self.mainView, message="Choose a csv file",
                            defaultDir=os.getcwd(), defaultFile="",
                            style=wx.OPEN | wx.CHANGE_DIR )
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.plotController[self.current_plotController].importData(path)
                dlg.Destroy()


    def importConfigData(self, evt):
        if self.loadFlag:
            dlg = wx.FileDialog(self.mainView, message="Choose a configuration csv file",
                                defaultDir=os.getcwd(), defaultFile="",
                                style=wx.OPEN | wx.CHANGE_DIR )
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.plotController[self.current_plotController].importConfigData(path)
                dlg.Destroy()


    def plotChanged(self, event):
        self.current_plotController = self.mainView.plot_notebook.GetSelection()
        event.Skip()



    def on_close(self, evt):
        evt.skip()
        print "True"
        exit()

if __name__=='__main__':
    
    app = wx.App(False)
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "Video Annotation Tool", size = (1280, 750))
    # call the derived class
    m = ToolController(frame, -1)
    frame.Show(1)
    app.MainLoop()