FROM python:3.9
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip
RUN pip install solara
RUN pip install ujson
RUN pip install requests-toolbelt
RUN pip install requests-ntlm
RUN pip install ntlm-auth

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install lxml

RUN pip install requests_oauthlib
RUN pip install geomet

RUN mkdir ./pages
COPY /pages ./pages

COPY /data/portalWebMaps_Test.csv ./data/portalWebMaps_Test.csv

ENV PROJ_LIB='/opt/conda/share/proj'

EXPOSE 8765

CMD ["solara", "run", "./pages", "--host=0.0.0.0"]
