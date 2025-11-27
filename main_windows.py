#main_windows.py
from tkinter import font as tkfont
import tkinter as tk
from const import CARS_SHOP_PATH, UPGRADES_SHOP_PATH
from garage import next_garage_car, previous_garage_car, type_garage_car
from points import type_points
from race import next_race, previous_race, race, send_race, type_race
from utility_functions import load_data, type_text
from auth import type_text
from shop import type_car, next_car, previous_car, buy_car, type_upgrade,next_upgrade, previous_upgrade, buy_upgrade


def show_secondary_menu(user_path:str, username:str, user_key):
    #General
    root_secondary_menu = tk.Tk()
    root_secondary_menu.title("CryptoRacers")
    root_secondary_menu.resizable(False, False)

    width = 800
    height = 600

    screen_width = root_secondary_menu.winfo_screenwidth()
    screen_height = root_secondary_menu.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root_secondary_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_secondary_menu.configure(bg="#191919")

    #Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")

    #Elementos
    tk.Label(root_secondary_menu, text=username, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_secondary_menu,
            text="VER PUNTOS",
            command=lambda: [root_secondary_menu.destroy(), show_points_menu(user_path, username, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    tk.Button(
            root_secondary_menu,
            text="TIENDA",
            command=lambda: [root_secondary_menu.destroy(), show_initial_shop_menu(user_path, username, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    tk.Button(
            root_secondary_menu,
            text="GARAJE",
            command=lambda: [root_secondary_menu.destroy(), show_garage_menu(user_path, username, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    tk.Button(
            root_secondary_menu,
            text="PROPONER CARRERA",
            command=lambda: [root_secondary_menu.destroy(), show_propose_race(user_path, username, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    tk.Button(
            root_secondary_menu,
            text="CARRERAS DISPONIBLES",
            command=lambda: [root_secondary_menu.destroy(), show_available_races(user_path, username, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 11, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    terminal = tk.Text(root_secondary_menu, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(30, 10))
    type_text(terminal, f"Preparado...\nListo...\n¡A correr!\nInicio de sesión exitoso\nBienvenido, {username}")

    root_secondary_menu.mainloop()

def show_points_menu(user_path:str, user_name:str, user_key):
    #General
    root_points_menu = tk.Tk()
    root_points_menu.title("CryptoRacers")
    root_points_menu.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_points_menu.winfo_screenwidth()
    screen_height = root_points_menu.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_points_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_points_menu.configure(bg="#191919")

    #Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=12, weight="bold")

    #Elementos
    tk.Label(root_points_menu, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_points_menu,
            text="ATRÁS",
            command=lambda: [root_points_menu.destroy(), show_secondary_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))

    terminal = tk.Text(root_points_menu, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(20, 20))
    type_points(user_path, terminal, user_key)

    root_points_menu.mainloop()

def show_initial_shop_menu(user_path:str, user_name:str, user_key):
    #General
    root_initial_shop_menu = tk.Tk()
    root_initial_shop_menu.title("CryptoRacers")
    root_initial_shop_menu.resizable(False, False)

    width = 800
    height = 600

    screen_width = root_initial_shop_menu.winfo_screenwidth()
    screen_height = root_initial_shop_menu.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root_initial_shop_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_initial_shop_menu.configure(bg="#191919")

    #Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")

    #Elementos
    tk.Label(root_initial_shop_menu, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_initial_shop_menu,
            text="COCHES",
            command=lambda: [root_initial_shop_menu.destroy(), show_cars_shop_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 14, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(85, 0))
    
    tk.Button(
            root_initial_shop_menu,
            text="MEJORAS",
            command=lambda: [root_initial_shop_menu.destroy(), show_upgrades_shop_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 14, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(50, 0))
    tk.Button(
            root_initial_shop_menu,
            text="ATRÁS",
            command=lambda: [root_initial_shop_menu.destroy(), show_secondary_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=("Consolas", 14, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(50, 0))

    root_initial_shop_menu.mainloop()

def show_cars_shop_menu(user_path:str, user_name:str, user_key):
    #Obtenemos la información de compra (no está cifrada ni nada)
    car_data = load_data(CARS_SHOP_PATH)
    #General
    root_cars_shop_menu = tk.Tk()
    root_cars_shop_menu.title("CryptoRacers")
    root_cars_shop_menu.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_cars_shop_menu.winfo_screenwidth()
    screen_height = root_cars_shop_menu.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_cars_shop_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_cars_shop_menu.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=12, weight="bold")

    # Elementos
    tk.Label(root_cars_shop_menu, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_cars_shop_menu,
            text="SIGUIENTE COCHE",
            command=lambda: [next_car(car_data, terminal)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    tk.Button(
            root_cars_shop_menu,
            text="ANTERIOR COCHE",
            command=lambda: [previous_car(car_data, terminal)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))
    tk.Button(
            root_cars_shop_menu,
            text="COMPRAR",
            command=lambda: [buy_car(car_data, user_path, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))
    tk.Button(
            root_cars_shop_menu,
            text="ATRÁS",
            command=lambda: [root_cars_shop_menu.destroy(), show_initial_shop_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))

    terminal = tk.Text(root_cars_shop_menu, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(20, 10))
    type_car(car_data, terminal)

    root_cars_shop_menu.mainloop()

def show_upgrades_shop_menu(user_path:str, user_name:str, user_key):
    #Obtenemos la información de compra (no está cifrada ni nada)
    upgrades_data = load_data(UPGRADES_SHOP_PATH)

    #General
    root_upgrades_shop_menu = tk.Tk()
    root_upgrades_shop_menu.title("CryptoRacers")
    root_upgrades_shop_menu.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_upgrades_shop_menu.winfo_screenwidth()
    screen_height = root_upgrades_shop_menu.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_upgrades_shop_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_upgrades_shop_menu.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    label_font = tkfont.Font(family="Consolas", size=17, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=10, weight="bold")

    # Elementos
    tk.Label(root_upgrades_shop_menu, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(5, 0))

    tk.Button(
            root_upgrades_shop_menu,
            text="SIGUIENTE MEJORA",
            command=lambda: [next_upgrade(upgrades_data, terminal)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    tk.Button(
            root_upgrades_shop_menu,
            text="ANTERIOR MEJORA",
            command=lambda: [previous_upgrade(upgrades_data, terminal)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))
    
    tk.Label(root_upgrades_shop_menu, text="Modelo al que se le aplica la mejora:", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 0))

    car_upgrade_entry = tk.Entry(root_upgrades_shop_menu, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    car_upgrade_entry.pack(pady=(10, 0))
    tk.Button(
            root_upgrades_shop_menu,
            text="COMPRAR",
            command=lambda: [buy_upgrade(upgrades_data, terminal, user_path, car_upgrade_entry.get(), user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))
    tk.Button(
            root_upgrades_shop_menu,
            text="ATRÁS",
            command=lambda: [root_upgrades_shop_menu.destroy(), show_initial_shop_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(20, 0))

    terminal = tk.Text(root_upgrades_shop_menu, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(20, 10))
    type_upgrade(upgrades_data, terminal)

    root_upgrades_shop_menu.mainloop()

def show_garage_menu(user_path:str, user_name:str, user_key):
    #General
    root_garage_menu = tk.Tk()
    root_garage_menu.title("CryptoRacers")
    root_garage_menu.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_garage_menu.winfo_screenwidth()
    screen_height = root_garage_menu.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_garage_menu.geometry(f"{width}x{height}+{x}+{y}")
    root_garage_menu.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=12, weight="bold")

    # Elementos
    tk.Label(root_garage_menu, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_garage_menu,
            text="SIGUIENTE COCHE",
            command=lambda: [next_garage_car(user_path, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))
    
    tk.Button(
            root_garage_menu,
            text="ANTERIOR COCHE",
            command=lambda: [previous_garage_car(user_path, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))

    tk.Button(
            root_garage_menu,
            text="ATRÁS",
            command=lambda: [root_garage_menu.destroy(), show_secondary_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(30, 0))

    terminal = tk.Text(root_garage_menu, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(20, 10))
    type_garage_car(user_path, terminal, user_key)

    root_garage_menu.mainloop()


def show_propose_race(user_path:str, user_name:str, user_key):
    #General
    root_propose_race = tk.Tk()
    root_propose_race.title("CryptoRacers")
    root_propose_race.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_propose_race.winfo_screenwidth()
    screen_height = root_propose_race.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_propose_race.geometry(f"{width}x{height}+{x}+{y}")
    root_propose_race.configure(bg="#191919")

    #Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    label_font = tkfont.Font(family="Consolas", size=14, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=11, weight="bold")

    #Elementos
    tk.Label(root_propose_race, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(5, 0))

    tk.Label(root_propose_race, text="Rival (introduce username):", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(2, 0))
    rival_username_entry = tk.Entry(root_propose_race, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    rival_username_entry.pack(pady=(10, 0))

    tk.Label(root_propose_race, text="Coche (elige tu coche para correr):", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 0))
    race_car_entry = tk.Entry(root_propose_race, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    race_car_entry.pack(pady=(10, 0))

    tk.Button(
            root_propose_race,
            text="ENVIAR CARRERA",
            command=lambda: [send_race(rival_username_entry.get(), race_car_entry.get(), user_name, terminal, user_path, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    tk.Button(
            root_propose_race,
            text="ATRÁS",
            command=lambda: [root_propose_race.destroy(), show_secondary_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    terminal = tk.Text(root_propose_race, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(10, 10))

    root_propose_race.mainloop()

def show_available_races(user_path:str, user_name:str, user_key):
    #General
    root_available_races = tk.Tk()
    root_available_races.title("CryptoRacers")
    root_available_races.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_available_races.winfo_screenwidth()
    screen_height = root_available_races.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_available_races.geometry(f"{width}x{height}+{x}+{y}")
    root_available_races.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=20, weight="bold")
    label_font = tkfont.Font(family="Consolas", size=13, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=9, weight="bold")

    #Elementos
    tk.Label(root_available_races, text=user_name, fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))

    tk.Button(
            root_available_races,
            text="MOSTRAR CARRERAS",
            command=lambda: [type_race(user_name, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))

    tk.Button(
            root_available_races,
            text="SIGUIENTE CARRERA",
            command=lambda: [next_race(user_name, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    tk.Button(
            root_available_races,
            text="ANTERIOR CARRERA",
            command=lambda: [previous_race(user_name, terminal, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))

    tk.Label(root_available_races, text="COCHE (elige uno de tus coches para correr)", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 0))
    race_car_entry = tk.Entry(root_available_races, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    race_car_entry.pack(pady=(10, 0))
  

    tk.Button(
            root_available_races,
            text="INICIAR CARRERA",
            command=lambda: [race(user_name, user_path, user_key, terminal, race_car_entry.get())],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    
    
    tk.Button(
            root_available_races,
            text="ATRÁS",
            command=lambda: [root_available_races.destroy(), show_secondary_menu(user_path, user_name, user_key)],
            fg="white",
            bg="#ac3333",
            activebackground="#bd6c6c",
            activeforeground="white",
            font=button_font,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=(10, 0))
    
    terminal = tk.Text(root_available_races, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(10, 10))

    root_available_races.mainloop()
