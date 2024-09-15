import json
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    path_to_project_root = Path("/home/suren/Projects/upwork/maroz/parser_and_search/")
    return render_template("index.html", list_of_results=[
        json.loads(open(path_to_project_root / "resources/tests_result/08_29_2024/to_generate_statistic_2024-08-27 134339.json").read())
    ][0], filterrr=eval)


app.run(
    debug=True
)