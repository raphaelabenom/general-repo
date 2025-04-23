import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

def validate_bucket_name(bucket_name):
    """
    Valida se o nome do bucket segue as regras:
    - Apenas letras minúsculas e números.
    - Deve ter entre 3 e 63 caracteres.
    """
    if not bucket_name or len(bucket_name) < 3 or len(bucket_name) > 63:
        return False
    if not bucket_name.islower() or not bucket_name.isalnum():
        return False
    return True
