FROM python:3.12-slim
ARG API_PORT
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY api.py ./
COPY config.py ./
COPY database.py ./
COPY main.py ./
COPY sqs.py ./
EXPOSE ${API_PORT}
CMD ["python", "main.py"]
