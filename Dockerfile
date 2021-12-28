FROM python:3

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory.
RUN mkdir /upscaler_website

WORKDIR /upscaler_website

COPY requirements.txt /upscaler_website/

# Install dependencies.
RUN pip install -r requirements.txt

# Copy project website.
COPY . /upscaler_website/

EXPOSE 8080