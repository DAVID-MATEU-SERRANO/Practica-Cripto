#race.py
from utility_functions import verify_signature
from utility_functions import sign_message
from utility_functions import decrypt_rsa_message
from utility_functions import generate_random_symmetric_key
import base64
import json
import random
from const import RACES_PATH, USERS_PATH
from shop import car_exists
from utility_functions import desencrypt_data, encrypt_data, encrypt_rsa_message, load_encrypted_data, store_encrypted_data, type_text, user_exists
from utility_functions import load_data, store_data, type_text
import tkinter as tk

#Variables globales
selected_race = 0

#Se encarga de crear el mensaje el cual se almacenara en el path indicado. Cada usuario tiene su archivo con todas las carreras que le han propuesto
def create_race(rival, race_car_data, user_name, terminal, user_key):
    path = RACES_PATH + f"{rival}" + "_races.json" 
    race_data = load_data(path)
    if race_data == {}:
        race_data = []

    user_data = load_data(USERS_PATH)
    # Antes de cifrar nada, firmamos el mensaje
    # Obtenemos la clave privada del usuario
    private_key_encrypted = base64.b64decode(user_data[user_name]["private_key_sign"])
    private_key = desencrypt_data(private_key_encrypted, user_key, terminal, False)

    # Firmamos el mensaje 
    race_car_json = json.dumps(race_car_data)
    signature = sign_message(private_key, race_car_json, terminal)
    race_car_bytes = race_car_json.encode("utf-8") # Se usará luego para encriptar
    
    # Dentro del mensaje el campo de race_car va encriptado usando el cifrado híbrido
    # Primer obtenemos la clave pública del rival (la que se usa para cifrar)
    rival_public_key = user_data[rival]["public_key_cod"].encode('ascii')

    # Generamos la clave simétrica temporal para el cifrado híbrido (AES-256 GCM)
    symmetric_key = generate_random_symmetric_key(terminal)
    
    # Ciframos el coche con la clave simétrica temporal
    cipher, ciphertext, tag = encrypt_data(symmetric_key, race_car_bytes, terminal)
    encrypted_car = cipher.nonce + tag + ciphertext
    
    # Ciframos la clave simétrica temporal con la clave pública del rival
    encrypted_symmetric_key = encrypt_rsa_message(symmetric_key, rival_public_key, terminal)
    
    # Creamos el mensaje
    race = {
        "rival":user_name,
        "race_car":base64.b64encode(encrypted_car).decode("ascii"),
        "symmetric_key":base64.b64encode(encrypted_symmetric_key).decode("ascii"),
        "signature":signature
    }
    race_data.append(race)
    store_data(race_data, path)
    type_text(terminal, "Carrera enviada correctamente\n")


# Se encarga de la lógica de enviar el mensaje (comprobaciones previas y cargar el coche que se quiere enviar)
def send_race(rival:str, race_car:str, user_name:str, terminal, user_path, user_key):
    if rival == "" or race_car == "":
        type_text(terminal, "Complete todos los campos por favor\n")
        return 
    if rival == user_name:
        type_text(terminal, "No puedes hacer una carrera contra ti mismo\nIntroduzca uno válido\n")
        return
    if not user_exists(rival, USERS_PATH):
        type_text(terminal, "Username no encontrado\nIntroduzca uno válido\n")
        return
    
    # Aquí se tiene que desencriptar los datos cifrados del usuario para acceder el coche que se quiere enviar
    user_data = load_encrypted_data(user_path, user_key, terminal)
    car, car_pos = car_exists(race_car, user_data)
    if not car:
        type_text(terminal, "No tienes este coche\nConsulta tu garage y elige uno\n")
        return  
    race_car_data = user_data["garage"][car_pos]
    create_race(rival, race_car_data, user_name, terminal, user_key)


