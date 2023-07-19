import requests
import logging
import pytz
from datetime import datetime
import sys
#sys.path.append("app/db/") # LOCAL
sys.path.append("db/") # CONTAINER

from db import db_connect

import env
from usd import get_currency_conversion
from exchange_time import get_time
from msg import send_message_to_telegram

# Configuração do logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#-------------------------------------
# FUNÇÃO QUE BUSCA TRANSAÇÕES A WALLET
#-------------------------------------
def get_wallet_transactions():
    url = f'https://blockchain.info/rawaddr/{env.WALLET_ADDRESS}'
    response = requests.get(url)
    
    try:
        response.raise_for_status()  # Verificar se ocorreu algum erro na resposta
        data = response.json()
        transactions = data['txs']
    except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError) as e:
        logger.error(f"Erro ao obter transações da carteira: {e}")
        transactions = []  # Definir uma lista vazia em caso de erro
    
    return transactions

#----------------------------------------------------------------
# FUNÇÃO QUE REALIZA O RASTREAMENTO DE NOVAS TRANSAÇÕES NA WALLET
#----------------------------------------------------------------
def track_wallet_transactions(context):
    transactions = get_wallet_transactions()
    for tx in transactions:
        inputs = tx['inputs']
        outputs = tx['out']
        for input_tx in inputs:
            if isinstance(input_tx, list):
                input_addresses = [inp['prev_out']['addr'] for inp in input_tx]
                if env.WALLET_ADDRESS in input_addresses:
                    process_transaction(tx, True)

        for output in outputs:
            if output['addr'] == env.WALLET_ADDRESS:
                process_transaction(tx, True)

#----------------------------------------------------------------------------------------------------
# FUNÇÃO QUE PROCESSA UMA TRANSAÇÃO E VERIFICA SE HÁ ENVOLVIMENTO DA WALLET. CONSTRÓI MSG DO TELEGRAM
#----------------------------------------------------------------------------------------------------
def process_transaction(tx, live=None):
    # CONEXÃO COM O BANCO DE DADOS
    conn, c = db_connect()

    # Verificar se o endereço da transação corresponde diretamente à sua carteira
    check_tx = {"Wallet_founded": False, "Type": None, "Index": None}
    for i, input in enumerate(tx['inputs']):
        if input['prev_out']['addr'] == env.WALLET_ADDRESS:
            check_tx["Wallet_founded"] = True
            check_tx["Type"] = "input"
            check_tx["Index"] = i
            #print(f"Encontrado endereço da WALLET no input {i}")
    for i, output in enumerate(tx['out']):
        if output['addr'] == env.WALLET_ADDRESS:
            check_tx["Wallet_founded"] = True
            check_tx["Type"] = "output"
            check_tx["Index"] = i
            #print(f"Encontrado endereço da WALLET no output {i}")
    if not check_tx["Wallet_founded"]:
        return

    # TIMESTAMP
    year, month, day, hour, minute, second = get_time(live, tx["time"])

    # Informações da transação
    transaction_hash = tx['hash']

    # Verificar se o hash da transação já existe no banco de dados
    c.execute("SELECT hash FROM transaction_hashes WHERE hash=?", (transaction_hash,))
    existing_hash = c.fetchone()
    if existing_hash and live:
        # Se o hash já existe e 'live' é True, não faz nada e retorna None
        conn.close()
        return None

    # Inserir o hash da transação no banco de dados se 'live' é True ou None
    if live:
        logger.info(f"Inserindo novo hash na tabela: " + tx['hash'])
        c.execute("INSERT INTO transaction_hashes (hash) VALUES (?)", (transaction_hash,))
        conn.commit()

    # Detectar se a transação é de saída (outcome) ou entrada (income) e selecionar dados da transação
    if check_tx["Type"] == "output":
        transaction_type = "Recebimento"
        transaction_value_btc = [out['value'] for out in tx['out'] if out['addr'] == env.WALLET_ADDRESS]
        sender_addresses = [input['prev_out']['addr'] for input in tx["inputs"] if input['prev_out']['addr'] != env.WALLET_ADDRESS]
        recipient_addresses = [out['addr'] for out in tx['out'] if out['addr'] == env.WALLET_ADDRESS]
        possiveis_dest = "Endereço"
        possiveis_remet = "Possíveis endereços"
    else:
        transaction_type = "Depósito"
        transaction_value_btc = [input['prev_out']['value'] for input in tx['inputs'] if input['prev_out']['addr'] == env.WALLET_ADDRESS]
        sender_addresses = [input['prev_out']['addr'] for input in tx["inputs"] if input['prev_out']['addr'] == env.WALLET_ADDRESS]
        recipient_addresses = [out['addr'] for out in tx['out'] if out['addr'] != env.WALLET_ADDRESS]
        possiveis_dest = "Possíveis endereços"
        possiveis_remet = "Endereço"

    transaction_time = datetime.fromtimestamp(tx['time'], pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
    transaction_value_btc = float(transaction_value_btc[0]) /  10**8
    usd_value = get_currency_conversion(f"{year:04d}", f"{month:02d}", f"{day:02d}", env.EXCHANGERATE_API_KEY, live)
    transaction_value_usd = transaction_value_btc / usd_value

    # Montar a mensagem com as informações da transação
    message = f"💰 Transação detectada!\n\n" \
              f"🔹 Tipo: {transaction_type}\n\n" \
              f"🔹 Hash de transação: {transaction_hash}\n\n" \
              f"🔹 {possiveis_remet} do Remetente: {', '.join(sender_addresses)}\n\n" \
              f"🔹 {possiveis_dest} do Destinatário: {', '.join(recipient_addresses)}\n\n" \
              f"🔹 Valor em BTC: {transaction_value_btc:.8f}\n\n" \
              f"🔹 Valor em USD: ${transaction_value_usd:.2f}\n\n" \
              f"🔹 Horário da Transação: {transaction_time}"

    conn.close()

    if live:
        send_message_to_telegram(env.CHAT_ID, message)

    return message

#----------------------------------------------
# FUNÇÃO QUE BUSCA A ÚLTIMA TRANSAÇÃO DA WALLET
#----------------------------------------------
def get_last_transaction():
    transactions = get_wallet_transactions()
    if transactions:
        return transactions[0]