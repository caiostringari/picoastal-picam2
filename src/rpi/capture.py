"""
# SCRIPT   : capture.py
# POURPOSE : Capture a sequence of frames record using the
#            raspberry pi HQ camera.
# AUTHOR   : Caio Eadi Stringari
# DATE     : 05/03/2021
# VERSION  : 2.0
"""

# system
import os
import sys
import subprocess

# files
from glob import glob
from natsort import natsorted

# dates
import datetime

# arguments
import json
import argparse

# PiCamera
from picamera2 import Picamera2
from picamera2.encoders import Quality


# logger
from loguru import logger


def set_camera_parameters(cfg: dict) -> Picamera2:
    """
    Set camera parameters.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary.

    Returns
    -------
    Picamera2
        Configured Picamera2 instance.
    """
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration()

    # set camera resolution [width x height]
    video_config["main"]["size"] = (cfg["capture"]["resolution"][0],
                                    cfg["capture"]["resolution"][1])
    picam2.configure(video_config)
    
    # set camera frame rate [Hz]
    picam2.set_controls({"FrameRate": cfg["capture"]["framerate"]})

    return picam2


def run_single_camera(cfg):
    """
    Capture frames and save them to a file.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary.

    Returns
    -------
    None
    """
    # set camera parameters
    picam2 = set_camera_parameters(cfg)
    
    # capture frames from the camera
    start = datetime.datetime.now()
    duration = cfg["capture"]["duration"]  # total number of seconds

    logger.info(f"Capturing {duration} seconds")
    logger.info(f"Capture started at {start}")
    fname = os.path.join(cfg["data"]["output"],
                         start.strftime("%Y%m%d_%H%M%S.mp4"))
    
    # start record and wait
    if cfg["capture"]["quality"].lower() == "low":
        quality = Quality.LOW
    elif cfg["capture"]["quality"].lower() == "medium":
        quality = Quality.MEDIUM
    elif cfg["capture"]["quality"].lower() == "high":
        quality = Quality.HIGH
    else:
        quality = Quality.HIGH
    
    picam2.start_and_record_video(output=fname, duration=duration, quality=quality)
    
    # stop recording
    end = datetime.datetime.now()
    logger.info(f"Capture finished at {end}")

    if cfg["post_processing"]["extract_frames"]:
        if cfg["post_processing"]["only_last_frame"]:
            logger.info("Extracting frames (only last frame)")
            out = os.path.join(cfg["data"]["output"],
                               start.strftime("%Y%m%d_%H%M"))
            extract_frames(fname, out, start, cfg["data"]["format"],
                           only_last=True)
        else:
            logger.info("Extracting frames")
            out = os.path.join(cfg["data"]["output"],
                               start.strftime("%Y%m%d_%H%M"))
            extract_frames(fname, out, start, cfg["data"]["format"])


def extract_frames(inp, out, date, ext, only_last=False):
    """
    Extract all frames from the encoded stream.

    Parameters
    ----------
    inp : str
        Input h.264 file.
    out : str
        Output path.
    date : datetime.datetime
        Capture date.
    ext : str
        File extension.
    only_last : bool, optional
        Extract only the last frame, by default False

    Returns
    -------
    None
    """
    if only_last:
        # make sure output path exists
        os.makedirs(out, exist_ok=True)

        logger.info("Calling FFMPEG (only last frame)")
        dt = date.strftime("%Y%m%d_%H%M")
        cmd = "ffmpeg -i {} -vf \"select=\'eq(n,1)\'\" -vframes 1 {}/first.bmp > /dev/null 2>&1".format(inp, out)
        subprocess.call(cmd, shell=True)
        logger.info("FFMPEG finished extracting frames")
        logger.info(f"First frame is: {os.path.join(out, 'first.bmp')}")
    else:
        # make sure output path exists
        os.makedirs(out, exist_ok=True)

        # call ffmpeg
        logger.info("Calling FFMPEG")
        dt = date.strftime("%Y%m%d_%H%M")
        cmd = "ffmpeg -i {} {}/000000-{}_%06d.{} > /dev/null 2>&1".format(
            inp, out, dt, ext)
        subprocess.call(cmd, shell=True)
        logger.info("FFMPEG finished extracting frames")

        # list all frames
        files = natsorted(glob(out + "/*.{}".format(ext)))
        logger.info("Extracted files are:")
        for file in files:
            logger.info(file)


def main():
    """
    Main function to run the capture process.

    Returns
    -------
    None
    """
    # verify if the configuraton file exists
    # if it does, then read it
    # else, stop
    inp = args.config[0]
    if os.path.isfile(inp):
        with open(inp, "r") as f:
            cfg = json.load(f)
        logger.info("Configuration file found, continue...")
    else:
        raise IOError("No such file or directory \"{}\"".format(inp))

    # get the date
    today = datetime.datetime.now()

    # check if current hour is in capture hours
    hour = today.hour
    capture_hours = cfg["data"]["hours"]
    if hour in capture_hours:
        logger.info("Sunlight hours. Starting capture cycle.")
    else:
        logger.info(f"Not enough sunlight at {today}. Not starting capture cycle.")
        sys.exit()

    # create output folder
    os.makedirs(cfg["data"]["output"], exist_ok=True)

    run_single_camera(cfg)


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