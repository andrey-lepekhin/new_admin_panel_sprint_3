# Pull base image
FROM python:3.10.2

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
RUN apt update
RUN apt-get install gettext -y # For Django translations to be able to compile

# Copy project
COPY . .

EXPOSE 8000/tcp

RUN chmod +x start.sh
RUN chmod +x wait-for-it.sh
CMD app/start.sh