FROM python:3.9-slim
WORKDIR /app
RUN pip install flask
COPY server.py .
EXPOSE 80
CMD ["python", "server.py"]
