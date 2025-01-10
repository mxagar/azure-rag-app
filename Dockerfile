FROM python:3.10

#COPY ./requirements.txt /backend/requirements.txt
COPY ./requirements.in /backend/requirements.in

WORKDIR /backend

RUN pip install pip-tools
RUN pip-compile requirements-dev.in
RUN pip install -r requirements.txt

COPY backend/* /backend

ENTRYPOINT [ "uvicorn" ]

CMD [ "--host", "0.0.0.0", "api:app" ]