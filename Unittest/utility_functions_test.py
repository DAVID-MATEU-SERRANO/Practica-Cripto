# test_utility_functions.py
import unittest
import tempfile
import os
import json
import base64
from unittest.mock import Mock, patch
import sys
from Crypto.Cipher import AES 

sys.path.append('.')

import utility_functions as uf

class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        """Configuración antes de cada test"""
        self.test_dir = tempfile.mkdtemp()
        self.mock_terminal = Mock()
        self.mock_terminal.delete = Mock()
        self.mock_terminal.insert = Mock()
        self.mock_terminal.see = Mock()
        self.mock_terminal.after = Mock()

    def tearDown(self):
        """Limpieza después de cada test"""
        import shutil
        shutil.rmtree(self.test_dir)
        uf.typing_after_id = None
        uf.typing_queue.clear()

    # Tests para hash_password
    def test_hash_password_generates_salt_when_none(self):
        """Test: hash_password genera salt cuando no se proporciona"""
        salt_password, salt_key, hash_b64 = uf.hash_password("TestPassword123-", self.mock_terminal)
        
        self.assertIsNotNone(salt_password)
        self.assertIsNotNone(salt_key)
        self.assertIsNotNone(hash_b64)
        self.assertEqual(len(base64.b64decode(salt_password)), 16)
        self.assertEqual(len(base64.b64decode(salt_key)), 16)
        self.assertEqual(len(base64.b64decode(hash_b64)), 32)

    def test_hash_password_uses_provided_salt(self):
        """Test: hash_password usa salt proporcionado"""
        provided_salt = b"provided_salt_16"
        salt_password, salt_key, hash_b64 = uf.hash_password("TestPassword123-", self.mock_terminal, provided_salt)
        
        decoded_salt = base64.b64decode(salt_password)
        self.assertEqual(decoded_salt, provided_salt)

    def test_hash_password_deterministic_with_same_salt(self):
        """Test: hash_password es determinístico con mismo salt y password"""
        salt = b"test_salt_16_bytes"
        password = "TestPassword123-"
        
        _, _, result1 = uf.hash_password(password, self.mock_terminal, salt)
        _, _, result2 = uf.hash_password(password, self.mock_terminal, salt)
        
        self.assertEqual(result1, result2)

    # Tests para generate_user_key
    def test_generate_user_key_returns_32_bytes(self):
        """Test: generate_user_key retorna clave de 32 bytes"""
        salt = b"test_salt_16_bytes"
        key = uf.generate_user_key("TestPassword123-", salt, self.mock_terminal)
        
        self.assertEqual(len(key), 32)  

    def test_generate_user_key_deterministic(self):
        """Test: generate_user_key es determinístico"""
        salt = b"test_salt_16_bytes"
        password = "TestPassword123-"
        
        key1 = uf.generate_user_key(password, salt, self.mock_terminal)
        key2 = uf.generate_user_key(password, salt, self.mock_terminal)
        
        self.assertEqual(key1, key2)

    # Tests para encrypt_data y desencrypt_data
    def test_encrypt_decrypt_round_trip(self):
        """Test: encrypt_data y desencrypt_data funcionan correctamente"""
        key = b"test_key_32_bytes_12345678901234"
        plaintext = b"Test plaintext message"
        
        cipher, ciphertext, tag = uf.encrypt_data(key, plaintext, self.mock_terminal)
        
        self.assertIsNotNone(cipher.nonce)
        self.assertIsNotNone(ciphertext)
        self.assertIsNotNone(tag)
        
        cipher2 = AES.new(key, AES.MODE_GCM, nonce=cipher.nonce)
        decrypted = cipher2.decrypt_and_verify(ciphertext, tag)
        
        self.assertEqual(decrypted, plaintext)

    @patch('utility_functions.type_text')
    def test_desencrypt_data_success(self, mock_type_text):
        """Test: desencrypt_data exitosa"""
        key = b"test_key_32_bytes_12345678901234"
        test_data = {"test": "data", "number": 123}
        plaintext = json.dumps(test_data).encode('utf-8')
        
        cipher = uf.encrypt_data(key, plaintext, self.mock_terminal)
        file_bytes = cipher[0].nonce + cipher[2] + cipher[1]  
        
        result = uf.desencrypt_data(file_bytes, key, self.mock_terminal)
        
        self.assertEqual(result, test_data)
        self.assertTrue(mock_type_text.called)

    @patch('utility_functions.type_text')
    def test_desencrypt_data_failure(self, mock_type_text):
        """Test: desencrypt_data con error"""
        key = b"test_key_32_bytes_12345678901234"
        wrong_key = b"wrong_key_32_bytes_1234567890123"
        test_data = {"test": "data"}
        plaintext = json.dumps(test_data).encode('utf-8')
        
        # Encriptar con una clave
        cipher = uf.encrypt_data(key, plaintext, self.mock_terminal)
        file_bytes = cipher[0].nonce + cipher[2] + cipher[1]
        
        # Intentar desencriptar con clave diferente
        result = uf.desencrypt_data(file_bytes, wrong_key, self.mock_terminal)
        
        # Verificar que retorna None y muestra error
        self.assertIsNone(result)
        mock_type_text.assert_called_with(
            self.mock_terminal,
            "ERROR GRAVE: las claves de cifrado y descifrado no coinciden o alguien ha modificado el archivo\n"
        )

    # Tests para load_data y store_data
    def test_store_and_load_data(self):
        """Test: store_data y load_data funcionan correctamente"""
        test_path = os.path.join(self.test_dir, "test.json")
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        # Guardar datos
        uf.store_data(test_data, test_path)
        
        # Verificar que el archivo existe
        self.assertTrue(os.path.exists(test_path))
        
        # Cargar datos
        loaded_data = uf.load_data(test_path)
        
        # Verificar que son iguales
        self.assertEqual(loaded_data, test_data)

    def test_load_data_file_not_found(self):
        """Test: load_data con archivo que no existe"""
        non_existent_path = os.path.join(self.test_dir, "nonexistent.json")
        
        # Debería retornar diccionario vacío
        result = uf.load_data(non_existent_path)
        self.assertEqual(result, {})

    def test_load_data_invalid_json(self):
        """Test: load_data con JSON inválido"""
        invalid_json_path = os.path.join(self.test_dir, "invalid.json")
        
        # Crear archivo con JSON inválido
        with open(invalid_json_path, 'w') as f:
            f.write("{invalid json")
        
        # Debería lanzar excepción
        with self.assertRaises(Exception) as context:
            uf.load_data(invalid_json_path)
        
        self.assertIn("Error leyendo el archivo", str(context.exception))

    # Tests para user_exists
    def test_user_exists_true(self):
        """Test: user_exists retorna True cuando usuario existe"""
        test_path = os.path.join(self.test_dir, "users.json")
        users_data = {"user1": {"data": "value1"}, "user2": {"data": "value2"}}
        
        with open(test_path, 'w') as f:
            json.dump(users_data, f)
        
        self.assertTrue(uf.user_exists("user1", test_path))
        self.assertTrue(uf.user_exists("user2", test_path))

    def test_user_exists_false(self):
        """Test: user_exists retorna False cuando usuario no existe"""
        test_path = os.path.join(self.test_dir, "users.json")
        users_data = {"user1": {"data": "value1"}}
        
        with open(test_path, 'w') as f:
            json.dump(users_data, f)
        
        self.assertFalse(uf.user_exists("nonexistent", test_path))

    def test_user_exists_file_not_found(self):
        """Test: user_exists con archivo que no existe"""
        non_existent_path = os.path.join(self.test_dir, "nonexistent.json")
        self.assertFalse(uf.user_exists("anyuser", non_existent_path))

    # Tests para car_exists
    def test_car_exists_true(self):
        """Test: car_exists encuentra coche existente"""
        user_data = {
            "garage": [
                {"brand": "Toyota", "model": "Supra"},
                {"brand": "Nissan", "model": "Skyline"},
                {"brand": "Honda", "model": "Civic"}
            ]
        }
        
        exists, position = uf.car_exists("Skyline", user_data)
        self.assertTrue(exists)
        self.assertEqual(position, 1)

    def test_car_exists_false(self):
        """Test: car_exists no encuentra coche inexistente"""
        user_data = {
            "garage": [
                {"brand": "Toyota", "model": "Supra"}
            ]
        }
        
        exists, _ = uf.car_exists("Ferrari", user_data)
        self.assertFalse(exists)

    def test_car_exists_empty_garage(self):
        """Test: car_exists con garage vacío"""
        user_data = {"garage": []}
        
        exists, position = uf.car_exists("AnyCar", user_data)
        self.assertFalse(exists)
        self.assertEqual(position, 0)

    # Tests para upgrade_exists
    def test_upgrade_exists_true(self):
        """Test: upgrade_exists encuentra mejora existente"""
        user_data = {
            "garage": [
                {
                    "brand": "Toyota",
                    "model": "Supra", 
                    "upgrades": [
                        {"name": "Turbo Boost"},
                        {"name": "Nitrous Oxide"}
                    ]
                }
            ]
        }
        
        exists = uf.upgrade_exists("Turbo Boost", user_data, 0)
        self.assertTrue(exists)

    def test_upgrade_exists_false(self):
        """Test: upgrade_exists no encuentra mejora inexistente"""
        user_data = {
            "garage": [
                {
                    "brand": "Toyota",
                    "model": "Supra",
                    "upgrades": [
                        {"name": "Turbo Boost"}
                    ]
                }
            ]
        }
        
        exists = uf.upgrade_exists("Spoiler", user_data, 0)
        self.assertFalse(exists)

    def test_upgrade_exists_no_upgrades(self):
        """Test: upgrade_exists sin mejoras"""
        user_data = {
            "garage": [
                {
                    "brand": "Toyota", 
                    "model": "Supra",
                    "upgrades": []
                }
            ]
        }
        
        exists = uf.upgrade_exists("AnyUpgrade", user_data, 0)
        self.assertFalse(exists)

    def test_generate_random_symmetric_key(self):
        """Test: generate_random_symmetric_key retorna clave de 32 bytes"""
        key = uf.generate_random_symmetric_key(self.mock_terminal)
        self.assertEqual(len(key), 32)
        self.assertIsInstance(key, bytes)

    @patch('utility_functions.RSA.generate')
    def test_generate_rsa_keypair(self, mock_rsa_generate):
        """Test: generate_rsa_keypair genera y guarda claves"""
        mock_key = Mock()
        mock_key.export_key.return_value = b"encrypted_private_key"
        mock_key.publickey.return_value.export_key.return_value = b"public_key"
        mock_rsa_generate.return_value = mock_key
        
        user_key = b"user_key_32_bytes_123456789012"
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            uf.generate_rsa_keypair(user_key, self.mock_terminal, "testuser", "cod")
            
            self.assertEqual(mock_file.call_count, 2)

    def test_encrypt_decrypt_rsa_message(self):
        """Test: encrypt_rsa_message y decrypt_rsa_message funcionan correctamente"""
        key = uf.RSA.generate(2048)
        public_key_pem = key.publickey().export_key()
        
        message = b"Secret message for hybrid encryption"
        
        encrypted = uf.encrypt_rsa_message(message, public_key_pem, self.mock_terminal)
        self.assertNotEqual(encrypted, message)
        
        decrypted = uf.decrypt_rsa_message(encrypted, key, self.mock_terminal)
        self.assertEqual(decrypted, message)

    def test_sign_verify_signature_success(self):
        """Test: Firma y verificación exitosa"""
        key = uf.RSA.generate(2048)
        public_key_pem = key.publickey().export_key()
        
        message = '{"data": "important race data"}'
        
        signature_b64 = uf.sign_message(key, message, self.mock_terminal)
        self.assertIsInstance(signature_b64, str)
        
        result = uf.verify_signature(public_key_pem, message, signature_b64, self.mock_terminal)
        self.assertTrue(result)

    def test_verify_signature_failure_modified_message(self):
        """Test: Verificación falla si el mensaje cambia"""
        key = uf.RSA.generate(2048)
        public_key_pem = key.publickey().export_key()
        
        message = '{"data": "original"}'
        signature_b64 = uf.sign_message(key, message, self.mock_terminal)
        
        modified_message = '{"data": "modified"}'
        result = uf.verify_signature(public_key_pem, modified_message, signature_b64, self.mock_terminal)
        self.assertFalse(result)

    def test_verify_signature_failure_invalid_signature(self):
        """Test: Verificación falla con firma inválida"""
        key = uf.RSA.generate(2048)
        public_key_pem = key.publickey().export_key()
        
        message = '{"data": "original"}'
        invalid_signature = base64.b64encode(b"invalid_signature").decode('ascii')
        
        result = uf.verify_signature(public_key_pem, message, invalid_signature, self.mock_terminal)
        self.assertFalse(result)

    @patch('subprocess.run')
    @patch('os.remove')
    def test_create_user_certificate(self, mock_remove, mock_subprocess):
        """Test: create_user_certificate ejecuta comandos OpenSSL"""
        mock_subprocess.return_value.stdout = "Certificate Content"
        
        user_key = b"user_key"
        
        with patch('builtins.open', unittest.mock.mock_open()):
            uf.create_user_certificate("testuser", user_key, "cod", self.mock_terminal, "AC2")
            
            self.assertTrue(mock_subprocess.called)
            self.assertEqual(mock_remove.call_count, 2)

    @patch('subprocess.run')
    def test_check_user_certificate_valid(self, mock_subprocess):
        """Test: check_user_certificate retorna clave pública si es válido"""
        def subprocess_side_effect(cmd, **kwargs):
            mock_res = Mock()
            if "verify" in cmd:
                mock_res.stdout = "testuser_cod_cert.pem: OK"
                mock_res.returncode = 0
            elif "x509" in cmd and "-pubkey" in cmd:
                mock_res.stdout = "PUBLIC KEY PEM CONTENT"
                mock_res.returncode = 0
            else:
                mock_res.returncode = 0
            return mock_res

        mock_subprocess.side_effect = subprocess_side_effect
        
        with patch('builtins.open', unittest.mock.mock_open()):
            public_key = uf.check_user_certificate("testuser", "cod", self.mock_terminal, "AC2")
            
            self.assertEqual(public_key, b"PUBLIC KEY PEM CONTENT")

    @patch('subprocess.run')
    def test_check_user_certificate_invalid(self, mock_subprocess):
        """Test: check_user_certificate retorna None si es inválido"""
        def subprocess_side_effect(cmd, **kwargs):
            mock_res = Mock()
            if "verify" in cmd:
                mock_res.stdout = "error 18 at 0 depth lookup: self signed certificate"
                mock_res.returncode = 1 
            else:
                mock_res.returncode = 0
            return mock_res

        mock_subprocess.side_effect = subprocess_side_effect
        
        with patch('builtins.open', unittest.mock.mock_open()):
            public_key = uf.check_user_certificate("testuser", "cod", self.mock_terminal, "AC2")
            
            self.assertIsNone(public_key)


if __name__ == '__main__':
    unittest.main()
    