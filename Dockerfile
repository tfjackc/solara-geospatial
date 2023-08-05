FROM jupyter/base-notebook:latest
RUN conda create -n geo python=3.9
RUN echo conda activate geo

FROM python:3.9

# Create a virtual environment and activate it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Update pip and install mamba (optional, but recommended for better dependency solving)
RUN pip install --upgrade pip
RUN pip install mamba

# Install the required packages using mamba (or pip, if applicable)
RUN mamba install -n geo -c conda-forge beautifulsoup4 plotly networkx pandas -y

# Install ArcGIS package (or any other specific package with its dependencies)
RUN mamba install -c esri arcgis --no-deps

# Copy your project files
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pages ./pages
COPY data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv

ENV PROJ_LIB='/opt/venv/share/proj'

USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

EXPOSE 8765

CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
