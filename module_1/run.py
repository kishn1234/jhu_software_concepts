# import Flask framework and render_template function
from flask import Flask, render_template

# create Flask app
app = Flask(__name__)

# define routes for home, projects, and contact pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
