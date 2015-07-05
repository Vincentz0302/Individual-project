import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
from plotfunc import *
from ttk import *
import cv2
import cv2.cv as cv
from cv2 import waitKey
from PIL import Image, ImageTk
from multiprocessing import Process

import threading

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk



global thumbnail_width
global thumbnail_height
global numPreview
global jump_speed
global preview_interval
global current_label
global labels_set
# it will be nice if numPreview < 9 for grid arrangement
numPreview = 5
preview_interval = 10
thumbnail_width = 120
thumbnail_height = 90
interval = 250
labels_set=[]

'''
#
#   bug 1: synchronized problem-> double clicked the forward or backward button will not move to
#   the correct frame
#   Solution: Queue, for thread handling(also improve performance   )
#
#
#
'''

def backward_for_n_frames(root,cv_capture):
    pos = int(cap.get(cv.CV_CAP_PROP_POS_FRAMES))
    count = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
    jump_to = 0
    if pos - interval < 0:
        jump_to = 0
    else:
        jump_to = pos- (interval - 1)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)
    update_preview(root, cv_capture)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)
    update_video(root, cv_capture)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)

def forward_for_n_frames(root, cv_capture):
    lock = threading.Lock()

    
    pos = int(cap.get(cv.CV_CAP_PROP_POS_FRAMES))
    count = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
    jump_to = 0
    if pos + interval > count:
        jump_to = count
    else:
        jump_to = pos + interval + 1
    lock.acquire()
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)
    update_preview(root, cv_capture)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)
    update_video(root, cv_capture)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES, jump_to)

    lock.release()

def update_video(root, cv_capture):
    widgets = root.winfo_children()
    pos = int(cv_capture.get(cv.CV_CAP_PROP_POS_FRAMES))
    _, pil_img = frame_to_image(cv_capture)
    pil_img = pil_img.resize((thumbnail_width*5,thumbnail_height*5), Image.ANTIALIAS)
    photo=ImageTk.PhotoImage(image=pil_img)
    widgets[numPreview].config(image=photo)
    widgets[numPreview]._image_cache=photo
    widgets[numPreview+1].config(text=pos)
    root.update()

def update_preview(root, cv_capture):
    #the first numPreview widgets are preview labels
    pos = int(cv_capture.get(cv.CV_CAP_PROP_POS_FRAMES))
    count = int(cv_capture.get(cv.CV_CAP_PROP_FRAME_COUNT))
    widgets = root.winfo_children()
    for i in range(numPreview):
        c_pos = 0
        if (pos + (i-numPreview/2) * preview_interval>=0) and (pos + (i-numPreview/2) * preview_interval<=count):
            cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, pos+(i-numPreview/2)*preview_interval)
            c_pos = pos+(i-numPreview/2)*preview_interval
            retval, pil_img=frame_to_image(cv_capture)
        else:
            cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES, pos)
            c_pos = pos
            retval, pil_img=frame_to_image(cv_capture)
        pil_img = pil_img.resize((thumbnail_width,thumbnail_height), Image.ANTIALIAS)
        photo=ImageTk.PhotoImage(image=pil_img)
        widgets[i].config(image=photo, text=c_pos)
        widgets[i]._image_cache=photo
        cv_capture.set(cv.CV_CAP_PROP_POS_FRAMES,pos)
    root.update()
    cap.set(cv.CV_CAP_PROP_POS_FRAMES,pos)

def on_scale(val):
    print val
    return val

def frame_to_image(cv_capture):
    retval, frame = cv_capture.read()
    cv_image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
    pil_img = Image.fromarray(cv_image)
    if retval == False:
        return {False, None}
    return True, pil_img

def _quit():
    root.quit()
    root.destroy()


def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata,event.ydata)
    circle = plt.Circle((event.xdata,event.ydata), radius=3, fc='y')
    plt.gca().add_patch(circle)
    plt.show()
