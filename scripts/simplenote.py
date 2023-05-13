import modules.scripts as scripts
from pathlib import Path
import platform
import gradio as gr
import os
import pathlib
import glob
import re

from modules import script_callbacks


targetlist = [
    'Model',
    'Lora',
    'TextualInversion',
    'Hypernetworks',
]

def get_list(path):
    retlist = []

    for curDir, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pt") or file.endswith(".safetensors") or file.endswith(".ckpt"):
                retlist.append(file)
    return retlist

def change_type(modeldropdown, filtertextbox):
    # Change Dropdown and Clear Area
    datalist = []
    if modeldropdown == targetlist[0]:
        path = os.path.join(scripts.basedir(), "models", "Stable-diffusion")
        datalist = get_list(path)
    elif modeldropdown == targetlist[1]:
        path = os.path.join(scripts.basedir(), "models", "Lora")
        datalist = get_list(path)
    elif modeldropdown == targetlist[2]:
        path = os.path.join(scripts.basedir(), "embeddings")
        datalist = get_list(path)
    elif modeldropdown == targetlist[3]:
        path = os.path.join(scripts.basedir(), "models", "hypernetworks")
        datalist = get_list(path)
    else:
        datalist = []
        return "Unknown", gr.Dropdown.update(choices=datalist, value="")
    
    #filter
    if not filtertextbox == "":
        tmplist = []
        for dt in datalist:
            if re.search(filtertextbox.lower(), dt.lower()) is not None:
                tmplist.append(dt)
        datalist = tmplist

    return "", gr.Dropdown.update(choices=datalist, value="")



def change_note(modeldropdown, notedropdown):
    if notedropdown == "":
        return ""
    
    filename = os.path.basename(notedropdown) + ".txt"
    path = os.path.join(scripts.basedir(), "extensions", "sd-webui-simplenote", "notes", modeldropdown, filename)
    if not os.path.exists(path):
        f = open(path, 'w')
        f.close()

    f = open(path, 'r')
    txt = f.read()
    f.close()

    return txt


def save_note(modeldropdown, notedropdown, notetextarea):
    if notedropdown == "":
        return
    
    filename = os.path.basename(notedropdown) + ".txt"
    path = os.path.join(scripts.basedir(), "extensions", "sd-webui-simplenote", "notes", modeldropdown, filename)
    f = open(path, 'w')
    f.write(notetextarea)
    f.close()


def create_dir():
    path = os.path.join(scripts.basedir(), "extensions", "sd-webui-simplenote", "notes")
    if not os.path.exists(path):
        os.makedirs(path)
    
    for tar in targetlist:
        path = os.path.join(scripts.basedir(), "extensions", "sd-webui-simplenote", "notes", tar)
        if not os.path.exists(path):
            os.makedirs(path)    

    

def on_ui_tabs():
    create_dir()

    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            # Note Type
            modeldropdown = gr.Dropdown(label="Type", choices=targetlist, interactive=True)
            notedropdown = gr.Dropdown(label="Note", choices=[], interactive=True)
            filtertextbox = gr.Textbox(label="Search filter", value="", interactive=True)

        notetextarea = gr.Textbox(label="Text", value="", interactive=True, lines=20, max_lines=200)
        savebutton =gr.Button(value="Save")        

        modeldropdown.change(fn=change_type, inputs=[modeldropdown, filtertextbox], outputs=[notetextarea, notedropdown])
        notedropdown.change(fn=change_note, inputs=[modeldropdown, notedropdown], outputs=[notetextarea])
        savebutton.click(fn=save_note, inputs=[modeldropdown, notedropdown, notetextarea])
        filtertextbox.change(fn=change_type, inputs=[modeldropdown, filtertextbox], outputs=[notetextarea, notedropdown])

        return [(ui_component, "Simple Note", "simple_note")]

script_callbacks.on_ui_tabs(on_ui_tabs)