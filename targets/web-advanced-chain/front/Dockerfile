FROM python:3.9-slim
WORKDIR /app
RUN pip install flask requests
COPY . .
EXPOSE 5003
CMD ["python", "app.py"]
