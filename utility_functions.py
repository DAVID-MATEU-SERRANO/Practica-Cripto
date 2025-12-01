#utility_functions.py
import json
import tkinter as tk
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
import base64
import hashlib
import os
from collections import deque
from const import DEFAULT_ITERATIONS
import subprocess

#VARIABLES GLOBALES para la función type_text
typing_after_id = None
typing_after_id = None
typing_queue = deque()

# FUNCIÓN HASH
def hash_password(password: str, terminal, salt_password: bytes = None, write = True) -> tuple:
    # Genera el hash de la contraseña introducida por el usuario
    if salt_password is None:
        salt_password = os.urandom(16) #El salt se genera aleatoriamente
    
    value = salt_password + (password).encode("utf-8") #Aplicamos salt (distinto al que se usa para obtener la clave de usuario)

    for _ in range(DEFAULT_ITERATIONS):
        #Iteramos para que sea más difícil un ataque a fuerza brutas
        value = hashlib.sha256(value).digest()
    
    if write:
        type_text(terminal, 
        "HASH SHA-256...\n"
        f"Salt de 16 bytes para la contraseña generado y aplicado -> {salt_password}\n"
        f"Aplicando {DEFAULT_ITERATIONS} iteraciones...\n"
        f"Hash SHA-256 de 32 bytes -> {base64.b64encode(value).decode("ascii")} generado correctamente...\n"
        "\n")
    
    return (
        base64.b64encode(salt_password).decode("ascii"),
        base64.b64encode(os.urandom(16)).decode("ascii"), #salt_key (salt para construir la clave de usuario)
        base64.b64encode(value).decode("ascii")
    )


# FUNCIONES PARA GENERAR CLAVES
def generate_user_key(password: str, salt: bytes, terminal, write = True) -> bytes:
    #Genera una clave a partir de la contraseña de cada usuario -> todos los datos del usuario se cifran con esta clave
    #Se le aplica un salt aleatorio para añadir seguridad (este salt es distinto al que se aplica al hash de la contraseña)
    value = salt + (password).encode("utf-8")
    for _ in range(DEFAULT_ITERATIONS):
        #Iteramos para que sea más difícil un ataque a fuerza brutas
        value = hashlib.sha256(value).digest()
    
    if write:
        type_text(terminal, 
        "GENERACIÓN CLAVE SIMÉTRICA AES-GCM...\n"
        f"Salt de 16 bytes para la clave generado y aplicado -> {base64.b64encode(salt).decode("ascii")}\n"
        f"Aplicando {DEFAULT_ITERATIONS} iteraciones...\n"
        f"Clave simétrica del usuario generada correctamente...\n"
    "\n")

    return value  # Retornamos la clave AES-256 de 32 bytes

def generate_rsa_keypair(user_key: bytes, terminal, username: str, key_type: str) -> tuple:
    # Generamos las claves RSA (las guardamos en .pem para luego poder usarlas con OpenSSL)
    key = RSA.generate(2048)

    # Exportar la clave privada CIFRADA en formato PEM OpenSSL (PKCS#8)
    encrypted_private_key_pem = key.export_key(
        passphrase=user_key.hex(), 
        pkcs=8, 
        protection="scryptAndAES256-CBC" 
    )
    # Exportar la clave pública en formato PEM
    public_key_pem = key.publickey().export_key()

    # Construir rutas
    base_path = f"PKI/Users/{username}/{key_type}"
    ruta_privada = f"{base_path}/private_{key_type}.pem"
    ruta_publica = f"{base_path}/public_{key_type}.pem"

    # Crear carpetas si no existen
    os.makedirs(base_path, exist_ok=True)
    
    # Guardado de claves
    with open(ruta_privada, 'wb') as f:
        f.write(encrypted_private_key_pem)
    
    with open(ruta_publica, 'wb') as f:
        f.write(public_key_pem)
    
    type_text(terminal, 
    "GENERACIÓN PAR DE CLAVES RSA-2048...\n"
    f"Clave privada generada, cifrada con estándar OpenSSL con clave del usuario...\n"
    f"Clave pública generada...\n"
    "\n")

