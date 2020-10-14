from python:latest
RUN pip install mysql-connector flask flask_restful
RUN pip install requests
RUN pip install asyncio pathlib websockets
RUN pip install numpy
RUN mkdir src
WORKDIR src