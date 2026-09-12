"""
Módulo de criptografia para proteger credenciais sensíveis
"""
from cryptography.fernet import Fernet
from config.settings import settings


class EncryptionManager:
    """Gerencia encriptação e desencriptação de dados sensíveis"""

    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt(self, data: str) -> str:
        """Encripta uma string"""
        if not data:
            return None
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Desencripta uma string"""
        if not encrypted_data:
            return None
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Instância global
encryption_manager = EncryptionManager()
