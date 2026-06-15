Kishore Narayanan
JHED ID: knaraya8@jh.edu

# Module 4: Pytest and Sphinx

This project builds on the Grad Cafe analytics application from Module 3. It adds automated Pytest coverage, Flask route testing, database write testing, integration testing, GitHub Actions continuous integration, and Sphinx documentation.

## Project Structure

```text
module_4/
├── src/
│   ├── flask_app.py
│   ├── load_data.py
│   ├── query_data.py
│   ├── templates/
│   └── static/
├── tests/
├── docs/
├── pytest.ini
├── requirements.txt
├── coverage_summary.txt
└── README.md
```

## Project Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## PostgreSQL Configuration

Create a PostgreSQL database named:

```text
gradcafe
```

Set the `DATABASE_URL` environment variable to point to your PostgreSQL database.

## Running the Flask Application

From the `module_4` directory run:

```bash
python src/flask_app.py
```

Open the application in a browser:

```text
http://127.0.0.1:5001/analysis
```

## Running Tests

Run the full Pytest suite:

```bash
python -m pytest
```

The project is configured to require 100% test coverage.

## Viewing Documentation

Sphinx documentation is located under:

```text
docs/
```

To generate the documentation:

```bash
cd docs
make html
```

Generated HTML files are available under:

```text
docs/build/html/
```

Open:

```text
docs/build/html/index.html
```

in a browser to view the documentation.

## Read the Docs

Project documentation:

https://kn-module4.readthedocs.io/en/latest/