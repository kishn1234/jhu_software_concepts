"""Flask routes for the Grad Cafe analytics web application."""

from flask import Flask, redirect, render_template, request, url_for

from src.web.app.query_data import get_analysis_results
from src.web.publisher import publish_task


DATA_REFRESH_STATE = {"running": False}


def create_app(test_config=None):
    """Create and configure the Flask application."""
    flask_app = Flask(
        __name__,
        template_folder="../templates",
    static_folder="../static"
)

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
            publish_task("scrape_new_data", payload={})
            message = (
                "Pull Data request was queued successfully. "
                "The worker service will load applicant records into PostgreSQL."
            )
        except RuntimeError:
            message = (
                "Pull Data could not be queued. "
                "Please check RabbitMQ and the worker service."
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

        try:
            publish_task("recompute_analytics", payload={})
            message = (
                "Update Analysis request was queued successfully. "
                "The worker service will recompute analytics in PostgreSQL."
            )
        except RuntimeError:
            message = (
                "Update Analysis could not be queued. "
                "Please check RabbitMQ and the worker service."
            )

        return redirect(url_for("index", message=message))

    return flask_app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5001)
