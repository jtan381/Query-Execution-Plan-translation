from tkinter import *
from tkinter import messagebox
import os
# from progreCommunicator import *

class loginMenu:
    def __init__(self):
        self.comm = None
        self.tableName = []
        self.attr = {}
        self.exitCond = False
        self.database = 'Enter_database'
        self.username = 'Enter_username'
        self.password = 'Enter_password'
        self.host = 'Enter_host'
        self.portnum = 'Enter_portnumber'

    def connect_DB(self):
        # init_DB (database, username, password, host, port)
        # parameter status: booblen, tablename: array, attr[tablename] : dict
        self.status, self.tableName, self.attr = self.comm.init_DB(entry_var_Database.get(), entry_var_UserName.get(),
                                                entry_var_Password.get(), entry_var_Host.get(),
                                                entry_var_Port.get())
        # if true init all table and attr
        if(self.status):
            main_screen.destroy()
            self.exitCond = True
        else:
            messagebox.showerror("Error", "Invaild user/password")

    def main_login_screen(self, comm):
        global main_screen
        global entry_var_Database
        global entry_var_UserName
        global entry_var_Password
        global entry_var_Host
        global entry_var_Port
        self.comm = comm

        main_screen = Tk()
        main_screen.geometry("300x250")
        main_screen.title("Account Login")
        entry_var_Database = StringVar(value=self.database)
        entry_var_UserName = StringVar(value=self.username)
        entry_var_Password = StringVar(value=self.password)
        entry_var_Host = StringVar(value=self.host)
        entry_var_Port = StringVar(value=self.portnum)
        
        Database_label = Label(text="Database:")
        Database_label.grid(row = 0 , column=0, columnspan = 1, sticky=W)
        entry_Database = Entry( textvariable=entry_var_Database)
        entry_Database.grid(row = 0 , column=1)

        Username_label = Label( text="UserName:")
        Username_label.grid(row = 1 , column=0, columnspan = 1, sticky=W)
        entry_UserName = Entry( textvariable=entry_var_UserName)
        entry_UserName.grid(row = 1 , column=1)

        Password_label = Label( text="Password:")
        Password_label.grid(row = 2 , column=0, columnspan = 1, sticky=W)
        entry_Password = Entry( textvariable=entry_var_Password, show='*')
        entry_Password.grid(row = 2 , column=1, columnspan = 1)

        Host_label = Label( text="Host:")
        Host_label.grid(row = 3 , column=0, columnspan = 1, sticky=W)
        entry_Host = Entry( textvariable=entry_var_Host)
        entry_Host.grid(row = 3 , column=1)

        Port_label = Label( text="Port:")
        Port_label.grid(row = 4 , column=0, sticky=W)
        entry_Port = Entry( textvariable=entry_var_Port)
        entry_Port.grid(row = 4 , column=1)

        connect_btn = Button( text='Connect', command=self.connect_DB)
        connect_btn.grid(row=5, column=0, pady =20 , columnspan=2)

        main_screen.mainloop()
        return (self.exitCond, self.tableName, self.attr)

