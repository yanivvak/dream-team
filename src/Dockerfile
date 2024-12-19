
FROM python:3.12-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gnupg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies  
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh
COPY ./requirements.txt .
    
RUN /root/.local/bin/uv sync --system --no-cache

RUN pip install --no-cache-dir playwright
RUN playwright install --with-deps chromium

RUN apt-get clean

# Clone the autogen repository and install the package
RUN git clone --depth 1 --branch v0.4.0.dev11 https://github.com/microsoft/autogen.git
WORKDIR /autogen

WORKDIR /app/autogen/python/packages/autogen-magentic-one
RUN uv pip install -e .
COPY . . 

# Expose the Streamlit port
EXPOSE 80

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=80"]