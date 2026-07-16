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


# Expose post used by gunicorn
EXPOSE 8000

# ... (rest of your file)


# CMD provides the default arguments to the entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "BioguardBackend.wsgi:application"]