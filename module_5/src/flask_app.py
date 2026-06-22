from flask import Flask, render_template, redirect, url_for, request
from src.query_data import get_analysis_results
import subprocess


data_refresh_running = False


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is not None:
        app.config.update(test_config)

    @app.route("/")
    @app.route("/analysis")
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
            subprocess.run(["python3", "load_data.py"], check=True)
            message = "Pull Data completed. Applicant records from the Module 2 applicant_data.json file were loaded into PostgreSQL. Existing records were preserved and duplicate records were skipped."
        except subprocess.CalledProcessError:
            message = "Pull Data could not complete. Please check the terminal for error details."
        finally:
            data_refresh_running = False

        return redirect(url_for("index", message=message))

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        global data_refresh_running

        if data_refresh_running:
            return redirect(url_for("index", message="Data is still being pulled. Please wait before updating the analysis."))

        return redirect(url_for("index", message="Update Analysis completed. The page now shows the latest PostgreSQL query results."))

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5001)