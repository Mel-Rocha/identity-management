FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

COPY requirements.txt .

# Instala dependências de sistema necessárias para o psycopg2
RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        gcc \
        python3-dev \
        build-essential \
        locales && \
    sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen pt_BR.UTF-8

# Configura o locale
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

# Instala dependências Python
RUN pip install -r requirements.txt

# Copia o restante dos arquivos da aplicação
COPY . .