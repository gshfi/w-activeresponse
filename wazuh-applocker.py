#!/usr/bin/env python
import os
import sys
import json
import datetime

# Constants
if os.name == 'nt':
    BASE_DIR = "C:\\Program Files (x86)\\ossec-agent\\active-response"
else:
    BASE_DIR = "/var/ossec/logs"

LOG_FILE = os.path.join(BASE_DIR, "active-responses.log")
RAW_DUMP_FILE = os.path.join(BASE_DIR, "alert-dump.json")
PARSED_DUMP_FILE = os.path.join(BASE_DIR, "parsed-dump.json")

ADD_COMMAND = 0
DELETE_COMMAND = 1
OS_SUCCESS = 0
OS_INVALID = -1

class Message:
    def __init__(self):
        self.alert = None
        self.command = OS_INVALID

def write_log(script_name, message):
    timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    with open(LOG_FILE, 'a') as log:
        log.write(f"{timestamp} {script_name}: {message}\n")

def parse_message(argv):
    msg = Message()
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            write_log(argv[0], "[ERROR] Empty stdin input")
            return msg
        
        data = json.loads(raw)
        msg.alert = data

        # Dump raw alert
        with open(RAW_DUMP_FILE, 'w') as dump:
            json.dump(data, dump, indent=4)

        command = data.get("command")
        if command == "add":
            msg.command = ADD_COMMAND
        elif command == "delete":
            msg.command = DELETE_COMMAND
        else:
            write_log(argv[0], f"[ERROR] Unknown command in alert: {command}")

    except Exception as e:
        write_log(argv[0], f"[ERROR] JSON parsing failed: {e}")
    
    return msg

# Recursive flattener
def flatten_json(nested, parent_key='', sep='.'):
    items = []
    if isinstance(nested, dict):
        for k, v in nested.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(nested, list):
        for i, v in enumerate(nested):
            new_key = f"{parent_key}{sep}{i}"
            items.extend(flatten_json(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, nested))
    return dict(items)

def extract_all_fields(alert):
    try:
        flat = flatten_json(alert)
        with open(PARSED_DUMP_FILE, 'w') as parsed:
            json.dump(flat, parsed, indent=4)
        return flat
    except Exception as e:
        return {"error": f"Failed to flatten alert: {e}"}

def main(argv):
    write_log(argv[0], "[INFO] AppLocker AR started")

    msg = parse_message(argv)
    if msg.command != ADD_COMMAND:
        write_log(argv[0], "[INFO] Not an ADD command, stopping")
        sys.exit(OS_SUCCESS)

    flat_data = extract_all_fields(msg.alert)

    if "error" in flat_data:
        write_log(argv[0], f"[ERROR] {flat_data['error']}")
    else:
        key_log = ', '.join([f"{k}={v}" for k, v in list(flat_data.items())[:5]])
        write_log(argv[0], f"[DEBUG] Extracted: {key_log} ...")

    write_log(argv[0], "[INFO] AppLocker AR completed")
    sys.exit(OS_SUCCESS)

if __name__ == '__main__':
    main(sys.argv)
