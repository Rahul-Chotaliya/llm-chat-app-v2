FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"
CMD ["uvicorn", "main:app", "--host", "0.0.0    0", "--port", "8000"]
