import wx
import cv2
import cv2.cv as cv
from MainView import *

import matplotlib
matplotlib.use('WXAgg')
from PlotController import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg

class ToolController():
    def __init__(self, parent, id):
        self.plotController = []
        self.current_plotController = -1
        self.mainView = MainView(parent, -1)
        self.timer = wx.Timer(self.mainView)

        fig = plt.figure(0)
        
        self.canvas = FigureCanvasWxAgg(self.mainView, -1, fig)
        fig.canvas.mpl_connect('button_press_event', self.onClick)
        #will be moved to main view
        self.mainView.sizer.Add(self.canvas, (1,6), span=(8,5))


        self.connect()
        self.timer.Start(100)
        self.fps = 1
        self.previewImage = []
    
    def connect(self):
        self.mainView.Bind(wx.EVT_BUTTON, self.onLoadFile, self.mainView.loadButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.onPlay, self.mainView.playButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.onPause, self.mainView.pauseButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.onStop, self.mainView.stopButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.showPreview, self.mainView.previewButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.show_current_position, self.mainView.showCurPosButton)
  
        self.mainView.Bind(wx.EVT_BUTTON, self.add_state, self.mainView.addStateButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.add_quantile_section, self.mainView.addQuantileButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.remove_quantile_section, self.mainView.removeQuantileButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.interpolate, self.mainView.interpolateButton)
        self.mainView.Bind(wx.EVT_BUTTON, self.exportToCSV, self.mainView.exportButton)
        self.mainView.Bind(wx.EVT_SLIDER, self.onSeek, self.mainView.slider)
        self.mainView.Bind(wx.EVT_TIMER, self.onTimer)
 


    
    def onPlay(self, evt):
        self.mainView.mc.Play()
    
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
            self.doLoadPlot()
            dlg.Destroy()




    def doLoadFile(self, path):
        if not self.mainView.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            folder, filename = os.path.split(path)
            self.cv_capture = cv2.VideoCapture(path)
            self.fps = self.cv_capture.get(cv.CV_CAP_PROP_FPS)
            self.mainView.slider.SetRange(0, self.mainView.mc.Length())


    def doLoadPlot(self):
        if self.current_plotController > -1:
            del self.plotController
            self.plotController = []
            plt.clf()
        plotController = PlotController(1, self.cv_capture.get(cv.CV_CAP_PROP_FRAME_COUNT),'')
        
        fig = plt.figure(0)
        self.current_plotController = 0
        self.plotController.append(plotController)
        #self.toolbar =Toolbar(self.canvas)
        self.plotController[0].set_visible(True)
        #self.mainView.SetSizer(self.mainView.sizer)
        self.mainView.Layout()


    def RepresentsInt(self,s):
        try:
            int(s)
            return True
        except ValueError:
            return False



    def show_current_position(self, evt):
        if self.current_plotController > -1:
            offset = self.mainView.mc.Tell()
            current_frame = int(offset*self.fps/1000)
            self.plotController[self.current_plotController].showFramePos(current_frame)

    def add_quantile_section(self, evt):
        if self.current_plotController != -1:
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
        if self.current_plotController > -1 and self.plotController[self.current_plotController].add_state(_state):
            self.mainView.add_check_box(_state)
            self.mainView.textField5.SetValue("")

    def show_landmark(self, frame, state_list):
        self.cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, frame)
        pos = (frame / self.fps) * 1000
        self.mainView.mc.Seek(pos)
        for cb in self.mainView.stateCheckBox:
            index = self.mainView.stateCheckBox.index(cb)
            if cb.GetLabel() in state_list:
                self.mainView.stateCheckBox[index].SetValue(True)
            else:
                self.mainView.stateCheckBox[index].SetValue(False)

    def add_or_show(self, current_frame, x, y, state_list):
        offset = self.plotController[self.current_plotController].plotView.nframes * 0.005
        for landmark in self.plotController[self.current_plotController].landmark_list:
            if landmark[0] > x - offset and landmark[0] < x + offset and landmark[1] > y - offset and landmark[1] < y + offset:
                #print "at frame %d"%(landmark[0])
                self.show_landmark(landmark[0], landmark[3])
                return
        self.plotController[self.current_plotController].add_landmark(current_frame, y, state_list)

    def onClick(self, evt):
        if self.current_plotController > -1 and evt.xdata and evt.ydata:
            offset = self.mainView.mc.Tell()
            self.cv_capture.set(cv.CV_CAP_PROP_POS_MSEC, offset)
            current_frame = self.cv_capture.get(cv.CV_CAP_PROP_POS_FRAMES)
            state_list = []


            if evt.button == 1:
                for cb in self.mainView.stateCheckBox:
                    if cb.GetValue():
                        state_list.append(cb.GetLabel())
            #if a landmark is clicked then show that frame
            #else add new landmark
            
                self.add_or_show(current_frame, evt.xdata, evt.ydata, state_list)
            else:
                self.plotController[self.current_plotController].remove_landmark(evt.xdata, evt.ydata)

        self.mainView.mc.SetFocus()
#print self.plotController[self.current_plotController].landmark_list


    def showPreview(self, evt):
        k = 5
        if self.current_plotController > -1:
            if self.previewImage:
                for p in self.previewImage:
                    self.previewImage.remove(p)
        
            offset = self.mainView.mc.Tell()
            k_frame = int(offset*self.fps/1000)
            if k_frame >= 2 * k:
                k_frame = k_frame - 2 * k
            for i in range(0,5):
                self.cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, k_frame)
                ret, frame = self.cv_capture.read()
                frame = cv2.resize(frame, (180, 135))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame.shape[:2]
                bmp = wx.BitmapFromBuffer(width, height, frame)
                control = wx.StaticBitmap(self.mainView, -1, bmp)
                control.SetPosition((1055, 15+135*i+10))
                self.previewImage.append(control)
                k_frame = k_frame + k
            self.cv_capture.set(cv.CV_CAP_PROP_POS_MSEC, offset)


    def interpolate(self, evt):
        self.plotController[self.current_plotController].fit_curve()


    def exportToCSV(self, evt):
        if self.current_plotController > -1:
            dlg = wx.FileDialog(self.mainView, "Save CSV file", "", "",
                                "CSV files (*.csv)|*.csv", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
            self.plotController[self.current_plotController].exportData(path, 0)


if __name__=='__main__':
    
    app = wx.App(False)
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "Video Annotation Tool", size = (1280, 720))
    # call the derived class
    m = ToolController(frame, -1)
    frame.Show(1)
    app.MainLoop()