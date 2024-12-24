# Use a lightweight base image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code
# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file to the working directory
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code to the working directory
COPY ./ /code/

# Expose the port on which the application will run
EXPOSE 8002

# Run app.py when the container launches
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

# Start kafka consumer
#-m Flag: The python -m flag allows Python to treat app.file_by_chunks_consumer.__main__ as a module,
# ensuring that imports resolve correctly.
CMD ["python", "-m", "app.file_by_chunks_consumer.__main__"]