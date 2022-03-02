# # https://www.pythontutorial.net/tkinter/tkinter-hello-world/
# # https://www.pythontutorial.net/tkinter/tkinter-grid/
# # pip3 install ttkthemes
# # pip3 install pillow
# pip3 install imutils
# pip3 install opencv-python
# # keybinds: https://www.pythontutorial.net/tkinter/tkinter-event-binding/
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw, ImageFont
from ttkthemes import ThemedTk
import io
import math

FONT = ("Monospace", 11)
FONT_IMAGE = ImageFont.truetype("assets/DejaVuSansMono.ttf", 12)	#font dell'etichetta
PLACEHOLDER = "Inserisci un messaggio... "
mic_status = True
cam_status = True
subtitles_status = False
mask_status = False
filters_status = False

class PhotoImage(ImageTk.PhotoImage):
	def __del__(self):
		try:
			super().__del__()
		except Exception:
			pass

class Gui:
	#roomJoiner: comunica al client la stanza a cui unirsi (il client lo invierà poi al server)
	#messageHandler: comunicazione tra gui e client per l'invio dei messaggi
	#muteHandler: comunicazione tra gui e client per comunicare lo stato del microfono
	#camHandler: per comunicare lo stato della cam
	def __init__(self, roomJoiner, messageHandler, muteHandler, camHandler):
		self.grid_size = 1	#numero di righe e di colonne delle cam (dato che è un quadrato: colonne = righe)
		self.counter_size = 1
		self.cams_container = None
		self.temp_client_list = []	#lista che conterrà le webcam temporanee durante la crezione della root
		self.cams = {}	#dizionario che conterrà le webcam dei client presenti
		self.roomJoiner = roomJoiner
		self.messageHandler = messageHandler
		self.muteHandler = muteHandler
		self.camHandler = camHandler
		self.mask = ""	#contiene il nome della maschera attiva
		self.filters = []	#lista che contiene i filtri attivi
		self.last_talker = ""	#indica a quale client appartengono gli ultimi sottotitoli
		self.line1 = ""	#prima riga di sottotitoli
		self.line2 = "" #seconda riga di sottotitoli
		self.root = ThemedTk(theme = "breeze")	#finestra padre con tema breeze
		self.root.title("Mitis")
		self.width_screen = self.root.winfo_screenwidth()	# larghezza dello schermo
		self.height_screen = self.root.winfo_screenheight() # altezza dello schermo
		# self.root.geometry(f"{self.width_screen}x{self.height_screen}")
		self.root.attributes('-zoomed', True)
		self.root.minsize(704, 396)	#grandezza minima finestra
		self.actual_window_width = self.width_screen
		self.actual_window_height = self.height_screen

		self.dialog = ttk.Frame(self.root)
		dialog_text = ttk.Label(self.dialog, text = "Inserisci codice stanza:", font = FONT)
		dialog_text.pack()
		room_code = tk.StringVar()
		self.input_entry= ttk.Entry(self.dialog, textvariable = room_code, font = FONT)
		self.input_entry.focus()
		self.input_entry.pack(side = "left", ipady = 3)
		self.key = tk.PhotoImage(file = "assets/key.png")
		self.submit = ttk.Button(self.dialog, image = self.key)
		self.root.bind("<Return>", lambda event:self.getJoinCode(event, room_code))
		self.submit.bind("<ButtonRelease>", lambda event:self.getJoinCode(event, room_code))
		self.submit.pack(side = "right", padx = 2)
		self.error = ttk.Label(self.dialog, text = "", foreground = "red", font = FONT)
		self.error.pack()
		self.dialog.pack(expand = True)

	def resizeWindow(self, event):
		if event.widget == self.root:
			self.actual_window_height = event.height
			self.actual_window_width = event.width
			self.textbox["width"] = int(1/49 * event.width)
			self.text_chat["width"] = int(1/35 * event.width)
			self.text_chat["height"] = int(2/37 * event.height)
			self.text_chat.see("end")
			self.updateCam()

	def micToggle(self, event, mute_button, mic_off, mic_on):
		global mic_status
		if(mic_status):	#se il microfono è attivo
			mute_button.config(image = mic_off)	#cambia l'immagine
			mic_status = False	#setta il microfono come disattivo
		else:
			mute_button.config(image = mic_on)
			mic_status = True
		self.muteHandler()

	def camToggle(self, event, cam_button, cam_off, cam_on):
		global cam_status
		if(cam_status):	#se la cam è attiva
			cam_button.config(image = cam_off)	#cambia l'immagine
			cam_status = False	#imposta la cam come disattivata
		else:
			cam_button.config(image = cam_on)
			cam_status = True
		self.camHandler()

	def subtitlesToggle(self, event, subtitles_button, subtitles_off, subtitles_on):
		global subtitles_status
		if(str(subtitles_button["state"]) != "disabled"):
			if(subtitles_status):
				subtitles_button.config(image = subtitles_off)
				subtitles_status = False
				self.subtitle["text"] = ""
			else:
				subtitles_button.config(image = subtitles_on)
				subtitles_status = True

	def placeSubtitle(self, name, line):
		global subtitles_status
		if subtitles_status:
			if (not line):	#se il sottotitolo è vuoto non fa nulla
				pass
			elif (len(line) + len(self.subtitle["text"]) > 45 or self.last_talker != name):	#se la lughezza è troppo lunga o se è un altro client a parlare
				if (not self.line1):	#se la prima riga del sottotitolo è vuota
					self.line1 = line
					self.subtitle["text"] = name + ": " + self.line1	#stampa nella prima riga
				elif (not self.line2):	#se la seconda è vuota
					self.line2 = line
					self.subtitle["text"] += "\n" + name + ": " + self.line2 	#lascia la prima e scrive nella seconda
				else:	#se entrambe contengono testo
					self.line1 = self.line2	#la prima diventa la seconda
					self.line2 = line	#la seconda diventa la nuova
					self.subtitle["text"] = self.last_talker + ": " + self.line1 + "\n" + name + ": " + self.line2	#la seconda va in cima e l'ultima va alla seconda riga
			
			elif (not self.subtitle["text"]):	#se il sottotitolo precedente è vuoto
				self.subtitle["text"] += name + ": " + line
			else:
				self.subtitle["text"] += " " + line	#appende il sottotitolo a quello precedente
		self.last_talker = name

	def clearTextbox(self, event, text):
		if (text.get() == PLACEHOLDER):
			self.textbox.delete(0, "end")	#elimina tutto il contenuto

	def receiveMessage(self, name, message):
		self.text_chat.configure(state = 'normal')
		self.text_chat.insert("end", "<" + name + "> " + message + "\n")
		self.text_chat.configure(state = 'disabled')
		self.text_chat.see("end")

	#invio del messaggio nella chat di testo
	def sendMessage(self, event, text):
		if (text.get() != PLACEHOLDER and text.get()):	#quando viene premuto il bottone invia impedisce in inviare il placeholder o una stringa vuota
			self.messageHandler(text.get())
			self.text_chat.configure(state = 'normal')
			self.text_chat.insert("end", "<Tu> " + text.get() + "\n")
			self.text_chat.configure(state = 'disabled')
			self.text_chat.see("end")
			self.textbox.delete(0, "end")

	def addPlaceholder(self, event, text):
		if (not text.get()):
			self.textbox.insert(0, PLACEHOLDER)

	#invia il codice della stanza al server
	def getJoinCode(self, event, room_code):
		self.error.config(text = "")
		self.error.update()
		if (room_code.get() != "" and str(self.submit["state"]) != "disabled"):
			self.submit["state"] = "disabled"
			self.input_entry["state"] = "disabled"
			self.roomJoiner(room_code.get())

	#mostra un messaggio di errore nel caso non si riesca a unirsi ad una stanza
	def failJoin(self):
		self.error.config(text = "ERRORE: il server non risponde")
		self.submit["state"] = "enabled"
		self.input_entry["state"] = "enabled"

	#aggiorna l'immagine di una webcam
	def updateCam(self, client_id = "", new_image_frame = None):
		try:
			self.cam_size = (int(math.ceil(16 * (40 - math.log(self.grid_size**2) * 8 - (self.width_screen / (self.actual_window_width/7))))),
							int(math.ceil(9 * (40 - math.log(self.grid_size**2) * 6 - (self.height_screen / (self.actual_window_height/6))))))	#decide la grandezza delle webcam
			if(self.cam_size[0] < 32 or self.cam_size[1] < 18):
				self.cam_size = (32, 18)

			temp_cams = list(self.cams.keys())
			x, y = (1, 0)	#coordinate iniziali (alto-sinistra) per la creazione dell'etichetta della webcam

			if (not client_id and not new_image_frame):	#si avvera quando la funzione viene chiamata da resizeWindow
				for cam in temp_cams:	#aggiorna tutte le webcam
					if(cam in self.cams and self.cams[cam].image):
						new_image = ImageTk.getimage(self.cams[cam].image)
						new_image = new_image.resize(self.cam_size)
						w, h = FONT_IMAGE.getsize(cam)
						client_name = ImageDraw.Draw(new_image, "RGBA")
						client_name.rectangle((0, 0, 2 + w, h), fill = (0, 0, 0, 70))	#sfondo etichetta
						client_name.text((x, y), cam, fill = "white", font = FONT_IMAGE) #testo etichetta
						new_frame = PhotoImage(image = new_image)
						self.cams[cam].config(image = new_frame)
						self.cams[cam].image = new_frame

			else:	#aggiorna una webcam specifica
				if not client_id:
					client_id = "Tu"
				if(client_id in self.cams):
					new_image = Image.open(io.BytesIO(new_image_frame))	#converto da byte a immagine con PIL
					new_image = new_image.resize(self.cam_size)
					w, h = FONT_IMAGE.getsize(client_id)	#ottengo la dimensione per lo spazion dell'id
					client_name = ImageDraw.Draw(new_image, "RGBA")
					client_name.rectangle((0, 0, 2 + w, h), fill = (0, 0, 0, 70))	#sfondo etichetta
					client_name.text((x, y), client_id, fill = "white", font = FONT_IMAGE) #testo etichetta
					new_frame = PhotoImage(image = new_image)
					self.cams[client_id].config(image = new_frame)
					self.cams[client_id].image = new_frame
		except RuntimeError as e:	#client eliminato durante il refresh dell'immagine
			pass
		except KeyError as e:	#client eliminato durante il refresh dell'immagine
			pass
		except AttributeError as e:	#byte dell'immagine non valdi
			pass

	#viene a conoscenza dell'aggiunta di un nuovo client
	def addCam(self, client_id):
		if not client_id:
			client_id = "Tu"
		if not self.cams_container:	#se la root non è pronta
			self.temp_client_list.append(client_id)	#salva il client appena collegato in una lista temporanea
		else:
			self.layoutCam(client_id)

	#aggiunge la nuova webcam alla lista di client
	def layoutCam(self, client_id):
		self.cams[client_id] = ttk.Label(self.cams_container)
		self.placeCams()

	def removeCam(self, client_id):
		self.cams[client_id].grid_forget()
		self.cams.pop(client_id, None)
		self.placeCams()

	#metodo che posiziona le webcam in una griglia
	def placeCams(self):
		column_number = 0
		row_number = 0
		temp_cams = list(self.cams.keys())
		cam_number = len(temp_cams)
		if (cam_number > (self.grid_size**2)):
			self.grid_size += 1
			self.counter_size += 4.10
		elif (cam_number <= ((self.grid_size - 1)**2)):
			self.grid_size -= 1
			self.counter_size -= 4.10

		for cam in temp_cams:
			self.cams[cam].grid(column = column_number, row = row_number, columnspan = 1)

			if (column_number == (self.grid_size - 1)):
				row_number += 1
				column_number = 0
			else: column_number += 1
	
	def selectMask(self, event, mask_button):
		global mask_status
		if(mask_status):
			self.mask = ""
			mask_button.config(image = self.mask_off)
			mask_status = False
		else:
			filetypes = (('image', '*.png'),)
			filename = filedialog.askopenfilename(title = "Scegli una maschera", initialdir = "masks", filetypes = filetypes)
			if (filename):
				self.mask = filename
				mask_button.config(image = self.mask_on)
				mask_status = True

	def showFilters(self, event, filters_button):
		global filters_status
		if(filters_status):
			filters_button.config(image = self.filters_off)
			self.grayscale.pack_forget()
			self.blur.pack_forget()
			self.invert.pack_forget()
			self.mirror.pack_forget()
			filters_status = False
		else:
			filters_button.config(image = self.hide_filters)
			self.grayscale.pack()
			self.blur.pack(pady = 2)
			self.invert.pack()
			self.mirror.pack(pady = 2)
			filters_status = True

	def toggleFilter(self, event, button, filter_name):
		if filter_name in self.filters:
			self.filters.remove(filter_name)
			button["style"] = "TButton"
		else:
			self.filters.append(filter_name)
			button["style"] = "W.TButton"

	#crea il layout della finestra dopo che si è entrati in una stanza
	def createWindow(self):
		self.dialog.pack_forget()
		highlight_style = ttk.Style()
		highlight_style.configure("W.TButton",
						font = ("monospace", 9, "bold"),
						foreground = "green")
		normal_style = ttk.Style()
		normal_style.configure("TButton",
						font = ("monospace", 9, "bold"),)

		#creazione delle colonne e delle righe
		self.root.columnconfigure(0, weight = 1)
		self.root.columnconfigure(1, weight = 17)
		self.root.columnconfigure(2, weight = 1)
		self.root.rowconfigure(0, weight = 10)
		self.root.rowconfigure(1, weight = 1)

		#creazione delle icone
		mic_off = tk.PhotoImage(file = "assets/mic_off.png")
		mic_on = tk.PhotoImage(file = "assets/mic.png")
		cam_off = tk.PhotoImage(file = "assets/cam_off.png")
		cam_on = tk.PhotoImage(file = "assets/cam.png")
		self.send = tk.PhotoImage(file = "assets/send_message.png")
		self.filters_off = tk.PhotoImage(file = "assets/filters.png")
		self.hide_filters = tk.PhotoImage(file = "assets/hide_filters.png")
		self.mask_off = tk.PhotoImage(file = "assets/mask.png")
		self.mask_on = tk.PhotoImage(file = "assets/remove_mask.png")
		subtitles_off = tk.PhotoImage(file = "assets/subtitles_off.png")
		subtitles_on = tk.PhotoImage(file = "assets/subtitles.png")

		subtitles_container = ttk.Frame(self.root)
		self.subtitle = ttk.Label(subtitles_container, text = "", font = FONT)
		self.subtitle.pack()
		subtitles_container.grid(column = 1, row = 0, sticky = "s")

		communication_tools = ttk.Frame(self.root)	#frame che contiene i bottoni per il mute e lo spegnimento della cam

		mute_button = ttk.Button(communication_tools, image = mic_on)
		mute_button.bind("<ButtonRelease>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on))	#chiama la funzione anche con il click del mouse quando rilasciato
		mute_button.pack(side = "right", padx = 5)

		cam_button = ttk.Button(communication_tools, image = cam_on)
		cam_button.bind("<ButtonRelease>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on))	#chiama la funzione anche con il click del mouse quando rilasciato
		cam_button.pack(side = "right")

		communication_tools.grid(column = 1, row = 1, sticky = "s", pady = 2)

		send_message_wrapper = ttk.Frame(self.root)	#frame che contiene la entry del messaggio e il bottone di invio
		text = tk.StringVar()	#variabile dove andrà salvato il testo della entry
		self.textbox = ttk.Entry(send_message_wrapper, textvariable = text, width = 39, font = ("Monospace", 10))
		self.textbox.insert(0, PLACEHOLDER)	# inserire del testo che fungerà da placeholder
		self.textbox.bind("<FocusIn>", lambda event:self.clearTextbox(event, text))
		self.textbox.bind("<FocusOut>", lambda event:self.addPlaceholder(event, text))
		self.textbox.pack(side = "left", ipady = 3)

		send_button = ttk.Button(send_message_wrapper, image = self.send)
		send_button.bind("<ButtonRelease>", lambda event:self.sendMessage(event, text))
		send_button.pack(padx = 5, pady = 1)
		send_message_wrapper.grid(column = 2, row = 1, sticky = "e")

		tools = ttk.Frame(self.root)	#frame che contiene tutti i tools secondari
		
		filters = ttk.Frame(tools)
		self.grayscale = ttk.Button(filters, text = "scala grigi", width = 13)
		self.grayscale.bind("<ButtonRelease>", lambda event:self.toggleFilter(event, self.grayscale, "grayscale"))
		self.blur = ttk.Button(filters, text = "sfocato", width = 13)
		self.blur.bind("<ButtonRelease>", lambda event:self.toggleFilter(event, self.blur, "blur"))
		self.invert = ttk.Button(filters, text = "inverti", width = 13)
		self.invert.bind("<ButtonRelease>", lambda event:self.toggleFilter(event, self.invert, "invert"))
		self.mirror = ttk.Button(filters, text = "specchio", width = 13)
		self.mirror.bind("<ButtonRelease>", lambda event:self.toggleFilter(event, self.mirror, "mirror"))

		filters.pack()

		filters_button = ttk.Button(tools, image = self.filters_off)
		filters_button.bind("<ButtonRelease>", lambda event:self.showFilters(event, filters_button))
		mask_button = ttk.Button(tools, image = self.mask_off)
		mask_button.bind("<ButtonPress>", lambda event:self.selectMask(event, mask_button))
		subtitles_button= ttk.Button(tools, image = subtitles_off)
		subtitles_button.bind("<ButtonRelease>", lambda event:self.subtitlesToggle(event, subtitles_button, subtitles_off, subtitles_on))

		filters_button.pack(side = "top")
		mask_button.pack(side = "top", pady = 7)
		subtitles_button.pack(side = "top")

		tools.grid(column = 0, row = 0)

		self.cams_container = ttk.Frame(self.root)
		self.cams_container.grid(column = 1, row = 0)

		self.chat = ttk.Frame(self.root)
		self.text_chat = tk.Text(self.chat,
								width = 51,
								font = ("Monospace", 9),
								highlightthickness = 0,
								borderwidth = 0,
								height = 2/37 * (self.actual_window_height - (7.5 * self.actual_window_height / 100)))
		self.scrollbar = ttk.Scrollbar(self.chat, command = self.text_chat.yview, orient = "vertical")
		self.text_chat.configure(yscrollcommand = self.scrollbar.set)

		self.chat.columnconfigure(0, weight = 1)

		self.scrollbar.grid(column = 1, row = 0, sticky="sn")
		self.text_chat.configure(state = 'disabled')
		self.text_chat.grid(column = 0, row = 0, sticky="snew")

		self.chat.grid(column = 2, row = 0, sticky = "ne")
		
		#shortcut
		self.root.bind("<Control-m>", lambda event:self.micToggle(event, mute_button, mic_off, mic_on))	#ctrl + m = mute/unmute
		self.root.bind("<Control-w>", lambda event:self.camToggle(event, cam_button, cam_off, cam_on))	#ctrl + w = cam off/cam on
		self.root.bind("<Return>", lambda event:self.sendMessage(event, text))	#enter = send message
		self.root.bind("<Control-s>", lambda event:self.subtitlesToggle(event, subtitles_button, subtitles_off, subtitles_on))	#ctrl + s = subtitles off/subtitles on
		self.root.bind("<Control-k>", lambda event:self.selectMask(event, mask_button))	#ctrl + k = select mask

		self.root.bind("<Configure>", self.resizeWindow)
		
		for i in self.temp_client_list:
			self.layoutCam(i)
		self.temp_client_list.clear()
