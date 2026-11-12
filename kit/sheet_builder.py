#!/usr/bin/env python3
"""Ideator Google Sheet report builder.

Builds the 15-tab report workbook (.xlsx) from one run's JSON data. Upload the
result to Google Drive converted to a native Google Sheet (see the skill).

Template set:   python3 sheet_builder.py /workspace/Ideator/<problem>/run.json --template /workspace/Ideator/<problem>/template-export.xlsx
  fills a COPY of the exported template; the template file is never written.
Template empty: python3 sheet_builder.py run.json
  builds the same 15-tab layout from scratch.
Report tabs always start at row 1, with or without a template; only the
template's own (non-report) tabs keep their content, untouched.
Output: /workspace/Ideator/<problem>/<name>.xlsx, next to the run JSON (--out-dir to change). Prints JSON with the
path, mode, per-tab row counts and any template/report column mismatches.

run.json holds judgments only; this script computes scores, ranks, auto-picks,
key results, board content rows, natural ID sort keys and the tab guide.
{
 "name": "problem-name-YYYY-MM-DD-HHMM", "title": "...", "problem": "verbatim statement",
 "run_started": "YYYY-MM-DD HH:MM[:SS] <zone>", "run_stopped": "optional, same format; defaults to build time", "cancelled": false,
 "template_ref": "<template file id>" | null,   # from the 'template' run knob
 "knobs": {"ideas":5,"pretotypes":4,"sources":5,"country":"...","language":"...","mode":"auto"},
 "knob_notes": {"country": "default (statement names no market)", ...},      # optional
 "sources": [{"id":"S1","citation":"...","url":"...","summary":"... incl. limitations","short":"Pew 2013"}],
 "challenges": [{"id":"C1","text":"...","evidence":"S1, S2" | "hypothesis, no evidence found",
                 "possible":4,"exciting":4, "picked": true|false (ask mode only), "reason": "..." (optional)}],
 "ideas": [{"id":"C3-I1","text":"...","cheap":5,"simple":5,"ev_level":"strong|some|hypothesis",
            "ev_src":"S3"|null,"u_level":"non-obvious|somewhat|obvious","u_reason":"...",
            "pick_reason": "..." (optional), "weighting": "..." (optional)}],
 "concepts": [{"id":"K1","name":"...","ids":["C2-I1","C2-I4"],"description":"..." (optional),
               "picked": true|false (ask mode only)}],
 "pretotypes": [{"id":"K1-P1","cid":"K1","recommended":true,"hypothesis":"...","test":"...",
                 "n":10,"of":60,"metric":"...","deadline":"YYYY-MM-DD",
                 "selected": true (optional; auto mode selects recommended tests),
                 "start":"YYYY-MM-DD"|null,"checkin":"YYYY-MM-DD"|null,
                 "observed":null,"decision":null,"status": "..." (optional)}],
 "materials": [{"pretotype":"K1-P1","type":"Sandwich board","text":"..."}]
}
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="0B6E4F")
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
CELL_FONT = Font(name="Calibri", size=11, color="000000")
ALT_FILL = PatternFill("solid", fgColor="F3F8F6")
PICK_COLOR = "A8E6A3"  # "green light" for selected rows; swap here to change it everywhere
PICK_FILL = PatternFill("solid", fgColor=PICK_COLOR)
PICK_FONT = Font(name="Calibri", size=11, color="000000", bold=True)
SELECTION_COLS = {"Challenges": "Picked", "Define picks": "Picked", "Ideas": "Top 5", "Concepts": "Picked",
                  "Pretotypes": "Recommended first test", "First tests": "Selected", "Board content": "Highlighted"}
_S = Side(style="thin", color="C5D0CC")
THIN = Border(left=_S, right=_S, top=_S, bottom=_S)
WRAP = Alignment(vertical="top", wrap_text=True)
WRAP_CENTER = Alignment(vertical="top", horizontal="center", wrap_text=True)
NUMERIC = {"int", "score1", "mult", "pct", "date", "formula_score", "formula_base", "formula_avg"}
# Column widths are in Excel character units (openpyxl/xlsx): about 7 px per unit plus 5 px padding
# at Calibri 11. Text columns are capped at about 300 px = (300 - 5) / 7 = 42 units.
TEXT_MAX_WIDTH = 42
TEXT_MIN_WIDTH = 8


def fit_text_widths(ws, types, header_row=1):
    """Text columns: wide enough to show short values on one line, capped at TEXT_MAX_WIDTH;
    longer text shows its first line and wraps the rest. Number columns keep WIDTHS."""
    for c, typ in enumerate(types, 1):
        if typ in NUMERIC:
            continue
        longest = 0
        for r in range(header_row, ws.max_row + 1):
            v = ws.cell(r, c).value
            if v not in (None, "") and not (isinstance(v, str) and v.startswith("=")):
                longest = max(longest, max(len(line) for line in str(v).split("\n")))
        ws.column_dimensions[get_column_letter(c)].width = min(TEXT_MAX_WIDTH, max(TEXT_MIN_WIDTH, longest + 2))
STICKY_COLORS = ["#ffe082", "#ffcc80", "#c5e1a5", "#80deea", "#ce93d8",
                 "#90caf9", "#ef9a9a", "#bcaaa4", "#a5d6a7", "#f48fb1"]

EV_MULT = {"strong": Decimal("1.3"), "some": Decimal("1.15"), "hypothesis": Decimal("1.0")}
U_MULT = {"non-obvious": Decimal("1.2"), "somewhat": Decimal("1.1"), "obvious": Decimal("1.0")}
EV_RANK = {"strong": 3, "some": 2, "hypothesis": 1}
U_RANK = {"non-obvious": 3, "somewhat": 2, "obvious": 1}

WIDTHS = {
    "Tab guide": [22, 28, 24, 12, 70],
    "Run knobs": [16, 18, 52, 40],
    "Problem": [22, 80, 45, 50],
    "Key results": [14, 10, 12, 80, 16, 14, 50, 12],
    "Sources": [12, 50, 55, 80, 36, 12],
    "Sticky notes": [10, 80, 32, 50, 12],
    "Challenges": [10, 10, 70, 12, 12, 10, 12, 32, 40, 12],
    "Define picks": [10, 10, 12, 10, 12, 12, 70, 40, 12],
    "Scoring weights": [28, 50, 55, 40],
    "Ideas": [12, 14, 62, 10, 10, 10, 16, 16, 14, 36, 14, 14, 16, 16, 10, 10, 55, 55, 40, 12],
    "Concepts": [10, 30, 70, 28, 12, 22, 12, 60, 44, 12],
    "Pretotypes": [12, 12, 28, 22, 50, 55, 50, 16, 16, 14, 14, 28, 24, 18, 14, 36, 12],
    "Materials": [14, 12, 28, 70, 50, 12],
    "First tests": [14, 14, 22, 20, 14, 14, 70, 50, 12],
    "Board content": [16, 12, 12, 70, 10, 14, 12, 70, 12],
}


def nkey(i: str) -> int:
    """Natural numeric sort key: C9 < C10, C2-I10 after C2-I9, K1-P2, S5."""
    nums = [int(n) for n in re.findall(r"\d+", i)] + [0, 0]
    return nums[0] * 1000 + nums[1]


def half_up(x: Decimal, places: int) -> float:
    return float(x.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def d(s):
    return date.fromisoformat(s) if s else None


def style_cell(cell, typ, row):
    cell.font, cell.border = CELL_FONT, THIN
    cell.alignment = WRAP_CENTER if typ in NUMERIC else WRAP
    if row % 2 == 0:
        cell.fill = ALT_FILL
    cell.number_format = {"int": "0", "formula_score": "0", "formula_base": "0", "score1": "0.0",
                          "mult": "0.000", "pct": "0.0%", "date": "YYYY-MM-DD", "formula_avg": "0.00"}.get(typ, "General")


def write_sheet(wb, title, headers, types, rows, formulas=None, height=None):  # height: unused, rows size to wrapped text
    ws = wb.create_sheet(title)
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        h = ws.cell(1, c)
        h.font, h.fill, h.border = HEADER_FONT, HEADER_FILL, THIN
        h.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
    formulas = formulas or {}
    for r, row in enumerate(rows, 2):
        for c, (val, typ) in enumerate(zip(row, types), 1):
            cell = ws.cell(r, c, formulas.get((r, c), val))
            style_cell(cell, typ, r)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{max(1 + len(rows), 1)}"
    for n, w in enumerate(WIDTHS.get(title, []), 1):
        ws.column_dimensions[get_column_letter(n)].width = w
    fit_text_widths(ws, types)
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    return ws


def challenge_reason(c, ranked, n_pick):
    first_out = ranked[n_pick] if len(ranked) > n_pick else None
    tied = [x for x in ranked if x is not c and (x["score"], x["exciting"], x["possible"]) == (c["score"], c["exciting"], c["possible"])]
    tie = f" Ties {', '.join(x['id'] for x in tied)} on score, exciting and possible: unresolved tie, order arbitrary (lowest ID first)." if tied else ""
    if c["picked"] == "yes":
        return f"Pick. Rank {c['rank']}, score {c['score']} (possible {c['possible']}, exciting {c['exciting']}).{tie}"
    if first_out is c:
        return f"Not picked. Score {c['score']} (possible {c['possible']}, exciting {c['exciting']}); first challenge left out.{tie}"
    return f"Not picked. Rank {c['rank']}, score {c['score']}, below the cutoff."


def idea_reasons(ranked, top_n):
    for idx, i in enumerate(ranked[:top_n]):
        nxt = ranked[idx + 1] if idx + 1 < len(ranked) else None
        if i.get("pick_reason") or nxt is None:
            continue
        if i["score"] != nxt["score"]:
            f = [x for x in (f"evidence {i['ev_level']} vs {nxt['ev_level']}" if i["ev_level"] != nxt["ev_level"] else "",
                             f"base {i['base']} vs {nxt['base']}" if i["base"] != nxt["base"] else "",
                             f"uniqueness {i['u_level']} vs {nxt['u_level']}" if i["u_level"] != nxt["u_level"] else "") if x]
            i["pick_reason"] = f"{i['id']} ({i['score']}) is above {nxt['id']} ({nxt['score']}) on weighted score" + (f"; deciding factors: {', '.join(f)}." if f else ".")
        else:
            for key, label, rank in (("ev_level", "evidence", EV_RANK), ("u_level", "uniqueness", U_RANK), ("simple", "simple", None), ("cheap", "cheap", None)):
                a, b = i[key], nxt[key]
                if (rank[a] if rank else a) != (rank[b] if rank else b):
                    i["pick_reason"] = f"{i['id']} and {nxt['id']} are equal on weighted score ({i['score']}); {i['id']} ranks higher on {label} ({a} vs {b})."
                    break
            else:
                i["pick_reason"] = (f"{i['id']} and {nxt['id']} are equal on weighted score, evidence, uniqueness, simple and cheap: "
                                    "unresolved tie, order arbitrary (lowest ID first).")
    base_hi = [i for i in sorted(ranked, key=lambda i: (-i["base"], -i["score"], nkey(i["id"]))) if i["base"] >= 9 and i["top5"] == "no"]
    risen = [i for i in ranked if i["top5"] == "yes" and i["base"] <= 8]
    for i in base_hi[:3]:
        i.setdefault("weighting", f"Weighting pushed down: {i['id']} has base {i['base']} but weighted {i['score']:.1f} ({i['ev_level']} evidence, {i['u_level']} uniqueness) and misses the top {top_n}.")
    for i in risen[:3]:
        i.setdefault("weighting", f"Weighting pushed up: {i['id']} (base {i['base']}) rises to #{i['rank']} at {i['score']:.1f} on evidence ({i['ev_level']}) and uniqueness ({i['u_level']}).")


def build(data: dict, out_dir: Path):
    name, kn = data["name"], data["knobs"]
    auto = kn.get("mode", "auto") == "auto"
    src_short = {s["id"]: s.get("short", s["id"]) for s in data["sources"]}

    # Define
    ch = [dict(c, score=c["possible"] + c["exciting"]) for c in data["challenges"]]
    ranked = sorted(ch, key=lambda c: (-c["score"], -c["exciting"], -c["possible"], nkey(c["id"])))
    for r, c in enumerate(ranked, 1):
        c["rank"] = r
        c["picked"] = ("yes" if r <= 5 else "no") if auto or "picked" not in c else ("yes" if c["picked"] else "no")
    n_pick = sum(c["picked"] == "yes" for c in ch)
    for c in ch:
        c["reason"] = c.get("reason") or challenge_reason(c, ranked, n_pick)

    # Develop / Deliver
    ideas = []
    for i in data["ideas"]:
        base = i["cheap"] + i["simple"]
        evm, um = EV_MULT[i["ev_level"]], U_MULT[i["u_level"]]
        ideas.append(dict(i, cid=i["id"].split("-")[0], base=base, evm=float(evm), um=float(um),
                          score=half_up(Decimal(base) * evm * um, 1)))
    ir = sorted(ideas, key=lambda i: (-i["score"], -EV_RANK[i["ev_level"]], -U_RANK[i["u_level"]], -i["simple"], -i["cheap"], nkey(i["id"])))
    for r, i in enumerate(ir, 1):
        i["rank"], i["top5"] = r, "yes" if r <= 5 else "no"
    idea_reasons(ir, 5)
    by_id = {i["id"]: i for i in ideas}

    concepts = []
    for k in data["concepts"]:
        m = [by_id[x] for x in k["ids"]]
        avg = half_up(sum(Decimal(str(x["score"])) for x in m) / len(m), 2)
        concepts.append(dict(k, avg=avg, count=len(m), mean_ev=sum(EV_RANK[x["ev_level"]] for x in m) / len(m),
                             description=k.get("description") or "Together: " + "; ".join(x["text"][0].lower() + x["text"][1:] for x in m) + "."))
    cr = sorted(concepts, key=lambda k: (-k["avg"], -k["mean_ev"], -k["count"], nkey(k["id"])))
    for r, k in enumerate(cr, 1):
        k["picked"] = ("yes" if r <= 2 else "no") if auto or "picked" not in k else ("yes" if k["picked"] else "no")
    pk = [k for k in cr if k["picked"] == "yes"]
    for k in concepts:
        if not k.get("reason"):
            top = ", ".join(f"{x['id']} {x['avg']:.2f}" for x in pk)
            nxt = next((x for x in cr if x["picked"] == "no"), None)
            k["reason"] = (f"Pick: highest averages ({top})" + (f"; next is {nxt['id']} at {nxt['avg']:.2f}." if nxt else ".")) if k["picked"] == "yes" \
                else f"Not picked. Average {k['avg']:.2f} is below the picks ({top})."
    cname = {k["id"]: k["name"] for k in concepts}
    crank = {k["id"]: r for r, k in enumerate(cr)}

    P = sorted(data["pretotypes"], key=lambda p: (crank[p["cid"]], nkey(p["id"])))
    for p in P:
        dl = d(p["deadline"])
        p["success_line"] = f"At least {p['n']} of {p['of']} {p['metric']} ({p['n'] / p['of']:.0%}) by {dl.strftime('%a %b %-d, %Y')}"
        p["go"] = f"Go if {p['n']}+ {p['metric']} by {dl.strftime('%b %-d')}"
        p["nogo"] = f"No-go if fewer than {p['n']}; iterate if within 3 of the threshold."
        p["rec"] = "yes" if p.get("recommended") else "no"
        p["sel"] = "yes" if p.get("selected", p.get("recommended") if auto else False) else "no"

    wb = Workbook()
    wb.remove(wb.active)
    guide = wb.create_sheet("Tab guide")
    W = lambda *a, **k: write_sheet(wb, *a, **k)

    notes = data.get("knob_notes", {})
    W("Run knobs", ["Knob", "Value", "Description", "Source"], ["text", "mixed", "text", "text"], [
        ["ideas", kn["ideas"], "number of ideas generated per picked challenge", f"{notes.get('ideas', 'set for this run')}"],
        ["pretotypes", kn["pretotypes"], "number of pretotype tests designed", f"{notes.get('pretotypes', 'set for this run')}"],
        ["sources", kn["sources"], "number of research sources consulted", f"{notes.get('sources', 'set for this run')}"],
        ["country", kn["country"], "target launch country for the product/service", f"{notes.get('country', 'set for this run')}"],
        ["language", kn["language"], "language of the output", f"{notes.get('language', 'set for this run')}"],
        ["format", data.get("format") or "sheet", "output file type: sheet = Google Sheet", (f"copy of report template {data['template_ref']}" if data.get("template_ref") else "built from scratch (no template set)")],
        ["mode", kn.get("mode", "auto"), "generation type: auto or ask", f"{notes.get('mode', 'set for this run')}"],
        ["template", data.get("template_ref") or "none", "report template sheet: a Google Sheet id, or none = build from scratch", ("template knob for this run (template is never modified)" if data.get("template_ref") else "template: none; built from scratch")]])
    stopped = data.get("run_stopped") or _now_like(data["run_started"])
    W("Problem", ["Field", "Value", "Source", "Notes"], ["text"] * 4, [
        ["Shared title", data["title"], "Ideator", "Report title."],
        ["Problem statement", data["problem"], "User's message", "Used verbatim."],
        ["Cancelled", "CANCELLED" if data.get("cancelled") else "no", "Ideator", None],
        ["Run started", data["run_started"], "Ideator", "Fresh web research; no earlier report or memory used."],
        ["Run stopped", stopped, "Ideator", "Set just before the final build; the upload and checks after it are not counted."],
        ["Run time", run_time(data["run_started"], stopped), "Ideator", "Run stopped minus run started."]], height=48)

    kr = []
    for n, i in enumerate(ir[:3], 1):
        ev = f"evidence {i['ev_level']} ({i['ev_src']}, {src_short.get(i['ev_src'], i['ev_src'])})" if i.get("ev_src") else "hypothesis, no evidence found"
        kr.append(["Top ideas", n, i["id"], i["text"], i["score"], None, f"Ideas tab, rank {i['rank']}; {ev}", nkey(i["id"])])
    best = pk[0] if pk else None
    ft = next((p for p in P if best and p["cid"] == best["id"] and p["rec"] == "yes"), None)
    if ft:
        kr.append(["First test", None, ft["id"], f"{cname[ft['cid']]}: {ft['test']} Success: {ft['success_line']}. Deadline: {d(ft['deadline']).strftime('%a %b %-d, %Y')}.",
                   None, d(ft["deadline"]), f"Pretotypes tab, {ft['id']}: recommended first test of best concept {ft['cid']} (avg {best['avg']:.2f})", nkey(ft["id"])])
    W("Key results", ["Part", "Rank", "ID", "Text", "Weighted score", "Deadline", "Source", "ID sort key"],
      ["text", "int", "text", "text", "score1", "date", "text", "int"], kr, height=60)
    W("Sources", ["Source ID", "Citation", "URL", "Research summary", "Source", "ID sort key"], ["text"] * 5 + ["int"],
      [[s["id"], s["citation"], s["url"], s["summary"], f"Discover", nkey(s["id"])] for s in sorted(data["sources"], key=lambda s: nkey(s["id"]))], height=120)
    nat = sorted(ch, key=lambda c: nkey(c["id"]))
    W("Sticky notes", ["ID", "Sticky note", "Evidence", "Source", "ID sort key"], ["text"] * 4 + ["int"],
      [[c["id"], c["text"], c["evidence"], f"Discover: challenges and sticky notes", nkey(c["id"])] for c in nat])
    rows, fx = [], {}
    for r, c in enumerate(ranked, 2):
        rows.append([c["rank"], c["id"], c["text"], c["possible"], c["exciting"], None, c["picked"], c["evidence"], f"Define ratings (judgment, not empirical)", nkey(c["id"])])
        fx[(r, 6)] = f"=D{r}+E{r}"
    W("Challenges", ["Rank", "ID", "Challenge", "Possible", "Exciting", "Score", "Picked", "Evidence", "Source", "ID sort key"],
      ["int", "text", "text", "int", "int", "formula_score", "text", "text", "text", "int"], rows, fx)
    rows, fx = [], {}
    for r, c in enumerate(ranked, 2):
        rows.append([c["id"], c["rank"], c["picked"], None, c["possible"], c["exciting"], c["reason"], f"Define {'auto-pick' if auto else 'user pick'}", nkey(c["id"])])
        fx[(r, 4)] = f"=E{r}+F{r}"
    W("Define picks", ["ID", "Rank", "Picked", "Score", "Possible", "Exciting", "Selection reason", "Source", "ID sort key"],
      ["text", "int", "text", "formula_score", "int", "int", "text", "text", "int"], rows, fx)
    SW = "Ideator scoring rules (Deliver)"
    W("Scoring weights", ["Item", "Value", "Meaning", "Source"], ["text", "mixed", "text", "text"], [
        ["Formula", "(cheap + simple) x evidence multiplier x uniqueness multiplier, rounded to 1 decimal", "Weighted score formula", SW],
        ["cheap scale", "1-5", "1 = expensive, 5 = very cheap", SW], ["simple scale", "1-5", "1 = complex, 5 = very simple", SW],
        ["base", "cheap + simple (2-10)", "Sum of cheap and simple before multipliers", SW],
        ["evidence strong", 1.3, "Source directly supports the idea; cite source ID", SW],
        ["evidence some", 1.15, "Source supports the challenge or something close; cite source ID", SW],
        ["evidence none", 1.0, "No source; hypothesis", SW],
        ["uniqueness non-obvious", 1.2, "Most teams would not think of it; not a common fix", SW],
        ["uniqueness somewhat", 1.1, "A known approach with a fresh angle", SW],
        ["uniqueness obvious", 1.0, "The standard fix, or a small copy or UI tweak", SW],
        ["tie-break order", "higher evidence, then higher uniqueness, then higher simple, then higher cheap; otherwise lowest ID first (natural order), marked unresolved tie, order arbitrary", "Deliver tie-break rule", SW]])
    rows, fx = [], {}
    for r, i in enumerate(ir, 2):
        rows.append([i["id"], i["cid"], i["text"], i["cheap"], i["simple"], None, i["ev_level"], i.get("ev_src") or "hypothesis", i["u_level"], i["u_reason"],
                     i["evm"], i["um"], None, i["score"], i["rank"], i["top5"], i.get("pick_reason") or None, i.get("weighting") or None, f"Develop/Deliver", nkey(i["id"])])
        fx[(r, 6)], fx[(r, 13)] = f"=D{r}+E{r}", f"=K{r}*L{r}"
    W("Ideas", ["ID", "Challenge ID", "Idea", "Cheap", "Simple", "Base", "Evidence level", "Evidence source", "Unique level", "Unique reason", "Evidence mult",
                "Unique mult", "Combined mult", "Weighted score", "Rank", "Top 5", "Pick reason", "Weighting note", "Source", "ID sort key"],
      ["text", "text", "text", "int", "int", "formula_base", "text", "text", "text", "text", "mult", "mult", "mult", "score1", "int", "text", "text", "text", "text", "int"],
      rows, fx, height=36)
    rows, fx = [], {}
    for r, k in enumerate(sorted(concepts, key=lambda k: nkey(k["id"])), 2):
        rows.append([k["id"], k["name"], k["description"], ", ".join(k["ids"]), k["count"], None, k["picked"], k["reason"], f"Deliver concepts", nkey(k["id"])])
        fx[(r, 6)] = "=ROUND(AVERAGE(" + ",".join(f'INDEX(Ideas!$N:$N,MATCH("{x}",Ideas!$A:$A,0))' for x in k["ids"]) + "),2)"
    W("Concepts", ["ID", "Concept", "Description", "Idea IDs", "Idea count", "Average weighted score", "Picked", "Pick reason", "Source", "ID sort key"],
      ["text", "text", "text", "text", "int", "formula_avg", "text", "text", "text", "int"], rows, fx, height=48)
    W("Pretotypes", ["ID", "Concept ID", "Concept name", "Recommended first test", "Hypothesis", "Test", "Success line", "Success number", "Success out of",
                     "Success rate", "Deadline", "Go rule", "No-go rule", "Observed result", "Decision", "Source", "ID sort key"],
      ["text", "text", "text", "text", "text", "text", "text", "int", "int", "pct", "date", "text", "text", "text", "text", "text", "int"],
      [[p["id"], p["cid"], cname[p["cid"]], p["rec"], p["hypothesis"], p["test"], p["success_line"], p["n"], p["of"], p["n"] / p["of"], d(p["deadline"]),
        p["go"], p["nogo"], p.get("observed"), p.get("decision"), f"Pretotypes (thresholds are proposed decision rules, not sourced predictions)", nkey(p["id"])] for p in P],
      height=60)
    mats = []
    for p in P:
        mine = [m for m in data.get("materials", []) if m["pretotype"] == p["id"]]
        if mine:
            mats += [[p["id"], p["cid"], m["type"], m["text"], f"Pretotypes: materials for {p['id']} (prepared only, not sent)", nkey(p["id"])] for m in mine]
        else:
            mats.append([p["id"], p["cid"], None, None, "No materials drafted (materials are prepared for recommended first tests).", nkey(p["id"])])
    W("Materials", ["Pretotype ID", "Concept ID", "Material type", "Text", "Source", "ID sort key"], ["text"] * 5 + ["int"], mats, height=48)
    W("First tests", ["Concept ID", "Pretotype ID", "Recommended first test", "Selected", "Start date", "Check-in date", "Check-in status", "Source", "ID sort key"],
      ["text", "text", "text", "text", "date", "date", "text", "text", "int"],
      [[p["cid"], p["id"], p["rec"], p["sel"], d(p.get("start")), d(p.get("checkin")),
        p.get("status") or ("I'll set up the check-in as soon as you tell me a start date." if p["sel"] == "yes" else "Not selected."),
        f"Pretotypes: first tests and check-ins", nkey(p["id"])] for p in P], height=48)
    bd = [["Sticky notes", n, c["id"], c["text"], None, "no", STICKY_COLORS[(n - 1) % 10], "Board row 1: sticky notes in natural order, 5 per line", nkey(c["id"])] for n, c in enumerate(nat, 1)]
    bd += [["Challenges", n, c["id"], c["text"], c["score"], c["picked"], "#0b6e4f" if c["picked"] == "yes" else "#90caf9", "Board row 2: challenge bars sorted by score, then exciting", nkey(c["id"])]
           for n, c in enumerate(ranked, 1)]  # same order as Challenges: score, then exciting, then possible, then ID
    bd += [["Ideas", n, i["id"], i["text"], i["score"], i["top5"], "#e65100" if i["top5"] == "yes" else "#b0bec5", "Board row 3: idea bars sorted by weighted score, top 5 labeled", nkey(i["id"])]
           for n, i in enumerate(ir, 1)]
    ws = W("Board content", ["Board row", "Sort order", "ID", "Text", "Score", "Highlighted", "Color", "Source", "ID sort key"],
           ["text", "int", "text", "text", "score1", "text", "text", "text", "int"], bd)
    for r in range(2, 2 + len(bd)):
        ws.cell(r, 7).fill = PatternFill("solid", fgColor=ws.cell(r, 7).value[1:])

    for t, col in SELECTION_COLS.items():  # selected rows in green, other rows plain
        ws = wb[t]
        k = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)].index(col) + 1
        for r in range(2, ws.max_row + 1):
            on = ws.cell(r, k).value == "yes"
            for c in range(1, ws.max_column + 1):
                if t == "Board content" and c == 7:
                    continue  # the Color cell shows the board color itself
                if on:
                    ws.cell(r, c).fill, ws.cell(r, c).font = PICK_FILL, PICK_FONT
                else:
                    ws.cell(r, c).fill = PatternFill(fill_type=None)

    counts = {t: wb[t].max_row - 1 for t in wb.sheetnames if t != "Tab guide"}
    G = [("Tab guide", "Guide to the tabs", "This tab", "One row per tab with what it holds and its row count. Sort by 'ID sort key' for natural ID order (C9 before C10)."),
         ("Run knobs", "Run knobs (8 run knobs)", "Run settings", "Actual value of each knob for this run."),
         ("Problem", "Title and problem statement", "Input", "Shared title, verbatim problem statement, cancelled flag, run start and stop times and run time."),
         ("Key results", "Key results", "Top ideas + First test", "Top three ideas by weighted score and the recommended first test of the best concept, with a Source column per row."),
         ("Sources", "Research sources and summary", "1. Discover", "Real sources with URLs, what each says, and limitations."),
         ("Sticky notes", "Sticky notes", "1. Discover", "Challenges in natural order with their source or 'hypothesis, no evidence found'."),
         ("Challenges", "Challenges with scores", "2. Define", "Ranked challenges; Score = Possible + Exciting (formula). Ratings are judgments."),
         ("Define picks", "Define selections and reasons", "2. Define", "Pick decision and reason for each challenge."),
         ("Scoring weights", "Scoring weights", "4. Deliver", "Formula, multipliers and tie-break order."),
         ("Ideas", "Ideas with scoring factors", "3. Develop / 4. Deliver", "All ideas ranked; Base and Combined mult are formulas, Weighted score is stored as computed (1 decimal)."),
         ("Concepts", "Concepts", "4. Deliver", "Concepts with idea IDs; average is a live formula from Ideas."),
         ("Pretotypes", "Pretotype tests", "5. Pretotypes", "Tests with hypothesis, success line, deadline, go/no-go; result and decision filled after tests run."),
         ("Materials", "Pretotype materials", "5. Pretotypes", "Ready-to-use text for recommended first tests (prepared only, nothing sent)."),
         ("First tests", "First tests and check-ins", "5. Pretotypes", "Selected tests, start dates and check-in status."),
         ("Board content", "Board content", "Overview", "Sticky notes, challenge bars and idea bars as sortable rows.")]
    counts["Tab guide"] = len(G)
    guide.append(["Tab", "Report part", "Ideator section", "Data rows", "What it holds"])
    write_into = [[t, part, sec, counts[t], what] for t, part, sec, what in G]
    for c in range(1, 6):
        h = guide.cell(1, c)
        h.font, h.fill, h.border = HEADER_FONT, HEADER_FILL, THIN
        h.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
    for r, row in enumerate(write_into, 2):
        for c, v in enumerate(row, 1):
            style_cell(guide.cell(r, c, v), "int" if c == 4 else "text", r)
    guide.freeze_panes = "A2"
    guide.auto_filter.ref = f"A1:E{1 + len(G)}"
    for n, w in enumerate(WIDTHS["Tab guide"], 1):
        guide.column_dimensions[get_column_letter(n)].width = w
    fit_text_widths(guide, ["text", "text", "text", "int", "text"])
    assert wb.sheetnames == [g[0] for g in G], wb.sheetnames
    # Row heights are never set: every cell wraps its text, so each row grows with its content.

    wb.properties.title = name
    wb.properties.creator = "Ideator"
    return wb, counts


# ---------- output: template copy or from scratch ----------

def _parse_time(t):
    """'YYYY-MM-DD HH:MM[:SS] <zone>' -> naive datetime, or None."""
    from datetime import datetime
    parts = str(t).split()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(" ".join(parts[:2]), fmt)
        except (ValueError, IndexError):
            pass
    return None


def _now_like(started):
    """Now (box clock = user's zone) in the run_started format, with its zone label."""
    from datetime import datetime
    zone = " ".join(str(started).split()[2:])
    return (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + (" " + zone if zone else "")).strip()


def run_time(started, stopped):
    a, b = _parse_time(started), _parse_time(stopped)
    if not a or not b or b < a:
        return "unknown"
    m, sec = divmod(int((b - a).total_seconds()), 60)
    h, m = divmod(m, 60)
    return (f"{h}h {m}m {sec}s" if h else f"{m}m {sec}s")


DEMO_LABEL = re.compile(r"example data|randomly generated|random(ly)?[- ]generated|sample (data|workbook)|fictional|placeholder data", re.I)


def _copy_tab(src, ws):
    """Template tab with no report header: lay the report tab in as built from scratch."""
    from copy import copy
    for row in src.iter_rows():
        for c in row:
            t = ws.cell(c.row, c.column, c.value)
            if c.has_style:  # copy style parts, not _style: style ids differ between workbooks
                t.font, t.fill, t.border = copy(c.font), copy(c.fill), copy(c.border)
                t.alignment, t.number_format, t.protection = copy(c.alignment), c.number_format, copy(c.protection)
    for r, d in src.row_dimensions.items():
        ws.row_dimensions[r].height = d.height
    for k, d in src.column_dimensions.items():
        ws.column_dimensions[k].width = d.width
    ws.freeze_panes, ws.auto_filter.ref = src.freeze_panes, src.auto_filter.ref


def _tab_fingerprint(ws):
    """Everything a template tab shows: cells with styles, sizes, images, merges, freeze, filter."""
    cells = tuple((c.coordinate, c.value, c.font.__repr__(), c.fill.__repr__(), c.border.__repr__(),
                   c.alignment.__repr__(), c.number_format) for row in ws.iter_rows() for c in row)
    rows = tuple(sorted((r, d.height, d.hidden) for r, d in ws.row_dimensions.items()))
    cols = tuple(sorted((k, d.width, d.hidden) for k, d in ws.column_dimensions.items()))
    return (cells, rows, cols, len(ws._images), tuple(sorted(map(str, ws.merged_cells.ranges))),
            ws.freeze_panes, ws.auto_filter.ref, ws.sheet_state)


def fill_template(template_xlsx: Path, scratch, template_ref: str):
    """Write the computed report into a COPY of the template workbook.

    The template file is opened read-only and never saved back; the caller saves
    the returned workbook under the run name. The copy keeps the template's own
    tabs that are not report tabs read-only: never written, resized or reformatted
    (checked by fingerprint). Every report tab is built from
    scratch and starts at row 1 (no branding rows, no search for free space), exactly as
    with no template: a same-named template tab is replaced in place. Every tab
    the template already has keeps its place, first; report tabs the template
    lacks are added after them, in report order.
    """
    from openpyxl import load_workbook
    wb = load_workbook(template_xlsx)
    warnings = []
    canon = {t.lower(): t for t in scratch.sheetnames}
    for ws in wb.worksheets:
        if ws.title not in scratch.sheetnames and ws.title.lower() in canon:
            target = canon[ws.title.lower()]  # copy only: align tab-name casing with the report
            ws.title = "__tmp_rename__"
            ws.title = target
    own = {}  # the template's own tabs are read-only: never written, resized or reformatted
    for ws in wb.worksheets:
        if ws.title not in scratch.sheetnames:
            warnings.append(f"template tab '{ws.title}' is not a report tab; kept as it is")
            own[ws.title] = _tab_fingerprint(ws)
    for i, t in enumerate(scratch.sheetnames):  # every report tab is built from scratch, never from the template's tab
        if t in wb.sheetnames:
            pos = wb.sheetnames.index(t)
            wb.remove(wb[t])
        else:  # tabs the template already has come first; new report tabs follow, in report order
            pos = len(wb.sheetnames)
        _copy_tab(scratch[t], wb.create_sheet(t, pos))
    for t, fp in own.items():
        assert _tab_fingerprint(wb[t]) == fp, f"template tab '{t}' changed"
    wb.active = 0
    wb.properties.title = scratch.properties.title
    wb.properties.creator = "Ideator"
    return wb, warnings


def make_template(scratch):
    """Turn a built workbook into a report template: headers, widths, frozen rows,
    filters and one styled row-2 pattern with formulas; no run data."""
    for ws in scratch.worksheets:
        if ws.max_row > 2:
            ws.delete_rows(3, ws.max_row - 2)
        for c in range(1, ws.max_column + 1):
            cell = ws.cell(2, c)
            if not (isinstance(cell.value, str) and cell.value.startswith("=")) or "MATCH(" in str(cell.value):
                cell.value = None
            cell.fill = PatternFill(fill_type=None)
        ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}2"
    scratch.properties.title = "ideator-report-template"
    return scratch


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Build an Ideator Google Sheet report workbook.")
    ap.add_argument("run_json")
    ap.add_argument("--template", help="template .xlsx exported from the 'template' run knob sheet; omit to build from scratch")
    ap.add_argument("--out-dir", default=None, help="output folder; defaults to the run JSON's directory")
    ap.add_argument("--make-template", help="maintainer only: write an empty template .xlsx to this path")
    a = ap.parse_args()
    data = json.loads(Path(a.run_json).read_text())
    out_dir = Path(a.out_dir) if a.out_dir else Path(a.run_json).resolve().parent
    if a.template:
        data["template_ref"] = data.get("template_ref") or "template"
    wb, counts = build(data, out_dir)
    if a.make_template:
        make_template(wb).save(a.make_template)
        print(json.dumps({"template": a.make_template}))
        sys.exit(0)
    warnings = []
    if a.template:
        wb, warnings = fill_template(Path(a.template), wb, data["template_ref"])
    for ws in wb.worksheets:  # report data is real run data; flag stray demo labels
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and DEMO_LABEL.search(c.value):
                    warnings.append(f"'{ws.title}'!{c.coordinate}: looks like an example/random-data label; remove it from the run JSON")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{data['name']}.xlsx"
    if a.template and out.resolve() == Path(a.template).resolve():
        sys.exit("refusing to overwrite the template file")
    wb.save(out)
    print(json.dumps({"xlsx": str(out), "mode": "template copy" if a.template else "from scratch", "rows": counts, "warnings": warnings}))
