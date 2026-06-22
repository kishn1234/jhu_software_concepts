"""Flask routes for the Grad Cafe analytics web application."""

import subprocess

from flask import Flask, redirect, render_template, request, url_for

from src.query_data import get_analysis_results


DATA_REFRESH_STATE = {"running": False}


def create_app(test_config=None):
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)

    if test_config is not None:
        flask_app.config.update(test_config)

    @flask_app.route("/")
    @flask_app.route("/analysis")
    def index():
        """Render the analysis dashboard."""
        results = get_analysis_results()
        message = request.args.get("message")
        return render_template(
            "index.html",
            results=results,
            message=message
        )

    @flask_app.route("/pull-data", methods=["POST"])
    def pull_data():
        """Run the data loading process and return to the analysis page."""
        if DATA_REFRESH_STATE["running"]:
            message = (
                "A data pull is already running. "
                "Please wait before starting another request."
            )
            return redirect(url_for("index", message=message))

        DATA_REFRESH_STATE["running"] = True

        try:
            subprocess.run(["python3", "load_data.py"], check=True)
            message = (
                "Pull Data completed. Applicant records from the Module 2 "
                "applicant_data.json file were loaded into PostgreSQL. "
                "Existing records were preserved and duplicate records "
                "were skipped."
            )
        except subprocess.CalledProcessError:
            message = (
                "Pull Data could not complete. "
                "Please check the terminal for error details."
            )
        finally:
            DATA_REFRESH_STATE["running"] = False

        return redirect(url_for("index", message=message))

    @flask_app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        """Refresh the analysis page after the database has been updated."""
        if DATA_REFRESH_STATE["running"]:
            message = (
                "Data is still being pulled. "
                "Please wait before updating the analysis."
            )
            return redirect(url_for("index", message=message))

        message = (
            "Update Analysis completed. "
            "The page now shows the latest PostgreSQL query results."
        )

        return redirect(url_for("index", message=message))

    return flask_app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5001)
