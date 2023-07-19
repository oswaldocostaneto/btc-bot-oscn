#------------------- docker build -t btc-bot-oscn . ---------------------#
# Imagem Python base
FROM python:3.9-slim-buster

# Copie o diretório do aplicativo para o contêiner
RUN mkdir /app
COPY app/requirements.txt /app

# Instale as dependências do script
RUN pip install --upgrade pip && pip install -r app/requirements.txt

# Defina o diretório de trabalho
WORKDIR /app

# Execute o script quando o contêiner for iniciado
CMD ["python", "main.py"]

# Volume compartilhado no comando docker run para a pasta app/