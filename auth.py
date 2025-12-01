# auth.py
import base64
import tkinter as tk
from tkinter import font as tkfont
from const import DEFAULT_ITERATIONS, USERS_PATH
from utility_functions import create_user_certificate, generate_rsa_keypair, generate_user_key, hash_password, load_data, store_data, store_encrypted_data, type_text, user_exists
import re
from main_windows import show_secondary_menu


#-- SHOW WINDOWS AUTHENTICATION --
def show_initial_window():
    #General
    root_initial = tk.Tk()
    root_initial.title("CryptoRacers")
    root_initial.resizable(False, False)

    width = 800
    height = 600

    screen_width = root_initial.winfo_screenwidth()
    screen_height = root_initial.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root_initial.geometry(f"{width}x{height}+{x}+{y}")
    root_initial.configure(bg="#191919")

    #Fuentes
    title_font = tkfont.Font(family="Impact", size=70, weight="bold")

    #Elementos
    tk.Label(root_initial, text="CRYPTO", fg="white", bg="#191919", font=title_font).pack(pady=(10, 0))
    tk.Label(root_initial, text="RACERS", fg="#ff0000", bg="#191919", font=title_font).pack()

    tk.Button(
            root_initial,
            text="INICIAR SESIÓN",
            command=lambda: [root_initial.destroy(), show_login_window()],
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
            root_initial,
            text="REGISTRARSE",
            command=lambda: [root_initial.destroy(), show_register_window()],
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
        ).pack(pady=(20, 0))

    foot_font = tkfont.Font(family="Impact", size=20)
    tk.Label(root_initial, text="夜の峠を制覇せよ  -  Domina la noche", fg="#ffffff", bg="#111", font = foot_font).pack(pady=(70, 0))

    root_initial.mainloop()

