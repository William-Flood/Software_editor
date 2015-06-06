#Developer environment; builds an app out of entry widgets

#Changelog: Made scrolling more stable

import tkinter

class Master:
    
    def __init__(self):
        self.root = tkinter.Tk() #Creates the window that code will be entered into
        self.max_tab = 0
        self.toolkit_frame = tkinter.Frame(self.root) #Creates a place to put a top menu
        self.toolkit = Toolpanel(self,self.toolkit_frame) #Provides buttons to add functionality
        self.toolkit_frame.pack(side='top',fill='x')
        self.scrollframe = tkinter.Frame(self.root) #Creates a frame into which a scrollbar will be entered
        self.scrollbar = tkinter.Scrollbar(self.scrollframe,command=self.scroll) #Creates a scrollbar
        self.scrollbar.pack(fill='y',expand=True) #Adds the scrollbar to the frame
        self.scrollframe.pack(side='right',fill='y') #Adds the scrollbar frame to the window
        self.loading_latch = True #Prevents the field for the index label from being scaled during file loading
        
        self.entry_frame = tkinter.Frame(self.root) #For entry widgets to be added
        self.entry_frame.pack(side='left')
        
        self.first_shelf = Shelf(self,self,1) #Creates a so-called 'shelf' object, which controls entry widgets
        
        self.child = Shape(self,self,self.first_shelf,0) #Creates a so-called 'shape' object, representing code statements
        
        self.top_of_block = self.child #top_of_block points to the first shape in a selected block
        self.first_shelf.set_companion(self.top_of_block) #Allows the first shelf to communicate with the first shape
        self.bottom_of_block = self.top_of_block #bottom_of_block points to the last shape in a selected block
        
        self.final = Terminal_Shape(self.bottom_of_block,self) #'Shapes' are tracked in a linked list; Terminal shapes
        #are the end of the list
        self.bottom_of_block.child = self.final #A 'child' of a shape comes immediately after that shape
        self.building_selection = False #When true, allows the user to create a selection
        self.seed_shelf = self.first_shelf #Controls to and from which shape a selection will be made
        self.selection_deletion_handle = lambda s: None #Accessed by shelves
        self.history = [] #A changelog; used to implement an 'undo' feature
        self.text = "START" #Used in debugging
        self.load_file() #Loads file from disk
        self.scroll("",0,-1) #Sets window to the top of the file
        self.root.bind_all("<MouseWheel>",self.wheeled) #Allows the mouse wheel to control scrolling
        self.root.mainloop() #Opens the main window on screen
        self.loaded_file = ""
        
        
    def got_click(self,shelf,y): #Modifies top_of_block and bottom_of_block; changes colors of widgets if necessary
        if self.building_selection: #Creates a multi-shape selection
            if y > self.seed_shelf.box.winfo_rooty(): #if the shelf clicked is below the previous shelf
                self.bottom_of_block = shelf.companion
            else:
                self.top_of_block = shelf.companion
            self.top_of_block.companion.paint_cascade('cyan',self.bottom_of_block.companion) #Paints new selection cyan
            self.building_selection = False
            self.selection_deletion_handle = lambda s: self.selection_deletion(s) #Allows selection to be deleted
        else: #Selects only a single shape
            self.seed_shelf = shelf
            try:
                self.top_of_block.companion.paint_cascade('white',self.bottom_of_block.companion) #Paints previous selection white
            except:
                #print("Unknown error") #Resetting the colors of the entry fields failed occasionally, causing the program to lock up
                try:
                    self.first_shelf.paint_cascade('white',None)
                except:
                    pass
            self.top_of_block = shelf.companion
            self.bottom_of_block = shelf.companion
            self.selection_deletion_handle = lambda s: None #Prevents shape from being deleted on backspace
            
            
            #Determines if moving selections in either direction is possible; disables and enables buttons as needed
        if self.top_of_block.parent == self:
            self.toolkit.moveup.config(state= 'disabled')
        else:
            self.toolkit.moveup.config(state= 'normal')
            
        if self.bottom_of_block.companion.final:
            self.toolkit.movedown.config(state= 'disabled')
        else:
            self.toolkit.movedown.config(state= 'normal')
            
        if not(self.top_of_block.parent == self) and (self.top_of_block.parent.text.startswith(("if","for","while",'class','def','elif','else','try','except'))or self.top_of_block.parent.tab > self.top_of_block.tab):
            self.toolkit.addtab.config(state = 'normal')
        else:
            self.toolkit.addtab.config(state = 'disabled')
            
            
    def select_primer(self): #Allows got_click to create a multi-shape selection
        if not(self.building_selection):
            self.top_of_block.companion.paint_cascade('white',self.bottom_of_block.companion)
            self.building_selection = True
            self.seed_shelf.box.config(bg='cyan')
            
    def bump_up(self): #Moves selection up
        archived_shape_1 = self.top_of_block.parent #This shape will be moved below the selection
        archived_shape_2 = archived_shape_1.parent
        if archived_shape_2 != self:
            self.update_history(archived_shape_2,self.bottom_of_block.child,archived_shape_2.companion.index.get()-1,archived_shape_2.from_shape(self.bottom_of_block.child)-1)
        else:
            self.update_history(archived_shape_2,self.bottom_of_block.child,0,archived_shape_2.from_shape(self.bottom_of_block.child))
        archived_shape_1.companion.box.config(bg='cyan') #Recolors shelves to mirror the changing shape organization
        self.bottom_of_block.companion.box.config(bg = 'white')
        archived_shape_1.companion = self.bottom_of_block.companion.child #archived_shape_1 listens to the 
                            #shelf just below the selection
        self.bottom_of_block.set_child(archived_shape_1) #archived_shape_1 is moved below the selection
        if archived_shape_2 == self:
            self.top_of_block.parent = self #The top of the selection points to the master object 
            self.top_of_block.companion = self.first_shelf #The top shape of the selection listens to the first shelf on screen
            self.first_shelf.set_companion(self.top_of_block) #The first shelf on screen listens to the top shape in the selection
            self.top_of_block.child.order_update_cascade(self.first_shelf) #The shapes below the top of the selection rearrange themselves on screen as needed
        else:
            archived_shape_2.child = self.top_of_block.child #Prepares for next line; ensures proper order of shapes
            archived_shape_2.set_child(self.top_of_block) #Places top shelf in selection below archived_shape_2
            
        #Activates/deactivates buttons as needed
        self.toolkit.movedown.config(state='normal')
        if self.top_of_block.parent == self:
            self.toolkit.moveup.config(state= 'disabled')
        else:
            self.toolkit.moveup.config(state= 'normal')
            
            
        self.seed_shelf = self.seed_shelf.parent #Determines direction when coloring a selection
        
    def bump_down(self): #moves selection down
        archived_shape = self.bottom_of_block.child #The shape to be moved
        self.update_history(self.top_of_block.parent,archived_shape.child,self.top_of_block.companion.index.get()-2,self.top_of_block.from_shape(archived_shape.child))
            #Saves current state should it need to be reverted
        archived_shape.companion.box.config(bg='cyan')
        self.top_of_block.companion.box.config(bg = 'white')
        self.top_of_block.parent.child = archived_shape #Places the archived shape above the top of the selection
        archived_shape.parent = self.top_of_block.parent
        self.bottom_of_block.child = archived_shape.child
        archived_shape.child.parent = self.bottom_of_block
        archived_shape.child = self.top_of_block
        self.top_of_block.parent = archived_shape
        archived_shape.companion = self.top_of_block.companion #Places the archived shape in its new place on screen
        archived_shape.companion.contents.set(archived_shape.text)
        archived_shape.companion.companion = archived_shape
        self.top_of_block.order_update_cascade(self.top_of_block.companion) #Reorganizes the rest of the shapes on screen
        self.root.update_idletasks()
        
        #Activates/deactivates buttons as needed
        self.toolkit.moveup.config(state= 'normal')
        if self.bottom_of_block.companion.final:
            self.toolkit.movedown.config(state= 'disabled')
        else:
            self.toolkit.movedown.config(state= 'normal')
            
        self.seed_shelf = self.seed_shelf.child #Determines direction when coloring a selection
        
    def selection_deletion(self,shelf): #Deletes selection
        shelf.contents.set(shelf.contents.get()+" ")
        shelf.box.config(bg='white')
        self.update_history(self.top_of_block.parent,self.bottom_of_block.child,self.top_of_block.companion.index.get()-2,0)
        if self.top_of_block.parent == self and self.bottom_of_block.child == self.final: #Ensures at least one entry field will be visible after the deletion
            self.bottom_of_block.new_shape(False)
        self.bottom_of_block.child.parent = self.top_of_block.parent #Makes the rest of the program ignore the selection
        self.top_of_block.parent.child = self.bottom_of_block.child
        if self.top_of_block.parent != self: #Updates the screen; special behavior is needed if the first shape in the project has been deleted
            self.bottom_of_block.child.order_update_cascade(self.top_of_block.parent.companion) 
        else:
            self.bottom_of_block.child.companion = self.first_shelf
            self.first_shelf.set_companion(self.bottom_of_block.child)
            self.child.child.order_update_cascade(self.first_shelf)
        
        if self.top_of_block.parent != self: #Determines which shelf object should get focus
            archived_shelf = self.top_of_block.parent.companion
        else:
            archived_shelf = self.first_shelf
        self.top_of_block = self.child #Ensures success of got_click method
        self.bottom_of_block = self.final.parent
        self.got_click(archived_shelf,archived_shelf.frame_a.winfo_rooty) #Gives focus to the archived shape
        
    def indent(self): #Adds indentation to a selection
        self.update_history(self.top_of_block.parent,self.bottom_of_block.child,\
            self.child.from_shape(self.top_of_block)-1,self.top_of_block.from_shape(self.bottom_of_block)+1)
        shape_pointer = self.top_of_block
        while  shape_pointer != self.bottom_of_block.child: #Adds indentation to the entire selection
            shape_pointer.tab +=1
            shape_pointer.companion.tab_marker.set("\u2503 \u250B "*((shape_pointer.tab+1)//2)+ "\u2503 "*((shape_pointer.tab+1)%2))
            shape_pointer = shape_pointer.child
        
    def de_indent(self): #Removes indentation; goes from the topmost selected shape to the end of the code block
        self.got_click(self.top_of_block.companion,self.top_of_block.companion.box.winfo_rooty())
        print(self.top_of_block.text)
        archive_tuple = self.top_of_block.de_indent(self.top_of_block.tab - 1) #Removes indentation; returns tuple for use in reverting changes
        self.history.append({'parent_index':self.child.from_shape(self.top_of_block)-1,\
            'distance_to_end':len(archive_tuple),'archive_tuple':archive_tuple}) #Saves previous state, should the change need to be reverted
        
        
    def update_history(self,top,bottom,index,distance_to_end): #Creates a changelog for the saved document
        if self.history == []: #Enables undo button if necessary
            self.toolkit.undo.config(state='normal')
        self.history.append({}) #Creates a dictionary for state to be saved to
        self.history[-1]["parent_index"] = index #Indicates where in the project the saved data belongs
        self.history[-1]["distance_to_end"] = distance_to_end #Determines how many lines to be added or removed when reverting changes
        archive_list = []
        shape_pointer = top.child
        while shape_pointer != bottom:
            archive_list.append([shape_pointer.text,shape_pointer.tab])
            shape_pointer = shape_pointer.child
        self.history[-1]["archive_tuple"] = tuple(archive_list)
        
    def revert(self): #Undoes an action
        template = self.history.pop() 
        if self.history == []: #Disables the undo button, if necessary
            self.toolkit.undo.config(state='disabled')
            
        if self.child.fetch_shape(template["parent_index"]) == self.final:
            self.child.fetch_shape(template["parent_index"]-1).new_shape(False)
            
        shape_pointer = self.child.fetch_shape(template["parent_index"]) #Finds the shape at which to start revision
        
        #print(shape_pointer.text)
        
        
        for line in template['archive_tuple']: #Adds data as needed
            
            if template['distance_to_end'] > 0 and shape_pointer.child != self.final:
                template['distance_to_end'] -= 1
                shape_pointer = shape_pointer.child
                shape_pointer.text = line[0]
                shape_pointer.tab = line[1]
                if shape_pointer.companion.companion == shape_pointer:
                    shape_pointer.companion.contents.set(line[0])
                    shape_pointer.companion.tab_marker.set\
                        ("\u2503 \u250B "*((line[1]+1)//2)+ "\u2503 "*((line[1]+1)%2))
                    
                    
            else:
                shape_pointer.new_shape(False)
                shape_pointer = shape_pointer.child
                if shape_pointer.companion.companion == shape_pointer:
                    shape_pointer.companion.contents.set(line[0])
                    shape_pointer.companion.tab_marker.set\
                        ("\u2503 \u250B "*((line[1]+1)//2)+ "\u2503 "*((line[1]+1)%2))
                shape_pointer.text = line[0]
                
        shape_clamp = shape_pointer.fetch_shape(template['distance_to_end']+1) #Determines which shape should be placed underneath the shape last written to.
        shape_pointer.child = shape_pointer.fetch_shape(template['distance_to_end']+2) 
        shape_pointer.set_child(shape_clamp) #Removes data as necessary
        
    def save_file(self): #Saves project to file
        self.top_of_block.update(True)
        self.file_window('Save',lambda f,t: self.execute_save(f,t))
        
    def load_file(self): #Loads a previously saved file
        self.file_window('Load',lambda f,t: self.execute_load(f,t))
        
    def file_window(self,prompt,function_handle):
        window_opened = tkinter.Toplevel()
        prompt_shown = tkinter.Label(window_opened,text="Name:")
        name_field = tkinter.Entry(window_opened)
        name_field.insert(0,self.loaded_file)
        continue_button = tkinter.Button(window_opened,text=prompt,command = lambda: function_handle(window_opened,name_field.get()))
        prompt_shown.pack(side='left')
        name_field.pack(side='right')
        continue_button.pack()
        
    def execute_save(self,window,file_name):
        self.loaded_file = file_name
        window.destroy()
        try:
            working_file = open(file_name,'w')
            
            self.child.save_file(working_file)
        except:
            print("Error saving")
            try:
                working_file.close()
            except:
                pass
                
                
    def execute_load(self,window_to_close,name):
        self.loaded_file = name
        self.loading_latch = False
        window_to_close.destroy()
        self.top_of_block = self.child
        self.bottom_of_block = self.final.parent
        self.selection_deletion(self.top_of_block.companion)
        file_open = True
        try:
            working_file = open(name,'r')
            i = 1
            t = 0
            for line in working_file: #Generates shapes
                #self.top_of_block.companion.contents.set(line[:-1]) #Loads line from file into new shape
                while not(line.startswith(" "*self.top_of_block.tab*4) or line.strip() == "")and self.top_of_block.companion.contents.get().strip() == "":
                    self.top_of_block.tab -= 1
                self.top_of_block.companion.contents.set(self.top_of_block.companion.contents.get()+line.strip())
                if self.top_of_block.companion.contents.get()[-1:] != "\\":
                    self.top_of_block.new_shape(False) #Creates a new shape to add information to
                    self.top_of_block = self.top_of_block.child
                else:
                    self.top_of_block.companion.contents.set(self.top_of_block.companion.contents.get()[:-1])
                if self.top_of_block.tab > t:
                    t = self.top_of_block.tab
                i+=1
            self.loading_latch = True
            self.pad_index(len(str(i)))
            #self.pad_indent(t)
            self.bottom_of_block = self.top_of_block
        except Exception as error_handle:
            print("error loading file")
            print(error_handle)
            file_open = False
            try:
                working_file.close()
            except:
                pass
                
        if file_open:
            working_file.close()
            
            
            
    def wheeled(self,event): #Allows the mouse wheel to control scrolling
        fraction_visible = self.root.winfo_height()/(self.first_shelf.box.winfo_height()*self.child.from_shape(self.final))
        if fraction_visible > 1:
            fraction_visible = 1
        percent_to_scroll = fraction_visible*.1
        if event.num == 5 or event.delta == -120:
            self.scroll('1',str(self.scrollbar.get()[0]+percent_to_scroll))
        else:
            self.scroll('1',str(self.scrollbar.get()[0]-percent_to_scroll))
            
    def scroll(self,jstring,string_fraction,jarg=None): #Allows user to scroll through project
        if  not(self.first_shelf.final and self.first_shelf.companion == self.child):
            self.key = False
            if jarg == 1: #jarg indicates which arrow button, if any, on the scrollbar was pressed
                string_fraction = '.9'
            elif jarg == -1:
                string_fraction = '0'
                
            fraction = float(string_fraction) #Converts the string argument into a floating point number
            fraction=fraction/.9
            
            #print(self.first_shelf.companion.text)
            
            back = self.child.from_shape(self.first_shelf.companion) #How many shapes are above the companion of the first shelf
            master_height = self.root.winfo_height()-50
            last_visible,remaining = self.first_shelf.tally_1(master_height,False)  #How many shapes are below the companion
            #of the last shelf on screen
            
            move_to = int(fraction*(back+remaining+1)) #How many shapes should be above the companion of the first shelf
            lines_scrolled = 0
            if move_to > back: #Determines if the app should scroll up or down
                while move_to > back and remaining > 0 and self.first_shelf.companion.child != self.final:
                    self.first_shelf.set_companion(self.first_shelf.companion.child) #The first shelf takes the child
                    #of its companion as its companion
                    back+=1 #Exits loop if back exceeds move_to
                    remaining -=1 #Exits loop if remaining becomes zero
                    lines_scrolled+=1
            else:
                while move_to < back and self.first_shelf.companion.parent != self:
                    self.first_shelf.set_companion(self.first_shelf.companion.parent) #The first shelf takes the parent
                    #of its companion as its companion
                    back-=1#Exits loop if move_to exceeds back
                    lines_scrolled -=1
                    
            self.first_shelf.companion.companion = self.first_shelf #Creates mutual companionship between
            #the first shelf and its current companion
            self.first_shelf.companion.child.order_update_cascade(self.first_shelf) #Updates the app
            if self.first_shelf.companion == self.child:
                self.first_shelf.scroll_update_cascade(1-self.first_shelf.index.get())
            else:
                self.first_shelf.scroll_update_cascade(lines_scrolled)
            self.scrollbar.set(fraction*.9,fraction*.9+.05) #Sets the scrollbar to where the user moved it to
            
    def pad_index(self,width_input): #Ensures index labels are aligned evenly
        if self.loading_latch:
            self.first_shelf.pad_index(width_input)
        
class Shape: #Control code statements
    def __init__(self,parent,master,companion,tab):
        self.parent = parent #The line of code above this one
        self.master = master #The window onto which this will be displayed
        self.companion = companion #The entry widget displaying this line of code
        self.text = "" #The statement itself
        self.garbage_lock = True
        self.tab = tab
        #self.master.pad_indent(tab)
        
    def new_shape(self,bool): #Places a new line of code beneath this one
        self.garbage_lock = False
        self.update(False) #Sets text to value in entry widget
        if bool:
            self.master.update_history(self.parent,self,self.companion.index.get()-1,0)
        if self.text.startswith(("if","for","while",'class','def','elif','else','try','except')):
            self.set_child(Shape(self,self.master,self.companion,self.tab+1))
        else:
            self.set_child(Shape(self,self.master,self.companion,self.tab))
        self.child.companion.box.focus_set()
        if self.child.companion.final and self.companion.index.get() < 75:
            self.master.scroll('filler','1')
            
    def order_update_cascade(self,shelf): #Used if shape objects have been moved
        if shelf.order_test(self): #Decides if line should be displayed at the current location on screen
            self.companion = shelf.child #Communicates with the child of the widget that was taken as an argument
            self.companion.adjust_field() #Gives the companion shelf the shape's held value
            try:
                self.child.order_update_cascade(self.companion) #Updates child; continues until 'order_test' returns false
            except:
                pass
                
    def update(self,bool): #Communicates with companion shelf
        total_contents = self.companion.contents.get() #Gets data from the shelf's main entry field
        for data in self.companion.overflow_contents: #Gets data from the overflow fields
            total_contents = total_contents + data.get()
            
        if self.text != total_contents: #Only runs update if a change is detected
            if bool: #Given as argument; indicates that user clicked out of shelf
                self.master.update_history(self.parent,self.child,self.companion.index.get()-2,1)
                
            self.text = total_contents #Sets text value to the value entered into the companion widget
            self.companion.adjust_field() #Moves data on screen into overflow, if needed
            
        elif self.text == "": #Prevents deletion if shape started as blank i.e. had yet to be modified
            self.garbage_lock = False
            
        if self.text == "" and self.parent != self.master and self.garbage_lock: #Deletes shape if companion widget is blank
            self.master.update_history(self.parent,self.child,self.companion.index.get()-2,0)
            self.child.parent = self.parent
            self.parent.child = self.child
            self.child.order_update_cascade(self.parent.companion)
        elif not(self.garbage_lock) and bool:
            self.garbage_lock = True
            
        #print("End")
        
        
    def set_child(self,child): #Places shape argument beneath self in project
        child.child = self.child
        self.child.parent = child
        self.child = child
        child.parent = self
        child.order_update_cascade(self.companion)
        
    def save_file(self,file): #Saves text value into file argument
        file.write(" "*self.tab*4+self.text+"\n")
        self.child.save_file(file) #Continues to the end of the document
        
    def from_shape(self,shape): #Determines how many generations this shape is from a given shape
        if shape == self:
            return 0
        else:
            continuation = self.child.from_shape(shape)
            if continuation >= 0:
                return continuation +1
            else:
                return -1
                
    def fetch_shape(self,generations): #Finds the shape at the given amount of generations down
        if generations <= 0:
            return self
        else:
            return self.child.fetch_shape(generations-1)
            
    def de_indent(self,check_tab): #Removes indentation as needed
        if self.tab > check_tab: #check_tab sent as argument; de_indent continues until the end of a code block
            self.tab -=1
            self.companion.tab_marker.set("\u2503 \u250B "*((self.tab+1)//2)+ "\u2503 "*((self.tab+1)%2))
            
            return ([self.text, self.tab+1],) + self.child.de_indent(check_tab) #Runs method in child shape; informs the master widget of previous configuration
        else:
            return ()
            
            
            
class Shelf: #Controls widgets on screen
    def __init__(self,parent,master,index):
        self.parent = parent #The widget above this one
        self.master = master #The owner of the window onto which this widget will be placed
        self.index = tkinter.IntVar()
        self.index.set(index)
        if len(str(index)) > len(str(index-1)) and index != 1:
            self.master.pad_index(len(str(index)))
            
            
        self.frame_a = tkinter.Frame(master.entry_frame) #A frame for the widget
        self.entry_frame = tkinter.Frame(self.frame_a)
        self.contents = tkinter.StringVar() #Contains the value entered into the widget
        self.box = tkinter.Entry(self.entry_frame,width = 150,textvariable = self.contents) #The widget itself
        self.tab_marker = tkinter.StringVar()
        self.tab_label = tkinter.Label(self.frame_a,textvar=self.tab_marker,anchor = 'w')
        self.index_label = tkinter.Label(self.frame_a,textvar=self.index,anchor = 'w')
        self.index_label.pack(side='left',anchor = 'w')
        self.tab_label.pack(side='left')
        self.box.pack(side='top')
        self.entry_frame.pack(side='left',expand = True)
        self.frame_a.pack(fill='x')
        self.box.bind("<Button-1>",lambda e: master.got_click(self,e.widget.winfo_rooty())) #Informs master that the widget was clicked
        self.box.bind("<Double-Button-1>",lambda e: master.select_primer()) #Allows user to make a selection if widget was double-clicked
        self.box.bind("<BackSpace>", lambda e: master.selection_deletion_handle(self)) #Allows user to delete a selection
        self.final = True #Is the last shelf to be created
        self.overflow_contents = []
        self.overflow_boxes = []
        
    def order_test(self,shape): #Determines if child shelf is paired to the correct shape; returns False if so
        if self.final:
            self.final = False
            self.child = Shelf(self,self.master,self.index.get()+1)
            self.child.set_companion(shape)
            return True
        elif self.child.companion == shape:
            return False
        else:
            self.child.set_companion(shape)
            return True
            
    def pass_child(self,shape): #Returns the widget below this one; creates widget if none exists
        if self.final:
            self.child = Shelf(self,self.master,self.index.get()+1)
            self.final = False
        self.child.set_companion(shape)
        return self.child
        
    def set_companion(self,shape): #Communicates with a shape, sets additional event bindings
        self.companion = shape
        self.contents.set(self.companion.text)
        tab_setting = self.companion.tab
        self.tab_marker.set("\u2503 \u250B "*((tab_setting+1)//2)+ "\u2503 "*((tab_setting+1)%2))
        self.box.bind("<Return>",lambda e: self.companion.new_shape(True)) #Creates a new shape if 'enter' key is pressed
        self.box.bind("<FocusOut>",lambda e: self.companion.update(True)) #Updates companion if keyboard focus is lost
        
    def paint_cascade(self,color,shelf): #Changes widget color, allows child to do the same, if appropriate
        text = self.contents.get()
        self.box.config(bg = color)
        if self != shelf and not(self.final): #Cascade continues, if the stopping point given as an argument hasn't been reached
            #or if no widget exists below this one
            self.child.paint_cascade(color, shelf)
            
    def truncate(self): #Destroys this widget and all beneath it
        self.parent.final = True
        self.box.destroy()
        self.frame_a.destroy()
        if not(self.final):
            self.child.truncate()
            
    def tally_1(self,y,downstream): #Determines how many generations this shelf is from the last shelf visible
        if self.final:
            return self,0
        elif self.frame_a.winfo_y() > y or (self.frame_a.winfo_y() == 0 and downstream):
            return self,self.child.tally_2()
        else:
            last_visible,remaining = self.child.tally_1(y,True)
            return last_visible,remaining
            
    def tally_2(self): #Determines how many generations this shelf is from the last in the app
        if self.final:
            return 1
        else:
            return self.child.tally_2()+1
            
    def scroll_update_cascade(self,i): #Updates index number
        self.index.set(self.index.get()+i)
        if not(self.final):
            self.child.scroll_update_cascade(i)
            
    def pad_index(self,width_input): #Ensures proper alignment of index label
        try:
            self.index_label.config(width = width_input)
        except:
            print("config failed" + str(self.index.get()) + str(width_input))
        if not(self.final): 
            try:
                self.child.pad_index(width_input)
            except:
                print("Final catch failed" + str(self.index.get()), self.final)
    
    def adjust_field(self):  #Moves text into overflow fields
        total_contents = self.companion.text #Acquires data from companion shape
        
        if len(total_contents) > 150: #Determines if splitting text is necessary
            break_index = total_contents[:150].rfind(" ")
        else:
            break_index = -1
            
        if break_index > 0: #Determines if splitting text is possible
            self.contents.set(total_contents[:break_index])
            total_contents = total_contents[break_index:]
        else:
            self.contents.set(total_contents)
            total_contents = ""
        i=0
        
        while len(total_contents) > 0: #Adds data to overflow widgets until no further data is left to be entered
            if i >= len(self.overflow_contents):
                self.overflow_contents.append(tkinter.StringVar())
                self.overflow_boxes.append(tkinter.Entry(self.entry_frame,textvariable = self.overflow_contents[i],width = 125))
                self.overflow_boxes[-1].pack()
            if len(total_contents) > 125:
                break_index = total_contents[:125].rfind(" ")
            else:
                break_index = -1
                
            if break_index > 0:
                self.overflow_contents[i].set(total_contents[:break_index])
                total_contents = total_contents[break_index:]
            else:
                self.overflow_contents[i].set(total_contents)
                total_contents = ""
            i +=1
            
        while len(self.overflow_boxes) > i: #Destroys entry fields if more exist than are needed
            self.overflow_boxes[-1].destroy()
            self.overflow_boxes.pop()
            self.overflow_contents.pop()
            
            
            
class Terminal_Shape: #The end point in the linked list of shapes
    def __init__(self,parent,master):
        self.master = master
        self.parent = parent
        self.text = "END" #Used in debugging
        
    def order_update_cascade(self,shelf):
        if not(shelf.final): #Determines if any widgets are beneath the one given as argument
            self.parent.companion.final = True #Informs argument widget that it is on the bottom of the screen
            self.parent.companion.child.truncate() #Destroys all widgets beneath the argument
            
    def update(self): #Prevents a crash if method is accessed
        pass
        
        
    def save_file(self,file): #Closes file
        file.close()
        
    def fetch_shape(self,generations): #Prevents a crash if method is accessed; fetch_shape will always return the terminal shape or one of its ancestors
        return self
        
    def from_shape(self,shape): 
        if shape == self: #If the terminal shape was sought, allows previous calls to determine distance from the shape
            return 0
        else: #Returns an error flag
            return -1
        
        
class Toolpanel: #Controls a window with buttons
    def __init__(self,master,frame):
        self.master = master #Master widget
        self.vertical_frame = tkinter.Frame(frame)
        
        self.moveup = tkinter.Button(self.vertical_frame,text = "\u2191",state='disabled',command = master.bump_up) #Moves selection up
        self.movedown = tkinter.Button(self.vertical_frame,text = "\u2193",state='disabled',command = master.bump_down) #Moves selection down
        self.select = tkinter.Button(frame,text = "Select",command = master.select_primer) #Allows user to make a selection
        self.make_save = tkinter.Button(frame,text = "Save",command = master.save_file) #Allows user to save project
        self.load = tkinter.Button(frame,text = "Load",command = master.load_file) #Allows user to load previous project
        self.addtab = tkinter.Button(frame,text = "\u2192",command = master.indent)   #Adds indentation
        self.tabback = tkinter.Button(frame,text = "\u2190",command = master.de_indent)   #Removes indentation
        self.undo = tkinter.Button(frame,text = "Undo",state='disabled',command = master.revert) #Allows user to undo an action
        
        self.vertical_frame.pack(side='left')
        self.moveup.pack()
        self.movedown.pack()
        self.addtab.pack(side='left')
        self.tabback.pack(side='left')
        self.select.pack(side='left')
        self.make_save.pack(side='left')
        self.load.pack(side='left')
        self.undo.pack(side='left')
        
        
        
this_app = Master()

