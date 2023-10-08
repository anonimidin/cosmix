# smaller base image of python
FROM python:3.11-slim

# a non root user for security reasons
RUN adduser --disabled-password --gecos '' no-root-user
USER no-root-user

# Set environment variables
ENV BOT_API_TOKEN=${BOT_API_TOKEN}
ENV NASA_API_KEY=${NASA_API_KEY}

WORKDIR /app
COPY . /app

# Upgrade pip and install packages
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r req.txt

# Make port 80 available 
EXPOSE 80

# Check if everthing is ok
HEALTHCHECK CMD curl --fail http://localhost/ || exit 1

CMD ["python", "cosmix.py"]
