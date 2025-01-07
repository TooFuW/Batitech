import requests
import json
import base64
import tkinter
from tkinter import ttk
import threading
import time
import unidecode
from datetime import datetime

# pyinstaller --onefile --windowed --icon=app.ico --name="Créateur de tâches Synchroteam" main.py

class Main:
    def __init__(self) -> None:
        
        self.is_progress_bar_running = False
        self.est_change = False
        self.state = None
        # On encode la clé API
        self.key = self.encode_b64(api_key="API_KEY")
        # On setup la vérifiaction des infos chargées
        self.client_charged = False
        # On lance tout en parrallèle
        thread_liste_clients = threading.Thread(target=self.liste_clients) 
        thread_liste_clients.start()
        thread_get_sites = threading.Thread(target=self.get_sites)
        thread_get_sites.start()
        tkinter_start = threading.Thread(target=self.show_gui)
        tkinter_start.start()

    def encode_b64(self,api_key : str):
        """On encode la string donnée

        Args:
            api_key (str): clé d'API à encoder

        Returns:
            str: clé d'API encodée
        """
        val = "batitech:"+api_key
        api_key_bin = val.encode('ascii')
        b64_bin = base64.b64encode(api_key_bin)
        b64_api_key = b64_bin.decode('ascii')
        return b64_api_key

    def is_date_good(self,string : str):
        """On vérifie si la date est valide

        Args:
            string (str): date valide/existante

        Returns:
            bool: False si la date n'est pas correcte, True sinon
        """
        try:
            if int(string[0:2]) > 31 or int(string[3:5]) > 12 or int(string[11:13]) > 23 or int(string[14:16]) > 59:
                print(1)
                return False
            if string[2] != "/" or string[5] != "/" or string[13] != ":":
                print(2)
                return False
            int(string[6:7])
            return len(string) == 16
        except:
            print(4)
            return False

    def liste_clients(self):
        """Récupére les clients et les range dans une liste de dictionnaires où chaque dictionnaire est un client, par exemple : [[page 1],[page 2]]  -- > page 1 : [{client 1},{client 2}]

        Returns:
            list: liste des clients
        """
        
        # On demande les clients
        cpt_page = 1

        url = f"https://ws.synchroteam.com/Api/v3/customer/list?page={cpt_page}&pageSize=100"

        headers = {
            'authorization': f"Basic {self.key}",
            'cache-control': "no-cache",
            'accept':'text/json'
            }
            
        payload = ""

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
        except:
            time.sleep(1)
            if not self.est_change:
                self.est_change = True
                print("cas no connection (clients)")
                self.state = 3
                self.client_charged = True
            return

        if response.status_code == 200: # reussite de la collection des données
            dico_list = [] # chaque dictionnaire de cette liste representera 1 page de 100 clients
            dico = json.loads(response.text)
            dico_list.append(dico)
            cpt = dico["recordsTotal"]-100

            # On charge autant de fois qu'il faut une nouvelle page jusqu'à avoir tout les clients
            while cpt > 0:
                cpt_page += 1
                url = f"https://ws.synchroteam.com/Api/v3/customer/list?page={cpt_page}&pageSize=100"

                # On va réutiliser le header et payload précédent

                try:
                    response = requests.request("GET", url, headers=headers, data=payload)
                except:
                    time.sleep(1)
                    if not self.est_change:
                        self.est_change = True
                        print("cas no connection (clients)")
                        self.state = 3
                        self.client_charged = True
                    return

                if response.status_code == 200: # reussite de la collection des données
                    # On ajoute les nouveaux clients chargés
                    dico_list.append(json.loads(response.text))
                    cpt -= 100

                else:
                    # En cas d'erreur on crée un log avec les erreurs
                    with open("./errorlog.json","w") as errorlog:
                        errorlog.write(response.text)
                        return response.status_code

        else:
            tkinter.messagebox.showwarning(title="Error", message=f"Une erreur s'est produite et les clients n'ont pas pu se charger.\n\n Message d'erreur : liste_client\n\n{str(response.status_code)}\n\n{response.text}\n\n{response.content}")
            
        #arrivé ici ça signifie que toutes les pages ont été correctement crées et saisies et que dico_list comporte le nombre de pages correct
        for i in range(len(dico_list)):
            dico_list[i] = dico_list[i]["data"]

        liste = []
        for i in dico_list:
            liste += i

        # Le chargement est fini on classe tout comme il faut
        self.clients = liste
        self.clients_display = self.get_display_list(self.clients)
        self.client_combobox["values"] = self.clients_display
        print("recuperation terminée.")
        # On dit que les clients sont chargés
        self.client_charged = True
        return liste

    def get_sites(self):
        """pareil que liste_clients() mais pour les sites

        Returns:
            list: liste des sites
        """

        # On demande les sites
        cpt_page = 1

        url = f"https://ws.synchroteam.com/api/v3/site/list?page=1&pageSize=100"

        payload = ""

        headers = {
            'authorization': f"Basic {self.key}",
            'accept': "text/json",
            'content-type': "application/json",
            'cache-control': "no-cache"
            }

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
        except:
            time.sleep(3)
            if not self.est_change:
                self.est_change = True
                print("cas no connection (clients)")
                self.state = 3
                self.client_charged = True
            return

        if response.status_code == 200: # reussite de la collection des données
            dico_list = [] # chaque dictionnaire de cette liste representera 1 page de 100 sites
            dico = json.loads(response.text)
            dico_list.append(dico)
            cpt = dico["recordsTotal"]-100

            # On charge autant de fois qu'il faut une nouvelle page jusqu'à avoir tout les sites
            while cpt > 0:
                cpt_page += 1

                url = f"https://ws.synchroteam.com/api/v3/site/list?page={cpt_page}&pageSize=100"

                # On va réutiliser le header et payload précédent

                try:
                    response = requests.request("GET", url, headers=headers, data=payload)
                except:
                    time.sleep(3)
                    if not self.est_change:
                        self.est_change = True
                        print("cas no connection (clients)")
                        self.state = 3
                        self.client_charged = True
                    return

                if response.status_code == 200: # reussite de la collection des données
                    # On ajoute les nouveaux sites chargés
                    dico = json.loads(response.text)
                    dico_list.append(dico)
                    cpt -= 100

                else:
                    # En cas d'erreur on crée un log avec les erreurs
                    with open("./errorlog.json","w") as errorlog:
                        errorlog.write(response.text)
                        
        else:
            tkinter.messagebox.showwarning(title="Error", message=f"Une erreur s'est produite et les sites n'ont pas pu se charger.\n\n Message d'erreur : get_sites\n\n{str(response.status_code)}\n\n{response.text}\n\n{response.content}")

        #arrivé ici ça signifie que toutes les pages ont été correctement crées et saisies et que dico_list comporte le nombre de pages correct
        for i in range(len(dico_list)):
            dico_list[i] = dico_list[i]["data"]

        liste = []
        for i in dico_list:
            liste += i

        # Le chargement est fini on classe tout comme il faut
        self.sites = liste
        self.sites_display = self.get_display_list(self.sites)
        return liste

    def get_display_list(self,liste : list):
        """Transforme la liste de clients ou sites donnée en liste affichable (jolie)

        Args:
            liste (list): liste de clients ou sites

        Returns:
            list: liste donnée affichable (jolie)
        """
        display_list = []
        for el in liste:
            display_list.append(el["myId"]+" - "+el["name"]+" - "+el["address"]+" - "+el["contactEmail"])
        return display_list
    
    def date_format_change(self,date : str):
        """Change le format de la date dans le format demandé par Synchroteam

        Args:
            date (str): date

        Returns:
            str: date dans le bon format
        """
        return f"{date[6:10]}-{date[3:5]}-{date[0:2]}{date[10:13]}:{date[14:16]}"
    
    def creer_tache(self):
        """Crée une tâche dans Synchroteam avec les infos fournies
        """
        # On récupére toutes les infos
        description = self.description_entry.get(1.0, tkinter.END).strip()
        date = self.date_entry.get()
        famille = self.famille_combobox.get()
        try:
            client = self.clients[self.clients_display.index(self.client_combobox.get())]["id"] if self.client_combobox.get() else ""
        except:
            client = ""
        prenom = self.prenom_entry.get()
        try:
            site = self.sites[self.sites_display.index(self.site_combobox.get())]["id"] if self.site_combobox.get() else ""
        except:
            print("no site")
            site = ""
        
        # On vérifie si les paramètres essentiels ont étés récupérés
        if description:
            if client:
                if date:
                    # On vérifie si la date est valide
                    if self.is_date_good(date):
                        # Si oui on la met dans le bon format
                        date = self.date_format_change(date)

                        # On envoit la requête à Synchroteam
                        url = "https://ws.synchroteam.com/Api/v3/tasks/send"
                        payload = f'{{\r\n  "content": "{prenom} - {description}",\r\n  "dateDue": "{date}",\r\n  "customer": {{\r\n    "id": {str(client)}\r\n  }},\r\n  "site": {{\r\n    "id": "{str(site)}"\r\n  }},\r\n  "user": {{\r\n    "id": 219802\r\n  }},\r\n  "category": "{famille}"\r\n}}'
                        payload_avec_accent = payload
                        for caractere in payload_avec_accent:
                            if caractere != unidecode.unidecode(caractere):
                                payload_avec_accent += '}'
                            
                        print(payload_avec_accent)
                        
                        headers = {
                            'authorization': f"Basic {self.key}",
                            'accept': 'text/json',
                            'content-type': 'application/json',
                            'cache-control': 'no-cache'
                            }

                        try:
                            response = requests.request("POST", url, data=payload_avec_accent, headers=headers)
                        except:
                            tkinter.messagebox.showwarning(title="Error", message="Vérifiez votre connexion internet et réessayez.")
                            return

                        # On enregistre le nom donné pour que l'utilisateur n'ai pas à le réécrire
                        with open("./username.txt", "w") as file:
                            file.write(self.prenom_entry.get())

                        # On affiche les pop-ups/messages correspondant à ce qui s'est passé et en précisant l'erreur s'il y en a une
                        if response.status_code == 200: # reussite de la collection des données
                            tkinter.messagebox.showinfo(title="Ajout de la tâche réussi !",message="La tâche a été ajoutée avec succès !")
                        else:
                            print(response.headers,response.text)
                            print("2eme requete")
                            print(payload)
                            payload = unidecode.unidecode(payload)

                            try:
                                response = requests.request("POST", url, data=payload_avec_accent, headers=headers)
                            except:
                                tkinter.messagebox.showwarning(title="Error", message="Vérifiez votre connexion internet et réessayez.")
                                return
                            
                            if response.status_code == 200: # reussite de la collection des données
                                tkinter.messagebox.showinfo(title="Ajout de la tâche réussi !",message="La tâche a été ajoutée avec succès !")
                            else:
                                tkinter.messagebox.showwarning(title="Error", message=f"Une erreur s'est produite la tâche n'a pas été ajoutée.\n\n Message d'erreur : creer_tache\n\n{str(response.status_code)}\n\n{response.text}\n\n{response.content}")
                    else:
                        tkinter.messagebox.showwarning(title="Error", message="Le format de la date n'est pas respecté (jj/mm/aaaa hh:mm)")
                else:
                    tkinter.messagebox.showwarning(title="Error", message="La description, date et le client sont obligatoires, veuillez entrer une date dans le format demandé dans la zone DATE")
            else:
                tkinter.messagebox.showwarning(title="Error", message="La description, date et le client sont obligatoires, veuillez sélectionner le client parmis ceux proposés dans le menu déroulant")
        else:
            tkinter.messagebox.showwarning(title="Error", message="La description, date et le client sont obligatoires, veuillez entrer du texte dans la zone DESCRIPTION")
        
    def on_client_selection(self,event):
        """Sélection des sites correspondant au client sélectionné à chaque fois qu'un client est sélectionné
        """
        self.site_combobox.set("")
        if self.client_combobox.get() != "":
            self.site_combobox["state"] = "normal"
            liste = []
            for i in self.sites:
                if i["customer"]['id'] == self.clients[self.clients_display.index(self.client_combobox.get())]["id"]:
                    liste.append(i)
            self.site_combobox["values"] = [""]+self.get_display_list(liste)
        else:
            self.site_combobox["state"] = "readonly"

    def effacer_infos(self):
        """On efface toutes les infos entrées
        """
        self.description_entry.delete("1.0", tkinter.END)
        date = str(datetime.now())
        self.date_entry.delete(0, tkinter.END)
        self.date_entry.insert(0, f"{date[8]}{date[9]}/{date[5]}{date[6]}/{date[0]}{date[1]}{date[2]}{date[3]} {date[11:16]}")
        self.famille_combobox.set("")
        self.client_combobox.set("")
        self.site_combobox.set("")

    def autocompletion_famille(self, event):
        """Propose les résultats correspondants à ce qui est tapé dans la combobox self.famille_combobox
        """
        current_text = self.famille_combobox.get().lower()
        # On récupére toutes les valeurs de la combobox
        all_items = ["", "Rappel", "Email", "Suivi", "Rendez-vous"]
        if current_text != "":
            # Et on filtre
            matching_items = [item for item in all_items if current_text in item.lower()]
            self.famille_combobox['values'] = matching_items
        else:
            self.famille_combobox['values'] = all_items
        # On fait apparaître le menu déroulant
        self.famille_combobox.event_generate('<Down>')

    def autocompletion_client(self, event):
        """Propose les résultats correspondants à ce qui est tapé dans la combobox self.client_combobox
        """
        current_text = self.client_combobox.get().lower()
        # On récupére toutes les valeurs de la combobox
        all_items = self.clients_display
        if current_text != "":
            # Et on filtre
            matching_items = [item for item in all_items if current_text in item.lower()]
            self.client_combobox['values'] = matching_items
        else:
            self.client_combobox['values'] = all_items
        # On fait apparaître le menu déroulant
        self.client_combobox.event_generate('<Down>')
            
    def autocompletion_site(self, event):
        """Propose les résultats correspondants à ce qui est tapé dans la combobox self.site_combobox
        """
        current_text = self.site_combobox.get().lower()
        # On récupére toutes les valeurs de la combobox
        all_items = [""] + self.get_display_list([i for i in self.sites if i["customer"]['id'] == self.clients[self.clients_display.index(self.client_combobox.get())]["id"]]) if self.client_combobox.get() != "" else []
        if current_text != "":
            # Et on filtre
            matching_items = [item for item in all_items if current_text in item.lower()]
            self.site_combobox['values'] = matching_items
        else:
            self.site_combobox['values'] = all_items
        # On fait apparaître le menu déroulant
        self.site_combobox.event_generate('<Down>')

    def start_progress_bar(self, direction):
        if not self.is_progress_bar_running:
            self.is_progress_bar_running = True
            
            """Lance la barre de chargement tant que tout n'est pas chargé

            Args:
                direction (bool): True si la barre va vers la droite, False si la barre va vers la gauche
            """
            # Si self.client_chargement
            if not isinstance(self.client_chargement, ttk.Progressbar):
                self.state = None
                self.est_change = False
                
                self.client_chargement_label["text"] = "Chargement des clients en cours..."
                self.client_chargement.destroy()
                self.client_chargement = ttk.Progressbar(self.general_info_frame, orient="horizontal", length=100, mode="indeterminate", takefocus=True, maximum=100, value=0)
                self.client_chargement.grid(row=1,column=1,padx=20,pady=20)
                self.client_charged = False
                # Relancer le chargement des clients et des sites
                self.thread_liste_clients = threading.Thread(target=self.liste_clients) 
                self.thread_liste_clients.start()
                self.thread_get_sites = threading.Thread(target=self.get_sites)
                self.thread_get_sites.start()
            
            # Si direction True on fait avancer
            if direction:
                self.client_chargement['value'] += 25
                # On change la direction en arrivant au bout
                if self.client_chargement['value'] + 25 > 100:
                    direction = False
                # On détruit la barre de chargement lorsque tout est chargé
                if self.client_charged:
                    if self.state == 3:
                        self.client_chargement_label["text"] = "Erreur : pas de connexion internet\nRecharger ?"
                        self.client_chargement.destroy()
                        self.client_chargement = tkinter.Button(self.general_info_frame, text="Recharger les clients", command= lambda: self.start_progress_bar(True))
                        self.client_chargement.grid(row=1,column=1,padx=20,pady=20)
                        self.is_progress_bar_running = False
                    else:
                        self.client_chargement_label["text"] = "Clients chargés !\nRecharger ?"
                        self.client_chargement.destroy()
                        self.client_chargement = tkinter.Button(self.general_info_frame, text="Recharger les clients", command= lambda: self.start_progress_bar(True))
                        self.client_chargement.grid(row=1,column=1,padx=20,pady=20)
                        self.is_progress_bar_running = False
                # Sinon on recommence
                else:
                    self.is_progress_bar_running = False
                    self.window.after(400, lambda: self.start_progress_bar(direction))
            # Sinon on fait reculer
            else:
                self.client_chargement['value'] -= 25
                # On change la direction en arrivant au bout
                if self.client_chargement['value'] - 25 < 0:
                    direction = True
                # On détruit la barre de chargement lorsque tout est chargé
                if self.client_charged:
                    self.client_chargement_label["text"] = "Clients chargés !\nRecharger ?"
                    self.client_chargement.destroy()
                    self.client_chargement = tkinter.Button(self.general_info_frame, text="Recharger les clients", command= lambda: self.start_progress_bar(True))
                    self.client_chargement.grid(row=1,column=1,padx=20,pady=20)
                    self.is_progress_bar_running = False
                # Sinon on recommence
                else:
                    self.is_progress_bar_running = False
                    self.window.after(400, lambda: self.start_progress_bar(direction))

    def show_gui(self):
        """Fonction qui fait apparaître toute l'interface
        """
        self.window = tkinter.Tk()
        self.window.title("Formulaire de création de tâche Synchroteam")

        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Explications d'utilisation de l'app
        self.explication_frame =tkinter.LabelFrame(self.frame, text="Comment utiliser")
        self.explication_frame.grid(row= 0, column=0, padx=20, pady=10)

        # Texte d'explication
        self.explication_text = "Application de création de tâches dans Synchroteam. Pour créer une tâche il faudra remplir les champs suivants :\n- Description (obligatoire): Description de la tâche\n- Date (obligatoire): Date pour laquelle vous créez la tâche (format : jj/mm/aaaa hh:mm)\n- Famille: Choisir entre l'une des différentes catégories disponibles (Intervention, Intervention urgente, Intervention David, Rendez-vous ou rien)\n- Client (obligatoire): Client en relation avec la tâche (1 max)\n- Site: Site du client en relation avec la tâche s'il en posséde (1 max)\n\nAppuyer sur Entrée pour valider la recherche des menus déroulants\nVotre nom est sauvegardé automatiquement, vous n'aurez à le rentrer que la première fois !\nVous pouvez écrire avec des accents et caractères spéciaux mais il y a un petit risque qu'ils ne soient pas envoyés sur Synchroteam"
        self.explication_text_label = tkinter.Label(self.explication_frame, text=self.explication_text, justify="left")
        self.explication_text_label.grid(row=0, column=0, padx=10, pady=5)

        for widget in self.explication_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # Infos utilisateur
        self.general_info_frame = tkinter.LabelFrame(self.frame, text="Informations générales")
        self.general_info_frame.grid(row=1,column=0,padx=20,pady=20)

        # Prénom de l'utilisateur
        self.prenom_label = tkinter.Label(self.general_info_frame, text="Votre prénom")
        self.prenom_label.grid(row=0, column=0)
        self.prenom_entry = tkinter.Entry(self.general_info_frame)
        self.prenom_entry.grid(row= 1, column=0, padx=20, pady=10)
        try:
            with open("./username.txt", "r") as file:
                self.prenom_entry.insert(0, file.read())
        except:
            with open("./username.txt","w"):
                pass

        # Barre de chargement des clients
        self.client_chargement_label = tkinter.Label(self.general_info_frame, text="Chargement des clients en cours...")
        self.client_chargement_label.grid(row=0, column=1)
        self.client_chargement = ttk.Progressbar(self.general_info_frame, orient="horizontal", length=100, mode="indeterminate", takefocus=True, maximum=100, value=0)
        self.client_chargement.grid(row=1,column=1,padx=20,pady=20)

        for widget in self.general_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # Infos à rentrer
        self.tache_info_frame =tkinter.LabelFrame(self.frame, text="Informations de la tâche")
        self.tache_info_frame.grid(row= 2, column=0, padx=20, pady=10)

        # Description
        self.description_label = tkinter.Label(self.tache_info_frame, text="Description")
        self.description_label.grid(row=0, column=0)
        self.description_entry = tkinter.Text(self.tache_info_frame, height=5, width=20)
        self.description_entry.grid(row=1, column=0)

        # Date
        self.date_label = tkinter.Label(self.tache_info_frame, text="Date\n(jj/mm/aaaa hh:mm)")
        self.date_label.grid(row=0, column=1)
        self.date_entry = tkinter.Entry(self.tache_info_frame)
        self.date_entry.grid(row=1, column=1)
        date = str(datetime.now())
        self.date_entry.insert(0, f"{date[8]}{date[9]}/{date[5]}{date[6]}/{date[0]}{date[1]}{date[2]}{date[3]} {date[11:16]}")

        # Famille
        self.famille_label = tkinter.Label(self.tache_info_frame, text="Famille")
        self.famille_combobox = ttk.Combobox(self.tache_info_frame, values=["", "Intervention", "Intervention Urgente", "Intervention David", "Rendez-vous"], state="readonly", justify="left")
        self.famille_label.grid(row=0, column=2)
        self.famille_combobox.grid(row=1, column=2)
        self.famille_combobox.bind("<Return>", self.autocompletion_famille)

        for widget in self.tache_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # Infos du client à rentrer
        self.client_info_frame =tkinter.LabelFrame(self.frame, text="Informations du client")
        self.client_info_frame.grid(row= 3, column=0, padx=20, pady=10)

        # Client
        self.client_label = tkinter.Label(self.client_info_frame, text="Client")
        self.client_combobox = ttk.Combobox(self.client_info_frame, values=[""], justify="left", width=100, height=20)
        self.client_label.grid(row=0, column=0)
        self.client_combobox.grid(row=1, column=0)
        # Lorsqu'on sélectionne un client
        self.client_combobox.bind("<<ComboboxSelected>>", self.on_client_selection)
        self.client_combobox.bind("<Return>", self.autocompletion_client)

        # Site
        self.site_label = tkinter.Label(self.client_info_frame, text="Site")
        self.site_combobox = ttk.Combobox(self.client_info_frame, values=[""], justify="left", width=100, height=20, state="readonly")
        self.site_label.grid(row=2, column=0)
        self.site_combobox.grid(row=3, column=0)
        self.site_combobox.bind("<Return>", self.autocompletion_site)

        for widget in self.client_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # Créer la tâche
        creer_tache = tkinter.Button(self.frame, text="Créer la tâche", command= self.creer_tache)
        creer_tache.grid(row=4, column=0, sticky="news", padx=20, pady=10)
        # Effacer infos
        effacer_infos = tkinter.Button(self.frame, text="Effacer", command= self.effacer_infos)
        effacer_infos.grid(row=5, column=0, sticky="news", padx=20, pady=10)

        if not self.client_charged:
            # On lance la barre de chargement tant que tout n'est pas chargé
            self.window.after(400, lambda: self.start_progress_bar(True))

        # On lance la boucle
        self.window.mainloop()

if __name__ == "__main__":
    main = Main()