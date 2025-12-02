# test_race.py
import unittest
import tempfile
import os
import json
import base64
from unittest.mock import Mock, patch
import sys

sys.path.append('.')

import race

class TestRaceFunctions(unittest.TestCase):

    def setUp(self):
        """Configuración antes de cada test"""
        self.test_dir = tempfile.mkdtemp()
        self.test_races_path = os.path.join(self.test_dir, "races")
        self.test_users_path = os.path.join(self.test_dir, "users.json")
        os.makedirs(self.test_races_path, exist_ok=True)
        
        race.RACES_PATH = self.test_races_path + "/"
        race.USERS_PATH = self.test_users_path
        
        self.mock_terminal = Mock()
        self.mock_terminal.delete = Mock()
        
        self.mock_user_key = b"fake_user_key_32_bytes_123456789"
        self.mock_msg_key = b"fake_msg_key_32_bytes_1234567890"
        
        self.sample_user_data = {
            "username": "testuser",
            "garage": [
                {
                    "brand": "Toyota",
                    "model": "Supra",
                    "stats": {
                        "speed": 80,
                        "handling": 70, 
                        "acceleration": 85,
                        "braking": 65
                    },
                    "upgrades": [
                        {"name": "Turbo Boost"},
                        {"name": "Sports Exhaust"}
                    ]
                }
            ],
            "points": 100000
        }
        
        self.sample_race_car = {
            "brand": "Nissan",
            "model": "Skyline",
            "stats": {
                "speed": 75,
                "handling": 80,
                "acceleration": 70,
                "braking": 75
            },
            "upgrades": []
        }
        
        with open(self.test_users_path, 'w') as f:
            json.dump({
                "rival_user": {"salt_password": "test", "salt_key": "test", "hash": "test"},
                "another_user": {"salt_password": "test", "salt_key": "test", "hash": "test"}
            }, f)

    def tearDown(self):
        """Limpieza después de cada test"""
        import shutil
        shutil.rmtree(self.test_dir)
        race.selected_race = 0

    # Tests para create_race
    @patch('race.RSA.import_key')
    @patch('race.encrypt_rsa_message')
    @patch('race.generate_random_symmetric_key')
    @patch('race.check_user_certificate')
    @patch('race.sign_message')
    @patch('race.store_data')
    @patch('race.load_data')
    @patch('race.encrypt_data')
    @patch('race.type_text')
    def test_create_race_success(self, mock_type_text, mock_encrypt, mock_load_data, mock_store_data,
                                mock_sign, mock_check_cert, mock_gen_sym_key, mock_encrypt_rsa, mock_import_key):
        """Test: Creación exitosa de carrera"""
        mock_load_data.side_effect = [
            [], # race_data
            {"rival_user": {"ac_name": "AC2"}} # rival_data
        ]
        mock_cipher = Mock()
        mock_cipher.nonce = b'16_bytes_nonce__'
        mock_encrypt.return_value = (mock_cipher, b'ciphertext', b'16_bytes_tag__')
        
        mock_sign.return_value = "signature_b64"
        mock_check_cert.return_value = b"rival_public_key"
        mock_gen_sym_key.return_value = b"symmetric_key_32_bytes"
        mock_encrypt_rsa.return_value = b"encrypted_symmetric_key"
        mock_import_key.return_value = Mock() # Return a mock key object
        
        # Mockear lectura de clave privada
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
            race.create_race("rival_user", self.sample_race_car, "testuser", self.mock_terminal, self.mock_user_key)
        
        # Verificar llamadas
        mock_sign.assert_called_once()
        mock_check_cert.assert_called_once()
        mock_gen_sym_key.assert_called_once()
        mock_encrypt.assert_called_once()
        mock_encrypt_rsa.assert_called_once()
        mock_store_data.assert_called_once()
        mock_type_text.assert_called_with(self.mock_terminal, "Carrera enviada correctamente\n")

    @patch('race.RSA.import_key')
    @patch('race.encrypt_rsa_message')
    @patch('race.generate_random_symmetric_key')
    @patch('race.check_user_certificate')
    @patch('race.sign_message')
    @patch('race.store_data')
    @patch('race.load_data')
    @patch('race.encrypt_data')
    def test_create_race_with_existing_races(self, mock_encrypt, mock_load_data, mock_store_data,
                                            mock_sign, mock_check_cert, mock_gen_sym_key, mock_encrypt_rsa, mock_import_key):
        """Test: Creación de carrera cuando ya existen carreras"""
        existing_races = [{"rival": "other_user", "race_car": "existing_data"}]
        mock_load_data.side_effect = [
            existing_races, # race_data
            {"rival_user": {"ac_name": "AC2"}} # rival_data
        ]
        mock_cipher = Mock()
        mock_cipher.nonce = b'16_bytes_nonce__'
        mock_encrypt.return_value = (mock_cipher, b'ciphertext', b'16_bytes_tag__')
        
        mock_check_cert.return_value = b"rival_public_key"
        mock_gen_sym_key.return_value = b"symmetric_key_32_bytes"
        mock_encrypt_rsa.return_value = b"encrypted_symmetric_key"
        mock_import_key.return_value = Mock()
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
            race.create_race("rival_user", self.sample_race_car, "testuser", self.mock_terminal, self.mock_user_key)
        
        saved_races = mock_store_data.call_args[0][0]
        self.assertEqual(len(saved_races), 2)
        self.assertEqual(saved_races[1]["rival"], "testuser")

    # Tests para send_race
    @patch('race.type_text')
    def test_send_race_empty_fields(self, mock_type_text):
        """Test: Envío de carrera con campos vacíos"""
        race.send_race("", "", "testuser", self.mock_terminal, "path", self.mock_user_key)
        mock_type_text.assert_called_with(self.mock_terminal, "Complete todos los campos por favor\n")

    # Eliminado test_send_race_invalid_msg_key ya que create_race ya no recibe msg_key (usa random)

    @patch('race.type_text')
    def test_send_race_self_race(self, mock_type_text):
        """Test: Envío de carrera contra uno mismo"""
        race.send_race("testuser", "Supra", "testuser", self.mock_terminal, "path", self.mock_user_key)
        mock_type_text.assert_called_with(
            self.mock_terminal, 
            "No puedes hacer una carrera contra ti mismo\nIntroduzca uno válido\n"
        )

    @patch('race.user_exists')
    @patch('race.type_text')
    def test_send_race_user_not_exists(self, mock_type_text, mock_user_exists):
        """Test: Envío de carrera a usuario inexistente"""
        mock_user_exists.return_value = False
        race.send_race("nonexistent_user", "Supra", "testuser", self.mock_terminal, "path", self.mock_user_key)
        mock_type_text.assert_called_with(
            self.mock_terminal, 
            "Username no encontrado\nIntroduzca uno válido\n"
        )

    @patch('race.load_encrypted_data')
    @patch('race.car_exists')
    @patch('race.user_exists')
    @patch('race.type_text')
    def test_send_race_car_not_exists(self, mock_type_text, mock_user_exists, mock_car_exists, mock_load_encrypted):
        """Test: Envío de carrera con coche inexistente"""
        mock_user_exists.return_value = True
        mock_load_encrypted.return_value = self.sample_user_data
        mock_car_exists.return_value = (False, 0)
        
        race.send_race("rival_user", "NonexistentCar", "testuser", self.mock_terminal, "path", self.mock_user_key)
        mock_type_text.assert_called_with(
            self.mock_terminal, 
            "No tienes este coche\nConsulta tu garage y elige uno\n"
        )

    @patch('race.create_race')
    @patch('race.load_encrypted_data')
    @patch('race.car_exists')
    @patch('race.user_exists')
    def test_send_race_success(self, mock_user_exists, mock_car_exists, mock_load_encrypted, mock_create_race):
        """Test: Envío de carrera exitoso"""
        mock_user_exists.return_value = True
        mock_load_encrypted.return_value = self.sample_user_data
        mock_car_exists.return_value = (True, 0)
        
        race.send_race("rival_user", "Supra", "testuser", self.mock_terminal, "path", self.mock_user_key)
        
        mock_create_race.assert_called_once_with(
            "rival_user", 
            self.sample_user_data["garage"][0], 
            "testuser", 
            self.mock_terminal, 
            self.mock_user_key
        )

    # Tests para type_race
    # Eliminado test_type_race_invalid_msg_key y test_type_race_no_msg_key ya que ahora se descifra con RSA

    @patch('race.type_text')
    @patch('race.load_data')
    def test_type_race_no_races(self, mock_load_data, mock_type_text):
        """Test: Visualización cuando no hay carreras"""
        mock_load_data.return_value = {}
        race.type_race("testuser", self.mock_terminal, self.mock_user_key)
        mock_type_text.assert_called_with(self.mock_terminal, "Vaya, nadie te ha desafiado aún\n")

    @patch('race.RSA.import_key')
    @patch('race.verify_signature')
    @patch('race.check_user_certificate')
    @patch('race.decrypt_rsa_message')
    @patch('race.desencrypt_data')
    @patch('race.load_data')
    @patch('race.type_text')
    def test_type_race_with_upgrades(self, mock_type_text, mock_load_data, mock_desencrypt, 
                                    mock_decrypt_rsa, mock_check_cert, mock_verify_sign, mock_import_key):
        """Test: Visualización de carrera con mejoras"""
        valid_base64_data = base64.b64encode(b"fake_encrypted_data_16_bytes").decode('ascii')
        valid_base64_key = base64.b64encode(b"fake_encrypted_key_32_bytes_").decode('ascii')
        
        race_data = [{
            "rival": "opponent", 
            "race_car": valid_base64_data,
            "symmetric_key": valid_base64_key,
            "signature": "sig"
        }]
        car_with_upgrades = {
            "brand": "Toyota",
            "model": "Supra",
            "stats": {"speed": 80, "handling": 70, "acceleration": 85, "braking": 65},
            "upgrades": [{"name": "Turbo"}, {"name": "Nitrous"}]
        }
        mock_load_data.side_effect = [
            race_data, # race_data
            {"opponent": {"ac_name": "AC2"}} # rival_data para verificar firma
        ]
        mock_desencrypt.return_value = car_with_upgrades
        mock_decrypt_rsa.return_value = b"sym_key"
        mock_check_cert.return_value = b"rival_pub_key"
        mock_verify_sign.return_value = True
        mock_import_key.return_value = Mock()
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
            race.type_race("testuser", self.mock_terminal, self.mock_user_key)
        
        mock_type_text.assert_called()
        call_args = mock_type_text.call_args[0][1]
        self.assertIn("- Turbo", call_args)
        self.assertIn("- Nitrous", call_args)

    # Tests para navegación
    @patch('race.type_race')
    def test_next_race(self, mock_type_race):
        """Test: Navegación a siguiente carrera"""
        initial_position = race.selected_race
        race.next_race("testuser", self.mock_terminal, self.mock_user_key)
        self.assertEqual(race.selected_race, initial_position + 1)
        mock_type_race.assert_called_once_with("testuser", self.mock_terminal, self.mock_user_key)

    @patch('race.type_race')
    def test_previous_race(self, mock_type_race):
        """Test: Navegación a carrera anterior"""
        race.selected_race = 1
        race.previous_race("testuser", self.mock_terminal, self.mock_user_key)
        self.assertEqual(race.selected_race, 0)
        mock_type_race.assert_called_once_with("testuser", self.mock_terminal, self.mock_user_key)

    # Tests para race (ejecución de carrera)
    # Eliminado test_race_invalid_msg_key

    @patch('race.RSA.import_key')
    @patch('race.verify_signature')
    @patch('race.check_user_certificate')
    @patch('race.decrypt_rsa_message')
    @patch('race.load_data')
    @patch('race.load_encrypted_data')
    @patch('race.car_exists')
    @patch('race.type_text')
    def test_race_car_not_exists(self, mock_type_text, mock_car_exists, mock_load_encrypted, mock_load_data,
                                mock_decrypt_rsa, mock_check_cert, mock_verify_sign, mock_import_key):
        """Test: Ejecución de carrera con coche inexistente"""
        valid_base64_data = base64.b64encode(b"fake_encrypted_car_data_16b").decode('ascii')
        valid_base64_key = base64.b64encode(b"fake_encrypted_key_32_bytes_").decode('ascii')
        race_data = [{
            "rival": "opponent", 
            "race_car": valid_base64_data,
            "symmetric_key": valid_base64_key,
            "signature": "sig"
        }]
        
        mock_load_data.side_effect = [
            race_data, # race_data
            {"opponent": {"ac_name": "AC2"}} # rival_data
        ]
        mock_load_encrypted.return_value = self.sample_user_data
        mock_car_exists.return_value = (False, 0)
        
        mock_decrypt_rsa.return_value = b"sym_key"
        mock_check_cert.return_value = b"rival_pub_key"
        mock_verify_sign.return_value = True
        mock_import_key.return_value = Mock()

        with patch('race.desencrypt_data') as mock_desencrypt:
            mock_desencrypt.return_value = {
                "brand": "Nissan", "model": "Skyline",
                "stats": {"speed": 70, "handling": 60, "acceleration": 65, "braking": 55},
                "upgrades": []
            }
            
            with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
                race.race("testuser", "path", self.mock_user_key, self.mock_terminal, "NonexistentCar")
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "No tienes este coche\nConsulta tu garage y elige uno\n"
            )

    @patch('random.randint')
    @patch('race.RSA.import_key')
    @patch('race.verify_signature')
    @patch('race.check_user_certificate')
    @patch('race.decrypt_rsa_message')
    @patch('race.store_encrypted_data')
    @patch('race.store_data')
    @patch('race.load_data')
    @patch('race.desencrypt_data')
    @patch('race.load_encrypted_data')
    @patch('race.car_exists')
    @patch('race.type_text')
    def test_race_user_wins(self, mock_type_text, mock_car_exists, mock_load_encrypted, 
                        mock_desencrypt, mock_load_data, mock_store_data, 
                        mock_store_encrypted, mock_decrypt_rsa, mock_check_cert, mock_verify_sign, mock_import_key, mock_randint):
        """Test: Usuario gana la carrera"""
        mock_car_exists.return_value = (True, 0)
        mock_load_encrypted.return_value = self.sample_user_data
        
        opponent_car = {
            "brand": "Nissan", "model": "Skyline",
            "stats": {"speed": 70, "handling": 60, "acceleration": 65, "braking": 55},  
            "upgrades": []
        }
        
        mock_desencrypt.return_value = opponent_car
        valid_base64_key = base64.b64encode(b"fake_encrypted_key_32_bytes_").decode('ascii')
        mock_load_data.side_effect = [
            [{"rival": "opponent", "race_car": "data", "symmetric_key": valid_base64_key, "signature": "s"}], # race_data
            {"opponent": {"ac_name": "AC2"}} # rival_data
        ]
        mock_randint.return_value = 5  
        
        mock_decrypt_rsa.return_value = b"sym_key"
        mock_check_cert.return_value = b"rival_pub_key"
        mock_verify_sign.return_value = True
        mock_import_key.return_value = Mock()

        race.selected_race = 0
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
            race.race("testuser", "path", self.mock_user_key, self.mock_terminal, "Supra")
        
        updated_user_data = mock_store_encrypted.call_args[0][0]
        self.assertEqual(updated_user_data["points"], 100000 + 200)
        
        from unittest.mock import ANY
        mock_store_data.assert_called_once_with([], ANY)

    @patch('random.randint')
    @patch('race.RSA.import_key')
    @patch('race.verify_signature')
    @patch('race.check_user_certificate')
    @patch('race.decrypt_rsa_message')
    @patch('race.store_encrypted_data')
    @patch('race.store_data')
    @patch('race.load_data')
    @patch('race.desencrypt_data')
    @patch('race.load_encrypted_data')
    @patch('race.car_exists')
    @patch('race.type_text')
    def test_race_user_loses(self, mock_type_text, mock_car_exists, mock_load_encrypted,
                           mock_desencrypt, mock_load_data, mock_store_data,
                           mock_store_encrypted, mock_decrypt_rsa, mock_check_cert, mock_verify_sign, mock_import_key, mock_randint):
        """Test: Usuario pierde la carrera"""
        mock_car_exists.return_value = (True, 0)
        
        user_data_losing = self.sample_user_data.copy()
        user_data_losing["points"] = 100000
        mock_load_encrypted.return_value = user_data_losing
        
        opponent_car = {
            "brand": "Nissan", "model": "Skyline",
            "stats": {"speed": 90, "handling": 80, "acceleration": 85, "braking": 75},  
            "upgrades": []
        }
        
        mock_desencrypt.return_value = opponent_car
        valid_base64_key = base64.b64encode(b"fake_encrypted_key_32_bytes_").decode('ascii')
        mock_load_data.side_effect = [
            [{"rival": "opponent", "race_car": "data", "symmetric_key": valid_base64_key, "signature": "s"}], # race_data
            {"opponent": {"ac_name": "AC2"}} # rival_data
        ]
        mock_randint.return_value = 5 
        
        mock_decrypt_rsa.return_value = b"sym_key"
        mock_check_cert.return_value = b"rival_pub_key"
        mock_verify_sign.return_value = True
        mock_import_key.return_value = Mock()
        
        race.selected_race = 0
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"encrypted_private_key")):
            race.race("testuser", "path", self.mock_user_key, self.mock_terminal, "Supra")
        
        updated_user_data = mock_store_encrypted.call_args[0][0]
        self.assertEqual(updated_user_data["points"], 100000 - 200)

if __name__ == '__main__':
    unittest.main()