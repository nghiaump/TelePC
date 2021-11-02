import socket
import tqdm
import os
import tkinter as tk
import tkinter.ttk as ttk
import pickle
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel, filedialog, messagebox
from pathlib import Path

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

def recvall(sock): 
    data = b''
    while True:
        while True:
            try:
                part = sock.recv(BUFFER_SIZE)
                data += part
                if len(part) < BUFFER_SIZE:
                    # either 0 or end of data
                    break
            except socket.error:
                return
        if data:
            break
    return data

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def listDirs(client, path):
    client.sendall(path.encode())
    file_name = "dirs.pkl"

    with open(file_name, "wb") as f:
        data = recvall(client)
        if (data != "error"):
            f.write(data)
        else:
            messagebox.showerror(message = "Cannot open this directory!")
            return []
    
    open_file = open(file_name, "rb")
    loaded_list = pickle.load(open_file)
    open_file.close()
    return loaded_list

class DirectoryTree_UI(Canvas):
    def __init__(self, parent, client):
        Canvas.__init__(self, parent)
        self.client = client
        self.currPath = ""
        self.nodes = dict()

        self.configure(
            #window,
            bg = "#FCD0E8",
            height = 600,
            width = 1000,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.place(x = 0, y = 0)
        self.image_image_1 = PhotoImage(
            file=relative_to_assets("bg.png"))
        self.image_1 = self.create_image(
            519.0,
            327.0,
            image=self.image_image_1
        )
        
        self.frame = tk.Frame(self, height = 200, width = 500)
        self.tree = ttk.Treeview(self.frame)
        self.frame.place(
            x=53.0,
            y=162.0,
            width=713.0,
            height=404.0
        )
        
        self.insText1 = "Click SHOW button to show the server's directory tree."
        self.label1 = tk.Label(self.frame, text=self.insText1)
        self.label1.pack(fill = tk.X)

        ysb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Server\'s Directory Tree', anchor='w')
        self.tree.pack(fill = tk.BOTH)

        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind("<<TreeviewSelect>>", self.select_node)

        self.insText2 = "Selected path.\n\
            Click COPY TO PATH button to select a file you want to copy to this path.\n\
            Click COPY THIS FILE to copy the selected file to your computer (client)\n\
            Click DELETE button to delete the file on this path.\nYou can click SHOW button again to see the changes."
        self.label2 = tk.Label(self.frame, text=self.insText2)
        self.label2.pack(fill = tk.X)
        self.path = Text(self.frame, height = 1, width = 26, state = "disable")
        self.path.pack(fill = tk.X)
        self.button_2 = Button(self, text = 'SHOW', width = 20, height = 5, fg = 'white', bg = 'IndianRed3',
            #image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.showTree,
            relief="flat"
        )
        self.button_2.place(
            x=838.0,
            y=152.0,
            width=135.0,
            height=53.0
        )
        self.button_3 = Button(self, text = 'COPY TO PATH', width = 20, height = 5, fg = 'white', bg = 'IndianRed3',
            #image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.copyFileTo,
            relief="flat"
        )
        self.button_3.place(
            x=838.0,
            y=238.0,
            width=135.0,
            height=53.0
        )
        self.button_4 = Button(self, text = 'COPY THIS FILE', width = 20, height = 5, fg = 'white', bg = 'IndianRed3',
            #image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.copyFile,
            relief="flat"
        )
        self.button_4.place(
            x=838.0,
            y=317.0,
            width=135.0,
            height=53.0
        )
        self.button_5 = Button(self, text = 'DELETE', width = 20, height = 5, fg = 'white', bg = 'IndianRed3',
            #image=button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=self.deleteFile,
            relief="flat"
        )
        self.button_5.place(
            x=839.0,
            y=396.0,
            width=135.0,
            height=53.0
        )
        self.button_6 = Button(self, text = 'BACK', width = 20, height = 5, fg = 'white', bg = 'IndianRed3',
            #image=button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.back(),
            relief="flat"
        )
        self.button_6.place(
            x=838.0,
            y=473.0,
            width=135.0,
            height=53.0
        )

    def insert_node(self, parent, text, abspath):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(abspath):
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            if os.path.isdir(abspath):
                self.tree.delete(self.tree.get_children(node))
                try:
                    dirs = listDirs(self.client, abspath)
                    for p in dirs:
                        self.insert_node(node, p, os.path.join(abspath, p))
                except:
                    messagebox.showerror(message = "Cannot open this directory!")

    def select_node(self, event):
        item = self.tree.selection()[0]
        parent = self.tree.parent(item)
        self.currPath = self.tree.item(item,"text")
        while parent:
            self.currPath = os.path.join(self.tree.item(parent)['text'], self.currPath)
            item = parent
            parent = self.tree.parent(item)

        self.path.config(state = "normal")
        self.path.delete("1.0", tk.END)
        self.path.insert(tk.END, self.currPath)
        self.path.config(state = "disable")

    def deleteTree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def showTree(self):
        self.deleteTree()
        self.client.sendall("SHOW".encode())
        isOk = self.client.recv(BUFFER_SIZE).decode()
        if (isOk == "OK"):
            for c in range(ord('A'), ord('Z') + 1):
                path = chr(c) + ":\\"
                try:
                    os.listdir(path)
                    abspath = os.path.abspath(path)
                    self.insert_node('', abspath, abspath)
                except:
                    continue

    # copy file from client to server
    def copyFileTo(self):
        self.client.sendall("COPYTO".encode())
        isOk = self.client.recv(BUFFER_SIZE).decode()
        if (isOk == "OK"):
            filename = filedialog.askopenfilename(title="Select File", 
                                                filetypes=[("All Files", "*.*")])
            destPath = self.currPath + "\\"
            self.client.send(f"{filename}{SEPARATOR}{destPath}".encode())
            isReceived = self.client.recv(BUFFER_SIZE).decode()
            if (isReceived == "received filename"):
                with open(filename, "rb") as f:
                    data = f.read()
                    self.client.sendall(data)
                isReceivedContent = self.client.recv(BUFFER_SIZE).decode()
                if (isReceivedContent == "received content"):
                    messagebox.showinfo(message = "Copy successfully!")
                    return True
        messagebox.showerror(message = "Cannot copy!")    
        return False

    # copy file from server to client
    def copyFile(self):
        self.client.sendall("COPY".encode())
        isOk = self.client.recv(BUFFER_SIZE).decode()
        if (isOk == "OK"):
            try:
                self.client.sendall(self.currPath.encode())
                destPath = filedialog.askdirectory()
                filename = os.path.basename(self.currPath)
                data = recvall(self.client)
                with open(destPath + "\\" + filename, "wb") as f:
                    f.write(data)
                messagebox.showinfo(message = "Copy successfully!")
            except:
                messagebox.showerror(message = "Cannot copy!")    
        else:
            messagebox.showerror(message = "Cannot copy!") 

    def deleteFile(self):
        self.client.sendall("DEL".encode())
        isOk = self.client.recv(BUFFER_SIZE).decode()
        if (isOk == "OK"):
            self.client.sendall(self.currPath.encode())
            res = self.client.recv(BUFFER_SIZE).decode()
            if (res == "ok"):
                messagebox.showinfo(message = "Delete successfully!")
            else:
                messagebox.showerror(message = "Cannot delete!") 
        else: 
            messagebox.showerror(message = "Cannot delete!")  

    def back(self):
        return