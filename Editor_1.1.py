#Developer environment; builds an app out of entry widgets

#Changelog: Made scrolling more stable

import tkinter

class Master:
    
    def __init__(self):
        self.root = tkinter.Tk() #Creates the window that code will be entered into
        self.scrollframe = tkinter.Frame(self.root) #Creates a frame into which a scrollbar will be entered
        self.scrollbar = tkinter.Scrollbar(self.scrollframe,command=self.scroll) #Creates a scrollbar
        self.scrollbar.pack(fill='y',expand=True)
        self.scrollframe.pack(side='right',fill='y')
        #self.old_scroll_point = 0
        
        self.entry_frame = tkinter.Frame(self.root) #For entry widgets to be added
        self.entry_frame.pack(side='left')
        
        self.first_shelf = Shelf(self,self) #Creates a so-called 'shelf' object, which controls entry frames
        
        self.child = Shape(self,self,self.first_shelf) #Creates a so-called 'Shape' object, representing code statements
        
        self.top_of_block = self.child #top_of_block points to the first shape in a selected block
        self.first_shelf.set_companion(self.top_of_block) #Allows the first shelf to communicate with the first shape
        self.bottom_of_block = self.top_of_block #bottom_of_block points to the last shape in a selected block
        
        self.final = Terminal_Shape(self.bottom_of_block,self) #'Shapes' are tracked in a linked list; Terminal shapes 
                                                            #are the end of the list
        self.bottom_of_block.child = self.final #A 'child' of a shape comes immediately after that shape
        self.building_selection = False #When true, allows the user to create a selection
        self.seed_shelf = self.first_shelf #Controls to and from which shape a selection will be made
        self.toolkit = Toolpanel(self) #Provides buttons to add functionality
        self.selection_deletion_handle = lambda s: None #Accessed by shelves
        self.history = [] #History hasn't been implemented yet
        self.text = "START" #Used in debugging
        #self.root.after_idle(update_history)
        self.root.mainloop() 
        
        
    def got_click(self,shelf,y): #Modifies top_of_block and bottom_of_block; changes colors of widgets if necessary
        if self.building_selection:
            if y > self.seed_shelf.box.winfo_rooty(): #if the shelf clicked is below the previous shelf
                self.bottom_of_block = shelf.companion
            else:
                self.top_of_block = shelf.companion
            self.top_of_block.companion.paint_cascade('cyan',self.bottom_of_block.companion) #Paints new selection cyan
            self.building_selection = False
            self.selection_deletion_handle = lambda s: self.selection_deletion(s) #Allows selection to be deleted
        else:
            self.seed_shelf = shelf
            self.top_of_block.companion.paint_cascade('white',self.bottom_of_block.companion) #Paints previous selection white
            self.top_of_block = shelf.companion 
            self.bottom_of_block = shelf.companion
            self.selection_deletion_handle = lambda s: None 
            
            #Determines if moving selections in either direction is possible
        if self.top_of_block.parent == self: 
            self.toolkit.moveup.config(state= 'disabled')
        else:
            self.toolkit.moveup.config(state= 'normal')
            
        if self.bottom_of_block.companion.final:
            self.toolkit.movedown.config(state= 'disabled')
        else:
            self.toolkit.movedown.config(state= 'normal')
            
        
            
        
    def select_primer(self): #Allows got_click to create a multi-shape selection
        if not(self.building_selection):
            self.top_of_block.companion.paint_cascade('white',self.bottom_of_block.companion)
            self.building_selection = True
            self.seed_shelf.box.config(bg='cyan')
    
    def bump_up(self): #Moves selection up
        archived_shape = self.top_of_block.parent
        archived_shape.companion.box.config(bg='cyan')
        self.bottom_of_block.companion.box.config(bg = 'white')
        self.top_of_block.parent = archived_shape.parent
        archived_shape.parent.child = self.top_of_block
        self.bottom_of_block.set_child(archived_shape)
        self.top_of_block.companion = archived_shape.companion
        self.top_of_block.companion.contents.set(self.top_of_block.text)
        self.top_of_block.companion.companion = self.top_of_block
        self.top_of_block.child.order_update_cascade(self.top_of_block.companion)
        self.root.update_idletasks()
        
        self.toolkit.movedown.config(state='normal')
        if self.top_of_block.parent == self:
            self.toolkit.moveup.config(state= 'disabled')
        else:
            self.toolkit.moveup.config(state= 'normal')
        
        
        self.seed_shelf = self.seed_shelf.parent
            
    def bump_down(self): #moves selection down
        archived_shape = self.bottom_of_block.child
        archived_shape.companion.box.config(bg='cyan')
        self.top_of_block.companion.box.config(bg = 'white')
        self.top_of_block.parent.child = archived_shape
        archived_shape.parent = self.top_of_block.parent
        self.bottom_of_block.child = archived_shape.child
        archived_shape.child.parent = self.bottom_of_block
        archived_shape.child = self.top_of_block
        self.top_of_block.parent = archived_shape
        archived_shape.companion = self.top_of_block.companion
        archived_shape.companion.contents.set(archived_shape.text)
        archived_shape.companion.companion = archived_shape
        self.top_of_block.order_update_cascade(self.top_of_block.companion)
        self.root.update_idletasks()
        
        self.toolkit.moveup.config(state= 'normal')
        if self.bottom_of_block.companion.final:
            self.toolkit.movedown.config(state= 'disabled')
        else:
            self.toolkit.movedown.config(state= 'normal')
            
        self.seed_shelf = self.seed_shelf.child
        
    def selection_deletion(self,shelf): #Deletes selection
        shelf.box.config(bg='white')
        if shelf.companion == self.top_of_block:
            self.top_of_block = self.top_of_block.child
        else:
            self.bottom_of_block = self.bottom_of_block.parent
            self.top_of_block.companion.box.focus_set()
        self.bottom_of_block.child.parent = self.top_of_block.parent
        self.top_of_block.parent.child = self.bottom_of_block.child
        if self.top_of_block.parent != self:
            self.bottom_of_block.child.order_update_cascade\
                    (self.top_of_block.parent.companion)
        else:
            self.bottom_of_block.child.companion = self.first_shelf
            self.first_shelf.set_companion(self.bottom_of_block.child)
            self.child.child.order_update_cascade(self.first_shelf)
        if self.top_of_block.parent != self:
            archived_shelf = self.top_of_block.parent.companion
        else:
            archived_shelf = self.first_shelf
        self.top_of_block = self.child
        self.bottom_of_block = self.final.parent
        self.got_click(archived_shelf,\
                    archived_shelf.box.winfo_rooty())
    
    #def update_history(self):
        #self.history.append(History(
    
    def undo(self): #Sets project to a previous saved state
        shape_pointer = self.history[-1].parent.child
        i = 0
        while shape_pointer != self.history[-1].child:
            if i != len(self.history[-1].text_tuple):
                shape_pointer.text = self.history[-1].text_tuple[i]
                shape_pointer = shape_pointer.child
                i+=1
            else:
                shape_pointer.companion.contents.set("")
                shape_pointer.update()
        shape_pointer = shape_pointer.parent
        while i != len(self.history[-1].text_tuple):
            shape_pointer.new_shape()
            shape_pointer = shape_pointer.child
            shape_pointer.text = history[-1].text_tuple[i]
            i+=1
            
    def save_file(self): #Saves project to file
        try:
            working_file = open('working_file.py','w') #Currently, the save/load file is hardcoded.  
            self.child.save_file(working_file)
        except:
            print("Error saving")
            try:
                working_file.close()
            except:
                pass
                
                
    def load_file(self): #Loads a previously saved file
        self.top_of_block = self.child
        self.bottom_of_block = self.final.parent
        self.selection_deletion(self.top_of_block.companion)
        file_open = True
        try:
            working_file = open('working_file.py','r')
        except:
            print("error loading file")
            file_open = False
            try:
                working_file.close()
            except:
                pass
        i = 1
        for line in working_file: #Generates shapes
            self.top_of_block.companion.contents.set(line[:-1]+" ") #Loads line from file into new shape
            self.top_of_block.new_shape() #Creates a new shape to add information to
            self.top_of_block = self.top_of_block.child 
            #print(line,self.first_shelf.final)
            i+=1
        self.bottom_of_block = self.top_of_block
        
        if file_open:
            working_file.close()
            
            
    def scroll(self,jstring,string_fraction,jarg=None): #Allows user to scroll through project
        if  not(self.first_shelf.final and self.first_shelf.companion == self.child):
            self.key = False
            if jarg == 1: #jarg indicates which arrow button, if any, on the scrollbar was pressed
                string_fraction = '.9'
            elif jarg == -1:
                string_fraction = '0'
            
            fraction = float(string_fraction) #Converts the string argument into a floating point number
            fraction=fraction/.9
            
            back = self.child.from_shelf(self.first_shelf) #How many shapes are above the companion of the first shelf
            master_height = self.root.winfo_height()-50
            last_visible,remaining = self.first_shelf.tally_1(master_height,False)  #How many shapes are below the companion
                                                                                    #of the last shelf on screen
            
            move_to = int(fraction*(back+remaining+1)) #How many shapes should be above the companion of the first shelf
            if move_to > back: #Determines if the app should scroll up or down
                while move_to > back and remaining > 0 and self.first_shelf.companion.child != self.final:
                    self.first_shelf.set_companion(self.first_shelf.companion.child) #The first shelf takes the child
                                              #of its companion as its companion
                    back+=1 #Exits loop if back exceeds move_to
                    remaining -=1 #Exits loop if remaining becomes zero
            else:
                while move_to < back and self.first_shelf.companion.parent != self:
                    self.first_shelf.set_companion(self.first_shelf.companion.parent) #The first shelf takes the parent
                                              #of its companion as its companion
                    back-=1#Exits loop if move_to exceeds back
                    
            self.first_shelf.companion.companion = self.first_shelf #Creates mutual companionship between 
                          #the first shelf and its current companion
            self.first_shelf.companion.child.order_update_cascade(self.first_shelf) #Updates the app
            self.scrollbar.set(fraction*.9,fraction*.9+.05) #Sets the scrollbar to where the user moved it to
            

