FROM python:3.9-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory.
RUN mkdir /development

WORKDIR /development

COPY requirements.txt /development/

# Install dependencies.
RUN pip install -r requirements.txt
RUN pip install Pillow numpy opencv-python
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Copy project website.
COPY . /development/

EXPOSE 8080