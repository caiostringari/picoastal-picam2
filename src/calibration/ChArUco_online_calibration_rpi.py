# SCRIPT   : ChArUco_online_calibraiton.py
# POURPOSE : Online camera calibration using ChArUco boards.
#            Only works with the raspberry pi camera.
# AUTHOR   : Caio Eadi Stringari

import os
import sys

# arguments
import json
import argparse

import cv2

import numpy as np

from time import sleep

import pickle
import json

# PiCamera
from picamera import PiCamera
from picamera.array import PiRGBArray

try:
    import gooey
    from gooey import GooeyParser
except ImportError:
    gooey = None


def flex_add_argument(f):
    """Make the add_argument accept (and ignore) the widget option."""

    def f_decorated(*args, **kwargs):
        kwargs.pop('widget', None)
        return f(*args, **kwargs)

    return f_decorated


# monkey-patching a private class
argparse._ActionsContainer.add_argument = flex_add_argument(
    argparse.ArgumentParser.add_argument)


# do not run GUI if it is not available or if command-line arguments are given.
if gooey is None or len(sys.argv) > 1:
    ArgumentParser = argparse.ArgumentParser

    def gui_decorator(f):
        return f
else:
    image_dir = os.path.realpath('../../doc/')
    ArgumentParser = gooey.GooeyParser
    gui_decorator = gooey.Gooey(
        program_name='ChArUco Board Creator',
        default_size=[800, 480],
        navigation="TABBED",
        show_sidebar=True,
        image_dir=image_dir,
        suppress_gooey_flag=True,
    )


# https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def set_camera_parameters(cfg):
    """
    Set camera parameters.

    All values come from the dict generated from the JSON file.

    :param cfg: JSON instance.
    :type cam: dict
    :return: None
    :rtype: None
    """
    # set camera resolution [width x height]
    camera = PiCamera()
    camera.resolution = cfg["capture"]["resolution"]

    # set camera frame rate [Hz]
    camera.framerate = cfg["capture"]["framerate"]

    # exposure mode
    camera.exposure_mode = cfg["exposure"]["mode"]

    if cfg["exposure"]["set_iso"]:
        camera.iso = cfg["exposure"]["iso"]

    return camera


