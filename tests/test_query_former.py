from app.query_former.service import generate_sql


def test_generate_sql_returns_select_statement():
    sql = generate_sql("How many rural facilities are there?")
    assert sql.lower().startswith("select")
