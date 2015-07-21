import sys
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

    def add_landmark(self, current_frame, y, audioflag = True, state=[], ):
        
        flag = False
        #if landmark is in a quantile section
        #use the level from that quantile section for this landmark
        #otherwise set the level to None
        qs_index = -1
        for qs in self.quantile_section:
            if y >=qs[0] and y < qs[1]:
                qs_index = self.quantile_section.index(qs)
        for landmark in self.landmark_list:
            if abs(landmark[0] - current_frame)<1:
                index = self.landmark_list.index(landmark)
                self.landmark_list[index][0] = current_frame
                self.landmark_list[index][1] = round(y,2)
                self.landmark_list[index][4] = state
                flag = True
                break
        if flag:
            #landmark already exist so we update the whole plot since
            #the score of the landmark is changed
            self.update()
        else:
            #the landmark is newly added so just draw the landmark

            self.landmark_list.append([current_frame, round(y, 2), qs_index, audioflag, state])
            self.plotView.draw_landmark(current_frame,round(y, 2))
            
                
    def add_quantile_section(self,lower, upper, desc='', color='yellow'):
        self.quantile_section.append([lower, upper, desc, color])
        self.plotView.draw_quantile_section(lower, upper, desc, color)
        #print "update the quantile section"
        for landmark in self.landmark_list:
            #   print landmark
            if landmark[1] >= lower and landmark[1] < upper:
                index = self.landmark_list.index(landmark)
                self.landmark_list[index][2]= len(self.quantile_section) - 1
            #    print "is in the bag"

    def add_state(self, _state):
        if _state not in self.state:
            self.state.append(_state)
            return True
        return False

    # at least for point should be in the array
    def fit_curve(self):
        if len(self.landmark_list) >= 4:
            #self.update()
            self.plotView.draw_curve(self.landmark_list, kind)

    def remove_landmark(self, landmark):

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
        self.plotView.update()


    def showFramePos(self, current_frame):
        plt.cla()
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
                print i
                row = []
                for k in range(0,4):
                    row.append(i[k])
                for k in i[4]:
                    row.append(k)
                filewriter.writerow(row)

    def exportConfigData(self, path):
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


    def importConfigData(self, path):

        with open(path, 'rb') as csvfile:
            filereader = csv.reader(csvfile)

            content = []
            for row in filereader:
                content.append(row)
            try:
                length = int(content[0][0])
                origin_qs = self.quantile_section
                origin_states = self.state
                
                temp_quantile_section = []
                
                self.quantile_section = []
                self.state = []
                for i in range(1, length+1):
                    temp_quantile_section.append([int(content[i][0]), int(content[i][1]), content[i][2], content[i][3]])
                self.quantile_section = temp_quantile_section
                print "Finish loading quantile sections"
                # if the states are not null
                if content[length+1]:
                    for state in content[length+1]:
                        self.add_state(state)
                print "Finish loading states"
                self.update()
            except:
                #roll back if fail to read
                self.quantile_section = origin_qs
                self.state = origin_states
                self.update()


    def importData(self, path, type = 0):
        with open(path, 'rb') as csvfile:
            filereader = csv.reader(csvfile)
            content = []
            for row in filereader:
                content.append(row)
            try:
                length = int(content[0][0])
                temp_quantile_section = []
                temp_state = []
                temp_landmark = []
                for i in range(1, length+1):
                    temp_quantile_section.append([int(content[i][0]), int(content[i][1]), content[i][2], content[i][3]])
                print "Finish loading quantile sections"
                # if the states are not null
                if content[length+1]:
                    for state in content[length+1]:
                        temp_state.append(state)
                print "Finish loading states"
                for i in range(length+2, len(content)):
                    # states exists
                    if len(content[i]) == 5:
                        temp_landmark.append([float(content[i][0]), float(content[i][1]), int(content[i][2]), bool(content[i][3]), content[i][4]])
                    # no states
                    else:
                        temp_landmark.append([float(content[i][0]), float(content[i][1]), int(content[i][2]), bool(content[i][3]), []])
                            
                            
                print "Finish loading landmarks"
            except:
                    print "Error in reading this file"
                    return
            #print temp_landmark
            self.landmark_list = temp_landmark
            self.quantile_section = temp_quantile_section
            self.state = temp_state
            self.update()
                                         
                                         
if __name__ == '__main__':


    pc1 = PlotController(1,2000, 'Happy')
    pc1.add_quantile_section(50,80,'pos', 'yellow')
    pc1.add_quantile_section(-50,50,'regular', 'blue')
    pc1.set_visible(True)
    pc1.add_quantile_section(80,100,'very pos','green')
    pc1.showFramePos(40)
    pc1.showFramePos(80)
    #pc2 = PlotController(2, 500, 'Arousal')
    pc1.importData("/Users/zhangyuxun/Desktop/Project Data/python/valence.csv")
    plt.show()

