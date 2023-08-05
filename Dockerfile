FROM jupyter/base-notebook:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir ./pages
COPY /pages ./pages

COPY /data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv

ENV PROJ_LIB='/opt/conda/share/proj'

USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}


EXPOSE 8765

CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
