# This file creates a Docker container for the app
FROM python:3.9

WORKDIR /NowTrending

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/update_database.py"]

# To use:
#     open /Applications/Docker.app -- STARTS THE DOCKER APP FROM THE TERMINAL
#     docker ps -- CHECKS IF IT IS RUNNING
#     docker build -t now-trending .
#     docker run now-trending