@gui_decorator
def main():
    print("\nCamera calibration starting, please wait...\n")

    # Argument parser
    if not gooey:
        parser = argparse.ArgumentParser()
    else:
        parser = GooeyParser(description="ChArUco Online Calibration")

    # input configuration file
    if not gooey:
        parser.add_argument("--configuration-file", "-cfg", "-i",
                            nargs=1,
                            action="store",
                            dest="config",
                            required=True,
                            default="../rpi/config_rpi.cfg",
                            help="Configuration file (JSON).",)
    else:
        parser.add_argument("--configuration-file", "-cfg", "-i",
                            help="Configuration file (JSON)",
                            widget='FileChooser',
                            nargs=1,
                            action="store",
                            dest="config",
                            default="../rpi/config_rpi.cfg",
                            required=True)

    # board definition
    parser.add_argument("--squares_x",
                        action="store",
                        dest="squares_x",
                        default=5,
                        required=False,
                        help="Number of squares in the x direction.")

    parser.add_argument("--squares_y",
                        action="store",
                        dest="squares_y",
                        default=7,
                        required=False,
                        help="Number of squares in the y direction.")

    parser.add_argument("--square_length",
                        action="store",
                        dest="square_length",
                        required=False,
                        default=413,
                        help="Square side length (in pixels).")

    parser.add_argument("--marker_length",
                        action="store",
                        dest="marker_length",
                        required=False,
                        default=247,
                        help="Marker side length (in pixels).")

    parser.add_argument("--dictionary_id",
                        action="store",
                        dest="dictionary_id",
                        default="6X6_250",
                        required=False,
                        help="ArUco Dictionary id.")

    parser.add_argument("--max_images", "-N",
                        action="store",
                        dest="max_images",
                        required=False,
                        default=25,
                        help="Maximum number of images to use.",)

    parser.add_argument("--output", "-o",
                        action="store",
                        dest="output",
                        required=True,
                        help="Output pickle file.",)

    parser.add_argument("--calibrate_on_device",
                        action="store_true",
                        dest="calibrate_on_device",
                        help="Will calibrate on device, if parsed.",)

    args = parser.parse_args()

    max_images = int(args.max_images)

    # parse parameters
    squares_x = int(args.squares_x)  # number of squares in X direction
    squares_y = int(args.squares_y)  # number of squares in Y direction
    square_length = int(args.square_length)  # square side length (in pixels)
    marker_length = int(args.marker_length)  # marker side length (in pixels)
    dictionary_id = args.dictionary_id  # dictionary id

    # create board
    dict_id = getattr(cv2.aruco, "DICT_{}".format(dictionary_id))
    dictionary = cv2.aruco.getPredefinedDictionary(dict_id)

    # create the board instance
    board = cv2.aruco.CharucoBoard_create(
        squares_x, squares_y, square_length, marker_length, dictionary)

    # set camera parameters
    inp = args.config
    if os.path.isfile(inp):
        with open(inp, "r") as f:
            cfg = json.load(f)
        print("\nConfiguration file found, continue...")
    else:
        raise IOError("No such file or directory \"{}\"".format(inp))
    camera = set_camera_parameters(cfg)

    # read the data
    rawCapture = PiRGBArray(camera)

    # warm-up the camera
    print("  -- warming up the camera --")
    sleep(2)
    print("  -- starting now --")

    # store data
    all_corners = []
    all_ids = []
    total_images = 0

    # capture frames from the camera
    for frame in camera.capture_continuous(
            rawCapture, format="bgr", use_video_port=True):

        # grab the raw NumPy array representing the image, then initialize the
        # timestamp and occupied/unoccupied text
        image = frame.array

        # covert to grey scale
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            grey, dictionary)
        cv2.aruco.refineDetectedMarkers(
            grey, board, corners, ids, rejectedImgPoints)

        if len(corners) > 0:  # if there is at least one marker detected

            # refine
            retval, ref_corners, ref_ids = cv2.aruco.interpolateCornersCharuco(
                corners, ids, grey, board)

            if retval > 5:  # calibrateCameraCharuco needs at least 4 corners

                # draw board on image
                im_with_board = cv2.aruco.drawDetectedCornersCharuco(
                    frame, ref_corners, ref_ids, (0, 0, 0))
                im_with_board = cv2.aruco.drawDetectedMarkers(
                    im_with_board, corners, ids)

                # append
                all_corners.append(ref_corners)
                all_ids.append(ref_ids)

                if total_images > max_images:
                    print("\n  --> Found all images I needed. "
                          "Breaking the loop after {} images.".format(
                              max_images))
                    break

                total_images += 1

        else:
            pass

        # image to be displayed
        try:
            stream_img = im_with_board
        except Exception:
            stream_img = image  # image without the board.

        # resize to fit on screen
        rsize = (int(cfg["stream"]["resolution"][0]),
                 int(cfg["stream"]["resolution"][1]))
        resized = cv2.resize(stream_img, rsize,
                             interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Camera calibration, press 'q' to quit.", resized)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # destroy any open CV windows
    cv2.destroyAllWindows()

    # finalize
    if args.calibrate_on_device:

        print(
            "\n - Starting calibrateCameraCharuco(), this will take a while.")

        # calibrate the camera
        imsize = grey.shape
        retval, mtx, dist, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
            all_corners, all_ids, board, imsize, None, None)

        print(f"\n    - Calibration error: {round(retval, 2)} units")

        # output the results of the calibration
        out = {}
        outfile = open(args.output, 'wb')
        out["error"] = retval
        out["camera_matrix"] = mtx
        out["distortion_coefficients"] = dist
        out["rotation_vectors"] = rvecs
        out["translation_vectors"] = tvecs
        out["corners"] = all_corners
        out["ids"] = all_ids
        out["chessboard_size"] = board.getChessboardSize()
        out["marker_length"] = board.getMarkerLength()
        out["square_length"] = board.getSquareLength()

        if args.output.lower().endswith("json"):
            with open(args.output, 'w') as fp:
                json.dump(out, fp, cls=NumpyEncoder)
        else:
            out["last_frame"] = im_with_board
            # out["board"] = board
            with open(args.output, 'wb') as fp:
                pickle.dump(out, fp)

        # display the results

        # undistort
        h,  w = stream_img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
            mtx, dist, (w, h), 1, (w, h))

        dst = cv2.undistort(stream_img, mtx, dist, None, newcameramtx)
        resized = cv2.resize(dst, rsize,
                             interpolation=cv2.INTER_LINEAR)
        cv2.imshow("Undistorted image. Displaying for 20 seconds.", resized)
        cv2.waitKey(20000)
        cv2.destroyAllWindows()

    # output the corners and ids.
    else:
        out = {}
        outfile = open(args.output, 'wb')
        out["corners"] = all_corners
        out["ids"] = all_ids
        out["last_frame"] = im_with_board
        pickle.dump(out, outfile)
        outfile.close()

    print("\nMy work is done!\n")


if __name__ == '__main__':

    main()
