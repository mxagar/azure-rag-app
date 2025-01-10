# Build the Docker image (use --no-cache if we want to force rebuild)
#   docker build -t azure-rag-app .
#   docker build --build-arg http_proxy=<proxy> --build-arg https_proxy=<proxy> -t azure-rag-app .
# Run the container: port-forward to our desktop 8080 port
#   docker run --env-file .env -p 8080:8000 azure-rag-app
# Open in browser: http://localhost:8080/docs

# Use Python 3.10 base image
FROM python:3.10

# Set proxy (if required)
ARG http_proxy
ARG https_proxy
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}

# Copy requirements.in into the container
COPY ./requirements.in /backend/requirements.in

# Set the working directory
WORKDIR /backend

# Install dependencies
RUN pip install pip-tools \
    && pip-compile requirements.in \
    && pip install -r requirements.txt

# Copy the backend code into the container
COPY ./backend /backend

# Expose the default Uvicorn port (optional)
EXPOSE 8000

# Set the entrypoint for the container
ENTRYPOINT [ "uvicorn" ]

# Define the default command
CMD [ "--host", "0.0.0.0", "--port", "8000", "api:app" ]
