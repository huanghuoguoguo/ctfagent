FROM python:3.9-slim
WORKDIR /app
RUN pip install flask
COPY . .
# Initial config file
RUN echo "SECRET_KEY = 'super_secret_ctf_chain_key_2026'" > config.txt
# Flag is at /flag
RUN echo "CTF{advanced_chain_ssrf_to_lfi_to_pickle_rce_2026}" > /flag
EXPOSE 8000
CMD ["python", "app.py"]