def show_login_window():
    #General
    root_login = tk.Tk()
    root_login.title("CryptoRacers")
    root_login.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_login.winfo_screenwidth()
    screen_height = root_login.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_login.geometry(f"{width}x{height}+{x}+{y}")
    root_login.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    label_font = tkfont.Font(family="Consolas", size=17, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=12, weight="bold")

    # Elementos
    tk.Label(root_login, text="INICIO SESIÓN", fg="white", bg="#191919", font=title_font).pack(pady=(10, 10))

    tk.Label(root_login, text="USUARIO", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 5))
    username_entry = tk.Entry(root_login, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    username_entry.pack(pady=(0, 20))

    tk.Label(root_login, text="CONTRASEÑA", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 5))
    password_entry = tk.Entry(root_login, show="*", font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    password_entry.pack(pady=(0, 0))

    tk.Button(
            root_login,
            text="INICIAR SESIÓN",
            command=lambda: [login_user(username_entry.get(), password_entry.get(), terminal, root_login)],
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
        ).pack(pady=(40, 0))
    
    tk.Button(
            root_login,
            text="ATRÁS",
            command=lambda: [root_login.destroy(), show_initial_window()],
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
        ).pack(pady=(20, 30))

    terminal = tk.Text(root_login, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(0, 20))
    type_text(terminal, "Bienvenido a CryptoRacers\nLa aplicación de carreras cifrada de extremo a extremo\nIntroduzca su usuario y contraseña :)")

    root_login.mainloop()


def show_register_window():
    #General
    root_register = tk.Tk()
    root_register.title("CryptoRacers")
    root_register.resizable(False, False)

    width = 800
    height = 600
    screen_width = root_register.winfo_screenwidth()
    screen_height = root_register.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root_register.geometry(f"{width}x{height}+{x}+{y}")
    root_register.configure(bg="#191919")

    # Fuentes
    title_font = tkfont.Font(family="Impact", size=50, weight="bold")
    label_font = tkfont.Font(family="Consolas", size=17, weight="bold")
    button_font = tkfont.Font(family="Consolas", size=12, weight="bold")

    #Elementos
    tk.Label(root_register, text="REGISTRO", fg="white", bg="#191919", font=title_font).pack(pady=(10, 10))

    tk.Label(root_register, text="USUARIO", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 5))
    username_entry = tk.Entry(root_register, font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    username_entry.pack(pady=(0, 20))

    tk.Label(root_register, text="CONTRASEÑA", fg="#FF0000", bg="#191919", font=label_font).pack(pady=(10, 5))
    password_entry = tk.Entry(root_register, show="*", font=("Consolas", 12), justify="center", bg="#2c2c2c", fg="white", insertbackground="white", relief="flat", width=30)
    password_entry.pack(pady=(0, 0))

    tk.Button(
            root_register,
            text="REGISTRARSE",
            command=lambda: [register_user(username_entry.get(), password_entry.get(), terminal)],
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
        ).pack(pady=(40, 0))
    
    tk.Button(
            root_register,
            text="ATRÁS",
            command=lambda: [root_register.destroy(), show_initial_window()],
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
        ).pack(pady=(20, 30))

    terminal = tk.Text(root_register, width=70, bg="#0e0e0e", fg="#29FFF4",
                       insertbackground="white", font=("Consolas", 11), relief="flat")
    terminal.pack(pady=(0, 20))
    type_text(terminal, "Bienvenido a CryptoRacers\nLa aplicación de carreras cifrada de extremo a extremo\nIntroduzca un usuario y contraseña :)")

    root_register.mainloop()


#-- REGISTER AND LOGIN FUNCTIONS -- (tienen que ir aqui para no crear imports circulares -> login destruye y crea una nueva ventana)
def register_user(username: str, password: str, terminal):
    # Comprobaciones iniciales
    if password == "" or username == "":
        terminal.delete("1.0", tk.END)
        type_text(terminal, "Complete todos los campos por favor\n")
        return 
    
    if user_exists(username, USERS_PATH):
        terminal.delete("1.0", tk.END)
        type_text(terminal, "El usuario ya existe\nIntroduzca uno distinto\n")
        return

    username_regex = re.compile(r'^(?=.*[a-zA-Z]).{5,}$')
    if not username_regex.match(username):
        terminal.delete("1.0", tk.END)
        type_text(terminal, "Debe introducir un nombre de usuario válido\nEl nombre de usuario debe tener longitud mínima de 5 y contener al menos 1 letra\n")
        return
    
    password_regex = re.compile(r'^(?=.{12,}$)(?=.*[A-Z])(?=.*\d)(?=.*[_-])\S+$')  
    if not password_regex.match(password):
        terminal.delete("1.0", tk.END)
        type_text(terminal, "Debe introducir una contraseña válida\nEsta debe contener al menos 1 mayúscula, 1 número, un símbolo (-, _) y tener una longitud mínima de 12")
        return 

    terminal.delete("1.0", tk.END)

    # Generamos hash password
    salt_password, salt_key, hash_b64 = hash_password(password, terminal)
    # Generamos clave a partir de la contraseña del usuario y encriptamos
    user_key = generate_user_key(password, base64.b64decode(salt_key), terminal)  
    # Generamos la clave pública y la privada del usuario (la privada ya viene cifrada con la clave del usuario) -> estas se usarán para en cifrado híbrido
    generate_rsa_keypair(user_key, terminal, username, "cod")
    # Generamos la clave pública y la privada del usuario (la privada ya viene cifrada con la clave del usuario) -> estas se usarán para firmar datos
    generate_rsa_keypair(user_key, terminal, username, "sign")
    
    # PKI: Generar certificados firmados por AC2 
    create_user_certificate(username, user_key, "cod", terminal)
    create_user_certificate(username, user_key, "sign", terminal)

    # Añadimos los datos del usuario a users.json
    users_auth = load_data(USERS_PATH)
    users_auth[username] = {
        "salt_password": salt_password,
        "salt_key": salt_key,
        "hash": hash_b64,
    }

    store_data(users_auth, USERS_PATH)

    # Añadimos los datos iniciales del usuario a username_data.json (irán cifrados)
    USER_DATA_PATH = f"User_data/{username}_data.json"
    user_data = load_data(USER_DATA_PATH)
    user_data["username"] = username
    user_data["garage"] = []
    # TODO: Cambiar los puntos iniciales a 200
    user_data["points"] = 2000000000

    store_encrypted_data(user_data, USER_DATA_PATH, user_key, terminal)

    type_text(terminal, "Registro completado con éxito\n")




def login_user(username: str, password: str, terminal, root):
    # Comprobaciones iniciales
    if password == "" or username == "":
        terminal.delete("1.0", tk.END)
        type_text(terminal, "Complete todos los campos por favor\n")
        return 
    
    if not user_exists(username, USERS_PATH):
        terminal.delete("1.0", tk.END)
        type_text(terminal, "Usuario no encontrado\nIntroduzca uno que esté registrado\n")
        return

    # Recuperamos salt para calcular el nuevo hash y ver si coincide con la contraseña introducida por el usuario
    users = load_data(USERS_PATH)
    user_data = users[username]
    salt_password = user_data["salt_password"]
    stored_hash = user_data["hash"]
    salt_password = base64.b64decode(salt_password)

    _, _,computed_hash = hash_password(password, terminal, salt_password, write=False)

    if computed_hash == stored_hash:
        USER_DATA_PATH = f"User_data/{username}_data.json"
        user_key = generate_user_key(password, base64.b64decode(user_data["salt_key"]), terminal, write=False)
        root.destroy()
        show_secondary_menu(USER_DATA_PATH, username, user_key) 
        return
    else:
        terminal.delete("1.0", tk.END)
        type_text(terminal, f"Los hashes no coinciden\nHash calculado -> {computed_hash}\nHash almacenado -> {stored_hash}\nContraseña incorrecta\nInténtelo de nuevo :(\n")
        return

