# Bridge PBN replay page on Render (Web Service, Docker, Free plan).
#
# No build step and no third-party packages: server.py uses only the
# Python standard library, and index.html is a single self-contained
# page (its assets are inlined). Render sets $PORT at runtime;
# server.py reads it and binds 0.0.0.0, so no port is hardcoded here.
#
# Free-plan note: Render sleeps a free Web Service after 15 minutes
# idle; the first request after sleep takes about a minute to wake
# the service. That is a free-tier limit, not a bug in this service.
# The DDS solver itself is a separate Render service
# (https://dds-jt98.onrender.com by default in the page's DDS settings).

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY index.html ./
COPY pbn ./pbn/
COPY server.py ./

ENV PYTHONUNBUFFERED=1
# EXPOSE is documentation only; Render uses $PORT at runtime.
EXPOSE 10000

CMD ["python3", "server.py"]
