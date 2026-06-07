import psycopg


def get_connection():
    return psycopg.connect(
        dbname="gradcafe",
        user="kishore.narayanan"
    )


def run_query(label, sql):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchall()

    print(f"\n{label}")
    for row in result:
        print(row)


def main():
    run_query("Q1 Fall 2026 entries", """
        SELECT COUNT(*)
        FROM applicants
        WHERE term = 'Fall 2026';
    """)

    run_query("Q2 Percent international students", """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN us_or_international = 'International' THEN 1 ELSE 0 END)
            / COUNT(*), 2
        )
        FROM applicants;
    """)

    run_query("Q3 Average GPA, GRE, GRE V, GRE AW", """
        SELECT
            ROUND(AVG(NULLIF(gpa, '')::numeric), 2),
            ROUND(AVG(NULLIF(gre, '')::numeric), 2),
            ROUND(AVG(NULLIF(gre_v, '')::numeric), 2),
            ROUND(AVG(NULLIF(gre_aw, '')::numeric), 2)
        FROM applicants;
    """)

    run_query("Q4 Average GPA of American students in Fall 2026", """
        SELECT ROUND(AVG(NULLIF(gpa, '')::numeric), 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND us_or_international = 'American';
    """)

    run_query("Q5 Percent of Fall 2026 entries that are acceptances", """
        SELECT ROUND(
            100.0 * SUM(CASE WHEN status LIKE 'Accepted%' THEN 1 ELSE 0 END)
            / COUNT(*), 2
        )
        FROM applicants
        WHERE term = 'Fall 2026';
    """)

    run_query("Q6 Average GPA of Fall 2026 accepted applicants", """
        SELECT ROUND(AVG(NULLIF(gpa, '')::numeric), 2)
        FROM applicants
        WHERE term = 'Fall 2026'
        AND status LIKE 'Accepted%';
    """)

    run_query("Q7 JHU Masters Computer Science entries", """
        SELECT COUNT(*)
        FROM applicants
        WHERE university ILIKE '%Johns Hopkins%'
        AND program ILIKE '%Computer Science%'
        AND degree = 'Masters';
    """)

    run_query("Q8 2026 PhD Computer Science acceptances for selected universities", """
        SELECT COUNT(*)
        FROM applicants
        WHERE date_added LIKE '%2026%'
        AND status LIKE 'Accepted%'
        AND degree = 'PhD'
        AND program ILIKE '%Computer Science%'
        AND (
            university ILIKE '%Georgetown%'
            OR university ILIKE '%MIT%'
            OR university ILIKE '%Stanford%'
            OR university ILIKE '%Carnegie Mellon%'
        );
    """)

    run_query("Q9 Same as Q8 using LLM generated fields", """
        SELECT COUNT(*)
        FROM applicants
        WHERE date_added LIKE '%2026%'
        AND status LIKE 'Accepted%'
        AND degree = 'PhD'
        AND llm_generated_program ILIKE '%Computer Science%'
        AND (
            llm_generated_university ILIKE '%Georgetown%'
            OR llm_generated_university ILIKE '%MIT%'
            OR llm_generated_university ILIKE '%Stanford%'
            OR llm_generated_university ILIKE '%Carnegie Mellon%'
        );
    """)

    run_query("Q10 Additional: Acceptance rate by degree type", """
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
    """)

    run_query("Q11 Additional: Top 5 universities by submitted entries", """
        SELECT university, COUNT(*) AS total_entries
        FROM applicants
        WHERE university IS NOT NULL
        GROUP BY university
        ORDER BY total_entries DESC
        LIMIT 5;
    """)


if __name__ == "__main__":
    main()