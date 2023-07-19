import requests
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()
EXCHANGERATE_API_KEY = os.getenv('EXCHANGERATE_API_KEY')

def get_currency_conversion(year, month, day, api_key, live):
    if live:
        url = f"http://apilayer.net/api/live?access_key={api_key}&currencies=BTC&source=USD&format=1"
    else:
        url = f"http://apilayer.net/api/historical?access_key={api_key}&date={year}-{month}-{day}&currencies=BTC&source=USD&format=1"
    response = requests.get(url)
    data = response.json()
    if 'quotes' in data:
        conversion_rate = data['quotes']['USDBTC']
        return float(conversion_rate)
    return 100000

