#utility_functions.py
import json
import tkinter as tk
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP 
import base64
import hashlib
import os
from collections import deque
from const import DEFAULT_ITERATIONS

#VARIABLES GLOBALES para la función type_text
typing_after_id = None
typing_after_id = None
typing_queue = deque()

# FUNCIÓN HASH
def hash_password(password: str, salt_password: bytes = None) -> tuple:
    # Genera el hash de la contraseña introducida por el usuario
    if salt_password is None:
        salt_password = os.urandom(16) #El salt se genera aleatoriamente
    
    value = salt_password + (password).encode("utf-8") #Aplicamos salt (distinto al que se usa para obtener la clave de usuario)

    for _ in range(DEFAULT_ITERATIONS):
        #Iteramos para que sea más difícil un ataque a fuerza brutas
        value = hashlib.sha256(value).digest()
    

    return (
        base64.b64encode(salt_password).decode("ascii"),
        base64.b64encode(os.urandom(16)).decode("ascii"), #salt_key (salt para construir la clave de usuario)
        base64.b64encode(value).decode("ascii")
    )


# FUNCIONES PARA GENERAR CLAVES
def generate_user_key(password: str, salt: bytes) -> bytes:
    #Genera una clave a partir de la contraseña de cada usuario -> todos los datos del usuario se cifran con esta clave
    #Se le aplica un salt aleatorio para añadir seguridad (este salt es distinto al que se aplica al hash de la contraseña)
    value = salt + (password).encode("utf-8")
    for _ in range(DEFAULT_ITERATIONS):
        #Iteramos para que sea más difícil un ataque a fuerza brutas
        value = hashlib.sha256(value).digest()

    return value  # Retornamos la clave AES-256 de 32 bytes

def generate_rsa_keypair(user_key: bytes) -> tuple:
    # Generamos las claves RSA
    key = RSA.generate(4096)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Ciframos la clave privada con la clave del usuario
    cipher, ciphertext, tag = encrypt_data(user_key, private_key)
    encrypted_private_key = cipher.nonce + tag + ciphertext

    # Lo devolvemos en base64 para poder guardarlo en json
    return base64.b64encode(encrypted_private_key).decode("ascii"), public_key.decode("ascii")

def generate_random_symmetric_key(terminal) -> bytes:
    # Generamos la clave simétrica temporal para el cifrado híbrido (AES-256 GCM)
    type_text(terminal, 
            "Generando clave simétrica temporal...\n"
            "Clave simétrica temporal generada correctamente\n"
            "\n") 
    return os.urandom(32)


