# Adobe-India-Hackathon25
docker build --platform linux/amd64 -t myr1asolution:latest .
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none myr1asolution:latest