FROM python:3.9

# Create a virtual environment and activate it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Update pip and install mamba (optional, but recommended for better dependency solving)
RUN pip install --upgrade pip
RUN pip install conda
# Create a virtual environment and activate it


RUN conda install -c conda-forge mamba
RUN mamba install -c conda-forge beautifulsoup4 plotly networkx pandas -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM jupyter/base-notebook:latest
RUN mamba install -c esri arcgis --no-deps

RUN mkdir ./pages
COPY /pages ./pages

COPY /data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv

ENV PROJ_LIB='/opt/conda/share/proj'

USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}


EXPOSE 8765

CMD ["solara", "run", "./pages", "--host=0.0.0.0"]



