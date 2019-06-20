#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from tkinter import *
    from tkinter import messagebox as msgbox
    from tkinter import filedialog as fd
    from tkinter.simpledialog import askfloat, askinteger, askstring
 
except:
    from Tkinter import *
    import tkMessageBox as msgbox
    import tkFileDialog as fd
    import tkSimpleDialog as simpledialog


from freetype import *

import numpy
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

import itertools
import unicodedata
import time
import os
import glob

from math import *

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")


class GUI:
    """Main tkinter GUI Class"""
    def __init__(self, root):
        """Initiate some values and set up main window"""
        self.root = root # root is a passed Tk object
        
        #title
        self.root.title("PLT Editor")

        #set root window background colour
        self.root.configure(background="black")
        
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        #min window size
        self.root.minsize(int(self.screen_width / 2), int(self.screen_height / 2))
        #self.root.wm_state('zoomed')
        
        #set window icon
        self.wrench = \
                    """R0lGODlhIAAhAPAAAAAAAAAAACH5BAEAAAAAIf8LSW1hZ2VNYWdpY2sOZ2FtbWE9
                       MC40NTQ1NDUALAAAAAAgACEAAAJWhI+py+0PU5g0Qoptw1kzPnkfKI6dEnhgirLW
                       2rrRKp8zbXAqDb98f/mRbkKbo6gjIjXC0uHnzPGiAGjU6sSWtCLu7mns1kLUqqtS
                       NifTajJbKnvLDwUAOw=="""

        img = PhotoImage(data=self.wrench)
        self.root.tk.call('wm', 'iconphoto', root._w, img)

        # menu bar
        self.menubar = Menu(self.root)
            
        # file Menu
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new)
        filemenu.add_separator()
        filemenu.add_command(label="Open", command=self.openplt)
        filemenu.add_separator()
        filemenu.add_command(label="Save", command=self.saveplt)
        filemenu.add_command(label="Save As", command=self.saveplt_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="File", menu=filemenu)

        # edit Menu
        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Remove Duplicates", command=self.remove_dups)
        editmenu.add_separator()
        self.menubar.add_cascade(label="Edit", menu=editmenu)


    
        # change pen Menu        
        changepenmenu = Menu(self.menubar, tearoff=0)
        changepenmenu.add_command(label="Pen 1", foreground="#000000", command=lambda:self.changepen(1))
        changepenmenu.add_command(label="Pen 2", foreground="#FF0000", command=lambda:self.changepen(2))
        changepenmenu.add_command(label="Pen 3", foreground="#00FF00", command=lambda:self.changepen(3))
        changepenmenu.add_command(label="Pen 4", foreground="#0000FF", command=lambda:self.changepen(4))
        changepenmenu.add_command(label="Pen 5", foreground="#00FFFF", command=lambda:self.changepen(5))
        changepenmenu.add_command(label="Pen 6", foreground="#FF00FF", command=lambda:self.changepen(6))
        changepenmenu.add_command(label="Pen 7", foreground="#FFFF00", command=lambda:self.changepen(7))
        editmenu.add_cascade(label="Change Pen", menu=changepenmenu)

        self.font = StringVar()    
        self.changefontmenu = Menu(self.menubar, tearoff=0)
        
        files = glob.glob('./fonts/*.ttf')
        for i, f in enumerate(files):
            if i==0: self.font.set(f)
            name = f.replace('.ttf','').replace('./fonts\\','')
            self.changefontmenu.add_radiobutton(label=name, foreground="#000000", value=f, variable=self.font)
        editmenu.add_cascade(label="Change Font", menu=self.changefontmenu)
 
 

            
        # View Menu
        viewmenu = Menu(self.menubar, tearoff=0)
        viewmenu.add_command(label="Home", command=self.home)
        viewmenu.add_command(label="Visualize Plot", command=self.visualize_plot)
        self.menubar.add_cascade(label="View", menu=viewmenu)

        
        # display the menu
        self.root.config(menu=self.menubar)
        
        # bindings
        self.root.bind("<KeyPress>", self.keydown)
        self.root.bind("<KeyRelease>", self.keyup)
        self.root.bind("<ButtonPress-1>", self.click)
        self.root.bind("<ButtonRelease-1>", self.release)
        self.root.bind("<Motion>", self.motion)
  
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        
        self.canvas = Canvas(self.root, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0,column=0, sticky=N+S+E+W )
        #scroll
        self.canvas.bind("<MouseWheel>", self.scale)
        self.canvas.bind("<Button-4>", self.scale)
        self.canvas.bind("<Button-5>", self.scale)
        # Hack to make zoom work on Windows
        root.bind_all("<MouseWheel>", self.scale)
        
       
        
        self.statusbar = Frame(self.root, bg="#FFFFFF", bd=1, height=20, relief=SUNKEN)
        self.statusbar.grid(row=2, column=0, sticky=E+W+S)

        self.mouse = StringVar()
        Label(self.statusbar, textvariable=self.mouse, bg="#FFFFFF", fg="#000000", justify=LEFT, anchor=W).grid(row=0, column=0)
        self.mouse.set("")

        self.status = StringVar()
        Label(self.statusbar, textvariable=self.status, bg="#FFFFFF", fg="#000000", justify=LEFT, anchor=W).grid(row=0, column=1)
        self.status.set("Selected: 0")

        self.command = StringVar()
        Label(self.statusbar, textvariable=self.command, bg="#FFFFFF", fg="#000000", justify=LEFT, anchor=W).grid(row=0, column=2)
        self.command.set("Command: Select")

        
        self.filename = None # this will always be the filename we are working on
        self.cmd = None
        self.visualize_plot = False
        self.selection_box = None
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.scan_mark = False
        self.start = None
        self.textx = None
        self.texty = None
        self.textc = 0
        self.textxstart = None
        self.textystart = None
        self.textstart = None
        self.textscale = 0
        self.selected_points = None
        self.linex1 = None
        self.liney1 = None
        self.circle_radius = 0
        self.lastx = None
        self.lasty = None

    def rotate(self):
        #TODO
        
        for item in self.canvas.find_withtag(ALL):  # get coord list of all lines in last character
            x1, y1, x2, y2 = self.canvas.coords(item)
            bbox = self.canvas.bbox(ALL)

            angle_in_degrees = 90
            angle_in_radians = angle_in_degrees * pi / 180
            line_length = (((x2 - x1) ** (2)) + ((y2 - y1) ** (2))) ** (0.5)
            center_x = x1
            center_y = y1
            end_x = center_x + line_length * math.cos(angle_in_radians)
            end_y = center_y + line_length * math.sin(angle_in_radians)

           
            self.canvas.coords(item, new_x1, new_y1, new_x2, new_y2)
                

                
    def new(self):
        self.filename = None
        self.cmd = None
        self.visualize_plot = False
        self.selection_box = None
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.scan_mark = False
        self.start = None
        self.textx = None
        self.texty = None
        self.textc = 0
        self.textxstart = None
        self.textystart = None
        self.textstart = None
        self.textscale = 0
        self.selected_points = None
        self.linex1 = None
        self.liney1 = None
        self.circle_radius = 0
        self.command.set("Command: Select")
        self.root.winfo_toplevel().title("PLT Editor")
        self.canvas.delete(ALL)
        self.home()
        
        
    def home(self):
        ''' Resets canvas to top left 0,0 '''
        self.canvas.configure(scrollregion=[0,0,self.canvas.winfo_width(), self.canvas.winfo_height()])
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.configure(scrollregion=[])
        
        


    def reset_scrollregion(self):
        x1 = int(self.canvas.canvasx(0))
        y1 = int(self.canvas.canvasy(0))
        x2 = int(self.canvas.canvasx(self.canvas.winfo_width()))
        y2 = int(self.canvas.canvasy(self.canvas.winfo_height()))

        self.canvas.configure(scrollregion=[x1,y1,x2,y2])

        
    def changepen(self, pen):
        color = self.get_pen_color(pen)
        selected = self.canvas.find_withtag("selected")
        for item in selected:
            # change color of line
            self.canvas.itemconfig(item, fill=color)
            # change pen tag of item
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag[0:3] == "pen":
                    self.canvas.dtag(item, tag)
            self.canvas.addtag_withtag("pen"+str(pen), item)
            tags = self.canvas.gettags(item)
        
    def scale(self, event): # scale on mouse wheel
        
        def delta(event):
            if event.num == 5 or event.delta < 0:
                return -1
            return 1
        
        widget = self.root.winfo_containing(event.x_root, event.y_root)

        if widget == self.canvas and self.cmd == "circle": #change radius of circle
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            if (delta(event) > 0):
                self.circle_radius += 1
            elif (delta(event) < 0):
                self.circle_radius -= 1
            
            self.circle(x, y, self.circle_radius, 0, 360)
            
        if widget == self.canvas and self.cmd == "scale":# scale everything

            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            
            if (delta(event) > 0):
                self.canvas.scale('all', x, y, 1.1, 1.1)
            elif (delta(event) < 0):
                self.canvas.scale('all', x, y, 0.9, 0.9)


            # reset grippers to 4x4
            self.canvas.delete("gripper")
            selected = self.canvas.find_withtag("selected")
            for item in selected:
                coords = self.canvas.coords(item)
                self.status.set('Selected: ' + str(len(self.canvas.find_withtag("selected"))))
                
                self.canvas.create_rectangle(coords[0]-2,coords[1]-2,coords[0]+2,coords[1]+2, fill="#FFFF00", tags=("gripper"))
                self.canvas.create_rectangle(coords[2]-2,coords[3]-2,coords[2]+2,coords[3]+2, fill="#FFFF00", tags=("gripper"))
                
        if widget == self.canvas and self.cmd == "text":# scale text
            xx = self.canvas.coords('text-guide')[0]
            yy = self.canvas.coords('text-guide')[3]
                    
            
            if (delta(event) > 0):
                self.canvas.scale('text_input', xx, yy, 1.05, 1.05)
                self.textscale += 1
            elif (delta(event) < 0):
                self.canvas.scale('text_input', xx, yy, 0.95, 0.95)
                self.textscale -= 1


        


        
    def bbox(self, coord_list):
        x1_max =  max(map(lambda x: x[0],coord_list))
        x1_min =  min(map(lambda x: x[0],coord_list))

        y1_max =  max(map(lambda x: x[1],coord_list))
        y1_min =  min(map(lambda x: x[1],coord_list))

        x2_max =  max(map(lambda x: x[2],coord_list))
        x2_min =  min(map(lambda x: x[2],coord_list))

        y2_max =  max(map(lambda x: x[3],coord_list))
        y2_min =  min(map(lambda x: x[3],coord_list))

        
        return [min(x1_min, x2_min),  min(y1_min, y2_min), max(x1_max, x2_max),  max(y1_max, y2_max)]

    def insert_text(self, text, x, y):
        
        if self.textx == None or self.texty == None:
            self.textx = x
            self.texty = y
            self.textxstart = x
            self.textystart = y

        if text:               
            xstart = self.textx
            spacing = 5
            face = Face(self.font.get())
            face.set_char_size( 1)

            for z, c in enumerate(text):

                if ord(c) != 8: # backspace
                    self.textc += 1
            
                if ord(c) == 32 or ord(c) == 8:
                    # (back)space, load some character so we can get width for space
                    face.load_char('a')
                else:
                    face.load_char(c)

              
                slot = face.glyph

                outline = slot.outline
                points = numpy.array(outline.points, dtype=[('x',float), ('y',float)])
                x, y = points['x'], points['y']

                figure = plt.figure(figsize=(8,10))
                axis = figure.add_subplot(111)
                start, end = 0, 0

                VERTS, CODES = [], []
                # Iterate over each contour
                for i in range(len(outline.contours)):
                    end    = outline.contours[i]
                    points = outline.points[start:end+1]
                    points.append(points[0])
                    tags   = outline.tags[start:end+1]
                    tags.append(tags[0])

                    segments = [ [points[0],], ]
                    for j in range(1, len(points) ):
                        segments[-1].append(points[j])
                        if tags[j] & (1 << 0) and j < (len(points)-1):
                            segments.append( [points[j],] )
                    verts = [points[0], ]
                    codes = [Path.MOVETO,]
                    for segment in segments:
                        if len(segment) == 2:
                            verts.extend(segment[1:])
                            codes.extend([Path.LINETO])
                        elif len(segment) == 3:
                            verts.extend(segment[1:])
                            codes.extend([Path.CURVE3, Path.CURVE3])
                        else:
                            verts.append(segment[1])
                            codes.append(Path.CURVE3)
                            for i in range(1,len(segment)-2):
                                A,B = segment[i], segment[i+1]
                                C = ((A[0]+B[0])/2.0, (A[1]+B[1])/2.0)
                                verts.extend([ C, B ])
                                codes.extend([ Path.CURVE3, Path.CURVE3])
                            verts.append(segment[-1])
                            codes.append(Path.CURVE3)
                    VERTS.extend(verts)
                    CODES.extend(codes)
                    start = end+1

                    #close plt to save memory
                    plt.close('all')


                # create line coord list
                x1 = None
                y1 = None
                coord_list = []
                for e, verts in enumerate(VERTS):
                    x, y = verts

                    if CODES[e] == 1:
                        x1 = None
                        y1 = None
                    
                    if x1 != None and y1 != None:
                        coord_list.append([x1, y1, x, y])
                    x1, y1 = verts

                bbox = self.bbox(coord_list)
                height = face.size.height
                width = bbox[2] - bbox[0]

                if ord(c) != 32 and ord(c) != 8: #only do if we aren't print a space
                    for coords in coord_list:
                        x1, y1, x2, y2 = coords
                        x1 = self.textx + x1
                        y1 = self.texty + (height - y1) - height
                        x2 = self.textx + x2
                        y2 = self.texty + (height - y2) - height

                        self.canvas.create_line(x1, y1, x2, y2,  fill="#000000", tags=('plt', 'pen1', 'text', 'text_input', 'text'+str(self.textc)))
                    
                if ord(c) == 8: # backspace
                    coord_list = []
                    for item in self.canvas.find_withtag('text'+str(self.textc)):  # get coord list of all lines in last character
                        coord_list.append(self.canvas.coords(item))
                    if len(coord_list): # set to left side of last text character
                        bbox = self.bbox(coord_list)
                        x1, y1, x2, y2 = bbox
                        self.textx = x1 
                    else: # must of been a non printable character
                        coord_list = []
                        for item in self.canvas.find_withtag('text'+str(self.textc)):
                            coord_list.append(self.canvas.coords(item))
                        if len(coord_list):
                            bbox = self.bbox(coord_list)
                            x1, y1, x2, y2 = bbox
                            self.textx = x2 
                            
                        elif self.textc == 0:
                            self.textx = self.canvas.coords('text-guide')[0]
                            self.textc = 0
                            
                            
                        else:
                            self.textx -= bbox[2]

                            
                    self.canvas.delete('text'+str(self.textc)) # delete last character
                    
                    if self.textc > 0: 
                        self.textc -= 1
                else:
                    self.textx += bbox[2] + spacing

                self.root.update()
            
    def saveplt(self):
        hpgl = self.create_hpgl()
        if hpgl is None:
            msgbox.showerror("Error", "Nothing to save!")
            return None

        if self.filename == None:
            f = fd.asksaveasfile(mode='w', defaultextension=".plt",filetypes = (("PLT files","*.plt"),("all files","*.*")))
        else:
            f = open(self.filename, "w")
            
        if f is None: 
            return
        self.filename = f.name
        self.root.winfo_toplevel().title("PLT Editor [" + os.path.basename(self.filename) + "]")
        f.write(hpgl)
        f.close()

    def saveplt_as(self):
        hpgl = self.create_hpgl()

        if hpgl is None:
            msgbox.showerror("Error", "Nothing to save!")
            return None
        
        f = fd.asksaveasfile(mode='w', defaultextension=".plt",filetypes = (("PLT files","*.plt"),("all files","*.*")))
        
        if f is None: 
            return
        self.filename = f.name
        self.root.winfo_toplevel().title("PLT Editor [" + os.path.basename(self.filename) + "]")
        f.write(hpgl)
        f.close() 
    
    def openplt(self):
        # open a plt file and recreate it on canvas
        fn = fd.askopenfilename(title = "Select file",filetypes = (("PLT files","*.plt"),("all files","*.*")))
        if fn is "": 
            return
        self.filename = fn
        self.root.winfo_toplevel().title("PLT Editor [" + os.path.basename(self.filename) + "]")
        f = open(fn, "r")
        hpgl = f.read()
        f.close()

        
        # parse hpgl
        self.parsehpgl(unicode(hpgl))


    def circle(self, xcenter, ycenter, radius, start_angle, end_angle, segarc=10):
        # xcenter, ycenter = start position
        # radius = radius of circle
        # start_angle, end_angle = angles to draw arc, or complete circle
        # segarc = degrees to start new line segment
        
        try:
            xmin = float(1e10)
            xmax = float(-1e10)
            ymin = float(1e10)
            ymax = float(-1e10)
        except:
            xmin = float(0)
            xmax = float(0)
            ymin = float(0)
            ymax = float(0)
        
        # since font definition has arcs as ccw, we need some font foo
        if end_angle < start_angle:
            start_angle -= 360.0

        # approximate arc with line seg every "segarc" degrees
        segs = int((end_angle - start_angle) / segarc) + 4
        angleincr = (end_angle - start_angle) / segs
        xstart = cos(radians(start_angle)) * radius + xcenter
        ystart = sin(radians(start_angle)) * radius + ycenter
        angle = start_angle

        
        stroke_list = []
        for i in range(segs):
            angle += angleincr
            xend = cos(radians(angle)) * radius + xcenter
            yend = sin(radians(angle)) * radius + ycenter
            coords = [xstart, ystart, xend, yend]
            stroke_list += [coords]
            xmax = max(xmax, coords[0], coords[2])
            ymax = max(ymax, coords[1], coords[3])
            xstart = xend
            ystart = yend

        self.canvas.delete("circle_input")
        for coords in stroke_list:
            x1, y1, x2, y2 = coords
            self.canvas.create_line(x1, y1, x2, y2, fill="#000000", tags=("plt", "pen1", "circle_input"))
        return stroke_list
    
    def keyup(self, event):            
        if event.keysym == "Alt_L" or event.keysym == "Alt_R":
            self.alt = False
        if event.keysym == "Control_L" or event.keysym == "Control_R":
            self.ctrl = False
        if event.keysym == "Shift_L" or event.keysym == "Shift_R":
            self.shift = False


    def keydown(self, event):
        if event.keysym == "Alt_L" or event.keysym == "Alt_R":
            self.alt = True
        if event.keysym == "Control_L" or event.keysym == "Control_R":
            self.ctrl = True
        if event.keysym == "Shift_L" or event.keysym == "Shift_R":
            self.shift = True           
            
        if event.keysym == "Escape":
            
            self.command.set("Command: Select")
            self.cmd = None
            self.visualize_plot = False
            
            # reset any selected item
            selected = self.canvas.find_withtag("selected")
            for item in selected:
                pen = self.get_pen_from_tag(item)
                color = self.get_pen_color(pen)
                self.canvas.itemconfig(item, fill=color, dash=())
            self.canvas.dtag("selected", "selected")
            # remove grippers
            self.canvas.delete("gripper")
            # remove any text input
            self.canvas.delete("text_input")
            self.canvas.delete("text-guide")
            self.textx = None
            self.texty = None
            self.textxstart = None
            self.textystart = None
            self.textstart = None
            self.linex1 = None
            self.liney1 = None
            self.canvas.delete("input_line")
            self.canvas.delete("circle_input")
                               
            # clear status
            self.status.set("Selected: 0")

        if self.cmd == 'circle':
            if event.keysym == "Return":
                self.canvas.dtag('circle_input', 'circle_input')
                self.cmd = None
                self.circle_radius = 0
                self.command.set("Command: Select")
                
                                 
                
        if self.cmd == 'text':
            if event.keysym == "Return":
                self.canvas.delete("text-guide")
                self.canvas.dtag("text_input", "text_input")
                self.command.set("Command: Select")
                self.cmd = None
                self.textx = None
                self.texty = None
                self.textxstart = None
                self.textystart = None
                self.textstart = None
                while self.textc > 0:
                    self.canvas.dtag('text'+str(self.textc), 'text'+str(self.textc))
                    self.textc -= 1                    
                
            elif event.keysym == "Insert" and self.shift:
                text = self.root.clipboard_get()
           
                if len(text):
                    self.insert_text(text, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
                    
            else:
                self.insert_text(event.char, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
                
            return
        
        if event.keysym == "Home":
            self.home()
            
        if event.keysym == "s" or event.keysym == "S":
            self.command.set("Command: Scale")
            self.cmd = "scale"

        if event.keysym == "m" or event.keysym == "M":

            self.command.set("Command: Move")
            self.cmd = "move"            
            
        if event.keysym == "h" or event.keysym == "H":
            self.command.set("Command: Pan")
            self.cmd = "pan"
            self.canvas.configure(scrollregion=[])

        if event.keysym == "l" or event.keysym == "L":
            self.command.set("Command: Line")
            self.cmd = "line"

            self.canvas.delete('text-guide')
            self.canvas.delete('circle_input')
            self.canvas.delete('input_line')
            self.linex1 = None
            self.liney1 = None

        if event.keysym == "c" or event.keysym == "C":
            self.circle_radius = 10
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.circle(x, y, self.circle_radius, 0, 360)
            self.command.set("Command: Circle")
            self.cmd = "circle"

            self.canvas.delete('text-guide')
            self.canvas.delete('circle_input')
            self.canvas.delete('input_line')
            self.linex1 = None
            self.liney1 = None
            
        if event.keysym == "t" or event.keysym == "T":
            self.textstart = event
            self.command.set("Command: Text")
            self.cmd = "text"
            # add guides to show text path
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            self.canvas.delete('text-guide')
            self.canvas.delete('circle_input')
            self.canvas.delete('input_line')
            self.linex1 = None
            self.liney1 = None

            xoffset = self.canvas.canvasx(self.canvas.winfo_width())  -x
            yoffset = self.canvas.canvasy(self.canvas.winfo_height()) -y

            self.canvas.create_line(x,self.canvas.canvasy(0),x,y,fill="red", dash=(1,1), tags=('text-guide'))
            self.canvas.create_line(x,y,x+(xoffset),y,fill="red", dash=(1,1), tags=('text-guide'))

        if event.keysym == "Delete":
            self.canvas.delete("selected")
            self.canvas.delete("gripper")
            self.status.set("Selected: 0")
            
            
        if event.keysym == 'Up': # up
            self.canvas.yview_scroll(-1, "units")
        if event.keysym == 'Down': # down
            self.canvas.yview_scroll(+1, "units")
        if event.keysym == 'Left': # left
            self.canvas.xview_scroll(-1, "units")
        if event.keysym == 'Right': #right
            self.canvas.xview_scroll(+1, "units")

    def motion(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        c = []
        lines = self.canvas.find_withtag('plt')
        if len(lines):
            for i, item in enumerate(lines): 
                coords = self.canvas.coords(item)
                c.append([coords[0], coords[1], coords[2], coords[3]])
                    
            if self.ctrl == False:
                closest = self.closest_snap(c, x, y)

                if closest[2] <= 5:
                
                    x = closest[1][0]
                    y = closest[1][1]

        if event.widget == self.canvas:
            self.mouse.set("x:"+str(round(x,1))+" y:"+str(round(y,1)))
        else:
            self.mouse.set("")
            
            
        if self.cmd == 'text':
            # add guides to show text path
                
            self.canvas.delete('text-guide')

            xoffset = self.canvas.canvasx(self.canvas.winfo_width())  -x
            yoffset = self.canvas.canvasy(self.canvas.winfo_height()) -y

            self.canvas.create_line(x,self.canvas.canvasy(0),x,y,fill="red", dash=(1,1), tags=('text-guide'))
            self.canvas.create_line(x,y,x+(xoffset),y,fill="red", dash=(1,1), tags=('text-guide'))

            # move any text already drawn
            diffX, diffY = (event.x - self.textstart.x), (event.y - self.textstart.y)
            self.canvas.move("text_input", diffX, diffY)
            self.textstart = event
            if self.textx and self.texty:
                self.textx += diffX
                self.texty += diffY
            
        

        if self.selection_box is not None:
            self.canvas.delete("selection_box")
            self.canvas.create_rectangle(self.selection_box[0], self.selection_box[1], x, y, fill="blue", stipple="gray12", tags=('selection_box'))

        if self.cmd == "move" and event.widget == self.canvas:
            if self.lastx != None and self.lasty != None:
                self.canvas.move("selected", x - self.lastx, y - self.lasty)
                self.canvas.move("gripper", x - self.lastx, y - self.lasty)
                self.lastx = event.x
                self.lasty = event.y
        
        if self.cmd == "pan" and self.scan_mark == True:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        if self.cmd == "line":
            if self.linex1 != None and self.liney1 != None:
                self.canvas.delete("input_line")                    
                self.canvas.create_line(self.linex1, self.liney1, x, y, fill="red", tags=("plt","input_line"))
                
        if self.cmd == "circle":
            
            self.circle(x, y, self.circle_radius, 0, 360)
            
        if self.selected_points is not None:            
            for point in self.selected_points:
                line = point[0]
                position = point[1]
                gripper = point[2]

                
                line_coords = self.canvas.coords(line)

                x1, y1, x2, y2 = line_coords

             
                if position == 1:
                    anchorx = x2
                    anchory = y2
                else: # acnhor is at other end
                    anchorx = x1
                    anchory = y1
                
                c = []
                lines = self.canvas.find_withtag('plt')
                for i, item in enumerate(lines): # get list of coords, except for selected items attached to gripper
                    for d in self.selected_points:
                        if d[0] == item:
                            continue
                    coords = self.canvas.coords(item)
                    c.append([coords[0], coords[1], coords[2], coords[3]])
                        
                if self.ctrl == False:
                    closest = self.closest_snap(c, x, y)
        

                    if closest[2] <= 5:
                        
                
                        movex = closest[1][0]
                        movey = closest[1][1]

                        if position == 1:
                            self.canvas.coords(line, movex, movey, anchorx, anchory)
                            self.canvas.coords(gripper, closest[1][0]-2, closest[1][1]-2, closest[1][0]+2, closest[1][1]+2)
                        else:
                            self.canvas.coords(line,anchorx, anchory,  movex, movey)
                            self.canvas.coords(gripper, closest[1][0]-2, closest[1][1]-2, closest[1][0]+2, closest[1][1]+2)
                    else:
                        movex = x
                        movey = y
                            
                        if position == 1:
                            self.canvas.coords(line, movex, movey, anchorx, anchory)
                            self.canvas.coords(gripper, x-2, y-2, x+2, y+2)
                        else:
                            self.canvas.coords(line, anchorx, anchory, movex, movey)
                            self.canvas.coords(gripper, x-2, y-2, x+2, y+2)           

                else:
                    movex = x
                    movey = y
                        
                    if position == 1:
                        self.canvas.coords(line, movex, movey, anchorx, anchory)
                        self.canvas.coords(gripper, x-2, y-2, x+2, y+2)
                    else:
                        self.canvas.coords(line, anchorx, anchory, movex, movey)
                        self.canvas.coords(gripper, x-2, y-2, x+2, y+2)                
                        
                
    def closest_snap(self, coord_list, x, y):
        closest = None
        closest_index = None
        closest_data = None
        closest_side = None
        # check x1, y1
        for i, coords in enumerate(coord_list):
            x1, y1, x2, y2 = coords
            d = (((x - x1) ** (2)) + ((y - y1) ** (2))) ** (0.5)
            if d < closest or closest == None:
                closest = d
                closest_index = i
                closest_data = [x1, y1]
                closest_side = 1
                
        # check x2, y2
        for i, coords in enumerate(coord_list):
            x1, y1, x2, y2 = coords
            d = (((x - x2) ** (2)) + ((y - y2) ** (2))) ** (0.5)
            if d < closest or closest == None:
                closest = d
                closest_index = i
                closest_data = [x2, y2]
                closest_side = 2
                
        return [closest_index, closest_data, closest, closest_side]
        
    def release(self, event):
        self.scan_mark = False
        self.selected_points = None
        
        self.lastx = None #used for move function
        self.lasty = None
                
        if self.selection_box is not None:
            x1 = self.selection_box[0]
            y1 = self.selection_box[1]
            x2 = self.canvas.canvasx(event.x)
            y2 = self.canvas.canvasy(event.y)
            self.canvas.delete("selection_box")
            self.selection_box = None
            items = self.canvas.find_overlapping(x1, y1, x2, y2)
            for item in items:
                self.root.update()
                if "plt" in self.canvas.gettags(item):
                    self.canvas.itemconfig(item, dash=(4, 4))
                    self.canvas.addtag_withtag("selected", item)
                    coords = self.canvas.coords(item)
                    # check we aren't duplicating grippers for multi select
                    grippers = self.canvas.find_withtag('gripper')
                    for grip in grippers:
                        c = self.canvas.coords(grip)
                        if c == [coords[0]-2,coords[1]-2,coords[0]+2,coords[1]+2] or c == [coords[2]-2,coords[3]-2,coords[2]+2,coords[3]+2]:
                            self.canvas.delete(grip)
                                    
                    self.canvas.create_rectangle(coords[0]-2,coords[1]-2,coords[0]+2,coords[1]+2, fill="#FFFF00", tags=("gripper"))
                    self.canvas.create_rectangle(coords[2]-2,coords[3]-2,coords[2]+2,coords[3]+2, fill="#FFFF00", tags=("gripper"))


            self.status.set('Selected: ' + str(len(self.canvas.find_withtag("selected"))))
        
    def click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)


        c = []
        lines = self.canvas.find_withtag('plt')
        if len(lines):
            for i, item in enumerate(lines): # get list of coords, except for selected items attached to gripper
                coords = self.canvas.coords(item)
                c.append([coords[0], coords[1], coords[2], coords[3]])
                    
            if self.ctrl == False:
                closest = self.closest_snap(c, x, y)

                if closest[2] <= 5:
                        
                    x = closest[1][0]
                    y = closest[1][1]

        if self.cmd == "move":
            if self.lastx == None and self.lasty == None:
                self.lastx = event.x
                self.lasty = event.y
            else:
                self.lastx = None
                self.lasty = None
            
        if self.cmd == "line":
                    if self.linex1 == None and self.liney1 == None:
                        self.linex1 = x
                        self.liney1 = y
                    else:
                        self.canvas.delete("input_line")
                        self.canvas.create_line(self.linex1, self.liney1, x, y, fill="#000000", tags=("plt", "pen1"))
                        self.linex1 = x
                        self.liney1 = y
                        
        elif event.widget == self.canvas:
            if len(self.canvas.gettags(CURRENT)):
                if self.cmd == None:
                    # if item is a gripper
                    if "gripper" in self.canvas.gettags(CURRENT):
                        
                        gbbox = self.canvas.bbox(CURRENT)
                        lines = self.canvas.find_withtag('selected')

                        selected_points = []
                        for line in lines:
                            lcoords = self.canvas.coords(line)
                            if gbbox[0] <= lcoords[0] and lcoords[0] <= gbbox[2] and gbbox[1] <= lcoords[1] and lcoords[1] <= gbbox[3]:
                                selected_points.append([line, 1, CURRENT])
                            elif gbbox[0] <= lcoords[2] and lcoords[2] <= gbbox[2] and gbbox[1] <= lcoords[3] and lcoords[3] <= gbbox[3]:
                                selected_points.append([line, 2, CURRENT])

                        self.selected_points = selected_points


                    else :
                        if self.ctrl == False:
                            # change color back to pen color
                            selected = self.canvas.find_withtag("selected")
                            for item in selected:
                                pen = self.get_pen_from_tag(item)
                                color = self.get_pen_color(pen)
                                self.canvas.itemconfig(item, fill=color, dash=())

                            # remove selected tag and grippers
                            self.canvas.dtag("selected", "selected")
                            self.canvas.delete("gripper")
                            
                        self.canvas.itemconfig(CURRENT, dash=(4,4))
                        self.canvas.addtag_withtag("selected", CURRENT)
                        
                        t = self.canvas.type(CURRENT)
                        if t == "line":
                            # add grippers
                            coords = self.canvas.coords(CURRENT)
                            self.status.set('Selected: ' + str(len(self.canvas.find_withtag("selected"))))
                            # check we aren't duplicating grippers for multi select
                            grippers = self.canvas.find_withtag('gripper')
                            for grip in grippers:
                                c = self.canvas.coords(grip)
                                if c == [coords[0]-2,coords[1]-2,coords[0]+2,coords[1]+2] or c == [coords[2]-2,coords[3]-2,coords[2]+2,coords[3]+2]:
                                    self.canvas.delete(grip)
                            self.canvas.create_rectangle(coords[0]-2,coords[1]-2,coords[0]+2,coords[1]+2, fill="#FFFF00", tags=("gripper"))
                            self.canvas.create_rectangle(coords[2]-2,coords[3]-2,coords[2]+2,coords[3]+2, fill="#FFFF00", tags=("gripper"))

            else:
                
                if self.cmd == "pan":
                    # scroll / drag canvas
                    self.canvas.scan_mark(event.x, event.y)
                    self.scan_mark = True
                    
                    
                elif self.cmd == None: # start selection box
                    if self.ctrl == False:
                        # reset any selected item
                        selected = self.canvas.find_withtag("selected")
                        for item in selected:
                            pen = self.get_pen_from_tag(item)
                            color = self.get_pen_color(pen)
                            self.canvas.itemconfig(item, fill=color, dash=())
                        self.canvas.dtag("selected", "selected")
                        # remove grippers
                        self.canvas.delete("gripper")
                        # clear status
                        self.status.set("Selected: 0")
                    
                    self.selection_box = [x, y]
                
    def parsehpgl(self, hpgl, tag='plt'):
        #remove garbage from file
        hpgl = remove_control_characters(hpgl)

        # TODO: find better way to deal with this, is this standard?
        hpgl = hpgl.replace('PDPA', 'PD')
        hpgl = hpgl.replace('PUPA', 'PU')
        hpgl = hpgl.replace('PA', 'PU')
        
        #create list of commands seperated by terminator
        commands = hpgl.split(';')
        
        # clear canavas
        self.canvas.delete("all")

        # initialize variables
        pen_position = 0
        pen_up = 0
        pen_down = 1
        x = 0
        y = 0
        xo = 0
        yo = 0
        
        for i, cmd in enumerate(commands):

            try:
                if len(cmd) > 1:
                    c = cmd[:2] # two letter command
                    p = iter(cmd[2:].replace(' ', ',').split(','))
                    if c == 'SP': # set pen
                        try:
                            pen = int(list(p)[0])
                        except:
                            pen = 0
                            
                    if c == 'PU': # pen up
                        pen_position = pen_up
                        for coords in p:
                            xo = float(coords)
                            yo = self.canvas.winfo_height() - float(next(p))
                            
                    if c == 'PD': # pen down
                        pen_position = pen_down
                        for coords in p:
                            x = float(coords)
                            y = self.canvas.winfo_height() - float(next(p))
                            color = self.get_pen_color(pen)
                            line = self.canvas.create_line(x, y-50, xo, yo-50, fill=color, tags=(tag, 'pen'+str(pen)))
                            
                            xo = x
                            yo = y
                        
            except ValueError:
                pass
                   
            
        bbox = self.canvas.bbox(ALL)
        self.canvas.move(ALL, 0-bbox[0], 0-bbox[1])

    def get_pen_from_color(self, color):
        if color == "#FFFFFF": # white
            return 0
        elif color == "#000000": # black
            return 1
        elif color == "#FF0000": # red
            return 2
        elif color == "#00FF00": # green
            return 3
        elif color == "#0000FF": # blue
            return 4
        elif color == "#00FFFF": # cyan
            return 5
        elif color == "#FF00FF": # magenta
            return 6
        elif color == "#FFFF00": # yellow
            return 7
        else: 
            return 0

    def get_pen_color(self, pen):
        if pen == 0: # white
            return "#FFFFFF"
        elif pen == 1: # black
            return "#000000"
        elif pen == 2: # red
            return "#FF0000"
        elif pen == 3: # green
            return "#00FF00"
        elif pen == 4: # blue
            return "#0000FF"
        elif pen == 5: # cyan
            return "#00FFFF"
        elif pen == 6: # magenta
            return "#FF00FF"
        elif pen == 7: # yellow
            return "#FFFF00"
        else: 
            return "#FFFFFF"
        
    def get_pen_from_tag(self, item):
        tags = self.canvas.gettags(item)
        if 'pen1' in tags:
            return 1
        if 'pen2' in tags:
            return 2
        if 'pen3' in tags:
            return 3
        if 'pen4' in tags:
            return 4
        if 'pen5' in tags:
            return 5
        if 'pen6' in tags:
            return 6
        if 'pen7' in tags:
            return 7
        else:
            return 0
        
    def get_pen(self, color):
        if color == "#FFFFFF":
            return 0
        elif color == "#000000":
            return 1
        elif color == "#FF0000":
            return 2
        elif color == "#00FF00":
            return 3
        elif color == "#0000FF":
            return 4
        elif color == "#00FFFF":
            return 5
        elif color == "#FF00FF":
            return 6
        elif color == "#FFFF00":
            return 7
        else:
            return 0

    def find_closest(self, coord_list, x, y):
        closest = None
        closest_index = None
        # check x1, y1
        for i, coords in enumerate(coord_list):
            x1, y1, x2, y2, color = coords
            d = (((x - x1) ** (2)) + ((y - y1) ** (2))) ** (0.5)
            if d <= closest or closest == None:
                closest = d
                closest_index = i
                closest_data = [x1, y1, x2, y2, color]
        # check x2, y2
        for i, coords in enumerate(coord_list):
            x1, y1, x2, y2, color = coords
            d = (((x - x2) ** (2)) + ((y - y2) ** (2))) ** (0.5)
            if d <= closest or closest == None:
                closest = d
                closest_index = i
                closest_data = [x2, y2, x1, y1, color]
                
        return [closest_index, closest_data]
        
    def opt(self, coord_list):
        o = []
        o.append(coord_list[0])
        coord_list.pop(0)
        while len(coord_list):
            closest = self.find_closest(coord_list, o[-1][2], o[-1][3])
            closest_index = closest[0]
            closest_data = closest[1]
            o.append(closest_data)
            coord_list.pop(closest_index)

        return o

    def visualize_plot(self):
        old_command = self.command.get()
        self.command.set("Command: Visualizing plot (ESC to cancel)")
        self.visualize_plot = True
        # reset any selected item
        selected = self.canvas.find_withtag("selected")
        for item in selected:
            pen = self.get_pen_from_tag(item)
            color = self.get_pen_color(pen)
            self.canvas.itemconfig(item, fill=color, dash=())
        self.canvas.dtag("selected", "selected")
        # remove grippers
        self.canvas.delete("gripper")
        
        
        items = self.canvas.find_all()

        if len(items) == 0: # if nothing to plot, return nothing
            return None

        # height needed to flip image because of (0,0) being top left instead of bottom left
        bbox = self.canvas.bbox(ALL)
        height = bbox[2] - bbox[0]

         #create a list of lines
        c = []
        for i, item in enumerate(items):
            t = self.canvas.type(item)
            if t == "line":
                color = self.canvas.itemcget(item, "fill")
                coords = self.canvas.coords(item)
                c.append([round(coords[0],2), round(height - coords[1],2),round(coords[2],2), round(height - coords[3],2), color])

        # remove duplicates
        c = self.remove_duplicates(c)

        # optimize plotter path
        c = self.opt(c)
        
        self.canvas.scan_mark(0,0)
        
        for i, coords in enumerate(c):
            if self.visualize_plot == False:
                continue
            x1, y1, x2, y2, color = coords

            self.canvas.scan_dragto((-int((x1) / 10)) + ((self.canvas.winfo_width() / 2)/ 10), -int((height - y1) / 10) + ((self.canvas.winfo_height() / 2)/ 10))
            self.canvas.update_idletasks()
            
            if i > 0:
                r = 4
                if c[i-1][2] != x1 and height - c[i-1][3] != height -y1:
                    self.canvas.create_line(c[i-1][2],height - c[i-1][3],x1,height -y1, fill="red", tags=('visualize_plot'))
                    root.update() # check if app needs updates to prevent hangs
                    time.sleep(.01)

                self.canvas.create_oval(x1-r, height - y1 -r, x1+r, height - y1+r, fill="blue", outline="#DDD", width=1, tags=('visualize_plot'))
                self.canvas.create_line(x1, height -y1, x2, height -y2, fill="#00ccFF", tags=('visualize_plot'))                    
                self.canvas.create_oval(x2-r, height - y2 -r, x2+r, height - y2+r, fill="blue", outline="#DDD", width=1, tags=('visualize_plot'))
                root.update()# check if app needs updates to prevent hangs
                time.sleep(.04)
                                        
        self.canvas.delete("visualize_plot")
        self.home()
        self.command.set(old_command)
        

    def remove_duplicates(self, coord_list):
        return [coord_list[i] for i in range(len(coord_list)) if i == 0 or coord_list[i] != coord_list[i-1]]
    
    def remove_dups(self):

        items = self.canvas.find_all()
        
        bbox = self.canvas.bbox(ALL)
        height = bbox[2] - bbox[0] 

         #create a list of lines
        c = []
        for i, item in enumerate(items):
            t = self.canvas.type(item)
            if t == "line":                    
                x1, y1, x2, y2 = self.canvas.coords(item)
                c.append([round(x1, 2), round(height - y1, 2),round(x2, 2), round(height - y2, 2)])

        s = c # create list to sort perserving index
        for i, item in enumerate(c):
           s[i] = sorted(item)

        cleanlist = []
        gooditems = []
        for i, item in enumerate(s):
            if item not in cleanlist:
                cleanlist.append(item)
                gooditems.append(items[i])

        for i, item in enumerate(items):
            if item not in gooditems:
                self.canvas.delete(item)

    def create_hpgl(self):        
        # reset any selected item
        selected = self.canvas.find_withtag("selected")
        for item in selected:
            pen = self.get_pen_from_tag(item)
            color = self.get_pen_color(pen)
            self.canvas.itemconfig(item, fill=color, dash=())
        self.canvas.dtag("selected", "selected")
        # remove grippers
        self.canvas.delete("gripper")
        
        
        items = self.canvas.find_all()

        if len(items) == 0: # if nothing to plot, return nothing
            return None

        # height needed to flip image because of (0,0) being top left instead of bottom left
        bbox = self.canvas.bbox(ALL)
        height = bbox[2] - bbox[0] 

        #create a list of lines
        c = []
        for i, item in enumerate(items):
            t = self.canvas.type(item)
            if t == "line":                    
                color = self.canvas.itemcget(item, "fill")
                coords = self.canvas.coords(item)
                c.append([round(coords[0],2), round(height - coords[1],2),round(coords[2],2), round(height - coords[3],2), color])

        # remove duplicates
        c = self.remove_duplicates(c)

        # optimize plotter path
        c = self.opt(c)

        #create hpgl
        # first item
        # set pen
        color = c[0][4]
        coords = [c[0][0],c[0][1],c[0][2],c[0][3]]
        hpgl = 'SP'+str(self.get_pen(color))+';\n'
        hpgl += 'PU' + str(round(c[0][0],2)) + ' ' + str(round(c[0][1],2)) + ';\n'
        hpgl += 'PD' + str(round(c[0][0],2)) + ' ' + str(round(c[0][1],2)) + ';\n'
        hpgl += 'PD' + str(round(c[0][2],2)) + ' ' + str(round(c[0][3],2)) + ';\n'
        c.pop(0)

        for i, x in enumerate(c):
            
            # change pen?
            last_color = color
            color = x[4]
            if color != last_color:
                hpgl += 'SP'+str(self.get_pen(color))+';\n'

            last_coords = coords
            coords = [x[0],x[1],x[2],x[3]]
            if last_coords[2] == coords[0] and last_coords[3] == coords[1]:
                hpgl += 'PD' + str(round(coords[2],2)) + ' ' + str(round(coords[3],2)) + ';\n'
                
            else:
                hpgl += 'PU' + str(round(coords[0],2)) + ' ' + str(round(coords[1],2)) + ';\n'
                hpgl += 'PD' + str(round(coords[0],2)) + ' ' + str(round(coords[1],2)) + ';\n'
                hpgl += 'PD' + str(round(coords[2],2)) + ' ' + str(round(coords[3],2)) + ';\n'

        return hpgl
  
   
root = Tk()
window = GUI(root)
root.mainloop()
