# Software_editor
A saving place for my software editor program
Uses python code and the tkinter module to construct app

The main window features a column of entry widgets, used to display and interact with a document stored as a background linked list of 'shape' objects; each shape represents a line of code, and communicates with one or more of the entry widgets.  When the data in an entry widget is changed and clicked out of, the change is saved to shape it communicates with.

Pressing the enter key while inside an entry widget will create a new shape, just after the one the widget communicates with in the linked list.  The newly created shape will communicate with the entry widget beneath the one which had focus, and all shapes after it in the list will communicate with the widget beneath the one it had previously communicated with.

Double-clicking on an entry widget will allow the creation of a multi-widget selection.  The widget clicked will form one end of the selection; the next widget clicked will form the other.  

Clicking on a vertical arrow on the top menue will increase or decrease the index of any selected shapes, which will be reflected on-screen.

Pressing backspace while in a multi-widget selection will remove the associated shapes from the linked list, and remove them from the screen.

Deleting the contents of an entry widget and focusing out of it will remove the associated shape from the linked list.

Pressing the right-pointing arrow will add indentation to the selected shapes.

Pressing the left-pointing arrow will remove one level of indentation from shapes, starting with the topmost-selected shape, and continuing until it reaches a shape with at most one level of indentation lower than the topmost-selected shape, or the end of the document.

The button labeled 'Undo' reverts the most recent change made to the document.

The button labeled 'Save' opens a new window, with a single entry widget and a button labeled 'Save'.  When the 'Save' button on the new window is pressed, the document will be saved to a file named with the contents of the entry widget at the time the button was pressed, and inside the same directory as the python script controlling the application.

The button labeled 'Load' opens a new window, with a single entry widget and a button labeled 'Load'.  When the 'Load' button on the new window is pressed, the application will look for a document with the name given in the entry widget; if such a document exists, it will be loaded into the application.

If the text saved to a shape contains more than 150 characters, a 'shelf' object controlling the entry widget which communicates with the shape will attempt to move some of the text to a new entry widget beneath the original widget.  The last whitespace character before the 150th index will be used to determine where to split the text.  If no such whitespace character exists, text will not be moved.  If any entry widget beneath the original would contain more than 120 characters, further splits will be attempted.
