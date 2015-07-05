import matplotlib.pyplot as plt
import matplotlib.collections as collections
import numpy as np
from operator import itemgetter
from PlotView import *
import csv
global kind
kind = 'cubic'

class PlotController:

    def __init__(self,_id,_nframes,_desc=None, _lower = -100, _upper = 100):
        self.plotView = PlotView(_id, _nframes, _desc, _lower, _upper)
        self.quantile_section = []
        self.landmark_list=[]
        self.state = []

    def add_landmark(self, x,y, state=[]):
        flag = False
        #if landmark is in a quantile section
        #use the level from that quantile section for this landmark
        #otherwise set the level to None
        qs_index = -1
        for qs in self.quantile_section:
            if y >=qs[0] and y < qs[1]:
                qs_index = self.quantile_section.index(qs)
        for landmark in self.landmark_list:
            if landmark[0] == x:
                index = self.landmark_list.index(landmark)
                self.landmark_list[index][1] = round(y,2)
                self.landmark_list[index][3] = state
                flag = True
                break
        if flag:
            #landmark already exist so we update the whole plot since
            #the score of the landmark is changed
            self.update()
        else:
            #the landmark is newly added so just draw the landmark

            self.landmark_list.append([int(x), round(y, 2), qs_index, state])
            self.plotView.draw_landmark(int(x),y)

                
    def add_quantile_section(self,lower, upper, desc='', color='yellow'):
        self.quantile_section.append([lower, upper, desc, color])
        self.plotView.draw_quantile_section(lower, upper, desc, color)
        for landmark in self.landmark_list:
            if landmark[1] >= lower and landmark[1] < upper:
                index = self.landmark_list.index(landmark)
                self.landmark_list[index][2]= len(self.quantile_section) - 1

    def add_state(self, _state):
        if _state not in self.state:
            self.state.append(_state)
            return True
        return False

    # at least for point should be in the array
    def fit_curve(self):
        if len(self.landmark_list) >= 4:
            self.update()
            self.plotView.draw_curve(self.landmark_list, kind)

    def remove_landmark(self, x, y):
        offset = self.plotView.nframes * 0.005
        for landmark in self.landmark_list:
            if landmark[0] > x - offset and landmark[0] < x + offset and landmark[1] > y - offset and landmark[1] < y + offset:
                self.landmark_list.remove(landmark)
        self.update()

    
    def remove_quantile_section(self, p):
        for qs in self.quantile_section:
            if p >= qs[0] and p <=qs[1]:
                self.quantile_section.remove(qs)
        self.update()


    def set_visible(self, value):
        self.plotView.set_visible(value)

    def set_nframes(self, _nframes):
        self.plotView.nframes = _nframes
        self.update()
    
    def update(self):
        self.plotView.draw(self.quantile_section, self.landmark_list)
    


    def showFramePos(self, current_frame):
        self.update()
        self.plotView.draw_line(current_frame, 100, current_frame, -100)
    def setPlotSize(self, width, height):
        pass
    
    
    # currrently we only export as CSV file
    # 0 = CSV
    def exportData(self, path, type = 0):
        with open(path, 'wb') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                        quoting=csv.QUOTE_MINIMAL)
            length = len(self.quantile_section)
            filewriter.writerow([length])
            for i in self.quantile_section:
                row = []
                for k in range(0,4):
                    row.append(i[k])
                filewriter.writerow(row)
            filewriter.writerow(self.state)
            for i in self.landmark_list:
                row = []
                for k in range(0,3):
                    row.append(i[k])
                for k in i[3]:
                    row.append(k)
                filewriter.writerow(row)


if __name__ == '__main__':


    pc1 = PlotController(1,200, 'Happy')
    pc1.add_quantile_section(50,80,'pos', 'yellow')
    pc1.add_quantile_section(-50,50,'regular', 'blue')
    pc1.set_visible(True)
    pc1.add_quantile_section(80,100,'very pos','green')
    pc1.showFramePos(40)
    pc1.showFramePos(80)
    fig = plt.figure(0)
    fig.canvas.draw()
    pc2 = PlotController(2, 500, 'Arousal')
    plt.show()

