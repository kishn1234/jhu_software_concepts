Kishore Narayanan
JHED ID: knaraya8@jh.edu

# Module 5: Software Assurance and Secure SQL (SQLi Defense)

## Project Overview

This project extends the Grad Cafe Analytics application developed in previous modules by adding software assurance, dependency analysis, secure database access, vulnerability scanning, packaging, and continuous integration.

The primary focus of Module 5 is improving application security and maintainability through:

* SQL injection defenses using parameterized queries and psycopg SQL composition
* Query limit enforcement
* Environment-based configuration
* Dependency analysis and visualization
* Vulnerability scanning with Snyk
* Automated CI validation using GitHub Actions
* Packaging support using setuptools

## Project Structure

```text
module_5/
├── src/
│   ├── flask_app.py
│   ├── load_data.py
│   ├── query_data.py
│   ├── templates/
│   └── static/
├── tests/
├── docs/
├── dependency.svg
├── snyk-analysis.png
├── setup.py
├── requirements.txt
├── pytest.ini
├── coverage_summary.txt
├── .env.example
├── README.md
└── module_5_report.pdf
```

## Environment Setup

### Using pip

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

### Using uv

Install dependencies using uv:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Environment Variables

Create a local `.env` file using `.env.example` as a template.

Example:

```text
DATABASE_URL=postgresql://username:password@localhost/gradcafe
```

Do not commit secrets or production credentials.

## PostgreSQL Configuration

Create a PostgreSQL database named:

```text
gradcafe
```

Set the `DATABASE_URL` environment variable before running the application.

## Running the Application

From the module_5 directory:

```bash
python src/flask_app.py
```

Open:

```text
http://127.0.0.1:5001/analysis
```

## Running Tests

Execute the full test suite:

```bash
python -m pytest
```

The project requires:

* 100% test coverage
* Passing integration tests
* Passing database tests

## Running Pylint

Run static analysis:

```bash
pylint src --fail-under=10
```

The project is configured to achieve a perfect pylint score of 10.00/10.

## Dependency Analysis

Generate the dependency graph:

```bash
pydeps src --noshow -T svg -o dependency.svg
```

The generated dependency graph is stored in:

```text
dependency.svg
```

## Security Improvements

The application implements several software assurance controls:

* Parameterized SQL queries
* Safe SQL composition using psycopg.sql
* Query limit validation and clamping
* Environment-based database configuration
* Separation of configuration from source code
* Least-privilege database access principles

## Vulnerability Scanning

Run Snyk dependency scanning:

```bash
snyk test
```

Scan results are documented in:

```text
snyk-analysis.png
```

## Continuous Integration

GitHub Actions automatically performs:

* Dependency installation
* Pylint validation
* Dependency graph generation
* Snyk dependency scanning
* Pytest execution

Workflow file:

```text
.github/workflows/ci.yml
```

## Documentation

Sphinx documentation is available under:

```text
docs/
```

To build documentation:

```bash
cd docs
make html
```

Generated documentation:

```text
docs/build/html/index.html
```
