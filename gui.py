# https://www.pythontutorial.net/tkinter/tkinter-hello-world/
# pip3 install ttkthemes
# keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/
#TODO fixare bottone che si preme solo in focus

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

FONT = ("Monospace", 11)
PLACEHOLDER = "Inserisci un messaggio... "

def micToggle(event, input_sorce = "none"):
	global mic_status
	message = ttk.Label(root, font=FONT)
	print(input_sorce)	#debug
	print(event)	#debug
	if(mic_status):	#se il microfono è attivo
		mute_button.config(image = mic_off)	#cambia l'immagine
		mic_status = False	#setta il microfono come disattivo
		message.config(text = "listening no ")
	else:
		mute_button.config(image = mic_on)
		mic_status = True
		message.config(text = "listening yes")
	message.grid(column = 1, row = 1, sticky = "s")

def camToggle(event, input_sorce = "none"):
	global cam_status
	message = ttk.Label(root, font=FONT)
	print(input_sorce)	#debug
	print(event)	#debug
	if(cam_status):	#se la cam è attiva
		cam_button.config(image = cam_off)	#cambia l'immagine
		cam_status = False	#imposta la cam come disattivata
		message.config(text = "watching no ")
	else:
		cam_button.config(image = cam_on)
		cam_status = True
		message.config(text = "watching yes")
	message.grid(column = 1, row = 1, sticky = "sw")

def subtitlesToggle(event):
	global subtitles_status
	message = ttk.Label(root, font=FONT)
	print(event)	#debug
	if(subtitles_status):
		subtitles_button.config(image = subtitles_off)
		subtitles_status = False
		message.config(text = "subtitles no ")
	else:
		subtitles_button.config(image = subtitles_on)
		subtitles_status = True
		message.config(text = "subtitles yes")
	message.grid(column = 0, row = 0, sticky = "se")

def clearTextbox(event):
	global textbox, delete_text, text
	if (text.get() == PLACEHOLDER):
		textbox.delete(0, "end")	#!approfondire

def sendMessage(event):
	global textbox, text
	if (text.get() != PLACEHOLDER):	#quando viene premuto il bottone invia impedisce in inviare il placeholder
		#TODO invio del messaggio
		print(text.get())
	textbox.delete(0, "end")
	textbox.insert(0, PLACEHOLDER)

def addPlaceholder(event):
	global text, textbox
	if (text.get() == ""):
		textbox.insert(0, PLACEHOLDER)

if __name__ == "__main__":
	root = ThemedTk(theme = "breeze")	#finestra padre con tema breeze
	root.title("Mitis")
	width_screen = root.winfo_screenwidth()	# larghezza dello schermo
	heigth_screen = root.winfo_screenheight() # altezza dello schermo
	screen_size = str(width_screen) + "x" + str(heigth_screen)
	root.geometry(screen_size)
	root.minsize(800, 500)	#grandezza minima finestra

	#creazione delle colonne e delle righe
	root.columnconfigure(0, weight = 1)
	root.columnconfigure(1, weight = 15)
	root.columnconfigure(2, weight = 1)
	root.rowconfigure(0, weight = 10)
	root.rowconfigure(1, weight = 1)

	#creazione delle icone
	mic_off = tk.PhotoImage(file = "assets/mic_off.png")
	mic_on = tk.PhotoImage(file = "assets/mic.png")
	cam_off = tk.PhotoImage(file = "assets/cam_off.png")
	cam_on = tk.PhotoImage(file = "assets/cam.png")
	send = tk.PhotoImage(file = "assets/send_message.png")
	filters = tk.PhotoImage(file = "assets/filters.png")
	# mask = tk.PhotoImage(file = "assets/mask.png")	#TODO
	subtitles_off = tk.PhotoImage(file = "assets/subtitles_off.png")
	subtitles_on = tk.PhotoImage(file = "assets/subtitles.png")

	communication_tools = ttk.Frame(root)	#frame che contiene i bottoni per il mute e lo spegnimento della cam
	
	mic_status = False
	mute_button = ttk.Button(communication_tools, image = mic_off)
	mute_button.bind("<Control-m>", lambda event:micToggle(event, "il microfono è stato mutato dalla shortcut"))	#shortcut: ctrl + m
	mute_button.bind("<ButtonRelease>", lambda event:micToggle(event, "il microfono è stato mutato dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
	mute_button.focus()	#rende il bottone sotto focus di default (per far funzionare la shortcut il bottone deve essere in focus)
	mute_button.pack(side="right", padx = 5)

	cam_status = False
	cam_button = ttk.Button(communication_tools, image = cam_off)
	cam_button.bind("<Control-w>", lambda event:camToggle(event, "la webcam è stata mutata dalla shortcut"))	#shortcut: ctrl + m
	cam_button.bind("<ButtonRelease>", lambda event:camToggle(event, "la webcam è stata mutata dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
	cam_button.pack()

	communication_tools.grid(column = 1, row = 1, sticky="n")

	send_message = ttk.Frame(root)
	text = tk.StringVar()
	textbox = ttk.Entry(send_message, textvariable=text, width = 45, font = FONT)
	textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder #!approfondire
	textbox.bind("<FocusIn>", lambda event:clearTextbox(event))
	textbox.bind("<FocusOut>", lambda event:addPlaceholder(event))
	textbox.pack(side = "left", ipady = 3)

	test_button = ttk.Button(send_message, image = send)
	test_button.bind("<ButtonRelease>",lambda event : sendMessage(event))
	test_button.pack(padx = 5, pady = 1)
	send_message.grid(column = 2, row = 1, sticky = "ne")

	tools = ttk.Frame(root)	#frame che contiene tutti i tools

	subtitles_status = False
	filters_button= ttk.Button(tools, image = filters)
	mask_button= ttk.Button(tools, text = "maschere")
	subtitles_button= ttk.Button(tools, image = subtitles_off)
	subtitles_button.bind("<ButtonRelease>", lambda event: subtitlesToggle(event))

	filters_button.pack(side = "top", pady = 10)
	mask_button.pack(side = "top")
	subtitles_button.pack(side = "top", pady = 10)
	

	tools.grid(column = 0, row = 0, sticky = "e")

	# ttk.Label(root, text = "tools", background = "green", foreground = "white").grid(column = 0, row = 0, rowspan = 2, sticky="ewns")
	ttk.Label(root, text = "cam zone", background = "red", foreground = "white").grid(column = 1, row = 0, sticky="ewns")
	ttk.Label(root, text = "chat zone", background = "orange", foreground = "black").grid(column = 2, row = 0, sticky="ewns")
	# ttk.Label(root, background = "pink", foreground = "black").grid(column = 1, row = 1, sticky="ewns")
	# ttk.Label(root, text = "write message", background = "brown", foreground = "white").grid(column = 2, row = 1, sticky="ewns")
	
	root.mainloop() # visualizza la finestra

	# https://www.pythontutorial.net/tkinter/tkinter-grid/