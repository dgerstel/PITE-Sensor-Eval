#!/usr/bin/python
# -*- coding: utf-8 -*-import sys

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter as tk
import ttk 
import tkMessageBox
from PIL import Image
from PIL import ImageTk
import sys
import os
import numpy as np
import FakeData 
import Classifier
import my_eval
import glob
import time
import datetime


matplotlib.use("Tkagg")
LARGE_FONT = ("Verdana", 12)
plotTab = []
    
DIR = "../data/"
sensor_data_path = DIR+"sensorData.dat"


# allowed ranges of params and their dictionary
ks = range(2,7)
train_test_ratios = [0.1 * i for i in range(3, 9)]
weights = ['distance', 'uniform']
metrics = ['minkowski', 'euclidean']
param_vals = {'train_test_ratio' : train_test_ratios, 'weights' : weights, 'metric' : metrics}
#param_vals = {'weights' : weights}
#param_vals = {'metric' : metrics}
#param_vals = {'train_test_ratio' : train_test_ratios}

# lambda function for building dictionaries from variable names list (e.g. 'a, b, c')
# of the shape variable_name : variable_value
arg_dict = lambda l: dict((k, globals()[k]) for k in l.split(', '))


def InitKNN():
    """
    Run KNN algorithm on real and fake data and print scores to console.
    Uses all "danefake*" files as input
    """

    files = os.listdir(os.curdir+"/"+DIR) 
    files = [filename for filename in files if 'danefake' in filename]
    for filename in files:
        for param in param_vals.keys():
            ScanParamKNN(param, filename, plots=True)
    tkMessageBox.showinfo( "", "Results have been saved to logs in .../PITEml/data/log/ directory.\nTo see summary plots click Back and Plots (they are saved to .../PITEml/fig/Analyse/)")    


def ScanParamKNN(param, filename, plots=False):
    """
    Scans over allowed values of `param` and numbers of neighbours k
    Returns 2-dim array of classification accuracy based on cross-validation

    =======
    params:
    param - (str) name of a param to be analysed; it is one of param_vals.keys()
    filename - (str) log output file name
    """

    # accuracy calculated from cross-validation; prepare 2-dim numpy array
    acc_cv = np.zeros([len(param_vals[param]), len(ks)])

    # begin logging
    saveout = sys.stdout  
    fsock = open(os.curdir+'/'+DIR+ '/log/' + 'Log_for_file_'+filename[8:-3]+param+'.log', 'w')                                             
    sys.stdout = fsock 
    print "############# FILENAME #############"
    print filename
    print "####################################"
    
    print "--Parameter scanned: ", param
    # scan over values of the chosen param
    for i, pval in enumerate(param_vals[param]):
        print "----Parameter value: ", param, " = ", pval
        globals()[param] = pval  # e.g. 'metric' = 'minkowski'
        # scan over number of neighbours k
        for j, k in enumerate(ks):
            print "------Number of neighbours, k: ", k
            globals()['k'] = k  # e.g. 'k' = 2
            args = 'k, ' + param
            d = Classifier.KNN(os.curdir+"/"+DIR+filename, sensor_data_path)
            #d = FakeData.KNN(os.curdir+"/"+DIR+filename, sensor_data_path)
            d.TrainAndPredict(**arg_dict(args)) 
            print "------Accuracy obtained using cross-validation: ", d.knn_score.mean()#, " for FILE ", filename
            print "####################################\n"
            acc_cv[i][j] = d.knn_score.mean()

        if plots:
            fig, ax = plt.subplots(1, 1)
            MakePlots(acc_cv, param, ax, filename)
            fig.savefig(os.curdir + "/../fig/analyse/" + filename[8:-3] + param + "_" + str(pval) + ".png")
    print "####################################\n"
    print "\n--Parameter >>", param, "<< summary-table of accuracy (cross-validation):", acc_cv
    print "####################################\n\n"
    # end logging
    sys.stdout = saveout
    fsock.close() 

    return acc_cv

    


