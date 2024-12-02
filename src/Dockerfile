
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

RUN apt-get clean

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir playwright
RUN playwright install --with-deps chromium

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clone the autogen repository and install the package
RUN git clone --depth 1 https://github.com/microsoft/autogen.git
WORKDIR /app/autogen/python/packages/autogen-magentic-one
RUN pip install -e .

COPY . . 

# Expose the Streamlit port
EXPOSE 80

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=80"]