def generate_random_symmetric_key(terminal) -> bytes:
    # Generamos la clave simétrica temporal para el cifrado híbrido (AES-256 GCM)
    type_text(terminal, 
            "GENERACIÓN CLAVE SIMÉTRICA TEMPORAL...\n"
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
            "DESCIFRADO SIMÉTRICO con AES-256 GCM...\n"
            f"Nonce extraído: {base64.b64encode(nonce).decode('ascii')}\n"
            f"Tag de autenticidad extraído: {base64.b64encode(tag).decode('ascii')}\n"
            "Verificación MAC exitosa\n"
            "Desencriptación simétrica exitosa\n"
            "\n") 
        if decode:
            return json.loads(plaintext.decode("utf-8")) # Se devuelve el texto ya desencriptado
        else:
            return plaintext
            
    except ValueError:
        #Eso significa que la autenticación ha fallado o que las claves no son las mismas
        type_text(terminal, "ERROR GRAVE: las claves de cifrado y descifrado no coinciden o alguien ha modificado el archivo\n") 
        return None

def encrypt_data(key, plaintext, terminal):
    # A partir de una clave y un texto (en bits) se encripta
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    type_text(terminal, 
    "CIFRADO SIMÉTRICO con AES-256 GCM...\n"
    f"Usando nonce generado aleatoriamente -> {base64.b64encode(cipher.nonce).decode("ascii")}\n"
    f"Usada clave del usuario de 32 bytes... \n"
    f"Generado tag de autenticacion {base64.b64encode(tag).decode("ascii")}\n"
    "Encriptación simétrica exitosa\n"
    "\n")
    return cipher,ciphertext,tag #Devolvemos la información adicional para guardarla luego


# FUNCIONES LOAD/STORE
# Funciones load/store pero antes de guardar/cargar tienen que encriptar/desencriptar
def load_encrypted_data(filepath: str, key: bytes, terminal) -> dict:
    with open(filepath, "rb") as f:
        file_bytes = f.read()
    type_text(terminal, "Datos encriptados cargados correctamente\n")
    return desencrypt_data(file_bytes, key, terminal)
    

def store_encrypted_data(data: dict, filepath: str, key: bytes, terminal):
    plaintext = json.dumps(data).encode("utf-8") 
    cipher, ciphertext, tag = encrypt_data(key, plaintext, terminal)
    
    # Guardamos nonce + tag + ciphertext en binario
    with open(filepath, "wb") as f:
        f.write(cipher.nonce + tag + ciphertext)

    type_text(terminal, "Datos encriptados guardados correctamente\n") 

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


# FUNCIONES DE CIFRADO ASIMÉTRICO (RSA - 2048 bits OAEP)
def encrypt_rsa_message(message: bytes, public_key_str: str, terminal) -> bytes:
    # Ciframos el mensaje con la clave pública
    public_key = RSA.import_key(public_key_str)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher_rsa.encrypt(message)
    type_text(terminal, 
                "CIFRADO ASIMÉTRICO con RSA-2048 OAEP...\n"
                f"Usando clave pública del rival-> {public_key_str}\n"
                "Encriptación con RSA OAEP exitosa\n"
                "\n") 
    
    return encrypted_message

def decrypt_rsa_message(encrypted_message: bytes, private_key_str: str, terminal) -> bytes:
    # Desciframos el mensaje con la clave privada
    private_key = RSA.import_key(private_key_str)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher_rsa.decrypt(encrypted_message)
    type_text(terminal, 
                "DESCIFRADO ASIMÉTRICO con RSA-2048 OAEP...\n"
                "Usando clave privada propia...\n"
                "Desencriptación con RSA OAEP exitosa\n"
                "\n") 
    
    return decrypted_message

# FUNCIONES DE FIRMA DIGITAL (RSASSA-PSS)
def sign_message(private_key_bytes: bytes, message: str, terminal) -> str:
    # Cargamos la clave privada de firma
    signing_key = RSA.import_key(private_key_bytes)
    
    # Calculamos el hash del mensaje (SHA-256)
    h = SHA256.new(message.encode('utf-8'))
    
    # Firmamos el hash usando RSASSA-PSS (añade padding y salt)
    signer = pss.new(signing_key)
    signature = signer.sign(h)
    type_text(terminal, 
                  "GENERACIÓN DE FIRMA DIGITAL RSASSA-PSS...\n"
                  "Usando clave privada propia...\n"
                  f"Firma digital generada exitosamente --> {base64.b64encode(signature).decode('ascii')}\n"
                  "\n") 

    return base64.b64encode(signature).decode('ascii')
    