def MakePlots(arr, param, ax, inputFileName):
    """
    Plots accuracy (cv-calculated) versus number of neighbours;
    graphs for all values of param (e.g. 'distance') superimposed on one plot

    ======
    params:
    arr - numpy 2-dim array as from ScanParamKNN
    param - (str) name of parameter analysed
    inputFileName - name of input file; it will be added to plot title
    """

    for i, row in enumerate(arr):
        ax.plot(ks, row, 'o', label=param_vals[param][i])

    ax.autoscale_view()
    ax.set_ylim(.95 * arr.min(), 1.02)
    ax.set_xlim(.95 * ks[0], 1.05 * ks[-1])
    
    plt.legend(loc='best')
    plt.xlabel('k (number of neighbours)')
    plt.ylabel('accuracy (cross-validation)')
    plt.title('**' + param + '**' + ' scan for ' + inputFileName)
    #plt.show()


def MakeTables(arr, param):
    """
    Similar to MakePlots (same input), but provides summary tables
    """

    pass


class SeaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        """
        Initialize components of GUI, set frame's properties 
        """
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "VELO sensor quality evaluation")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (WelcomePage, StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive, PageSix, PageSeven):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            #frame.grid_rowconfigure(7, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        self.show_frame(WelcomePage)


    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize frame representing welcome page in GUI
        """
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="VELO sensor quality evaluation", font=("Helvetica", 30)).pack(pady=10, padx=10)

        img = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/VELO.jpg'))
        label1= tk.Label(self, image=img)
        label1.image = img # keep a reference!
        label1.pack() 

        ttk.Button(self, text="Start",command=lambda: controller.show_frame(StartPage)).pack()

class StartPage(tk.Frame):
     
    def printsensordata(self):
        """
        Print some parameters of real sensors
        """
        datafile = open(sensor_data_path,"r")
        sensorsdata = datafile.readlines()
        print "                 Average  RMS      Skewness  Kurtosis Mark"
        for i in range(len(sensorsdata)):
            print "Sensor number "+str(i)+": "+sensorsdata[i][0:-2]

    def evaluatesensors(self):
        """
        Print sensors evaluation to console  
        """
        from_sensors = np.loadtxt(sensor_data_path, delimiter=",")
        for i in range(len(from_sensors)):
            print "Sensor number "+str(i)+" quality: "+str(my_eval.fuzzyRating(from_sensors[i], my_eval.exp_norm))+" %"

    def __init__(self, parent, controller):
        """
        Initialize frame representing start page in GUI
        """
        tk.Frame.__init__(self, parent)
 
        ttk.Button(self, text="Run model",command=lambda: controller.show_frame(PageOne)).grid(row=0, sticky="wens")
        ttk.Button(self, text="Print sensor data to console",command=self.printsensordata).grid(row=1, sticky="wens")
        ttk.Button(self, text="Print evaluation of sensors reliability to console",command=self.evaluatesensors).grid(row=2, sticky="wens")
        ttk.Button(self, text="Average parameter histogram(real sensor data)",command=lambda: controller.show_frame(PageTwo)).grid(row=3, sticky="wens")
        ttk.Button(self, text="RMS parameter histogram(real sensor data)",command=lambda: controller.show_frame(PageThree)).grid(row=4, sticky="wens")
        ttk.Button(self, text="Skewness parameter histogram(real sensor data)",command=lambda: controller.show_frame(PageFour)).grid(row=5, sticky="wens")
        ttk.Button(self, text="Kurtosis parameter histogram(real sensor data)",command=lambda: controller.show_frame(PageFive)).grid(row=6, sticky="wens")
        ttk.Button(self, text="Plots", command=lambda: controller.show_frame(PageSeven)).grid(row=6, sticky="wens")

        img = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/VELO.jpg'))
        label1= tk.Label(self, image=img)
        label1.image = img # keep a reference!
        label1.grid(row=7, sticky="wens")


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)

        ttk.Button(self, text="Generate new fake data",command=lambda: controller.show_frame(PageSix)).grid(row=0, sticky="wens")
        ttk.Button(self, text="Start KNN on generated and real data",command=lambda: InitKNN()).grid(row=1, sticky="wens")
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage)).grid(row=2, sticky="wens")
        
        img = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/VELO.jpg'))
        label1= tk.Label(self, image=img)
        label1.image = img # keep a reference!
        label1.grid(row=3, sticky="wens")


class PageTwo(tk.Frame):
    
    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Average parameter histogram", font=LARGE_FONT).pack(pady=10, padx=10)

        ttk.Button(self, text="Back",command=lambda: controller.show_frame(StartPage)).pack()
        f = Figure(figsize=(5, 5), dpi=100)

        a = f.add_subplot(111)
        from_sensors = np.loadtxt(sensor_data_path, delimiter=",")
        average_list = [i[0] for i in from_sensors]
        a.hist(average_list, bins = 40)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class PageThree(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="RMS parameter histogram", font=LARGE_FONT).pack(pady=10, padx=10)

        ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage)).pack()

        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        from_sensors = np.loadtxt(sensor_data_path, delimiter=",")
        rms_list = [i[1] for i in from_sensors]
        a.hist(rms_list, bins = 40)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class PageFour(tk.Frame):
    
    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Skewness parameter histogram", font=LARGE_FONT).pack(pady=10, padx=10)

        ttk.Button(self, text="Back",command=lambda: controller.show_frame(StartPage)).pack()

        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        from_sensors = np.loadtxt(sensor_data_path, delimiter=",")
        skewness_list = [i[2] for i in from_sensors]
        a.hist(skewness_list, bins = 40)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class PageFive(tk.Frame):
     
    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Kurtosis parameter histogram", font=LARGE_FONT).pack(pady=10, padx=10)

        ttk.Button(self, text="Back",command=lambda: controller.show_frame(StartPage)).pack()
        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        from_sensors = np.loadtxt(sensor_data_path, delimiter=",")
        kurtosis_list = [i[3] for i in from_sensors]
        a.hist(kurtosis_list, bins = 40)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class PageSix(tk.Frame):
    def generate(self):
        """
        Generate fake data with parameters given to Entry widgets
        """
        if (self.entry1.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry2.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry3.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry4.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry5.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry6.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry7.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry8.get().lstrip('-').replace(".", "", 1).isdigit() and self.entry9.get().lstrip('-').replace(".", "", 1).isdigit()):
            min_a = float(self.entry1.get())
            max_a = float(self.entry2.get())
            min_r = float(self.entry3.get())
            max_r = float(self.entry4.get())
            min_s = float(self.entry5.get())
            max_s = float(self.entry6.get())
            min_k = float(self.entry7.get())
            max_k = float(self.entry8.get())
            samples_ = int(self.entry9.get())
            FakeData.generateFakeData(sensor_data_path, DIR+"danefake"+str(min_a)+"-"+str(max_a)+".dat", [[min_a,max_a], [min_r,max_r], [min_s,max_s], [min_k,max_k]], samples=samples_)
            tkMessageBox.showinfo( "", "Sample fake data files were generated in .../PITEml/data/ directory.")    
        else:
            tkMessageBox.showwarning('Warning', 'Incorrect data type! Type int or float digits.')	 

    
    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)

        tk.Label(self, text = "Average minimal multiplying factor").grid(row = 0, column = 0, sticky = "we")
        self.entry1 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.2"))
        self.entry1.grid(row = 0, column = 1, sticky = "we")

        tk.Label(self, text = "Average maximal multiplying factor").grid(row = 0, column = 2, sticky = "we")
        self.entry2 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.5"))
        self.entry2.grid(row = 0, column = 3, sticky = "we")

      	tk.Label(self, text = "RMS minimal multiplying factor").grid(row = 1, column = 0, sticky = "we")
        self.entry3 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.2"))
        self.entry3.grid(row = 1, column = 1, sticky = "we")

        tk.Label(self, text = "RMS maximal multiplying factor").grid(row = 1, column = 2, sticky = "we")
        self.entry4 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.5"))
        self.entry4.grid(row = 1, column = 3, sticky = "we")

        tk.Label(self, text = "Skewness minimal multiplying factor").grid(row = 2, column = 0, sticky = "we")
        self.entry5 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.2"))
        self.entry5.grid(row = 2, column = 1, sticky = "we")

        tk.Label(self, text = "Skewness maximal multiplying factor").grid(row = 2, column = 2, sticky = "we")
        self.entry6 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.5"))
        self.entry6.grid(row = 2, column = 3, sticky = "we")

      	label1 = tk.Label(self, text = "Kurtosis minimal multiplying factor")
        label1.grid(row = 3, column = 0, sticky = "we")
        self.entry7 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.2"))
        self.entry7.grid(row = 3, column = 1, sticky = "we")

        tk.Label(self, text = "Kurtosis maximal multiplying factor").grid(row = 3, column = 2, sticky = "we")
        self.entry8 = tk.Entry(self, textvariable=tk.StringVar(self, value="1.5"))
        self.entry8.grid(row = 3, column = 3, sticky = "we")

        tk.Label(self, text = "Type number of fake data samples (should be int)").grid(row = 4, column = 0,columnspan = 2, sticky = "we")
        self.entry9 = tk.Entry(self, textvariable=tk.StringVar(self, value="50"))
        self.entry9.grid(row = 4, column = 2,columnspan = 2, sticky = "we")

        ttk.Button(self, text="GENERATE", command=lambda: self.generate()).grid(row=5, columnspan = 4, sticky="wens")
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(PageOne)).grid(row=6,columnspan = 4, sticky="wens")

        img = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/VELO.jpg'))
        label1= tk.Label(self, image=img)
        label1.image = img # keep a reference!
        label1.grid(row=7, columnspan = 4, sticky="wens")

class PageSeven(tk.Frame):
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta/120), "units")

    def modification_date(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def __init__(self, parent, controller):
        """
        Initialize frame representing page in GUI
        """
        tk.Frame.__init__(self, parent)
        button1 = ttk.Button(self, text="Back",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()
        canv = tk.Canvas(self, relief=tk.SUNKEN)
        canv.config(width=800, height=600)                
        canv.config(scrollregion=(0,0,0, 13900))         
        canv.config(highlightthickness=0)                 
        canv.bind_all("<MouseWheel>", self._on_mousewheel)
        sbar = tk.Scrollbar(self)
        sbar.config(command=canv.yview)                   
        canv.config(yscrollcommand=sbar.set)              
        sbar.pack(side=tk.RIGHT, fill=tk.Y)                     
        canv.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)   
        
        
        

        self.height=360
        self.tab = []
        self.d = {}


        for file in os.listdir(os.curdir+'/../fig/analyse/'):
            if file.endswith(".png"):
                self.tab.append(file)
                
        title = time.ctime(os.path.getctime(os.curdir+"/../fig/analyse/"+file))
        
        for x in range(len(self.tab)):
            self.d["self.img"+str(x)] = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/analyse/'+self.tab[x]))

        #print(self.d)
        canv.create_text(400,30,font="Times 20 italic bold",
                        text="Created: "+ title) 

        
        for key, value in self.d.iteritems():
            
            canv.create_image(400,self.height,image=value)
            self.height= self.height+600
            
            
            
                
            

            

        

               

        
       # self.img = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/analyse/1.2-1.5.metric_euclidean.png'))

       # canv.create_image(400,300,image=self.img)


       # self.img2 = ImageTk.PhotoImage(Image.open(os.curdir+'/../fig/analyse/1.2-1.5.metric_minkowski.png'))

        #canv.create_image(400,900,image=self.img2)

        






	

	
try:
    app = SeaofBTCapp()
    app.eval('tk::PlaceWindow %s center' % app.winfo_pathname(app.winfo_id()))
    app.mainloop()
except:
    print("Bląd GUI lub ogólny błąd aplikacji")
    sys.exit()

