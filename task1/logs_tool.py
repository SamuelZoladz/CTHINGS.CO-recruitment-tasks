import argparse
from datetime import datetime
import logging

import config
import database

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
        timestamp = datetime.strptime(timestamp_str.strip(), '%Y-%m-%d %H:%M:%S,%f')
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


def format_log_entry(log_entry):
    try:
        dt = log_entry['datetime']
        if not isinstance(dt, datetime):
            logging.error("Datetime value is not a datetime object")
            return None

        formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

        service = log_entry['service']
        severity = log_entry['severity']
        message = log_entry['message']

        formatted_log = f"{formatted_dt} - {service} - {severity} - {message}"
        logging.debug("Log entry formatted successfully")
        return formatted_log
    except KeyError as e:
        logging.error(f"Missing key in log entry: {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while formatting the log entry: {e}")
        return None


def get_logs(args):
    allowed_fields = {'message', 'severity', 'service', 'datetime'}

    if args.field not in allowed_fields:
        logger.error(f"The field '{args.field}' is not allowed. Allowed fields are: {', '.join(allowed_fields)}.")
        return

    if args.field != 'datetime' and (args.lt is not None or args.gt is not None):
        logger.error("'--lt' and '--gt' filters can only be used with the 'datetime' field.")
        return

    filters = {
        '$eq': args.eq,
        '$ne': args.ne,
        '$lt': args.lt,
        '$gt': args.gt
    }

    set_filters = {key: val for key, val in filters.items() if val is not None}
    count = len(set_filters)

    if count == 1:
        filter_type, filter_value = next(iter(set_filters.items()))
        try:
            if args.field == 'datetime':
                filter_value = datetime.strptime(filter_value, '%Y-%m-%d %H:%M:%S,%f')
                logger.debug(f"Formated datetime:{filter_value}")

            mongo_client = database.MongoDBClient()
            data = mongo_client.find_data(args.field, filter_type, filter_value)
            if data:
                for x in data:
                    print(format_log_entry(x))
            else:
                logger.warning(f"No logs found that meet the requirements")
        except datetime.strptime as e:
            logger.error(f"Invalid date format. {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    else:
        if count == 0:
            logger.error("Error: No filter option specified. You must specify one of --eq, --ne, --lt, --gt.")
        else:
            logger.error("Error: Multiple filter options specified. You must specify exactly one of --eq, --ne, --lt, "
                         "--gt.")


def main():
    parser = argparse.ArgumentParser(description="Log File Manager: A tool for managing and querying log files.")
    subparsers = parser.add_subparsers(help='Available commands')

    add_parser = subparsers.add_parser(
        name='add',
        help='Add a new log file to the system',
        description='Add a log file to the system by specifying the file path. This operation stores the log file for '
                    'further querying.'
    )
    add_parser.add_argument('--file', required=True, help='Path to the log file that needs to be added')
    add_parser.set_defaults(func=add_logs)

    get_parser = subparsers.add_parser(
        name='get',
        help='Retrieve logs with specific filters',
        description='Retrieve logs based on specified filtering conditions. Requires --field parameter and at least '
                    'one other filter. Note: Filters --lt and --gt can only be applied to the "datetime" field.'
    )
    get_parser.add_argument(
        '--field',
        required=True,
        help='The field of the log entries to filter by, such as "datetime". Note: Comparison filters --lt and --gt '
             'are only available for "datetime".'
    )
    get_parser.add_argument('--eq', help='Retrieve log entries where the field is equal to this value')
    get_parser.add_argument('--ne', help='Retrieve log entries where the field is not equal to this value')
    get_parser.add_argument(
        '--lt',
        help='Retrieve log entries where the field is earlier/lower than this value (only valid for "datetime" field)'
    )
    get_parser.add_argument(
        '--gt',
        help='Retrieve log entries where the field is later/greater than this value (only valid for "datetime" field)'
    )
    get_parser.set_defaults(func=get_logs)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
