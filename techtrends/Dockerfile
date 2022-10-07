FROM python:3.9.7
LABEL maintainer="Christos Mavrogiannis"

COPY . /app

WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "app.py" ]