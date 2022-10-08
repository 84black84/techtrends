FROM python:3.9.7
LABEL maintainer="Christos Mavrogiannis"

COPY . /techtrends

WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]

EXPOSE 3111