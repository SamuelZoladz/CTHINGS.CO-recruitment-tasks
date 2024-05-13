# Logs Tool

Logs Tool is a command-line application designed for managing and querying log files stored in a MongoDB database. The 
tool allows you to add log from file to the database and retrieve logs based on specific filtering conditions.

## Features

- **Add Log Files**: Import log entries from a file into MongoDB for persistent storage and further querying.
- **Query Logs**: Retrieve logs with the ability to filter based on log entry fields.

## Installation

Clone the repository and navigate into the application directory:

```bash
git clone https://github.com/SamuelZoladz/CTHINGS.CO-recruitment-tasks.git
cd CTHINGS.CO-recruitment-tasks/task1
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables in your system to configure the application:

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO if not set.
- `MONGODB_URI`: URI for connecting to MongoDB.
- `DATABASE_NAME`: The name of the database to use in MongoDB.
- `COLLECTION_NAME`: The name of the collection to store log data in MongoDB.


## Usage

The application is executed from the command line using the `logs_tool.py` script.

### Adding Log Files

To add a log file to the system:

```bash
python logs_tool.py add --file path/to/logfile
```

### Querying Logs

To retrieve logs based on specific conditions:

```bash
python logs_tool.py get --field datetime --eq "2021-12-01 00:00:00,000"
```

Valid fields include `datetime`, `message`, `severity`, and `service`. Note that comparison filters `--lt` (less than) 
and `--gt` (greater than) can only be applied to the `datetime` field.

To learn more about the commands, use the `-h` or `--help` flag

## Testing

Run tests using the following command from the root of the application (task1):

```bash
python -m unittest discover tests
```

