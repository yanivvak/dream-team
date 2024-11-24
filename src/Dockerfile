
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
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

RUN pip install playwright
RUN playwright install --with-deps chromium

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Clone the autogen repository and install the package
RUN git clone https://github.com/microsoft/autogen.git
WORKDIR /app/autogen/python/packages/autogen-magentic-one
RUN pip install -e .

WORKDIR /app

# Expose the Streamlit port
EXPOSE 80

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=80"]
