# Usa uma imagem base com Python e suporte a GUI
FROM python:3.11-slim

# Instala dependências do sistema (tkinter e libs gráficas)
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    xauth \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos para o container
WORKDIR /app
COPY . .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura variáveis de ambiente para GUI (X11)
ENV DISPLAY=host.docker.internal:0.0

# Comando para executar o aplicativo
CMD ["python", "login_app.py"]