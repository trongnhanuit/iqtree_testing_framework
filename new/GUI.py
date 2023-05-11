import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("GUI Example")

        self.create_tabs()

        self.create_input_areas()

        self.create_file_drop_area()

    def create_tabs(self):
        self.tabs = ttk.Notebook(self.master)
        self.tabs.pack()

        self.tab1 = ttk.Frame(self.tabs)
        self.tabs.add(self.tab1, text='Tab 1')

        self.tab2 = ttk.Frame(self.tabs)
        self.tabs.add(self.tab2, text='Tab 2')

    def create_input_areas(self):
        self.entry1 = tk.Entry(self.tab1)
        self.entry1.pack()

        self.entry2 = tk.Entry(self.tab2)
        self.entry2.pack()

    def create_file_drop_area(self):
        self.file_drop_label = tk.Label(self.tab1, text="Drag file here", font=("Arial", 14))
        self.file_drop_label.pack(pady=10)

        self.file_drop_label.bind('<<DragEnter>>', self.drag_enter)
        self.file_drop_label.bind('<<DragLeave>>', self.drag_leave)
        self.file_drop_label.bind('<<Drop>>', self.drop)

    def drag_enter(self, event):
        self.file_drop_label.config(bg='lightblue')

    def drag_leave(self, event):
        self.file_drop_label.config(bg='white')

    def drop(self, event):
        file_path = event.data['text'].strip()
        file_name = file_path.split('/')[-1]
        self.file_drop_label.config(text=file_name)


root = tk.Tk()
gui = GUI(root)
root.mainloop()