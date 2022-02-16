# https://www.pythontutorial.net/tkinter/tkinter-hello-world/
# pip3 install ttkthemes
# keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/
#TODO fixare bottone che si preme solo in focus

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

FONT = ("Monospace", 11)
PLACEHOLDER = "Inserisci un messaggio... "
mic_status = False
cam_status = False
subtitles_status = False

class Gui:
	def __init__(self):
		self.root = ThemedTk(theme = "breeze")	#finestra padre con tema breeze
		self.root.title("Mitis")
		self.width_screen = self.root.winfo_screenwidth()	# larghezza dello schermo
		self.heigth_screen = self.root.winfo_screenheight() # altezza dello schermo
		self.screen_size = str(self.width_screen) + "x" + str(self.heigth_screen)
		self.root.geometry(self.screen_size)
		self.root.minsize(800, 500)	#grandezza minima finestra

		#creazione delle colonne e delle righe
		self.root.columnconfigure(0, weight = 1)
		self.root.columnconfigure(1, weight = 15)
		self.root.columnconfigure(2, weight = 1)
		self.root.rowconfigure(0, weight = 10)
		self.root.rowconfigure(1, weight = 1)

		#creazione delle icone
		self.mic_off = tk.PhotoImage(file = "assets/mic_off.png")
		self.mic_on = tk.PhotoImage(file = "assets/mic.png")
		self.cam_off = tk.PhotoImage(file = "assets/cam_off.png")
		self.cam_on = tk.PhotoImage(file = "assets/cam.png")
		self.send = tk.PhotoImage(file = "assets/send_message.png")
		self.filters = tk.PhotoImage(file = "assets/filters.png")
		self.mask = tk.PhotoImage(file = "assets/mask.png")
		self.subtitles_off = tk.PhotoImage(file = "assets/subtitles_off.png")
		self.subtitles_on = tk.PhotoImage(file = "assets/subtitles.png")

		self.communication_tools = ttk.Frame(self.root)	#frame che contiene i bottoni per il mute e lo spegnimento della cam
		
		self.mute_button = ttk.Button(self.communication_tools, image = self.mic_off)
		self.mute_button.bind("<Control-m>", lambda event:self.micToggle(event, self.mute_button, self.mic_off, self.mic_on, "il microfono è stato mutato dalla shortcut"))	#shortcut: ctrl + m
		self.mute_button.bind("<ButtonRelease>", lambda event:self.micToggle(event,self.mute_button, self.mic_off, self.mic_on, "il microfono è stato mutato dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
		self.mute_button.focus()	#rende il bottone sotto focus di default (per far funzionare la shortcut il bottone deve essere in focus)
		self.mute_button.pack(side = "right", padx = 5)

		self.cam_button = ttk.Button(self.communication_tools, image = self.cam_off)
		self.cam_button.bind("<Control-w>", lambda event:self.camToggle(event, self.cam_button, self.cam_off, self.cam_on, "la webcam è stata mutata dalla shortcut"))	#shortcut: ctrl + m
		self.cam_button.bind("<ButtonRelease>", lambda event:self.camToggle(event, self.cam_button, self.cam_off, self.cam_on, "la webcam è stata mutata dal mouse"))	#chiama la funzione anche con il click del mouse quando rilasciato
		self.cam_button.pack()

		self.communication_tools.grid(column = 1, row = 1, sticky = "n")

		self.send_message_wrapper = ttk.Frame(self.root)
		self.text = tk.StringVar()
		self.textbox = ttk.Entry(self.send_message_wrapper, textvariable = self.text, width = 45, font = FONT)
		self.textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder
		self.textbox.bind("<FocusIn>", lambda event:self.clearTextbox(event, self.textbox, self.text))
		self.textbox.bind("<FocusOut>", lambda event:self.addPlaceholder(event, self.textbox, self.text))
		self.textbox.pack(side = "left", ipady = 3)

		self.send_button = ttk.Button(self.send_message_wrapper, image = self.send)
		self.send_button.bind("<ButtonRelease>",lambda event:self.sendMessage(event, self.textbox, self.text))
		self.send_button.pack(padx = 5, pady = 1)
		self.send_message_wrapper.grid(column = 2, row = 1, sticky = "ne")

		self.tools = ttk.Frame(self.root)	#frame che contiene tutti i tools

		self.filters_button= ttk.Button(self.tools, image = self.filters)
		self.mask_button= ttk.Button(self.tools, image = self.mask)
		self.subtitles_button= ttk.Button(self.tools, image = self.subtitles_off)
		self.subtitles_button.bind("<ButtonRelease>", lambda event:self.subtitlesToggle(event, self.subtitles_button, self.subtitles_off, self.subtitles_on))

		self.filters_button.pack(side = "top", pady = 10)
		self.mask_button.pack(side = "top")
		self.subtitles_button.pack(side = "top", pady = 10)
		

		self.tools.grid(column = 0, row = 0)

		# ttk.Label(self.root, text = "tools", background = "green", foreground = "white").grid(column = 0, row = 0, rowspan = 2, sticky="ewns")
		ttk.Label(self.root, text = "cam zone", background = "red", foreground = "white").grid(column = 1, row = 0, sticky="ewns")
		ttk.Label(self.root, text = "chat zone", background = "orange", foreground = "black").grid(column = 2, row = 0, sticky="ewns")
		# ttk.Label(self.root, background = "pink", foreground = "black").grid(column = 1, row = 1, sticky="ewns")
		# ttk.Label(self.root, text = "write message", background = "brown", foreground = "white").grid(column = 2, row = 1, sticky="ewns")

		# https://www.pythontutorial.net/tkinter/tkinter-grid/

	def micToggle(self, event, mute_button, mic_off, mic_on, input_source = "none"):
		global mic_status
		message = ttk.Label(self.root, font=FONT)
		print(input_source)	#debug
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

	def camToggle(self, event, cam_button, cam_off, cam_on, input_source = "none"):
		global cam_status
		message = ttk.Label(self.root, font=FONT)
		print(input_source)	#debug
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

	def subtitlesToggle(self, event, subtitles_button, subtitles_off, subtitles_on):
		global subtitles_status
		message = ttk.Label(self.root, font = FONT)
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

	def clearTextbox(self, event, textbox, text):
		if (text.get() == PLACEHOLDER):
			textbox.delete(0, "end")	#elimina tutto il contenuto

	def sendMessage(self, event, textbox, text):
		if (text.get() != PLACEHOLDER):	#quando viene premuto il bottone invia impedisce in inviare il placeholder
			#TODO invio del messaggio
			print(text.get())
		textbox.delete(0, "end")
		textbox.insert(0, PLACEHOLDER)

	def addPlaceholder(self, event, textbox, text):
		if (text.get() == ""):
			textbox.insert(0, PLACEHOLDER)