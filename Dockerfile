FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run binds to $PORT on 0.0.0.0; the VM deploy keeps its own gunicorn.conf.py
RUN cp gunicorn.cloudrun.py gunicorn.conf.py

# Pre-compute every practical's default outputs and bake them into the image
# so /practical/N renders the result figures instantly and prints them as-is.
# This downloads the Gonzalez & Woods CH02 + CH03 datasets at build time.
RUN python precompute.py

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
