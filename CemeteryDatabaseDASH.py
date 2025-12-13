
# CemeteryDatabaseDASH.py
import os
from dotenv import load_dotenv
load_dotenv()  # loads .env in local dev

from dash import Dash, dcc, html, Input, Output, State, dash_table
import pandas as pd
from CRUD_Module import CRUD
from datetime import datetime

def _iso_date(s):
    if not s: return None
    try: return datetime.strptime(s.strip(), "%Y-%m-%d").date().isoformat()
    except Exception: return None

crud = CRUD()

app = Dash(__name__)
server = app.server   # <-- expose Flask server for gunicorn

app.layout = html.Div([
    html.H2("Cemetery Explorer"),
    html.Div([
        dcc.Input(id="search_last", placeholder="Last name", type="text"),
        html.Button("Search", id="btn_search")
    ], style={"display":"flex","gap":"8px"}),


    html.Hr(),
    dash_table.DataTable(id="tbl", page_size=10, sort_action="native"),

    html.H3("Add record"),
    html.Div([
        dcc.Input(id="cemetery", placeholder="Cemetery", type="text", style={"width": "190px"}),
        dcc.Input(id="section", placeholder="Section", type="text", style={"width": "100px"}),
        dcc.Input(id="row", placeholder="Row", type="number", style={"width": "90px"}),
        dcc.Input(id="lot", placeholder="Lot", type="number", style={"width": "90px"}),
    ], style={"display": "flex", "gap": "8px", "marginBottom": "8px"}),

    html.Div([
        dcc.Input(id="first", placeholder="First", type="text", style={"width": "160px"}),
        dcc.Input(id="middle", placeholder="Middle", type="text", style={"width": "120px"}),
        dcc.Input(id="last", placeholder="Last", type="text", style={"width": "160px"}),
    ], style={"display": "flex", "gap": "8px", "marginBottom": "8px"}),

    html.Div([
        dcc.Input(id="birth_date", placeholder="Birth YYYY-MM-DD", type="text", style={"width": "170px"}),
        dcc.Input(id="death_date", placeholder="Death YYYY-MM-DD", type="text", style={"width": "170px"}),
        dcc.Input(id="burial_date", placeholder="Burial YYYY-MM-DD", type="text", style={"width": "170px"}),
    ], style={"display": "flex", "gap": "8px", "marginBottom": "8px"}),

    html.Div([
        dcc.Dropdown(
            id="burial_type",
            placeholder="Burial type",
            options=[{"label": x, "value": x} for x in ["Cremation", "Casket", "Mausoleum", "Other"]],
            style={"width": "220px"}
        ),
        dcc.RadioItems(
            id="military_veteran",
            options=[{"label": "Veteran: No", "value": "no"}, {"label": "Veteran: Yes", "value": "yes"}],
            inline=True,
        ),
        dcc.Dropdown(
            id="branch",
            placeholder="Branch (if veteran)",
            options=[{"label": x, "value": x} for x in
                     ["Army", "Navy", "Air Force", "Marines", "Coast Guard", "Space Force"]],
            style={"width": "220px"}
        ),
    ], style={"display": "flex", "gap": "12px", "alignItems": "center", "marginBottom": "8px"}),

    dcc.Textarea(id="notes", placeholder="Notes", style={"width": "100%", "height": "70px"}),
    html.Button("Add", id="btn_add", style={"marginTop": "8px"}),
    html.Div(id="msg", style={"color": "green", "marginTop": "8px"})
    ])

# --- helpers ---
def flatten(doc: dict) -> dict:
    dec = (doc or {}).get("decedent", {}) or {}
    plot = (doc or {}).get("plot", {}) or {}
    return {
        "cemetery": doc.get("cemetery"),
        "section": plot.get("section"),
        "row": plot.get("row"),
        "lot": plot.get("lot"),
        "first": dec.get("first"),
        "last": dec.get("last"),
        "birth_date": doc.get("birth_date"),
        "death_date": doc.get("death_date"),
        "burial_date": doc.get("burial_date"),
        "burial_type": doc.get("burial_type"),
        "notes": doc.get("notes"),
        "military_veteran": doc.get("military_veteran"),
        "branch": doc.get("branch"),
    }

# --- search ---
@app.callback(
    Output("tbl", "data"),
    Output("tbl", "columns"),
    Input("btn_search", "n_clicks"),
    State("search_last", "value"),

    prevent_initial_call=True
)
def do_search(_, last):
    q = {}
    if last:
        q["decedent.last"] = {"$regex": f"^{last}", "$options": "i"}


    docs = crud.read(q, projection={"_id": 0})

    if not docs:
        return [], []

    import pandas as pd
    df = pd.json_normalize(docs)

    # merge nested/top-level plot fields
    for field in ("section", "row", "lot"):
        nested = f"plot.{field}"
        if nested in df.columns and field in df.columns:
            df[field] = df[nested].fillna(df[field])
        elif nested in df.columns:
            df[field] = df[nested]

    df = df.rename(columns={
        "decedent.first": "first",
        "decedent.middle": "middle",
        "decedent.last": "last",
    })

    cols = [c for c in [
        "cemetery", "section", "row", "lot",
        "first", "middle", "last",
        "birth_date", "death_date", "burial_date",
        "burial_type", "notes", "military_veteran", "branch"
    ] if c in df.columns]

    return df[cols].to_dict("records"), [{"name": c, "id": c} for c in cols]

# --- add ---
@app.callback(
    Output("msg", "children"),
    Input("btn_add", "n_clicks"),
    State("cemetery","value"),
    State("section","value"),
    State("row","value"),
    State("lot","value"),
    State("first","value"),
    State("middle","value"),
    State("last","value"),
    State("birth_date","value"),
    State("death_date","value"),
    State("burial_date","value"),
    State("burial_type","value"),
    State("military_veteran","value"),
    State("branch","value"),
    State("notes","value"),
    prevent_initial_call=True
)
def do_add(_, cemetery, section, row, lot, first, middle, last,
           birth_date, death_date, burial_date, burial_type,
           military_veteran, branch, notes):

    # required fields
    if not (first and last and section):
        return "Missing required fields: first, last, section."

    def to_int(v):
        try:
            return int(v) if v not in ("", None) else None
        except Exception:
            return None

    doc = {
        "cemetery": (cemetery or "").strip() or None,
        "decedent": {
            "first":  (first  or "").strip(),
            "middle": (middle or "").strip() or None,
            "last":   (last   or "").strip(),
        },
        "plot": {
            "section": (section or "").strip(),
            "row": to_int(row),
            "lot": to_int(lot),
        },
        "birth_date":  _iso_date(birth_date),
        "death_date":  _iso_date(death_date),
        "burial_date": _iso_date(burial_date),
        "burial_type": burial_type or None,
        "military_veteran": (military_veteran or "no"),
        "branch": branch or None,
        "notes": (notes or "").strip() or None,
    }

    # prune empties to keep docs clean
    doc = {k:v for k,v in doc.items() if v not in (None, "", {})}
    if "decedent" in doc:
        doc["decedent"] = {k:v for k,v in doc["decedent"].items() if v not in (None, "", {})}
    if "plot" in doc:
        doc["plot"] = {k:v for k,v in doc["plot"].items() if v not in (None, "", {})}

    try:
        _id = crud.create(doc)
        return f"Inserted record with _id={_id}"
    except Exception as e:
        return f"Insert failed: {e}"

if __name__ == "__main__":
    # Local dev server (hot reload)
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8050")), debug=True)
