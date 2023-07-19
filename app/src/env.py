import os
from dotenv import load_dotenv

# Obtém o caminho absoluto para o diretório superior
dir_path = os.path.dirname(os.path.abspath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))

# Constrói o caminho absoluto para o arquivo .env
env_path = os.path.join(parent_dir_path, '.env')

# Carrega as variáveis do arquivo .env
load_dotenv(env_path)

# Configurações do bot do Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')

# Configurações da carteira Bitcoin
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')