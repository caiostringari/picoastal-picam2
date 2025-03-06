# SCRIPT   : make_ChArUco_board.py
# POURPOSE : Create a board for calibration using the ChArUco model.
# AUTHOR   : Caio Eadi Stringari

# Exampple from here:
# https://github.com/chriskiehl/Gooey/issues/296

import os
import sys

import argparse

import cv2

try:
    import gooey
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


@gui_decorator
def main():
    """Call the main program."""

    # argument parser
    parser = argparse.ArgumentParser()

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

    parser.add_argument("--border_bits",
                        action="store",
                        dest="border_bits",
                        default=0,
                        required=False,
                        help=" Number of bits in marker borders.")

    parser.add_argument("--show",
                        action="store_true",
                        dest="show",
                        help="Show results on screen.")

    parser.add_argument("--output", "-o",
                        action="store",
                        dest="output",
                        default="ChArUco_6X6_250.png",
                        required=True,
                        help="Output file name.")

    args = parser.parse_args()

    # parse parameters
    squares_x = int(args.squares_x)  # number of squares in X direction
    squares_y = int(args.squares_y)  # number of squares in Y direction
    square_length = int(args.square_length)  # square side length (in pixels)
    marker_length = int(args.marker_length)  # marker side length (in pixels)
    dictionary_id = args.dictionary_id  # dictionary id

    margins = square_length - marker_length  # margins size (in pixels)
    # border_bits = int(args.border_bits)  # number of bits in marker borders

    # compute image size
    image_width = squares_x * square_length + 2 * margins
    image_height = squares_y * square_length + 2 * margins
    image_size = (image_width, image_height)  # needs to be a tuple

    # create board
    dict_id = getattr(cv2.aruco, "DICT_{}".format(dictionary_id))
    dictionary = cv2.aruco.getPredefinedDictionary(dict_id)

    # create the board instance
    board = cv2.aruco.CharucoBoard_create(
        squares_x, squares_y, square_length, marker_length, dictionary)

    # create an image
    board_img = board.draw(image_size)

    # show if requested
    if args.show:
        cv2.imshow("ChArUco DICT_{}".format(dictionary_id), board_img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()

    # write to file
    cv2.imwrite(args.output, board_img)


if __name__ == '__main__':

    main()
