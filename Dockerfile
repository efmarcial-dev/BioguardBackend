FROM python:3.12-slim 

WORKDIR /app


RUN apt-get update && apt-get install -y \
gcc \
libpq-dev \
postgresql-client \
&& rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# add this line to make the script executable
RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]

# Expose post used by gunicorn
EXPOSE 8000

#Gunicorn binds to port 8000
CMD [ "gunicorn" , "--bind", "0.0.0.0:8000", "BioguardBackend.wsgi:application" ]