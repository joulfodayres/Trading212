"""
Módulo de criptografia para proteger credenciais sensíveis
"""
from cryptography.fernet import Fernet
from config.settings import settings


class EncryptionManager:
    """Gerencia encriptação e desencriptação de dados sensíveis"""

    def __init__(self):
        # ENCRYPTION_KEY deve ser uma string base64 válida (32 bytes)
        key = settings.ENCRYPTION_KEY
        # Se já for string, converter para bytes
        if isinstance(key, str):
            key = key.encode()
        self.cipher = Fernet(key)

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


# Funções de conveniência (wrapper)
def encrypt_text(data: str) -> str:
    """Encripta uma string usando a instância global"""
    return encryption_manager.encrypt(data)


def decrypt_text(encrypted_data: str) -> str:
    """Desencripta uma string usando a instância global"""
    return encryption_manager.decrypt(encrypted_data)
