cd src
docker build -t public-spending-api .
docker run --rm -d -p 5000:5000 --name pub-spend-api public-spending-api