if __name__=='__main__':
    
    
    '''
    this is a testing video file which will be 
    changed in the future
    '''
    
    cap = cv2.VideoCapture("/Users/zhangyuxun/Desktop/Project Data/videos/test.mp4")
    root = Tk.Tk()
    
    '''
    intitial the main interface
    set the size of main interface to orginal window size
    '''
    root.protocol( "WM_DELETE_WINDOW", _quit )
    RWidth = root.winfo_screenwidth()
    RHeight = root.winfo_screenheight()
    root.geometry("%dx%d+0+0" %(RWidth, RHeight))
    root.title("Video Annotater")
    

    
    
    #labels for frame previewing
    i=0
    tk_imgs = []
    preview_labels = []
    pos = int(cap.get(cv.CV_CAP_PROP_POS_FRAMES))
    count = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
    for i in range(numPreview):
        c_pos = 0
        if (pos + (i-numPreview/2) * preview_interval>=0) and (pos + (i-numPreview/2) * preview_interval<=count):
            cap.set(cv.CV_CAP_PROP_POS_FRAMES, pos+(i-numPreview/2)*preview_interval)
            c_pos = pos+(i-numPreview/2)*preview_interval
            retval, pil_img=frame_to_image(cap)
        else:
            cap.set(cv.CV_CAP_PROP_POS_FRAMES, pos)
            c_pos = 0
            retval, pil_img=frame_to_image(cap)
        pil_img = pil_img.resize((thumbnail_width,thumbnail_height), Image.ANTIALIAS)
        tk_imgs.append(ImageTk.PhotoImage(image=pil_img))
        preview_labels.append(Label(root,image=tk_imgs[i]))
        label_text = "%d"%(c_pos)
        preview_labels[i].config(text=label_text,compound=Tk.TOP)
        preview_labels[i].pack()
        preview_labels[i].grid(row=numPreview+i/5,column=i%5,sticky=Tk.W)
        cap.set(cv.CV_CAP_PROP_POS_FRAMES,pos)

    root.update()
    #start from the kth frame to the (n-k)th frame
    cap.set(cv.CV_CAP_PROP_POS_FRAMES,0)

    #video player is not available right now, this is a static screen shot to fit the place of the video player
    retval, pil_img = frame_to_image(cap)
    pil_img = pil_img.resize((thumbnail_width*5,thumbnail_height*5), Image.ANTIALIAS)
    tkimg=ImageTk.PhotoImage(image=pil_img)
    cap.set(cv.CV_CAP_PROP_POS_FRAMES,0)
    label = Label(root)
    label.config(image=tkimg)
    label.pack()
    label.grid(row=0, columnspan=numPreview,rowspan=numPreview,padx=5,pady=5)

    f_label = Label(root,text="0",background="white")
    f_label.pack()
    f_label.grid(row=0, column=0,sticky=Tk.N+Tk.W,padx=10,pady=10)
    backward = Button(root, text="backward", command=lambda:backward_for_n_frames(root,cap))

    backward.pack()
    backward.grid(row=numPreview+numPreview/5+1,column=0,padx=5,sticky=Tk.W+Tk.E+Tk.N+Tk.S)

    forward=Button(root,text="forward",command=lambda:forward_for_n_frames(root,cap))
    forward.pack();
    forward.grid(row=numPreview+numPreview/5+1,column=2, sticky=Tk.W+Tk.E+Tk.N+Tk.S)


    

    # create matplotlib graph
    # intergrate matplotlib into main interface

    fig, labels= create_canvas(count, -100, 100)
    labels_set.append(labels)
    current_label = 0
    canvas = FigureCanvasTkAgg(fig, master = root)
    canvas.show()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


    canvas.get_tk_widget().grid(row = 0, column=11, padx= 10, pady=10)
    canvas.mpl_connect('button_press_event', onclick)
    root.focus_force()
    root.mainloop()  

    
