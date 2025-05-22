FROM python:3.11-slim

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy source code
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Setup cron job
COPY cronjob/cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob && \
    crontab /etc/cron.d/cronjob

# Create the log file
RUN touch /var/log/cron.log

# Expose Flask port
EXPOSE 5005

# Run cron + Flask together
CMD cron && python app.py
