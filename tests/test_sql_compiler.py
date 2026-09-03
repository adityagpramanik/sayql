from app.query_former.sql_compiler import compile_query


def test_compile_query_accepts_select_statement():
    sql = "SELECT * FROM facility WHERE location_type = 'rural'"
    assert compile_query(sql) == sql


def test_compile_query_rejects_non_select_statement():
    try:
        compile_query("DELETE FROM facility")
        assert False, "Expected ValueError for unsafe SQL"
    except ValueError:
        pass