class Shape: #Control code statements
    def __init__(self,parent,master,companion):
        self.parent = parent #The line of code above this one
        self.master = master #The window onto which this will be displayed
        self.companion = companion #The entry widget displaying this line of code
        self.text = "" #The statement itself
        
    def new_shape(self): #Places a new line of code beneath this one
        self.update() #Sets text to value in entry widget
        self.set_child(Shape(self,self.master,self.companion))
        self.child.order_update_cascade(self.companion)
        self.child.companion.box.focus_set()
        #if self.child.companion.final:
            #self.master.scroll('filler','1')
        
    def order_update_cascade(self,shelf): #Used if shape objects have been moved
        if shelf.order_test(self): #Decides if line should be displayed at the current location on screen
            self.companion = shelf.child #Communicates with the child of the widget that was taken as an argument
            self.companion.contents.set(self.text) #Gives the companion shelf the shape's held value
            self.child.order_update_cascade(self.companion) #Updates child
            
                
    def update(self): #Communicates with companion shelf
        #self.master.history.append(History(self.parent,self.child))
        self.text = self.companion.contents.get() #Sets text value to the value entered into the companion widget
        if self.text == "" and self.parent != self.master: #Deletes shape if companion widget is blank
            self.child.parent = self.parent
            self.parent.child = self.child
            self.child.order_update_cascade(self.parent.companion)
        
                
    def set_child(self,child): #Places shape argument beneath self in project
        child.child = self.child
        self.child.parent = child
        self.child = child
        child.parent = self
        
    def save_file(self,file): #Saves text value into file argument
        file.write(self.text+"\n")
        self.child.save_file(file)
        
    def from_shelf(self,shelf): #Determines how many generations this shape is from the companion of the shelf argument
        if shelf.companion == self:
            return 0
        else:
            return self.child.from_shelf(shelf) + 1
    

