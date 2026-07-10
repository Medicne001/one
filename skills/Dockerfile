FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# install wkhtmltopdf and font dependencies for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    fontconfig \
    libxrender1 libxext6 libx11-6 \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
