# Use a suitable base-image.
FROM python:3.12.2-slim@sha256:5dc6f84b5e97bfb0c90abfb7c55f3cacc2cb6687c8f920b64a833a2219875997
RUN apt-get update && apt-get upgrade -y 
RUN apt-get install libgl1-mesa-glx -y
RUN apt-get install libglib2.0-0 libsm6 libxext6 libxrender-dev -y

# Copy our service
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY main.py /
COPY cleanup.py /
COPY entrypoint.sh /
COPY gunicorn.conf.py /
RUN chmod +x /entrypoint.sh
COPY src/ /src/
# Run the service
ENTRYPOINT ["/entrypoint.sh"]