class Shelf: #Controls widgets on screen
    def __init__(self,parent,master):
        self.parent = parent #The widget above this one
        self.master = master #The owner of the window onto which this widget will be placed
        self.frame = tkinter.Frame(master.entry_frame) #A frame for the widget
        self.contents = tkinter.StringVar() #Contains the value entered into the widget
        self.box = tkinter.Entry(self.frame,width = 100,textvariable = self.contents) #The widget itself
        self.box.pack()
        self.frame.pack()
        self.box.bind("<Button-1>",lambda e: master.got_click(self,e.widget.winfo_rooty())) #Informs master that the widget was clicked
        self.box.bind("<Double-Button-1>",lambda e: master.select_primer()) #Allows user to make a selection if widget was double-clicked
        self.box.bind("<BackSpace>", lambda e: master.selection_deletion_handle(self)) #Allows user to delete a selection
        self.final = True #Is the last shelf to be created
        
    def order_test(self,shape): #Determines if child shelf is paired to the correct shape; returns False if so
        if self.final:
            self.final = False
            self.child = Shelf(self,self.master)
            self.child.set_companion(shape)
            return True
        elif self.child.companion == shape:
            return False
        else:
            self.child.set_companion(shape)
            return True
    
    def pass_child(self,shape): #Returns the widget below this one; creates widget if none exists
        if self.final:
            self.child = Shelf(self,self.master)
            self.final = False
        self.child.set_companion(shape)
        return self.child
        
    def set_companion(self,shape): #Communicates with a shape, sets additional event bindings
        self.companion = shape
        self.contents.set(self.companion.text)
        self.box.bind("<Return>",lambda e: self.companion.new_shape()) #Creates a new shape if 'enter' key is pressed
        self.box.bind("<FocusOut>",lambda e: self.companion.update()) #Updates companion if keyboard focus is lost
        
    def paint_cascade(self,color,shelf): #Changes widget color, allows child to do the same, if appropriate
        self.box.config(bg = color)
        if self != shelf and not(self.final): #Cascade continues, if the stopping point given as an argument hasn't been reached
                                                #or if no widget exists below this one
            self.child.paint_cascade(color, shelf)
            
    def truncate(self): #Destroys this widget and all beneath it
        self.box.destroy()
        self.frame.destroy()
        if not(self.final):
            self.child.truncate()
            
    def tally_1(self,y,downstream): #Determines how many generations this shelf is from the last shelf visible
        if self.final:
            return self,0
        elif self.frame.winfo_y() > y or (self.frame.winfo_y() == 0 and downstream):
            return self,self.child.tally_2()
        else:
            last_visible,remaining = self.child.tally_1(y,True)
            return last_visible,remaining

    def tally_2(self): #Determines how many generations this shelf is from the last in the app
        if self.final:
            return 1
        else:
            return self.child.tally_2()+1

