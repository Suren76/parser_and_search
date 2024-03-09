#!/home/suren/.cache/pypoetry/virtualenvs/slack-bot-e3O-PR5L-py3.11/bin/python3.11

import argparse

# from config import PATH_TO_FILES_DIR, PATH_TO_OUTPUT_DIRECTORY
import os
from main import get_text_files_from_path

# path = PATH_TO_FILES_DIR
# path_to_output_directory = PATH_TO_OUTPUT_DIRECTORY

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--directory", help="get path to directory and set as files folder")
parser.add_argument("-O", "--output-directory", help="sets the folder where files will be saved")
parser.add_argument("-I", "--image-save", action='store_true')
parser.add_argument("-MA", "--move-archives", action='store_true')


args = parser.parse_args()

# if args.shell:
#     while True:
#         pass

print(args)

if args.directory:
    path = args.directory
if args.output_directory:
    path_to_output_directory = args.output_directory


get_text_files_from_path(path, path_to_output_directory, args.image_save, args.move_archives)
