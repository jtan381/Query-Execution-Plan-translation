from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from gtts import gTTS
from QEPTreeGraph import draw_query_plan
import pygame

class App():
    def __init__(self):
        self.tableName = []
        self.attr = {}
        self.pause = False
        self.marks = False
        self.comm = None

    def text_to_voice (self):
        self.pause = False 
        tts = gTTS(text=self.result_textbox.get('1.0', END), lang='en')
        tts.save("good1.mp3")        
        pygame.mixer.init()
        pygame.mixer.music.load("good1.mp3")
        pygame.mixer.music.play()

    def SQL_query1 (self):
        # send to backend to process the input SQL query1
        status, QEP_text = self.comm.ConvertQueryToText(self.query1_textbox.get('1.0', END), 1)

        if(status == True):
            self.query1_plane_textbox.configure(state='normal')
            self.query1_plane_textbox.delete('1.0', END)
            for text in QEP_text:
                self.query1_plane_textbox.insert(END, text + '\n')
            self.query1_plane_textbox.configure(state='disabled')
        else:
            messagebox.showerror("Error", "Incorrect1 query")

    def SQL_query2 (self):
        # send to backend to process the input sQL query2
        status, QEP_text = self.comm.ConvertQueryToText(self.query2_textbox.get('1.0', END), 2)

        if(status == True):
            self.query2_plane_textbox.configure(state='normal')
            self.query2_plane_textbox.delete('1.0', END)
            for text in QEP_text:
                self.query2_plane_textbox.insert(END, text + '\n')
            self.query2_plane_textbox.configure(state='disabled')
        else:
            messagebox.showerror("Error", "Incorrect2 query")

    def disconnect (self):
        self.main_screen.destroy()
        self.marks = True
        
    def reset1 (self):
        self.query1_textbox.delete('1.0', END)

    def reset2 (self):
        self.query2_textbox.delete('1.0', END)

    # def voice_to_text (self):
    #     self.question_textbox.delete('1.0', END)
    #     self.question_textbox.insert(END, "Recording...")
    #     generate_voice()
    #     text = voice_text()
    #     self.question_textbox.delete('1.0', END)
    #     self.question_textbox.insert(END, text)

    def init_tables (self, tableName, attr):
        for table in tableName:
            id = self.tree.insert("", (len(self.tree.get_children())+1), value=table, text=table)
            for attribute in attr[table]:
                self.tree.insert(id, "end", value=attribute, text=str(attribute))

    def OnDoubleClick(self, event):
        item = self.tree.selection()[0]
        # self.query1_textbox.insert(END, self.tree.item(item,"text") + " ")

        if(self.tree.item(item)['open']==1):
            self.tree.item(item, open = False)
        else:
            self.tree.item(item, open = True)

    def open_nodes(self):
        # print('ckpt')
        for child in (self.tree.get_children()):
            print(child)
            self.tree.item(child, open=True)

    def un_paused(self):
        if (self.pause):
            self.pause = False
            pygame.mixer.music.unpause()
        else:
            self.pause = True
            pygame.mixer.music.pause()      

    def compareQuery(self):
        compareList = []
        compareList = self.comm.CompareQEPs()
        
        self.result_textbox.configure(state='normal')
        self.result_textbox.delete('1.0', END)
        for text in compareList:
            self.result_textbox.insert(END, text + '\n')
        self.result_textbox.configure(state='disabled')     

    def normal_query_excute(self):
        status = self.comm.ExecuteQuery(self.normal_query.get('1.0', END))
        if(status):
            messagebox.showerror("Success")
        else:
            messagebox.showerror("Unsuccess")

    def ShowTree1(self):
        i =1
        plan = self.comm.GetPlan(i)
        draw_query_plan(plan)

    def ShowTree2(self):
        i =2
        plan = self.comm.GetPlan(i)
        draw_query_plan(plan)

    def initialize(self):
        self.connect_states_text = StringVar()
        self.connect_states_text.set('Connected')

        self.root = Frame(self.main_screen)
        self.root.pack()
        self.top_panel = Frame(self.root, width=100, height=100)
        self.top_panel.pack(side = TOP)
        self.left_panel = Frame(self.root, width=100, height=0)
        self.left_panel.pack(side = LEFT)
        self.main_panel = Frame(self.root, width=0, height=0)
        self.main_panel.pack()

        self.input_frame = Frame(self.main_panel, width=100, height=0, highlightbackground="black",
                                    highlightcolor="black", highlightthickness=1, bd=0)
        self.input_frame.grid(row=0, column=1)
        self.input_box = Frame(self.input_frame, width=200, height=0)
        self.input_box.grid(row=0)

        self.query_plan_frame = Frame(self.main_panel, width=300, height=0, highlightbackground="black",
                                    highlightcolor="black", highlightthickness=1, bd=0)
        self.query_plan_frame.grid(row=3, column=1)

        self.result_frame = Frame(self.main_panel, width=300, height=0, highlightbackground="green",
                                    highlightcolor="green", highlightthickness=1, bd=0)
        self.result_frame.grid(row=5, column=1)

        self.connect_btn = Button(self.top_panel, text='Disconnect', command=self.disconnect)
        self.connect_btn.grid(row=1, column=5)
        self.connect_states_label = Label(self.top_panel, textvariable = self.connect_states_text, fg="black", bg="#aeff47")
        self.connect_states_label.grid(row = 1, column = 6, sticky="wns")

        self.tree = ttk.Treeview(self.left_panel, height=20)
        self.tree.heading("#0",text="Tables")
        self.tree.grid(row =1, rowspan=4, columnspan=3, sticky='ew')
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        
        self.vsb = ttk.Scrollbar(self.left_panel, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=1, rowspan=4, column=3, sticky='ns')
        self.tree.config(yscrollcommand=self.vsb.set)
        
        self.normal_query_label = Label(self.left_panel, text = "Query Editor", fg="black", bg="cyan")
        self.normal_query_label.grid(row = 5, column = 1, sticky="nsew")
        self.normal_query = ScrolledText(self.left_panel, height=10, width = 20,wrap=WORD)
        self.normal_query.grid(row=6, columnspan=4, sticky='ew')
        self.normal_query_btn = Button(self.left_panel, text='Execute Query', command=self.normal_query_excute)
        self.normal_query_btn.grid(row = 7, column = 1, sticky="nsew")

        self.sql_query1_label = Label(self.input_box, text="SQL Query1", fg="black", bg="cyan")
        self.sql_query1_label.grid(row = 0, column = 1,columnspan=2)
        self.sql_query2_label = Label(self.input_box, text="SQL Query2", fg="black", bg="cyan")
        self.sql_query2_label.grid(row = 0, column =5, columnspan=2)
        self.query1_textbox = ScrolledText(self.input_box, height=7,width=50, wrap=WORD)
        self.query1_textbox.grid(row=1,column=0, columnspan=4)
        self.query2_textbox = ScrolledText(self.input_box, height=7,width=50, wrap=WORD)
        self.query2_textbox.grid(row=1,column=4, columnspan=4)
        self.SQL_query1_btn = Button(self.input_box, text='Query1', command=self.SQL_query1)
        self.SQL_query1_btn.grid(row=2, column=1, sticky = 'ew')
        self.reset_btn1 = Button(self.input_box, text='Reset Query 1', command=self.reset1)
        self.reset_btn1.grid(row=2, column=2, sticky = 'ew')
        self.SQL_query2_btn = Button(self.input_box, text='Query2', command=self.SQL_query2)
        self.SQL_query2_btn.grid(row=2, column=5, sticky = 'ew')
        self.reset_btn2 = Button(self.input_box, text='Reset Query 2', command=self.reset2)
        self.reset_btn2.grid(row=2, column=6, sticky = 'ew')

        self.query1_plane_label = Label(self.query_plan_frame, text="Natural Language QEP1", fg="black", bg="cyan")
        self.query1_plane_label.grid(row=0, columnspan=2)
        self.query1_plane_textbox = ScrolledText(self.query_plan_frame, height=13,width=50, wrap=WORD)
        self.query1_plane_textbox.grid(row=1,column=0, columnspan=2)
        self.query1_plane_textbox.config(state=DISABLED)

        self.query2_plane_label = Label(self.query_plan_frame, text="Natural Language QEP2", fg="black", bg="cyan")
        self.query2_plane_label.grid(row=0, column=2, columnspan=2)
        self.query2_plane_textbox = ScrolledText(self.query_plan_frame, height=13,width=50, wrap=WORD)
        self.query2_plane_textbox.grid(row=1,column=2, columnspan=2)
        self.query2_plane_textbox.config(state=DISABLED)

        self.displayTreebtn1 = Button(self.query_plan_frame, text='Display QEP1 Tree', command=self.ShowTree1)
        self.displayTreebtn1.grid(row=2, column=1, sticky = 'w')

        self.displayTreebtn2 = Button(self.query_plan_frame, text='Display QEP2 Tree', command=self.ShowTree2)
        self.displayTreebtn2.grid(row=2, column=3, sticky = 'w')

        # self.question_label = Label(self.question_frame, text="Question the system", fg="black", bg="cyan")
        # self.question_label.grid(row=0, column=1, columnspan=2)
        # self.question_textbox = ScrolledText(self.question_frame, height=5, wrap=WORD)
        # self.question_textbox.grid(columnspan =4)
        # self.request_btn = Button(self.question_frame, text='Request', command=self.text_to_voice1)
        # self.request_btn.grid(row=2, column=1, sticky="e")
        # self.voice_text_btn = Button(self.question_frame, text='voice_text', command=self.voice_to_text)
        # self.voice_text_btn.grid(row=2, column=2, sticky="w")

        self.result_label = Label(self.result_frame, text="Result", fg="black", bg="cyan")
        self.result_label.grid(row=0, column=1, columnspan=2)
        self.result_textbox = ScrolledText(self.result_frame, height=7, width=103, wrap=WORD)
        self.result_textbox.grid(row =1, column=0, columnspan =4)
        self.compare_QEP_btn = Button(self.result_frame, text='Compare QEP 1 & 2', command=self.compareQuery)
        self.compare_QEP_btn.grid(row=2, column=1, sticky = 'e')
        self.text_voice_btn1 = Button(self.result_frame, text='Text_to_Voice', command=self.text_to_voice)
        self.text_voice_btn1.grid(row=2,column=2, sticky = 'w')
        
    def GUI_main(self, tableName, attr, comm):
        self.comm = comm
        self.marks = False
        self.main_screen = Tk()
        self.initialize()
        self.init_tables(tableName, attr)
        # self.open_nodes()
        w, h = self.main_screen.winfo_screenwidth(), self.main_screen.winfo_screenheight()
        self.main_screen.geometry("%dx%d+0+0" % (w, h))
        self.main_screen.title('CZ4031 GUI')
        self.main_screen.mainloop()
        print(self.marks)
        return self.marks
        # self.main_screen.quit()


