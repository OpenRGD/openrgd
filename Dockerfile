# Usa un'immagine Python leggera ufficiale
FROM python:3.11-slim

# Metadati
LABEL maintainer="rfc@openrgd.org"
LABEL description="OpenRGD CLI - The Cognitive BIOS Toolchain"

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file del progetto nel container
COPY . /app

# Installa il pacchetto in modalità non-editable (installazione reale)
# --no-cache-dir riduce le dimensioni dell'immagine
RUN pip install --no-cache-dir .

# Imposta il comando di default.
# Quando lanci il container, è come se scrivessi "rgd"
ENTRYPOINT ["rgd"]

# Comando di default se l'utente non scrive nulla
CMD ["--help"]