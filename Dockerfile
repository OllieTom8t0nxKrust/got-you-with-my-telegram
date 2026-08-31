# Dockerfile
FROM ubuntu:24.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies: python3, python3-pip, python3-venv, git, and tshark
RUN apt-get update && apt-get install -yq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    tshark \
    && rm -rf /var/lib/apt/lists/*

# Clone repository and copy updated script
RUN git clone https://github.com/n0a/telegram-get-remote-ip
COPY ./tg_get_ip.py ./telegram-get-remote-ip/tg_get_ip.py
COPY ./requirements.txt ./telegram-get-remote-ip/requirements.txt

# Create virtual environment, upgrade pip, and install updated requirements
RUN cd telegram-get-remote-ip \
    && python3 -m venv venv \
    && ./venv/bin/python3 -m pip install --no-cache-dir --upgrade pip \
    && ./venv/bin/python3 -m pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /telegram-get-remote-ip

# Default command using virtual environment python
CMD ["./venv/bin/python3", "tg_get_ip.py"]
