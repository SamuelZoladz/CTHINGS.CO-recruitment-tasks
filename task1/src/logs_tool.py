import argparse
import datetime
import logging

from src import config
from src import database


logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def parse_log_line(line):
    split_signs = ' - '
    parts = line.split(split_signs)
    if len(parts) < 4:
        raise ValueError("Log line is malformed, not enough parts: {}".format(line))
    while len(parts) > 4:
        parts[-2] = parts[-2] + split_signs + parts[-1]
        parts.pop()
    timestamp_str, service, level, message = parts

    try:
        timestamp = datetime.datetime.strptime(timestamp_str.strip(), '%Y-%m-%d %H:%M:%S,%f')
    except ValueError as ve:
        raise ValueError("Timestamp format is incorrect: {}".format(timestamp_str)) from ve

    return {
        'datetime': timestamp,
        'service': service.strip(),
        'severity': level.strip(),
        'message': message.strip()
    }


def parse_log_file(file_content):
    logs = []
    for i, line in enumerate(file_content, start=1):
        if line.strip():
            try:
                parsed_line = parse_log_line(line)
                logs.append(parsed_line)
            except ValueError as e:
                logger.error(f'Error parsing line {i}: {e}')
                return None

    return logs


def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
        return file_content
    except FileNotFoundError:
        logger.error(f"The file at {file_path} does not exist.")
        return None
    except PermissionError:
        logger.error(f"Permission denied when trying to read {file_path}.")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def add_logs(args):
    log_file_content = read_log_file(args.file)
    if log_file_content:
        parsed_logs = parse_log_file(log_file_content)
        if parsed_logs:
            mongo_client = database.MongoDBClient()
            mongo_client.insert_data(parsed_logs)
        else:
            logger.error("Failed to parse log file.")


def main():
    parser = argparse.ArgumentParser(description="Log File Manager")
    subparsers = parser.add_subparsers(help='commands')

    add_parser = subparsers.add_parser('add', help='Add log file')
    add_parser.add_argument('--file', required=True, help='Path to the log file')
    add_parser.set_defaults(func=add_logs)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
