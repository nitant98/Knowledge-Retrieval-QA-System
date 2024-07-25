FROM python:3.9

WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Now copy the rest of the app's source code
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "220"]
