FROM python:3.10-slim

WORKDIR /app

COPY app/ /app/
# Copy requirements.txt separately because it lets Docker cache the install step if the code changes but the
# dependencies don’t — this makes builds faster.
COPY app/requirements.txt .

# Install FastAPI and OR-Tools dependencies.
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]