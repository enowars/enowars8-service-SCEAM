FROM python:3.9-buster
RUN apt-get update && apt-get upgrade -y 
RUN apt-get install libzbar0 -y
RUN apt-get install libgl1 -y
RUN apt-get install libglx-mesa0 -y

# add checker user
RUN useradd -ms /bin/bash -u 1000 checker

WORKDIR /checker

COPY requirements.txt .

USER checker
RUN python3 -m pip install -r requirements.txt

COPY ./src .

USER root
RUN chown -R checker:checker /checker
USER checker
RUN python ./background_processor.py

ENTRYPOINT [ "/home/checker/.local/bin/gunicorn", "-c", "gunicorn.conf.py", "checker:app" ]
