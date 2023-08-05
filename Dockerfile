FROM python:3.9

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install -U pip

# Install the solara package and other required packages
RUN pip install solara ujson requests-toolbelt requests-ntlm ntlm-auth lxml requests_oauthlib geomet pandas plotly networkx

# Set the working directory
WORKDIR /app

# Create the .solara directory inside the user's home directory
ENV HOME=/app
RUN mkdir -p $HOME/.solara

# Copy your pages and data files
COPY pages /app/pages
COPY data/portalWebMaps_Test.csv /app/data/portalWebMaps_Test.csv

# Set the PROJ_LIB environment variable
ENV PROJ_LIB='/opt/conda/share/proj'

# Expose the port
EXPOSE 8765

# Run the solara command
CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