def verify_signature(public_key_bytes: bytes, message: str, signature_b64: str, terminal) -> bool:
    try:
        # Cargamos la clave pública
        verification_key = RSA.import_key(public_key_bytes)
        
        signature_bytes = base64.b64decode(signature_b64)
        
        # Recalcular el hash del mensaje recibido
        h = SHA256.new(message.encode('utf-8'))
        
        verifier = pss.new(verification_key)
        
        # Verificar la firma (lanza excepción si no es válida)
        verifier.verify(h, signature_bytes)
        
        type_text(terminal, 
                  "VERIFICACIÓN DE FIRMA DIGITAL RSASSA-PSS...\n"
                  "Usando clave pública del rival...\n"
                  f"Firma digital verificada exitosamente --> {signature_b64}\n"
                  "\n") 
        
        return True
        
    except (ValueError, TypeError):
        # La firma no era correcta
        type_text(terminal, 
                  "VERIFICACIÓN DE FIRMA DIGITAL RSASSA-PSS...\n"
                  "Usando clave pública...\n"
                  f"Firma digital verificada incorrectamente --> {signature_b64}\n"
                  "\n") 
        return False

## FUNCIONES DE CERTIFICADOS OPENSSL
def create_user_certificate(username: str, user_key: bytes, key_type: str, terminal):
    """
    Genera un CSR (Certificate Signing Request) usando OpenSSL y lo envía a AC2 para firmarlo. AC2 lo firma y 
    envía el certificado firmado al usuario. 
    """
    user_dir = f"PKI/Users/{username}/{key_type}"
    private_key_path = f"{user_dir}/private_{key_type}.pem"
    csr_path = f"{user_dir}/{username}_{key_type}_req.pem"
    cert_path = f"{user_dir}/{username}_{key_type}_cert.pem"
    
    # Campos del certificado
    email = f"{username}@criptoracers.es"
    subject = f"/C=ES/ST=MADRID/O=Cryptoracers - Fundacion/CN={username}/emailAddress={email}"
    
    # Generar el CSR
    cmd_csr = [
        "openssl", "req",
        "-new",
        "-key", private_key_path,
        "-out", csr_path,
        "-subj", subject,
        "-passin", f"pass:{user_key.hex()}"  
    ]
    
    try:
        subprocess.run(cmd_csr, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        type_text(terminal, f"ERROR generando CSR: {e.stderr}\n")
        return None
    except Exception as e:
        type_text(terminal, f"ERROR inesperado en CSR: {str(e)}\n")
        return None
    
    # Copiar CSR a AC2/solicitudes
    ac2_solicitudes = "PKI/AC2/solicitudes"
    dest_csr = f"{ac2_solicitudes}/{username}_{key_type}_req.pem"
    subprocess.run(["cp", csr_path, dest_csr], capture_output=True, text=True, check=True)

    #Leer la solicitud del certificado
    # Leer el contenido de la solicitud (CSR)
    cmd_read_csr = [
        "openssl", "req",
        "-in", f"./solicitudes/{username}_{key_type}_req.pem",
        "-text",
        "-noout"
    ]
    result = subprocess.run(cmd_read_csr, cwd="PKI/AC2", capture_output=True, text=True, check=True)
    csr_content = result.stdout  

    # Comando para firmar (ejecutado desde el directorio de AC2)
    cmd_sign = [
        "openssl", "ca",
        "-in", f"./solicitudes/{username}_{key_type}_req.pem",
        "-out", f"./nuevoscerts/{username}_{key_type}_cert.pem", "-notext",
        "-config", "openssl_AC2.cnf",
        "-passin", "pass:cripto_racers_private_key_password_ac2",
        "-batch"  
    ]
    
    try:
        subprocess.run(cmd_sign, cwd="PKI/AC2", capture_output=True, text=True, check=True)
        type_text(terminal, f"Certificado firmado por AC2 correctamente\n")
    except subprocess.CalledProcessError as e:
        type_text(terminal, f"Error firmando certificado: {e.stderr}\n")
        return None

    # Leer el contenido del certificado firmado
    cmd_read_cert = [
        "openssl", "x509",
        "-in", f"./nuevoscerts/{username}_{key_type}_cert.pem",
        "-text",
        "-noout"
    ]
    result = subprocess.run(cmd_read_cert, cwd="PKI/AC2", capture_output=True, text=True, check=True)
    cert_content = result.stdout
    
    # Copiar certificado firmado a la carpeta del usuario
    signed_cert_source = f"PKI/AC2/nuevoscerts/{username}_{key_type}_cert.pem"
    subprocess.run(["cp", signed_cert_source, cert_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    type_text(terminal, 
    f"CREACIÓN DE CERTIFICADO X.509 PARA {username}...\n"
    "Solicitud del certificado generada correctamente:\n"
    f"{csr_content}\n"
    "Enviando solicitud al AC2...\n"
    "Firma del certificado por AC2 exitosa:\n"
    f"{cert_content}\n"
    "Certificado guardado correctamente\n"
    "\n")