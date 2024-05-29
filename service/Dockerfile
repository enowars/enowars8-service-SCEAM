# Use a suitable base-image.
FROM python:3.12.2-slim

# Create a seperate user and chown new directories if necessary
# RUN addgroup --system service
# RUN adduser --system --ingroup service --uid 1000 service

# Create our mapped data volume endpoint
# RUN mkdir /data/

# Copy our entrypoint.sh and make it executable
# COPY entrypoint.sh /
# RUN chmod +x /entrypoint.sh

# Copy our service
COPY src/ /src/
COPY main.py /
COPY requirements.txt /
COPY cleanup.py /
COPY entrypoint.sh /

# Change the working directory.
# WORKDIR /service/
# Expose the service's port
# EXPOSE 8000




RUN pip install -r requirements.txt

# Run the service
ENTRYPOINT ["/entrypoint.sh"]


