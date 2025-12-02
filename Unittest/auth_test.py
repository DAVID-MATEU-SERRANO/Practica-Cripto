# test_auth.py
import unittest
import tempfile
import os
import json
import base64
from unittest.mock import Mock, patch
import sys
import re

sys.path.append('.')

import auth

class TestAuthFunctions(unittest.TestCase):

    def setUp(self):
        # Crear directorio temporal para pruebas
        self.test_dir = tempfile.mkdtemp()
        self.test_users_path = os.path.join(self.test_dir, "users.json")
        self.test_user_data_path = os.path.join(self.test_dir, "User_data")
        os.makedirs(self.test_user_data_path, exist_ok=True)
        
        auth.USERS_PATH = self.test_users_path
        auth.USER_DATA_PATH = self.test_user_data_path
        
        self.mock_terminal = Mock()
        self.mock_terminal.delete = Mock()
        
        self.mock_root = Mock()
        self.mock_root.destroy = Mock()
        
        with open(self.test_users_path, 'w') as f:
            json.dump({}, f)

    def tearDown(self):
        #Limpieza después de cada test
        import shutil
        shutil.rmtree(self.test_dir)

    # Tests para register_user
    def test_register_user_empty_fields(self):
        """Test: Registro con campos vacíos"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("", "", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal, 
                "Complete todos los campos por favor\n"
            )

    def test_register_user_already_exists(self):
        """Test: Registro con usuario que ya existe"""
        with open(self.test_users_path, 'w') as f:
            json.dump({"existing_user": {"salt": "test", "hash": "test"}}, f)
        
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("existing_user", "ValidPassword123-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "El usuario ya existe\nIntroduzca uno distinto\n"
            )

    def test_register_user_invalid_username_short(self):
        """Test: Registro con nombre de usuario muy corto"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("user", "ValidPassword123-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir un nombre de usuario válido\nEl nombre de usuario debe tener longitud mínima de 5 y contener al menos 1 letra\n"
            )

    def test_register_user_invalid_username_no_letters(self):
        """Test: Registro con nombre de usuario sin letras"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("12345", "ValidPassword123-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir un nombre de usuario válido\nEl nombre de usuario debe tener longitud mínima de 5 y contener al menos 1 letra\n"
            )

    def test_register_user_invalid_password_short(self):
        """Test: Registro con contraseña muy corta"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("validuser", "Short1-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir una contraseña válida\nEsta debe contener al menos 1 mayúscula, 1 número, un símbolo (-, _) y tener una longitud mínima de 12"
            )

    def test_register_user_invalid_password_no_uppercase(self):
        """Test: Registro con contraseña sin mayúsculas"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("validuser", "invalidpass123-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir una contraseña válida\nEsta debe contener al menos 1 mayúscula, 1 número, un símbolo (-, _) y tener una longitud mínima de 12"
            )

    def test_register_user_invalid_password_no_number(self):
        """Test: Registro con contraseña sin números"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("validuser", "InvalidPass-", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir una contraseña válida\nEsta debe contener al menos 1 mayúscula, 1 número, un símbolo (-, _) y tener una longitud mínima de 12"
            )

    def test_register_user_invalid_password_no_symbol(self):
        """Test: Registro con contraseña sin símbolos"""
        with patch('auth.type_text') as mock_type_text:
            auth.register_user("validuser", "InvalidPass123", self.mock_terminal)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Debe introducir una contraseña válida\nEsta debe contener al menos 1 mayúscula, 1 número, un símbolo (-, _) y tener una longitud mínima de 12"
            )

    @patch('auth.create_user_certificate')
    @patch('auth.generate_rsa_keypair')
    @patch('auth.store_encrypted_data')
    @patch('auth.generate_user_key')
    @patch('auth.hash_password')
    @patch('auth.store_data')
    @patch('auth.load_data')
    def test_register_user_success(self, mock_load_data, mock_store_data, mock_hash_password, 
                                mock_generate_key, mock_store_encrypted, mock_gen_rsa, mock_create_cert):
        """Test: Registro exitoso"""
        valid_salt_password = b"16_bytes_salt!!"
        valid_salt_key = b"16_bytes_key_salt"
        valid_hash = b"32_bytes_hash_1234567890123456"
        
        valid_salt_password_b64 = base64.b64encode(valid_salt_password).decode('ascii')
        valid_salt_key_b64 = base64.b64encode(valid_salt_key).decode('ascii')
        valid_hash_b64 = base64.b64encode(valid_hash).decode('ascii')
        
        def load_data_side_effect(path):
            if path == auth.USERS_PATH:
                return {}  
            else:
                return {}  
        
        mock_load_data.side_effect = load_data_side_effect
        mock_hash_password.return_value = (
            valid_salt_password_b64,
            valid_salt_key_b64, 
            valid_hash_b64
        )
        mock_generate_key.return_value = b"32_bytes_user_key_123456789012"
        
        with patch('auth.type_text') as mock_type_text:
            # Ejecutar registro
            auth.register_user("validuser", "ValidPassword123-", self.mock_terminal)
            
            mock_store_data.assert_called_once()
            call_args = mock_store_data.call_args[0]
            saved_users = call_args[0]  # Primer argumento: datos a guardar
            save_path = call_args[1]    # Segundo argumento: path
            
            self.assertIn("validuser", saved_users)
            user_data = saved_users["validuser"]
            self.assertEqual(user_data["salt_password"], valid_salt_password_b64)
            self.assertEqual(user_data["salt_key"], valid_salt_key_b64)
            self.assertEqual(user_data["hash"], valid_hash_b64)
            
            mock_store_encrypted.assert_called_once()
            
            mock_generate_key.assert_called_once_with(
                "ValidPassword123-", 
                valid_salt_key,
                self.mock_terminal
            )
            
            # Verificar llamadas a PKI
            self.assertEqual(mock_gen_rsa.call_count, 2) # cod y sign
            self.assertEqual(mock_create_cert.call_count, 2) # cod y sign
            
            self.assertTrue(mock_type_text.called)

    # Tests para login_user
    def test_login_user_empty_fields(self):
        """Test: Login con campos vacíos"""
        with patch('auth.type_text') as mock_type_text:
            auth.login_user("", "", self.mock_terminal, self.mock_root)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Complete todos los campos por favor\n"
            )

    def test_login_user_not_exists(self):
        """Test: Login con usuario que no existe"""
        with patch('auth.type_text') as mock_type_text:
            auth.login_user("nonexistent", "password", self.mock_terminal, self.mock_root)
            
            mock_type_text.assert_called_with(
                self.mock_terminal,
                "Usuario no encontrado\nIntroduzca uno que esté registrado\n"
            )

    @patch('auth.show_secondary_menu')
    @patch('auth.generate_user_key')
    @patch('auth.hash_password')
    def test_login_user_success(self, mock_hash_password, mock_generate_key, mock_show_menu):
        """Test: Login exitoso"""
        user_data = {
            "salt_password": base64.b64encode(b"fake_salt_16_bytes").decode('ascii'),
            "salt_key": base64.b64encode(b"fake_salt_key_16_bytes").decode('ascii'),
            "hash": base64.b64encode(b"fake_hash_32_bytes_123456789012").decode('ascii')
        }
        
        with open(self.test_users_path, 'w') as f:
            json.dump({"testuser": user_data}, f)
        
        mock_hash_password.return_value = (None, None, user_data["hash"])
        mock_generate_key.return_value = b"fake_user_key_32_bytes_123456"
        
        with patch('auth.type_text') as mock_type_text:
            auth.login_user("testuser", "ValidPassword123-", self.mock_terminal, self.mock_root)
            
            self.mock_root.destroy.assert_called_once()
            
            mock_show_menu.assert_called_once()

    @patch('auth.hash_password')
    def test_login_user_wrong_password(self, mock_hash_password):
        """Test: Login con contraseña incorrecta"""
        user_data = {
            "salt_password": base64.b64encode(b"fake_salt_16_bytes").decode('ascii'),
            "salt_key": base64.b64encode(b"fake_salt_key_16_bytes").decode('ascii'),
            "hash": "stored_hash_b64"
        }
        
        with open(self.test_users_path, 'w') as f:
            json.dump({"testuser": user_data}, f)
        
        mock_hash_password.return_value = (None, None, "different_hash_b64")
        
        with patch('auth.type_text') as mock_type_text:
            auth.login_user("testuser", "WrongPassword123-", self.mock_terminal, self.mock_root)
            
            mock_type_text.assert_called()
            call_args = mock_type_text.call_args[0][1]
            self.assertIn("Los hashes no coinciden", call_args)
            self.assertIn("Contraseña incorrecta", call_args)

if __name__ == '__main__':
    unittest.main()