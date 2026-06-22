"""Database query helpers for the Grad Cafe analytics dashboard."""

import psycopg


def get_connection():
    """Create a PostgreSQL connection for analytics queries."""
    return psycopg.connect(
        dbname="gradcafe",
        user="kishore.narayanan"
    )


def get_queries():
    """Return the dashboard questions and SQL statements."""
    return [
        ("Q1", "How many entries are Fall 2026 entries?", """
            SELECT COUNT(*)
            FROM applicants
            WHERE term = 'Fall 2026';
        """),

        ("Q2", "What percentage of entries are from international students?", """
            SELECT ROUND(
                100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
                / COUNT(*), 2
            )
            FROM applicants;
        """),

        ("Q3", "What is the average GPA, GRE, GRE V, and GRE AW?", """
            SELECT
                ROUND(AVG(gpa)::numeric, 2),
                ROUND(AVG(gre)::numeric, 2),
                ROUND(AVG(gre_v)::numeric, 2),
                ROUND(AVG(gre_aw)::numeric, 2)
            FROM applicants;
        """),

        ("Q4", "What is the average GPA of American students in Fall 2026?", """
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term = 'Fall 2026'
            AND us_or_international = 'American';
        """),

        ("Q5", "What percent of Fall 2026 entries are acceptances?", """
            SELECT ROUND(
                100.0 * SUM(CASE WHEN status LIKE 'Accepted%' THEN 1 ELSE 0 END)
                / COUNT(*), 2
            )
            FROM applicants
            WHERE term = 'Fall 2026';
        """),

        ("Q6", "What is the average GPA of Fall 2026 accepted applicants?", """
            SELECT ROUND(AVG(gpa)::numeric, 2)
            FROM applicants
            WHERE term = 'Fall 2026'
            AND status LIKE 'Accepted%';
        """),

        (
            "Q7",
            (
                "How many entries are from applicants who applied to JHU "
                "for a masters degree in Computer Science?"
            ),
            """
            SELECT COUNT(*)
            FROM applicants
            WHERE university ILIKE '%Johns Hopkins%'
            AND program ILIKE '%Computer Science%'
            AND degree = 'Masters';
            """
        ),

        (
            "Q8",
            (
                "How many 2026 PhD Computer Science acceptances are from "
                "Georgetown, MIT, Stanford, or Carnegie Mellon?"
            ),
            """
            SELECT COUNT(*)
            FROM applicants
            WHERE EXTRACT(YEAR FROM date_added) = 2026
            AND status LIKE 'Accepted%'
            AND degree = 'PhD'
            AND program ILIKE '%Computer Science%'
            AND (
                university ILIKE '%Georgetown%'
                OR university ILIKE '%MIT%'
                OR university ILIKE '%Stanford%'
                OR university ILIKE '%Carnegie Mellon%'
            );
            """
        ),

        ("Q9", "Does the answer for Q8 change when using LLM generated fields?", """
            SELECT
                standard_count,
                llm_count,
                CASE
                    WHEN standard_count = llm_count THEN 'No, the answer does not change.'
                    ELSE 'Yes, the answer changes.'
                END AS comparison
            FROM (
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM applicants
                        WHERE EXTRACT(YEAR FROM date_added) = 2026
                        AND status LIKE 'Accepted%'
                        AND degree = 'PhD'
                        AND program ILIKE '%Computer Science%'
                        AND (
                            university ILIKE '%Georgetown%'
                            OR university ILIKE '%MIT%'
                            OR university ILIKE '%Stanford%'
                            OR university ILIKE '%Carnegie Mellon%'
                        )
                    ) AS standard_count,
                    (
                        SELECT COUNT(*)
                        FROM applicants
                        WHERE EXTRACT(YEAR FROM date_added) = 2026
                        AND status LIKE 'Accepted%'
                        AND degree = 'PhD'
                        AND llm_generated_program ILIKE '%Computer Science%'
                        AND (
                            llm_generated_university ILIKE '%Georgetown%'
                            OR llm_generated_university ILIKE '%MIT%'
                            OR llm_generated_university ILIKE '%Stanford%'
                            OR llm_generated_university ILIKE '%Carnegie Mellon%'
                        )
                    ) AS llm_count
            ) AS counts;
        """),

        ("Q10", "Additional: What is the acceptance rate by degree type?", """
            SELECT
                degree,
                COUNT(*) AS total_entries,
                SUM(CASE WHEN status LIKE 'Accepted%' THEN 1 ELSE 0 END) AS acceptances,
                ROUND(
                    100.0 * SUM(CASE WHEN status LIKE 'Accepted%' THEN 1 ELSE 0 END)
                    / COUNT(*), 2
                ) AS acceptance_rate
            FROM applicants
            WHERE degree IN ('Masters', 'PhD')
            GROUP BY degree
            ORDER BY degree;
        """),

        ("Q11", "Additional: What are the top 5 universities by submitted entries?", """
            SELECT university, COUNT(*) AS total_entries
            FROM applicants
            WHERE university IS NOT NULL
            GROUP BY university
            ORDER BY total_entries DESC
            LIMIT 5;
        """)
    ]


def get_analysis_results():
    """Run all dashboard queries and return formatted result dictionaries."""
    results = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for number, question, sql in get_queries():
                cur.execute(sql)
                rows = cur.fetchall()

                results.append({
                    "number": number,
                    "question": question,
                    "sql": sql,
                    "rows": rows
                })

    return results


def main():
    """Print all dashboard query results to the terminal."""
    results = get_analysis_results()

    for result in results:
        print()
        print(result["number"], result["question"])

        for row in result["rows"]:
            print(row)


if __name__ == "__main__":  # pragma: no cover
    main()
