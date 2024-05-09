# Use a suitable base-image.
FROM python:3.10.9-slim

# Create a seperate user and chown new directories if necessary
# RUN addgroup --system service
# RUN adduser --system --ingroup service --uid 1000 service

# Create our mapped data volume endpoint
RUN mkdir /data/

# Copy our entrypoint.sh and make it executable
# COPY entrypoint.sh /
# RUN chmod +x /entrypoint.sh

# Copy our service
COPY src/ /src/
COPY main.py /
COPY requirements.txt /

# Change the working directory.
# WORKDIR /service/
# Expose the service's port
# EXPOSE 8000




RUN pip install -r requirements.txt

# Run the service
# ENTRYPOINT ["/entrypoint.sh"]
CMD gunicorn --bind 0.0.0.0:5000 main:app
