FROM python:3.9.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["app.py"]