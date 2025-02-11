### 1. Build the Docker Image

Run the following command to build the Docker image for the scraper:

```bash
docker build -t my_scraper_app .
```

This command:
- Uses the Dockerfile in the current directory to create a Docker image named `my_scraper_app`.
- Installs all dependencies specified in `requirements.txt`.

### 2. Run the Docker Container

Once the image is built, run the container with the following command:

```bash
docker run -d -v "$(pwd)/output:/app/output" my_scraper_app
```

This command:
- Maps the `output` directory on your host system to `/app/output` inside the container.
- Ensures that any JSON data saved in `/app/output` within the container will be accessible in the `output` folder on your host.


```bash
docker ps
docker logs CONTAINER ID
```