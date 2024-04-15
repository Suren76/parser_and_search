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
parser.add_argument("-lm", "--result-limits", help="sets the limit of founded models to use in 'from_text filter by images' phase, default: 300")
parser.add_argument("-data", "--login-data", help="get path to login data file and set folder as a env variable store path")
parser.add_argument("-driver", "--path-to-chromedriver", help=f"sets the path for chromedriver, default:http://localhost:4444/wd/hub")
parser.add_argument("-I", "--image-save", action='store_true')
parser.add_argument("-t", "--timeout", help="get timeout for image compare requests")
parser.add_argument("-MA", "--move-archives", action='store_true')
parser.add_argument("-OIS", "--old-image-search", action='store_true')
parser.add_argument("--DEBUG", action='store_true')


args = parser.parse_args()

# if args.shell:
#     while True:
#         pass

print(args)

result_limits_for_image_compare = 300
_timeout = None
login_data = None
path_to_chromedriver = "http://localhost:4444/wd/hub"

if args.directory:
    path = args.directory
if args.output_directory:
    path_to_output_directory = args.output_directory
if args.timeout:
    _timeout = int(args.timeout)
if args.login_data:
    login_data = args.login_data
if args.path_to_chromedriver:
    path_to_chromedriver = args.path_to_chromedriver
if args.result_limits:
    result_limits_for_image_compare = int(args.result_limits)


get_text_files_from_path(
    _path_to_archives=path,
    _path_to_save_directory=path_to_output_directory,
    _to_download_image=args.image_save,
    _to_move_archives=args.move_archives,
    _limit_for_result_to_use_in_image_compare=result_limits_for_image_compare,
    _debug=args.DEBUG,
    _request_timeout=_timeout,
    _path_to_login_datas_file=login_data,
    _path_to_chromedriver=path_to_chromedriver,
    _old_image_search=args.old_image_search
)
