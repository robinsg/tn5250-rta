# Stage 1: The Builder (Compiles tn5250 v0.18 from GitHub)
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    autoconf \
    automake \
    libtool \
    libncurses-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone https://github.com/tn5250/tn5250.git
WORKDIR /tmp/tn5250

RUN ./autogen.sh \
    && ./configure --prefix=/usr/local --with-ssl \
    && make \
    && make install

# Stage 2: The Runtime (Clean, Small, Secure)
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    tmux \
    libncurses6 \
    libssl3 \
    iputils-ping \
    git \
    imagemagick \
    task-spooler \
    && rm -rf /var/lib/apt/lists/*

# 1. Copy the Binary
COPY --from=builder /usr/local/bin/tn5250 /usr/local/bin/

# 2. Copy the Terminal Definitions (Colors/Keys)
COPY --from=builder /usr/local/share/tn5250 /usr/local/share/tn5250

# 3. [NEW] Copy the Shared Libraries (The missing piece!)
COPY --from=builder /usr/local/lib/lib5250* /usr/local/lib/

# 4. [NEW] Register the libraries so Linux can find them
RUN ldconfig

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

CMD ["robot", "--outputdir", "results", "tests"]