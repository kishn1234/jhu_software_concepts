from flask import Flask, render_template, redirect, url_for, request
from query_data import get_analysis_results
import subprocess


app = Flask(__name__)

data_refresh_running = False


@app.route("/")
def index():
    results = get_analysis_results()
    message = request.args.get("message")
    return render_template("index.html", results=results, message=message)


@app.route("/pull-data", methods=["POST"])
def pull_data():
    global data_refresh_running

    if data_refresh_running:
        return redirect(url_for("index", message="A data pull is already running. Please wait before starting another request."))

    data_refresh_running = True

    try:
        subprocess.run(["python3", "load_data.py"])

        message = "Pull Data completed. New Grad Cafe data was scraped and added to PostgreSQL without deleting existing usable records."
    except:
        message = "Pull Data could not complete. Please check the terminal for error details."

    data_refresh_running = False

    return redirect(url_for("index", message=message))


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    global data_refresh_running

    if data_refresh_running:
        return redirect(url_for("index", message="Data is still being pulled. Analysis will update after the pull finishes."))

    return redirect(url_for("index", message="Update Analysis completed. The page now shows the latest PostgreSQL query results."))


if __name__ == "__main__":
    app.run(debug=True, port=5001)