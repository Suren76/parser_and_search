#!/home/suren/.cache/pypoetry/virtualenvs/slack-bot-e3O-PR5L-py3.11/bin/python3.11

import argparse

# from config import PATH_TO_FILES_DIR, PATH_TO_OUTPUT_DIRECTORY
import os
from pathlib import Path
from typing import Literal, LiteralString

from main import get_text_files_from_path
from extensions.get_statistic import get_statistic
from extensions.add_id_to_image_name import add_id_to_image_name

# path = PATH_TO_FILES_DIR
# path_to_output_directory = PATH_TO_OUTPUT_DIRECTORY

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--directory", help="get path to directory and set as files folder")
parser.add_argument("-O", "--output-directory", help="sets the folder where files will be saved")
parser.add_argument("-EFF", "--excluded-files-folder", help="sets the folder where files will be saved")
parser.add_argument("-lm", "--result-limits", help="sets the limit of founded models to use in 'from_text filter by images' phase, default: 300")
parser.add_argument("-data", "--login-data", help="get path to login data file and set folder as a env variable store path")
parser.add_argument("-driver", "--path-to-chromedriver", help=f"sets the path for chromedriver, default:http://localhost:4444/wd/hub")
parser.add_argument("-I", "--image-save", action='store_true')
parser.add_argument("-t", "--timeout", help="get timeout for image compare requests")
parser.add_argument("-MA", "--move-archives", action='store_true')
parser.add_argument("-OIS", "--old-image-search", action='store_true')
parser.add_argument("--DEBUG", action='store_true')


subparser = parser.add_subparsers()


extra_tools_parser = subparser.add_parser("extra_tools", help="command to run extra tools which is not included in main app functionality."
                                         "you can pass 'get_statistic' and 'add_id_to_image_name' values to run.",
                                          formatter_class=argparse.RawTextHelpFormatter
                                          )

extra_tools_parser.add_argument("extra_tool_to_run", type=str, choices=["get_statistic", "add_id_to_image_name"],
                                help=
                                    "get_statistic: you give the path to the directory \n"
                                    
                                    "add_id_to_image_name: you give the path to the directory and you should give path to login data file before app run \n"
                                )

extra_tools_parser.add_argument("-d", "--extra-tools-directory", help="get path to directory and set as files folder where to work script")


args = parser.parse_args()

# if args.shell:
#     while True:
#         pass

print(args)

if "extra_tool_to_run" in args:
    tool_name = args.extra_tool_to_run
    extra_tool_directory = args.extra_tools_directory

    if tool_name == "get_statistic":
        get_statistic(Path(extra_tool_directory))
    if tool_name == "add_id_to_image_name":
        add_id_to_image_name(Path(extra_tool_directory), args.login_data)
    # print(args.extra_tool_to_run)
    exit(0)

result_limits_for_image_compare = 300
_timeout = None
login_data = None
# path_to_chromedriver = "http://172.17.0.2:4444/wd/hub"
path_to_chromedriver = None
folder_to_exclude_files = None

if args.directory:
    path = args.directory
if args.output_directory:
    path_to_output_directory = args.output_directory
if args.excluded_files_folder:
    folder_to_exclude_files = args.excluded_files_folder
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
    _old_image_search=args.old_image_search,
    _folder_to_exclude_files=folder_to_exclude_files
)
