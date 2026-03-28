FROM python:3.9-slim
WORKDIR /app
RUN pip install flask
COPY . .
# Flag is in /flag
RUN echo "CTF{rce_found_your_way_through_2026}" > /flag
EXPOSE 5002
CMD ["python", "app.py"]
