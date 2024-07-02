import logging
import colorlog as colorlog


def logger_init():
    logging.basicConfig(filename='./applog.txt',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(asctime)s - %(log_color)s%(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_yellow',
        },
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)


logger_init()