# Función que se encarga de mostrar por terminal todas las carreras disponibles para un usuario (para ello hay que descifrarlas primero con la contraseña simétrica cifrada)
def type_race(user_name, terminal, user_key):
    global selected_race
    terminal.delete("1.0", tk.END)

    race_path = RACES_PATH + f"{user_name}" + "_races.json" 
    
    # Cargamos el archivo de las carreras y hacemos las comprobaciones previas
    race_data = load_data(race_path)
    if race_data == {}:
        type_text(terminal, "Vaya, nadie te ha desafiado aún\n")
        return

    if selected_race == len(race_data):
        selected_race = 0
    
    if selected_race < 0:
        selected_race = len(race_data) - 1

    race_car = decrypt_selected_race(user_name, terminal, user_key, race_data) #Realiza la comprobación de la firma y descifra el coche
    if not race_car:
        # La firma era incorrecta
        return
    
    if race_car["upgrades"]:
        upgrades_text = ""
        for u in race_car["upgrades"]:
            upgrades_text += f"    - {u["name"]}"
    else:
        upgrades_text = "    (Sin mejoras)"

    type_text(terminal, 
    f"""
    --- {race_car["brand"]} {race_car["model"]} de {race_data[selected_race]["rival"]} ---
    Velocidad: {race_car["stats"]["speed"]}
    Manejo: {race_car["stats"]["handling"]}
    Aceleración: {race_car["stats"]["acceleration"]}
    Frenada: {race_car["stats"]["braking"]}
    Mejoras: {upgrades_text}""")

# Lógica para ir cambiando de carrera
def next_race(user_name:str, terminal, user_key):
    global selected_race
    selected_race +=1
    type_race(user_name, terminal, user_key)

def previous_race(user_name:str, terminal, user_key):
    global selected_race
    selected_race -=1
    type_race(user_name, terminal, user_key)    

