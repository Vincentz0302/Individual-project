import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import matplotlib.collections as collections
import numpy as np
from matplotlib.widgets import Button
from matplotlib.lines import Line2D

class PlotView:
    
    def __init__(self, _id,_nframes,_desc=None, _lower = -100, _upper = 100):
        #_id is the unique id of the video
        self.id = _id
        self.nframes = _nframes
        self.desc = _desc
        self.lower= _lower
        self.upper = _upper
        fig = plt.figure(0)

        #each plot view constructs an axes for figure 0
        self.axes = fig.add_axes([.1,.1,.8,.8], label='videos id: %d'%(_id))
        self.draw_axis()
        
        self.set_visible(False)
    




    
    def remove_quantile_section(self, lower, upper):
        plt.cla()
    
    def set_visible(self,value):
        self.axes.set_visible(value)

    def set_axis_size(self, width, height):
        pass

    def draw_landmark(self, x, y):
        self.axes.plot(x, y, 'or')
        fig = plt.figure(0)
        fig.canvas.draw()



    def draw_axis(self):
        self.axes.set_xlim([0, self.nframes])
        self.axes.set_ylim([self.lower,self.upper])
        self.axes.set_title(self.desc)
        plt.axhline(0, color='black')
        
        plt.yticks(np.linspace(-100,100,21))
        
        
        fig = plt.figure(0)
        fig.canvas.draw()
    
    def draw_quantile_section(self, lower, upper, level='', color='yellow'):
        xrange = [(0, self.nframes)]
        #yrange = ymin, ywidth
        yrange = (lower, upper-lower)
        
        c = collections.BrokenBarHCollection(xrange, yrange, facecolor=color, alpha = 0.1)
        self.axes.text(self.nframes/2, lower,level, fontsize=15, ha='center', alpha = 0.2)
        self.axes.add_collection(c)
        fig = plt.figure(0)
        fig.canvas.draw()

    def draw_line(self, x1, y1, x2, y2):
        l =  Line2D([x1,x1],[y1,y2], linestyle='--',color = 'black')
        self.axes.add_line(l)
        fig = plt.figure(0)
        fig.canvas.draw()
            
    def draw_curve(self, landmark_list = [], _kind = 'cubic'):
        x = []
        y = []
        for landmark in landmark_list:
            x.append(landmark[0])
            y.append(landmark[1])
        f = interp1d(x, y, kind = _kind)
        
        xnew = np.linspace(min(x), max(x), max(x))
        self.axes.plot(xnew,f(xnew),'-')
        fig = plt.figure(0)
        fig.canvas.draw()
    
            
    def draw(self, quantile_section=[], landmark=[]):
        plt.cla()
        self.draw_axis()
        #draw quantile sections
        for qs in quantile_section:
            self.draw_quantile_section(qs[0], qs[1], qs[2], qs[3])
        #draw landmark
        for la in landmark:
            self.draw_landmark(la[0], la[1])

    def close(self):
        plt.close('all')


if __name__ == '__main__':
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 9
    plt.rcParams["figure.figsize"] = fig_size
    view1 = PlotView(1,2339, 'Happy')
    view2 = PlotView(2,2339,'Arousal')
    view2.set_visible(True)
    view2.draw_quantile_section(50,80,'pos', 'yellow')
    l = [[1,3],[8,22],[33,10],[40, 8],[59,12]]

    view2.draw_curve(l, 'cubic')
    plt.show()
    view2.draw_quantile_section(-50,50,'regular', 'blue')
    view2.draw_quantile_section(80,100,'very pos','green')
    view2.draw_landmark(100,50)





    #view2.remove_quantile_section(50,80)