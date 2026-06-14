Kishore Narayanan
JHED ID: knaraya8@jh.edu

Module 3 Assignment: Database Queries
Due 6/7/2026

Overview:
This project builds off work completed in Module 2, loading Grad Cafe applicant data into a 
PostgreSQL database. It then performs SQL analysis and displays results through a Flask web 
application.

Setup:
Install PostgreSQL
Create a database named "gradcafe"
Install required Python packages: pip install -r requirements.txt

Loading Data into PostgreSQL: python3 load_data.py

This script creates the applicants table, loads applicant records from Module 2 applicant_data.json, 
preserves existing records, and skips duplicate records.


Completing Analysis Questions: python3 query_data.py

This script answers all 11 total questions.


Starting/Running Flask Application:
run: python3 app.py
open in browser: http://127.0.0.1:5001

Buttons:
    Pull data - loads applicant records from Module 2 applicant_data.json into PostgreSQL.
        - existing records preserved
        - duplicates skipped
        - status messages displayed
    Update Analysis - refreshes the page, displaying most current analysis results from PostgreSQL.
        - application prevents conflicting requests and informs the user