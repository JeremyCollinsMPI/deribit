docker run --rm -d -v $PWD:/src --name ui -p 5000:5000 jeremycollinsmpi/deribit:ui python api.py
docker run --rm -d -v $PWD:/src --name trader jeremycollinsmpi/deribit:ui python main.py