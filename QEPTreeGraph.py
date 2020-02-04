import json
import os
from tkinter import *
from Node import Node

NODE_WIDTH = 90
NODE_HEIGHT = 65
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
node_list = []
# Maps GUI elements to logical elements
visual_to_node = {}
instance = None
MAX_DURATION=0

def enter(event,canvas):
    node = visual_to_node[event.widget.find_withtag("current")[0]]
    global instance
    if node.duration == MAX_DURATION:
        instance = canvas.create_text(200, 50, text=node.plan_info,
                                      fill="red", width=350)
    else:
        instance = canvas.create_text(200, 50, text=node.plan_info,
                                      fill="blue", width=350)

def leave(event,canvas):
    canvas.delete(instance)

def help(root):
    help_info = open("help_info.txt").read()
    help_window = Toplevel(root)
    help_window.geometry("800x820")
    help_window.title("Help")
    help_canvas = Canvas(help_window, width=800, height=820)
    help_canvas.pack()
    help_canvas.create_text(400, 420, text=help_info, width=800)

def draw_query_plan(data):
    '''
    Main method to be called to draw query plan
    :param data: json object
    '''
    print(data)
    node_list.clear()
    node_list.append(Node(0, CANVAS_WIDTH,10, NODE_HEIGHT))
    build_node_list(data, node_list[0])
    global MAX_DURATION
    MAX_DURATION=max([x.duration for x in node_list])
    # actual drawing
    root = Tk()
    root.geometry("1000x1000")
    root.title("Query execution plan")
    frame=Frame(root,width=1000,height=1000)
    frame.pack()
    canvas = Canvas(frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,scrollregion=(0,0,1000,1500))
    vbar = Scrollbar(frame, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=canvas.yview)
    canvas.config(yscrollcommand=vbar.set)
    canvas.pack()
    canvas2 = Canvas(frame, width=400, height=100)
    canvas2.pack()
    canvas2.place(x=600,y=0)
    canvas3 = Canvas(frame, width=100, height=50)
    canvas3.pack()
    help_button = Button(canvas3, command=lambda: help(root), text="Help", anchor=W)
    help_button.configure(width=5, activebackground="#33B5E5", relief=FLAT)
    canvas3.create_window(10, 10, anchor=NW, window=help_button)
    canvas3.place(x=0, y=0)
    Misc.lift(canvas2)
    Misc.lift(canvas3)
    Misc.lift(vbar)

    # 3 different for loops are needed for logical binding of rectangles in the node_list
    for element in node_list:
        x = element.center[0]
        y = element.center[1]
        rect = canvas.create_rectangle(x - NODE_WIDTH / 2, y + NODE_HEIGHT / 2, x + NODE_WIDTH / 2, y - NODE_HEIGHT / 2,
                                       fill='grey', tags="hover")
        visual_to_node[rect] = element

    for element in node_list:
        gui_text = canvas.create_text((element.center[0], element.center[1]), text=element.text, tags="clicked")
        visual_to_node[gui_text] = element

    for element in node_list:
        for child in element.children:
            canvas.create_line(child.center[0], child.center[1] - NODE_HEIGHT / 2, element.center[0],
                               element.center[1] + NODE_HEIGHT / 2, arrow=LAST)

    # canvas.tag_bind("clicked", "<Button-1>", lambda event: clicked(event, canvas=canvas2))
    canvas.tag_bind("hover","<Enter>",lambda event:enter(event,canvas=canvas2))
    canvas.tag_bind("hover", "<Leave>", lambda event: leave(event,canvas=canvas2))
    root.mainloop()

def build_node_list(plan, obj):
    '''
    Builds the list of nodes by recursively calling itself
    :param plan: plan dictionary
    :param obj: corresponding node object of plan
    '''
    print('ckpt')
    print(plan)
    obj.text = plan["Node Type"]
    # info=getInfo(plan)
    # obj.plan_info =info[0]
    # obj.duration=info[1]
    if "Plans" in plan.keys():
        x1, x2, y1, y2 = obj.x1, obj.x2, obj.y1, obj.y2
        no_children = len(plan['Plans'])
        for i in range(no_children):
            child_obj = Node((i) * ((x2 - x1) / no_children), (i + 1) * ((x2 - x1) / no_children), y2 + NODE_HEIGHT,
                             y2 + 2 * NODE_HEIGHT)
            node_list.append(child_obj)
            obj.children.append(child_obj)
            build_node_list(plan["Plans"][i], child_obj)





    
    # return (parsed_plan, '')
