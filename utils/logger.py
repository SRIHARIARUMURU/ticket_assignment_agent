import logging
import os


def setup_logger():

    # Create logs folder if it does not exist
    if not os.path.exists("logs"):

        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(

        filename="logs/application.log",

        level=logging.INFO,

        format=(

            "%(asctime)s - "

            "%(levelname)s - "

            "%(message)s"

        )

    )

    return logging