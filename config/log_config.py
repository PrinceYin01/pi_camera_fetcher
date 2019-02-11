# -*- coding:utf-8 -*-
logging_configure = {
    'version': 1,
    "disable_existing_loggers": "false",
    "formatters": {
        "basic": {
            "class": "logging.Formatter",
            # "datefmt": "%I:%M:%S",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "basic",
            "stream": "ext://sys.stdout"
        },
        "info_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "basic",
            "filename": "/home/pi/Desktop/pi_camera_fetcher/logs/info/info.log",
            "when": "midnight",
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "basic",
            "filename": "/home/pi/Desktop/pi_camera_fetcher/logs/error/error.log",
            "when": "midnight",
            "encoding": "utf-8"
        },
        "debug_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "basic",
            "filename": "/home/pi/Desktop/pi_camera_fetcher/logs/debug/debug.log",
            "encoding": "utf-8",
            "maxBytes": 10000000,
            "backupCount": 1
        }
    },

    # "loggers": {
    #     "email_fetcher": {
    #         "handlers": ["console", "info_file", "error_file"],
    #         "level": "INFO"
    #     }
    # },

    "root": {
        # "handlers": ["console", "info_file", "error_file"],
        "handlers": ["info_file", "error_file", "debug_file"],
        "level": "INFO"
    }
}
