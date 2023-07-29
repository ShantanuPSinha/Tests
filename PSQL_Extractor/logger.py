import logging
import os
import json

def init_logger():
    global logger, newline
    log_file = "logs/log.log"
    i = 0

    while os.path.exists(log_file):
        log_file = f"logs/log{i}.log"
        i += 1
    
    # Configure logging
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)

    newline = logging.getLogger("newline")
    newline.setLevel(logging.ERROR)

    # Create a file handler and set the log file path
    fh1 = logging.FileHandler(log_file)

    # Create formatters for each logger
    f1 = logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
    f2 = logging.Formatter("%(message)s")

    # Set the formatters on the respective handlers
    fh1.setFormatter(f1)
    fh2 = logging.FileHandler(log_file)
    fh2.setFormatter(f2)

    # Add the handlers to the loggers
    logger.addHandler(fh1)
    newline.addHandler(fh2)

    logger.info(f"Starting New Run:")
    newline.error(f"=============================================================")

    return logger, newline


def dump_error(records : list):
    dump_file = "errorDumps.txt"

    with open (dump_file, "a") as f:
        json.dump(records, f)
        f.write('\n')