# FUNCIONES PARA ENCRIPTADO / DESENCRIPTADO SIMÉTRICO
def desencrypt_data(file_bytes, key, terminal, decode=True):
    # Obtenemos el nonce, tag y el texto cifrado
    try:
        nonce = file_bytes[:16]
        tag = file_bytes[16:32]
        ciphertext = file_bytes[32:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        # Nos aseguramos de que el tag sea el mismo de cuando se cifró ya que si no, significa que alguien ha modificado el documento
        plaintext = cipher.decrypt_and_verify(ciphertext, tag) 
        type_text(terminal, 
            "Desencriptando archivo del usuario...\n"
            f"Nonce extraído: {base64.b64encode(nonce).decode('ascii')}\n"
            f"Tag de autenticidad extraído: {base64.b64encode(tag).decode('ascii')}\n"
            f"Verificación MAC exitosa\n"
            f"Desencriptación con AES-256 GCM exitosa\n"
            "\n") #Los espacios son para q tarde un tiempo en saltar al siguient mensaje en cola
        if decode:
            return json.loads(plaintext.decode("utf-8")) # Se devuelve el texto ya desencriptado
        else:
            return plaintext
            
    except ValueError:
        #Eso significa que la autenticación ha fallado o que las claves no son las mismas
        print(f"USADA_KEY ->>> {key}")
        type_text(terminal, "ERROR GRAVE: las claves de cifrado y descifrado no coinciden o alguien ha modificado el archivo\n") 
        return None

def encrypt_data(key, plaintext):
    # A partir de una clave y un texto (en bits) se encripta
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return cipher,ciphertext,tag #Devolvemos la información adicional para guardarla luego


# FUNCIONES LOAD/STORE
# Funciones load/store pero antes de guardar/cargar tienen que encriptar/desencriptar
def load_encrypted_data(filepath: str, key: bytes, terminal) -> dict:
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    return desencrypt_data(file_bytes, key, terminal)
    

def store_encrypted_data(data: dict, filepath: str, key: bytes, terminal):
    plaintext = json.dumps(data).encode("utf-8") 
    cipher, ciphertext, tag = encrypt_data(key, plaintext)
    
    # Guardamos nonce + tag + ciphertext en binario
    with open(filepath, "wb") as f:
        f.write(cipher.nonce + tag + ciphertext)

    type_text(terminal, 
                  "Encriptando archivo del usuario...\n"
                  f"Usando nonce generado aleatoriamente -> {base64.b64encode(cipher.nonce).decode("ascii")}\n"
                  f"Usada clave para AES-GCM de 32 bytes... \n"
                  f"Generado tag de autenticacion {base64.b64encode(tag).decode("ascii")}\n"
                  f"Encriptación con AES-256 GCM exitosa\n"
                  "Datos del usuario guardados correctamente\n"
                  "\n") 

#Funcion load/store estandar (para cuando no hay que usar nada de cifrado)
def load_data(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8", newline="") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    except json.JSONDecodeError:
        raise Exception("Error leyendo el archivo\n")
    return users

def store_data(data: dict, path: str):
    try:
        with open(path, "w", encoding="utf-8", newline="") as file:
                json.dump(data, file, indent=2)
    except json.JSONDecodeError:
        raise Exception("Error guardando el archivo\n")


# FUNCION PARA LA TERMINAL DE TKINTER
#Función que se encarga de imprimir por la terminal de la ventana de tkinter
#Delay -> como de lento escribe
def type_text(terminal, text, delay=2, index=0):
    #Escribe el texto en el terminal letra a letra usando una cola.
    global typing_after_id, typing_queue

    if index == 0:
        # Añadimos a la cola y salimos
        if typing_after_id is not None:
            typing_queue.append(text)
            return
        
    if index < len(text):
        terminal.insert(tk.END, text[index])
        terminal.see(tk.END)
        typing_after_id = terminal.after(delay, type_text, terminal, text, delay, index + 1, )
    else:
        terminal.insert(tk.END, "\n")
        typing_after_id = None
        
        # Si hay mensajes en la cola, procesamos el siguiente
        if typing_queue:
            next_text = typing_queue.popleft()
            type_text(terminal, next_text, delay, 0)


# FUNCIONES PARA COMPROBAR LA EXISTENCIA DE ALGO
def user_exists(username: str, user_file) -> bool:
    users = load_data(user_file)
    return username in users


def car_exists(model:str, user_data:dict):
    car_pos = 0
    for car in user_data["garage"]:
        if car["model"] == model:
            return True, car_pos
        else:
            car_pos +=1
    return False, car_pos

def upgrade_exists(upgrade:str, user_data:dict, car_pos:int):
    for up in user_data["garage"][car_pos]["upgrades"]:
        if up["name"] == upgrade:
                    return True
    return False


# FUNCIONES DE CIFRADO ASIMÉTRICO (RSA)
def encrypt_rsa_message(message: bytes, public_key_str: str, terminal) -> bytes:
    public_key = RSA.import_key(public_key_str)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher_rsa.encrypt(message)
    type_text(terminal, 
                  "Encriptando clave simétrica temporal...\n"
                  "Buscando clave pública del rival...\n"
                  f"Usando clave pública del rival -> {public_key_str}\n"
                  f"Encriptación con RSA OAEP exitosa\n"
                  "\n") 
    
    return encrypted_message

def decrypt_rsa_message(encrypted_message: bytes, private_key_str: str, terminal) -> bytes:
    private_key = RSA.import_key(private_key_str)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher_rsa.decrypt(encrypted_message)
    type_text(terminal, 
                  "Desencriptando clave simétrica temporal...\n"
                  "Usando clave privada...\n"
                  f"Desencriptación con RSA OAEP exitosa\n"
                  "\n") 
    
    return decrypted_message
