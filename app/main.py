from html import escape

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from app.api.routes.query import router as query_router
from app.db.postgres import execute_query
from app.query_former.service import generate_sql

app = FastAPI(title="NL Data Analyst", version="0.1.0")
app.include_router(query_router)


def render_query_page(
        question: str = "",
        results: list[dict] | None = None,
        error: str = "",
) -> str:
        result_markup = ""
        if results is not None:
                if results:
                        headers = list(results[0].keys())
                        header_markup = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
                        rows_markup = "".join(
                                "<tr>"
                                + "".join(f"<td>{escape(str(row.get(header, '')))}</td>" for header in headers)
                                + "</tr>"
                                for row in results
                        )
                        result_markup = f"<table><thead><tr>{header_markup}</tr></thead><tbody>{rows_markup}</tbody></table>"
                else:
                        result_markup = "<p class='muted'>No rows returned.</p>"

        error_markup = f"<p class='error'>{escape(error)}</p>" if error else ""
        return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SayQL</title>
    <style>
        :root {{ color-scheme: light; font-family: ui-sans-serif, system-ui, sans-serif; color: #17202a; background: #f4f1ea; }}
        body {{ max-width: 960px; margin: 0 auto; padding: 5rem 1.25rem; }}
        h1 {{ margin-bottom: .35rem; font-size: clamp(2.2rem, 6vw, 4.5rem); letter-spacing: -.04em; }}
        .intro {{ color: #59636e; margin-top: 0; }}
        form {{ display: flex; gap: .75rem; margin: 2rem 0; }}
        input {{ flex: 1; min-width: 0; border: 1px solid #c8c1b5; border-radius: 6px; padding: 1rem; font: inherit; background: #fffdf8; }}
        button {{ border: 0; border-radius: 6px; padding: 0 1.25rem; font: inherit; font-weight: 700; color: #fffdf8; background: #b84a2d; cursor: pointer; }}
        button:hover {{ background: #963b24; }}
        section {{ margin-top: 2rem; }}
        pre, table {{ width: 100%; overflow-x: auto; background: #fffdf8; border: 1px solid #ded7cb; border-radius: 6px; }}
        pre {{ box-sizing: border-box; padding: 1rem; white-space: pre-wrap; }}
        table {{ border-collapse: collapse; text-align: left; }}
        th, td {{ padding: .7rem .8rem; border-bottom: 1px solid #e8e1d6; }}
        th {{ background: #ece6da; }}
        .error {{ color: #a52d2d; font-weight: 700; }}
        .muted {{ color: #59636e; }}
        @media (max-width: 600px) {{ form {{ flex-direction: column; }} button {{ padding: .9rem 1.25rem; }} }}
    </style>
</head>
<body>
    <main>
        <h1>Ask SayQL</h1>
        <p class="intro">
            Describe the data you need in plain language.
            <br>
            Sample data available: Tables => Facility (healthcare facility), State, District, Sub District
            <br>
            Facility -> name, id, type etc
            <br>
            State, District, Sub District -> id, name 
        </p>
        <form method="post" action="/">
            <input name="question" value="{escape(question)}" minlength="3" required placeholder="e.g. find the 10 most recently added facilities">
            <button type="submit">Run query</button>
        </form>
        {error_markup}
        {result_markup}
    </main>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
        return HTMLResponse(render_query_page())


@app.post("/", response_class=HTMLResponse)
def submit_query(question: str = Form(...)) -> HTMLResponse:
        try:
                sql = generate_sql(question)
                rows = execute_query(sql)
                return HTMLResponse(render_query_page(question=question, results=rows))
        except:
                return HTMLResponse(render_query_page(question=question, error="Query execution failed"), status_code=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}