#!/usr/bin/env python3


import pyzed.sl as sl
import os
import shutil
import json
import sys
import argparse
import warnings
from pathlib import Path
import coloredlogs, logging
from tqdm import tqdm

def main(filepath, start, end, dir_path):

    filepath = os.path.abspath(filepath)
    dir_path = os.path.abspath(dir_path)

    logging.debug(f"filepath: {filepath}")
    logging.debug(f"start: {start}% end: {end}%")

    input_type = sl.InputType()
    input_type.set_from_svo_file(filepath)

    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.coordinate_units = sl.UNIT.METER   

    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime_parameters = sl.RuntimeParameters()

    image = sl.Mat()
    image_r = sl.Mat()
    
    logging.debug(f"Trying to delete the {dir_path} directory")
    try:
        shutil.rmtree(dir_path)
        logging.debug("Cleared the {dir_path} directory!")
    except OSError as e:
        logging.error("Error: %s : %s" % (dir_path, e.strerror))

    for frame_idx in tqdm(range(start, end)):
        if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            zed.set_svo_position(frame_idx)
            # create the outputm directory
            output_dir = os.path.join(dir_path, "frame_{}/images".format(i) )    
            os.makedirs( output_dir, exist_ok=True )
            # reading and writing the images to the output directory
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_image(image_r, sl.VIEW.RIGHT)
            image.write( os.path.join(output_dir, 'left_image.jpg') )
            image_r.write( os.path.join(output_dir, 'right_image.jpg') )
    zed.close()

if __name__ == "__main__":

    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--svo_path', type=str, required = True, help='target svo file path')
    parser.add_argument('--start_frame', type=int, required = True, help='number of frames to be extracted')
    parser.add_argument('--end_frame', type=int, required = True, help='number of frames to be extracted')
    parser.add_argument('--output_dir', type=str, required = True, help='output directory path')
    args = parser.parse_args()  
    
    logging.debug(f"svo_path: {args.svo_path}")
    logging.debug(f"start_frame: {args.start_frame}")
    logging.debug(f"end_frame: {args.end_frame}")
    logging.debug(f"output_dir: {args.output_dir}")

    main(Path(args.svo_path), args.start_percentage, args.end_percentage , Path(args.output_dir))