class Terminal_Shape: #The end point in the linked list of shapes
    def __init__(self,parent,master):
        self.master = master
        self.parent = parent
        self.text = "END" #Used in debugging
        
    def order_update_cascade(self,shelf):
        if not(shelf.final): #Determines if any widgets are beneath the one given as argument
            self.parent.companion.final = True #Informs argument widget that it is on the bottom of the screen
            self.parent.companion.child.truncate() #Destroys all widgets beneath the argument
                
    def update(self):
        pass
        
    def paint_cascade(self):
        pass
        
    def save_file(self,file): #Closes file
        file.close()


            
class Toolpanel: #Controls a window with buttons
    def __init__(self,master):
        self.win = tkinter.Toplevel() #Creates buttons
        self.master = master #Master widget
        
        self.moveup = tkinter.Button(self.win,text = "↑",state='disabled',command = master.bump_up) #Moves selection up
        self.movedown = tkinter.Button(self.win,text = "↓",state='disabled',command = master.bump_down) #Moves selection down
        self.select = tkinter.Button(self.win,text = "Select",command = master.select_primer) #Allows user to make a selection
        self.make_save = tkinter.Button(self.win,text = "Save",command = master.save_file) #Allows user to save project
        self.load = tkinter.Button(self.win,text = "Load",command = master.load_file) #Allows user to load previous project
        self.addtab = tkinter.Button(self.win,text = "→",state='disabled')#,command = )   Adds indentation; yet to be implemented
        self.tabback = tkinter.Button(self.win,text = "←",state='disabled')#,command = )   Removes indentation; yet to be implemented
        
        self.moveup.grid(row = 0)
        self.movedown.grid(row = 1)
        self.addtab.grid(column = 1, row = 0)
        self.tabback.grid(column = 1, row = 1)
        self.select.grid(row = 2,column = 0,columnspan = 2)
        self.make_save.grid(row = 3,column = 0,columnspan = 2)
        self.load.grid(row = 4,column = 0,columnspan = 2)
        

class History: #Yet to be implemented; will allow an 'undo' function
    def __init__(self,shape_parent,shape_child):
        self.parent = shape_parent
        self.child = shape_child
        text_list = []
        shape_pointer = shape_parent.child
        while shape_pointer != shape_child:
            print(shape_pointer.text)
            text_list.append(shape_pointer.text)
            shape_pointer = shape_pointer.child
        self.text_tuple = tuple(text_list)
        


this_app = Master()
