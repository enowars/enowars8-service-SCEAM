# Use a suitable base-image.
FROM python:3.12.2-slim
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


