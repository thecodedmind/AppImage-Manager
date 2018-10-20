from tkinter import ttk, filedialog
import json
from functools import partial
import tkinter.messagebox
import socket
import subprocess
import os
version = "18.10.18"
appgui = None
checkbox_show_grouped = False
scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
def getConfig():
	with open("config.json") as f:
		return json.load(f)

def setConfig(key:str, value):
	data = getConfig()
	data[key] = value
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def dumpConfig(data):
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)
	
def internet(host="8.8.8.8", port=53, timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		print( ex)
		return False
		
def commit_cfg(root, downloads_entry, apps_entry):
	print(downloads_entry.get())
	print(apps_entry.get())
	dl = downloads_entry.get()
	apps = apps_entry.get()
	if not dl.endswith("/"):
		dl = dl+"/"
	if not apps.endswith("/"):
		apps = apps+"/"
	setConfig('downloads_path', dl)
	setConfig('apps_path', apps)
	root.destroy()
	
def browser(entry):
	old = entry.get()
	if old != "":
		fpath = filedialog.askdirectory(initialdir=old)
	else:
		fpath = filedialog.askdirectory()
	
	fpath = fpath+"/"
	entry.delete(0, 'end')	
	entry.insert(0, fpath)
	
def open_config_win():
	w = tkinter.Tk()
	w.title("Config")
	basecfg = getConfig()
	en_lab = tkinter.Label(w, text="Downloads path: ")
	en = tkinter.Entry(w, width=50)
	en2_lab = tkinter.Label(w, text="AppImages storage path: ")
	en2 = tkinter.Entry(w, width=50)
	cp = partial(commit_cfg, w, en, en2)
	browse_dl = partial(browser, en)
	browse_apps = partial(browser, en2)
	en1_but = tkinter.Button(w, text="...", command=browse_dl)
	en2_but = tkinter.Button(w, text="...", command=browse_apps)
	en_but = tkinter.Button(w, text="Save", command=cp)
	en_lab.grid(row=0, column=0)
	en2_lab.grid(row=1, column=0)
	en.grid(row=0, column=1)
	en2.grid(row=1, column=1)
	en_but.grid(row=2, column=0)
	en1_but.grid(row=0, column=2)
	en2_but.grid(row=1, column=2)
	
	en.insert(0, basecfg['downloads_path'])
	en2.insert(0, basecfg['apps_path'])

def chkgrp():
	global checkbox_show_grouped
	if checkbox_show_grouped:
		checkbox_show_grouped = False
	else:
		checkbox_show_grouped = True
	
def refresh_apps():
	print("refreshing")
	pth = getConfig()['apps_path']
	groups = getConfig()['groups']
	for item in appgui.appscat.tabs():
		appgui.appscat.forget(item)
		
	appgui.mainframe = ttk.Frame(appgui.appscat)
	
	appgui.apps = tkinter.Listbox(appgui.mainframe, width=30, height=20)
	appgui.appscat.add(appgui.mainframe, text="Main")
	appgui.modules_scroll = tkinter.Scrollbar(appgui.mainframe)
	appgui.modules_scroll.grid(column=1, row=0, rowspan=10, sticky="ns")
	appgui.modules_scroll.config(command=appgui.apps.yview)
	appgui.apps.config(yscrollcommand=appgui.modules_scroll.set)	
	appgui.apps.bind('<<ListboxSelect>>', onselect)
	appgui.apps.grid(column=0, row=0, rowspan=10)
	cats = {}
	for item in groups:
		if len(groups[item]) > 0:
			gf = ttk.Frame(appgui.appscat)
			apps = tkinter.Listbox(gf, width=30, height=20)
			apps.grid(column=0, row=0, rowspan=10)
			modules_scroll = tkinter.Scrollbar(gf)
			modules_scroll.grid(column=1, row=0, rowspan=10, sticky="ns")
			modules_scroll.config(command=apps.yview)
			apps.config(yscrollcommand=modules_scroll.set)	
			apps.bind('<<ListboxSelect>>', onselect)
			appgui.appscat.add(gf, text=item)
			cats[item] = apps
	
	print(cats)
	appgui.apps.delete(0, tkinter.END)
	count = 0
	applist = []
	for file in os.listdir(pth):
		count += 1
		filename = os.fsdecode(file)
		if filename.lower().endswith(".appimage"):
			applist.append(filename)
	
	for item in sorted(applist, reverse=True):
		#print(item)
		grouped = False
		for group in groups:
			#print(groups[group])
			if item in groups[group]:
				cats[group].insert(0, item)
				grouped = True
				
		if not grouped:
			appgui.apps.insert(0, item)	
		elif checkbox_show_grouped:
			appgui.apps.insert(0, item)	
	appgui.infolab.config(text=f"{count} appimages found.")
		
def run_app():
	try:
		index = int(appgui.apps.curselection()[0])
	except IndexError:
		return
	name = appgui.apps.get(index)
	if tkinter.messagebox.askokcancel(title=f"Run {name}", message=f"Launch {name}?"):
		#os.popen(getConfig()['apps_path']+name)
		try:
			subprocess.Popen(getConfig()['apps_path']+name)
		except PermissionError:
			tkinter.messagebox.showerror(message=f"Setting executable permissions for {name}...")
			subprocess.run(['chmod', 'u+x', getConfig()['apps_path']+name])
			subprocess.Popen(getConfig()['apps_path']+name)

def set_group(root, new_group, app):
	print(app+" to "+new_group)
	try:
		groups = getConfig()['groups']
	except:
		setConfig('groups', {})
		groups = {}
	
	try:
		cur_group = groups[new_group]
	except:
		cur_group = []
	
	if app in cur_group:
		tkinter.messagebox.showerror(message="Item is already in this group.")
		return
	cur_group.append(app)
	groups[new_group] = cur_group
	setConfig('groups', groups)
	root.destroy()
	
def set_group_en(root, en, app):
	new_group = en.get()
	print(app+" to "+new_group)
	try:
		groups = getConfig()['groups']
	except:
		setConfig('groups', {})
		groups = {}
	
	try:
		cur_group = groups[new_group]
	except:
		cur_group = []
	
	if app in cur_group:
		tkinter.messagebox.showerror(message="Item is already in this group.")
		return
	cur_group.append(app)
	groups[new_group] = cur_group
	setConfig('groups', groups)
	root.destroy()
	
def group_app():
	try:
		index = int(appgui.apps.curselection()[0])
	except IndexError:
		return
	
	name = appgui.apps.get(index)
	w = tkinter.Tk()
	w.title("Group")
	en = tkinter.Entry(w)
	#en.grid()
	setcat1 = partial(set_group_en, w, en, name)
	bu = tkinter.Button(w, text="Enter", command=setcat1)
	bu.grid(row=0, column=1)
	g = getConfig()['groups']
	i = 0
	for item in g:
		setcat = partial(set_group, w, item, name)
		be = tkinter.Button(w, text=item, command=setcat)
		be.grid(row=2, column=i)
		i += 1
	en.grid(row=0, column=0, columnspan=i)
	bu.grid(row=0, column=i+1)
	
def remove_group(root, apps, group):
	try:
		index = int(apps.curselection()[0])
	except IndexError:
		return
	
	name = apps.get(index)
	print(name)
	
	g = getConfig()['groups']
	if name in g[group]:
		g[group].remove(name)
		setConfig('groups', g)
	
	root.destroy()
	
def group_man(root, group):
	try:
		g = getConfig()['groups'][group]
		w = tkinter.Tk()
		w.title(group)
		apps = tkinter.Listbox(w, width=30, height=20)
		apps.grid(column=0, row=0, rowspan=10)
		modules_scroll = tkinter.Scrollbar(w)
		modules_scroll.grid(column=1, row=0, rowspan=10, sticky="ns")
		modules_scroll.config(command=apps.yview)
		apps.config(yscrollcommand=modules_scroll.set)	
		apps.bind('<<ListboxSelect>>', onselect)
		for item in g:
			apps.insert(0, item)
		remcat = partial(remove_group, w, apps, group)
		del_but = tkinter.Button(w, text="Remove", command=remcat)
		del_but.grid(row=11)
		root.destroy()
		
	except Exception as e:
		tkinter.messagebox.showerror(message=e)

def group_man_main():
	w = tkinter.Tk()
	w.title("Group")
	g = getConfig()['groups']
	i = 0
	for item in g:
		if len(g[item]) > 0:
			setcat = partial(group_man, w, item)
			bu = tkinter.Button(w, text=item, command=setcat)
			bu.grid(row=0, column=i)
			i += 1
	
def delete_app():
	try:
		index = int(appgui.apps.curselection()[0])
	except IndexError:
		return
	name = appgui.apps.get(index)
	if tkinter.messagebox.askokcancel(title=f"Delete {name}", message=f"Permenantly delete {name} from system?"):
		res = subprocess.run(["rm", getConfig()['apps_path']+name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		output = str(res.stdout,"latin-1")
		output += str(res.stderr,"latin-1")
		if output != "":
			tkinter.messagebox.showinfo(message=output)
	
def install_apps():
	master = tkinter.Tk()
	master.geometry("580x360")
	S = tkinter.Scrollbar(master)
	
	S.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
	T = tkinter.Text(master, height=20, width=70)
	T.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.YES)
	S.config(command=T.yview)
	T.config(yscrollcommand=S.set)	
	
	master.title("Updating")
	#master.mainloop()
	T.insert('1.0',"Starting update.\n")
	pth = getConfig()['downloads_path']
	to_pth = getConfig()['apps_path']

	files = []
	for file in os.listdir(pth):
		filename = os.fsdecode(file)
		if filename.lower().endswith(".appimage"):
			files.append(filename)
	
	fstr = ', '.join(files)	

	if len(files) > 0:
		T.insert('1.0', "Install "+fstr+"\n")
		if tkinter.messagebox.askyesno(message="Install these apps? (Refer to output window for list)"):
			for file in os.listdir(pth):
				filename = os.fsdecode(file)
				if filename.lower().endswith(".appimage"):
					os.rename(pth+filename, to_pth+filename)
					T.insert('1.0', "Installing "+filename+"\n")
			
			T.insert('1.0', "Done.")
			
	refresh_apps()
	
def onselect(evt):
	w = evt.widget
	try:
		index = int(w.curselection()[0])
	except IndexError:
		return
	appgui.infolab.config(text=w.get(index))	
		
class GuiMan:
	def __init__(self):
		self.online = internet()
		self.mainwin = tkinter.Tk()
		self.appscat = ttk.Notebook(self.mainwin)
		
		self.mainframe = ttk.Frame(self.appscat)
		
		self.apps = tkinter.Listbox(self.mainframe, width=30, height=20)
		self.appscat.add(self.mainframe, text="Main")
		self.modules_scroll = tkinter.Scrollbar(self.mainframe)
		self.modules_scroll.grid(column=1, row=0, rowspan=10, sticky="ns")
		self.modules_scroll.config(command=self.apps.yview)
		self.apps.config(yscrollcommand=self.modules_scroll.set)	
		self.apps.bind('<<ListboxSelect>>', onselect)
		self.b_cfg = tkinter.Button(self.mainwin, text="Config", command=open_config_win, cursor="hand1", width=10)
		self.b_ref = tkinter.Button(self.mainwin, text="Refresh", command=refresh_apps, cursor="hand1", width=10)
		self.b_run = tkinter.Button(self.mainwin, text="Run", command=run_app, cursor="hand1", width=10)
		self.b_del = tkinter.Button(self.mainwin, text="Delete", command=delete_app, cursor="hand1", width=10)
		self.b_ins = tkinter.Button(self.mainwin, text="Install...", 
command=install_apps, cursor="hand1", width=10)
		self.b_grp = tkinter.Button(self.mainwin, text="Group...", 
command=group_app, cursor="hand1", width=5)
		self.b_gman = tkinter.Button(self.mainwin, text="Edit", 
command=group_man_main, cursor="hand1", width=5)
		self.infolab = tkinter.Label(self.mainwin, text="Selected info will appear here.")
		self.infolab.grid(row=11, columnspan=6)
		self.apps.grid(column=0, row=0, rowspan=10)
		self.appscat.grid(column=0, row=0, rowspan=10)
		#self.mainframe.grid(column=0, row=0)
		self.b_cfg.grid(column=2, row=0, columnspan=2)
		self.b_ref.grid(column=2, row=1, columnspan=2)
		self.b_run.grid(column=2, row=2, columnspan=2)
		self.b_del.grid(column=2, row=3, columnspan=2)
		self.b_ins.grid(column=2, row=4, columnspan=2)
		self.b_grp.grid(column=2, row=5)
		self.b_gman.grid(column=3, row=5)
		self.chk = tkinter.Checkbutton(self.mainwin, text="Show grouped apps", command=chkgrp)
		self.chk.grid(row=6, column=2, columnspan=2)
		self.mainwin.title("AppImage Manager")
		self.config = getConfig()		
		imgicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'icon.png'))
		self.mainwin.tk.call('wm', 'iconphoto', self.mainwin, imgicon)  
		
								
appgui = GuiMan()	
appgui.mainwin.mainloop()
