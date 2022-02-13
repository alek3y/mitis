# https://www.pythontutorial.net/tkinter/tkinter-hello-world/
#temi: breeze-dark, yaru
# pip3 install ttkthemes
# temi: https://ttkthemes.readthedocs.io/en/latest/example.html
# keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/

#TODO fixare bottone che si preme solo in focus
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import time

FONT = ("Monospace", 16)
PLACEHOLDER = "Inserisci un messaggio... "

def hello(event, stringa = "ciao"):
	global mic_state
	message = ttk.Label(root, font=FONT)
	print(stringa)	#debug
	print(event)	#debug
	if(mic_state):	#se il microfono è attivo
		mute_button.config(image = mic_off)	#cambia l'immagine
		mic_state = False	#setta il microfono come disattivo
		message.config(text = "muted")
	else:
		mute_button.config(image = mic_on)
		mic_state = True
		message.config(text = "unmuted")
	message.grid(column = 1, row = 1, sticky = "s")

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


	mic_off = tk.PhotoImage(file = "assets/mute.png")
	mic_on = tk.PhotoImage(file = "assets/unmute.png")
	mic_state = False

	communication_tools = ttk.Frame(root)	#frame che contiene i bottoni per il mute e lo spegnimento della cam

	cam_button = ttk.Button(communication_tools, text = "cam on/off")
	mute_button = ttk.Button(communication_tools, image = mic_off)
	mute_button.bind("<Control-m>", lambda event:hello(event, "il microfono è stato mutato dalla shortcut"))	#shortcut: ctrl + m
	mute_button.bind("<ButtonRelease>", lambda event:hello(event, "il microfono è stato mutato dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
	mute_button.focus()	#rende il bottone sotto focus di default (per far funzionare la shortcut il bottone deve essere in focus)
	
	mute_button.pack(side="right", padx = 5)
	cam_button.pack()

	communication_tools.grid(column = 1, row = 1, sticky="n")

	send_message = ttk.Frame(root)
	text = tk.StringVar()
	textbox = ttk.Entry(send_message, textvariable=text, width = 50)
	textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder #!approfondire
	textbox.bind("<FocusIn>", lambda event:clearTextbox(event))
	textbox.bind("<FocusOut>", lambda event:addPlaceholder(event))
	textbox.pack(side = "left")

	test_button = ttk.Button(send_message, text = "invia")
	test_button.bind("<ButtonRelease>",lambda event : sendMessage(event))
	test_button.pack(padx = 5, pady = 1)
	send_message.grid(column = 2, row = 1, sticky = "ne")

	tools = ttk.Frame(root)	#frame che contiene tutti i tools

	filters_button= ttk.Button(tools, text = "filtri")
	mask_button= ttk.Button(tools, text = "maschere")
	freeze_button= ttk.Button(tools, text = "freeze")

	filters_button.pack(side = "top", pady = 10)
	mask_button.pack(side = "top")
	freeze_button.pack(side = "top", pady = 10)

	tools.grid(column = 0, row = 0, sticky = "e")

	# ttk.Label(root, text = "tools", background = "green", foreground = "white").grid(column = 0, row = 0, rowspan = 2, sticky="ewns")
	ttk.Label(root, text = "cam zone", background = "red", foreground = "white").grid(column = 1, row = 0, sticky="ewns")
	ttk.Label(root, text = "chat zone", background = "orange", foreground = "black").grid(column = 2, row = 0, sticky="ewns")
	# ttk.Label(root, background = "pink", foreground = "black").grid(column = 1, row = 1, sticky="ewns")
	# ttk.Label(root, text = "write message", background = "brown", foreground = "white").grid(column = 2, row = 1, sticky="ewns")
	
	root.mainloop() # visualizza la finestra

	# https://www.pythontutorial.net/tkinter/tkinter-grid/