FROM python:3

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set work directory.
RUN mkdir /development

WORKDIR /development

COPY requirements.txt /development/

# Install dependencies.
RUN pip install -r requirements.txt
RUN pip install Pillow

# Copy project website.
COPY . /development/

EXPOSE 8080