# API-SQS-MongoDB Service

This project demonstrates a FastAPI-based service that integrates with AWS SQS (Simple Queue Service) and MongoDB. The 
service allows you to send messages to the SQS queue, then retrieve them from that queue and add them to the MongoDB 
database.
## Setup and Installation

To run this project, you will need Docker and Docker Compose installed on your machine. Follow the steps below to get 
started.

### Step 1: Clone the Repository

```bash
git clone https://github.com/SamuelZoladz/CTHINGS.CO-recruitment-tasks.git
cd CTHINGS.CO-recruitment-tasks/task2
```

### Step 2: Create a `.env` File

Create a `.env` file in the project root directory with the necessary environment variables.

For example:

```plaintext
LOG_LEVEL=INFO
MONGODB_URI=mongodb+srv://<username>:<password>@<mongodb_url>/?retryWrites=true&w=majority&appName=<app_name>
DATABASE_NAME=api
COLLECTION_NAME=api
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_ENDPOINT_URL=http://localstack:4566
WORKER_QUEUE_URL=http://sqs.us-east-1.localstack.localstack.cloud:4566/000000000000/app-queue
API_PORT=8000
```

Make sure to replace the placeholder values with your actual configuration.

### Step 3: Build and Run the Docker Containers

```bash
docker-compose up --build
```

This command will build the Docker images and start the containers as defined in the `docker-compose.yml` file.


## Configuration

The following environment variables are used to configure the service:

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO if not set.
- `MONGODB_URI`: URI for connecting to MongoDB.
- `DATABASE_NAME`:  The name of the database to use in MongoDB.
- `COLLECTION_NAME`: The name of the collection to store log data in MongoDB.
- `AWS_DEFAULT_REGION`: AWS region (e.g., us-east-1).
- `AWS_ACCESS_KEY_ID`: AWS access key ID (for local development, you can use `test`).
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key (for local development, you can use `test`).
- `AWS_ENDPOINT_URL`: URL of the AWS endpoint.
- `WORKER_QUEUE_URL`: URL of the SQS queue.
- `API_PORT`: Port on which the FastAPI application will run.

## Usage

Once the service is up and running, you can interact with it by sending requests to the FastAPI endpoint.

### Posting a Message

To post a message to the queue and subsequently store it in MongoDB, send a POST request to the `/event` endpoint:

```bash
curl -X POST "http://localhost:8000/event" -H "Content-Type: application/json" -d '{"msg": "Your message here"}'
```

If successful, the message will be sent to the SQS queue and eventually inserted into the MongoDB collection specified 
in your configuration.

## Testing

Run tests using the following command from the app folder:

```bash
python -m unittest discover tests
```