# Carrera
def race(user_name, user_path, user_key, terminal, selected_race_car):
    global selected_race
    terminal.delete("1.0", tk.END)
    race_path = RACES_PATH + f"{user_name}" + "_races.json" 
    race_data = load_data(race_path)
    race_car = decrypt_selected_race(user_name, terminal, user_key, race_data)
    if not race_car:
        # La firma era incorrecta
        return

    oponent_race_car = race_car

    user_data = load_encrypted_data(user_path, user_key, terminal)
    car, car_pos = car_exists(selected_race_car, user_data)
    if not car:
        type_text(terminal, "No tienes este coche\nConsulta tu garage y elige uno\n")
        return

    user_race_car = user_data["garage"][car_pos]
    oponnent_score = oponent_race_car["stats"]["speed"] +  oponent_race_car["stats"]["handling"] +  oponent_race_car["stats"]["acceleration"] +  oponent_race_car["stats"]["braking"]
    user_score = user_race_car["stats"]["speed"] +  user_race_car["stats"]["handling"] +  user_race_car["stats"]["acceleration"] +  user_race_car["stats"]["braking"]
    # Hasta aquí recopila todos los datos necesarios (la info del coche del usuario actual y la info del coche que le han mandado)
    # Aquí comienza la carrera, que mediante los puntos de cada coche y algo de aleatoriedad acaba con un ganador y un perdedor
    # Despueés de actualizan los puntos correspondientemente
    adelantamiento = random.randint(1, 10)
    race_msg = ""
    race_msg += "###############################\n"
    if oponnent_score > user_score:
        race_msg += f"El {oponent_race_car["brand"]} {oponent_race_car["model"]} de {race_data[selected_race]["rival"]} toma la delantera!!\n"
        if adelantamiento > 7:
            race_msg += f"Increíble, el {oponent_race_car["brand"]} {oponent_race_car["model"]} de {race_data[selected_race]["rival"]} se ha salido en una curva y el {user_race_car["brand"]} {user_race_car["model"]} de {user_name} toma la delantera!!\n"
            winer_car = user_race_car
            winner = user_name
            loser_car = oponent_race_car
        else:
            winer_car = oponent_race_car
            winner = race_data[selected_race]["rival"]
            loser_car = user_race_car

    elif oponnent_score < user_score:
        race_msg += f"El {user_race_car["brand"]} {user_race_car["model"]} de {user_name} toma la delantera!!\n"
        if adelantamiento > 7:
            race_msg +=  f"Increíble, el {user_race_car["brand"]} {user_race_car["model"]} de {user_name} se ha salido en una curva y el {oponent_race_car["brand"]} {oponent_race_car["model"]} de {race_data[selected_race]["rival"]} toma la delantera!!\n"
            winer_car = oponent_race_car
            winner = race_data[selected_race]["rival"]
            loser_car = user_race_car
        else:
            winer_car = user_race_car
            winner = user_name
            loser_car = oponent_race_car
    else:
        race_msg += f"Ambos coches se mantienen par a par!!\n"
        if adelantamiento > 5:
            race_msg += f"Increíble, el {oponent_race_car["brand"]} {oponent_race_car["model"]} de {race_data[selected_race]["rival"]} se ha salido en una curva y el {user_race_car["brand"]} {user_race_car["model"]} de {user_name} toma la delantera!!\n"
            winer_car = user_race_car
            winner = user_name
            loser_car = oponent_race_car
        else:
            race_msg += f"Increíble, el {user_race_car["brand"]} {user_race_car["model"]} de {user_name} se ha salido en una curva y el {oponent_race_car["brand"]} {oponent_race_car["model"]} de {race_data[selected_race]["rival"]} toma la delantera!!\n"
            winer_car = oponent_race_car
            winner = race_data[selected_race]["rival"]
            loser_car = user_race_car

    if winner == user_name:
        race_msg += f"Enhorabuena tu {winer_car["brand"]} {winer_car["model"]} ha saido victorioso🏆\nSe te sumarán 200 puntos                         \n"
        user_data["points"] += 200

    else:
        race_msg += f"Vaya, parece que tu {loser_car["brand"]} {loser_car["model"]} ha perdido👎\nSe te restarán 200 puntos                         \n"
        user_data["points"] -= 200
    race_msg += "###############################\n"
    race_data.pop(selected_race)
    # Cuando ya acaba la carrera, se elimina esta de la lista de carreras posibles y se vuelven a encriptar los datos del usuario (ya que se han actualizado los puntos)
    type_text(terminal, "3                                                                                                \n")
    type_text(terminal, "2                                                                                                \n")
    type_text(terminal, "1                                                                                                \n")
    type_text(terminal, "YA!                                               \n")  
    type_text(terminal, race_msg)
    # Guardamos los datos del usuario y la lista de carreras
    store_data(race_data, race_path)
    store_encrypted_data(user_data, user_path, user_key, terminal)

# Función auxiliar que descifra la carrera seleccionada y verifica la firma 
def decrypt_selected_race(user_name, terminal, user_key, race_data):
    global selected_race
    # Desciframos la carrera seleccionada 
    # Primero desciframos la clave simétrica temporal
    user_data = load_data(USERS_PATH)
    private_key_encrypted = base64.b64decode(user_data[user_name]["private_key_cod"])
    private_key = desencrypt_data(private_key_encrypted, user_key, terminal, False)
    symmetric_key = decrypt_rsa_message(base64.b64decode(race_data[selected_race]["symmetric_key"]), private_key, terminal)
    # Luego desciframos el coche
    race_car = desencrypt_data(base64.b64decode(race_data[selected_race]["race_car"]), symmetric_key, terminal)

    # Verificamos la firma
    # Reconstruimos el string JSON para verificar la firma
    race_car_json = json.dumps(race_car)
    sign = verify_signature(user_data[race_data[selected_race]["rival"]]["public_key_sign"].encode("ascii"), race_car_json, race_data[selected_race]["signature"], terminal)
    if not sign:
        type_text(terminal, "Firma digital incorrecta\n")
        return
    return race_car
