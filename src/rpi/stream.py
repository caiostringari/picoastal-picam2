"""
# SCRIPT   : stream.py
# POURPOSE : Stream the camera to the screen.
# AUTHOR   : Caio Eadi Stringari
# DATE     : 05/03/2025
# VERSION  : 2.0
"""

# system
import os
from time import sleep

import json
import argparse

# PiCamera
from picamera2 import Picamera2, Preview

# logger
from loguru import logger
    

def run_single_camera(cfg: dict):
    """
    Capture frames and display them on the screen.
    
    Parameters
    ----------
    cfg : dict
        Configuration dictionary.
        
    Returns
    -------
    None
    """

    picam2 = Picamera2()
    picam2.start_preview(Preview.QTGL)

    preview_config = picam2.create_preview_configuration()
    
    # Set frame rate and size
    preview_config["main"]["size"] = (cfg["stream"]["width"], cfg["stream"]["height"])
    preview_config["main"]["framerate"] = cfg["stream"]["framerate"]
    
    picam2.configure(preview_config)

    picam2.start()
    sleep(cfg["stream"]["duration"])


def main():
    # verify if the configuraton file exists
    # if it does, then read it
    # else, stop
    inp = args.config[0]
    if os.path.isfile(inp):
        with open(inp, "r") as f:
            cfg = json.load(f)
        logger.info("Configuration file found...")
    else:
        raise IOError("No such file or directory \"{}\"".format(inp))

    # start the stream
    logger.info("Streaming the camera")
    
    run_single_camera(cfg)

    logger.info("Stream has ended.")


if __name__ == "__main__":


    # Argument parser
    parser = argparse.ArgumentParser()

    # input configuration file
    parser.add_argument("--configuration-file", "-cfg", "-i",
                        nargs=1,
                        action="store",
                        dest="config",
                        required=True,
                        help="Configuration JSON file.",)

    args = parser.parse_args()

    # call the main program
    main()