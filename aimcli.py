import json
import subprocess
import argparse
import sys
import os
scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
version = "18.10.23"
def getConfig():
	try:
		with open(scriptdir+"config.json") as f:
			return json.load(f)
	except:
		open(scriptdir+"config.json", 'w+').close()
		data = {}
		data["apps_path"] = scriptdir+"/apps/"
		subprocess.run(['mkdir', scriptdir+'apps/'])
		data["downloads_path"] = ""
		data["cli_quit_when_run"] = "true"
		dumpConfig(data)
		with open(scriptdir+"config.json") as f:
			return json.load(f)
		
def setConfig(key:str, value):
	try:
		data = getConfig()
		data[key] = value
		with open(scriptdir+'config.json', "w") as s:
			json.dump(data, s, indent=4, sort_keys=True)
	except:
		open(scriptdir+"config.json", 'w+').close()
		with open(scriptdir+"config.json") as f:
			return json.load(f)
		
def dumpConfig(data):
	try:
		with open(scriptdir+'config.json', "w") as s:
			json.dump(data, s, indent=4, sort_keys=True)
	except:
		open(scriptdir+"config.json", 'w+').close()
		with open(scriptdir+"config.json") as f:
			json.dump(data, s, indent=4, sort_keys=True)
		
def process_command(command):
	if command[0] == "install":
		install()
	
	elif command[0] == "find":
		try:
			find(command[1])
		except IndexError:
			find()
			
	elif command[0] == "run":
		try:
			run(command[1])
		except:
			print("No app name given.")
			
	elif command[0] == "delete":
		try:
			delete(command[1])
		except:
			print("No app name given.")	
	
	elif command[0] == "set":
		try:
			setConfig(command[1], command[2])
			print(f"Value {command[1]} set: {getConfig()[command[1]]}")
		except:
			print("Missing something; set <key> <value>")	
			
	elif command[0] == "get":
		try:
			v = getConfig()[command[1]]
			print(v)
		except IndexError:
			print("Missing key name; get <key>")
		except KeyError:
			print("Value not found.")
			
	elif command[0] == "help":
		print("===========================")
		print("AppImage-CLI "+version)
		print("")
		print("Use any of these commands as the launch argument for this script.\n")
		print("install: Checks the download directory for appimages and moves them to the apps directory.\n")
		print("run <appname>: Runs the app from the apps directory. Only partial name is required, e.i. run yout > this will find any file with yout in the name, like youtube.\n")
		print("find <optional appname>: Searches app directory for apps. If no name is supplied, lists all. If a name is given, will find all apps with a matching name.")
		print("set <key> <value>: Sets the config variables.")
		print("get <key>: Shows the config value.")
		print("delete <appname>: Deletes the app from the apps directory. Only partial name is required.\n")
		print("help: This help menu... not that you needed this help menu to tell you that it was a help menu, but thats just a thing help menus seem to do. Hi, I'm a help menu, I'm here to help. But I can't help you with help, I can only help those who help themself...... help me.")
		print("===========================")
		
def install():
	pth = getConfig()['downloads_path']
	to_pth = getConfig()['apps_path']
	files = []
	for file in os.listdir(pth):
		filename = os.fsdecode(file)
		if filename.lower().endswith(".appimage"):
			files.append(filename)
	
	fstr = ', '.join(files)	
	
	while True:
		r = input(f"Install these files? ({fstr}) y/n\n")
		if r == "n":
			print("Cancelling.")
			break
		elif r == "y":
			print("Begin install...")
			for filename in files:
				os.rename(pth+filename, to_pth+filename)
				print("Installing "+filename+"\n")
			break
		else:
			print("Respond with either y or n.")
		
	
def find(appname = ""):
	pth = getConfig()['apps_path']
	print("=======================================")
	if appname == "":
		for file in os.listdir(pth):
			filename = os.fsdecode(file)
			if filename.lower().endswith(".appimage"):
				print(filename)
	else:
		for file in os.listdir(pth):
			filename = os.fsdecode(file)
			if filename.lower().endswith(".appimage") and appname.lower() in filename.lower():
				print(filename)
	print("=======================================")
	
def run(app):
	pth = getConfig()['apps_path']
	print(f"Runing {app}")
	if ".appimage" not in app.lower():
		print(f"Finding closest match to {app}.")
		for file in os.listdir(pth):
			filename = os.fsdecode(file)
			if filename.lower().endswith(".appimage") and app.lower() in filename.lower():
				app = filename
				print(f"Matched with {app}")
				break
	try:
		subprocess.Popen(getConfig()['apps_path']+app)
			
	except PermissionError:
		print(f"Setting executable permissions for {app}...")
		subprocess.run(['chmod', 'u+x', getConfig()['apps_path']+app])
		subprocess.Popen(getConfig()['apps_path']+app)
		
	except Exception as e:
		print(e)
		
def delete(app):
	print(f"Del {app}")

def cliloop(command):
	subprocess.run(['clear'])
	while True:
		print("AppImage Manager\nInteractive Mode. ('exit' or 'quit' to close. Clear the terminal text with 'clear'.)")
		f = input("Input command: ")
		command = f.split(" ")
		if command[0] == "exit" or command[0] == "quit":
			break
		if command[0] == "clear":
			subprocess.run(['clear'])
		
		process_command(command)
		if command[0] == "run" and getConfig()['cli_quit_when_run'].lower() == "true":
			break
			
if __name__ == "__main__":
	command = sys.argv[1:]

	
	if len(command) > 0:
		process_command(command)
	else:
		subprocess.run(['clear'])
		while True:
			print("AppImage Manager\nInteractive Mode. ('exit' or 'quit' to close. Clear the terminal text with 'clear'.)")
			f = input("Input command: ")
			command = f.split(" ")
			if command[0] == "exit" or command[0] == "quit":
				break
			if command[0] == "clear":
				subprocess.run(['clear'])
			
			process_command(command)
			if command[0] == "run" and getConfig()['cli_quit_when_run'].lower() == "true":
				break
