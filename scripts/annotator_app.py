#!/usr/bin/env python3
"""
Standalone annotator app for Label Studio text-to-SQL review.

Run on any host/port for independent annotator sessions. Each annotator runs
their own instance (different port or different machine). Submits annotations
to a shared Label Studio instance.

Usage:
  # Single annotator (default port 8766)
  LABEL_STUDIO_URL=http://localhost:8081 LABEL_STUDIO_USER_TOKEN=xxx python scripts/annotator_app.py

  # Multiple annotators on one host (different ports)
  python scripts/annotator_app.py --port 8766 &
  python scripts/annotator_app.py --port 8767 &
  python scripts/annotator_app.py --port 8768 &

  # Different hosts: run on each annotator's machine, same LABEL_STUDIO_URL
  python scripts/annotator_app.py --port 8766

Requires: LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN
"""
import csv
import io
import json
import os
import re
import secrets
import sys
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

# Auth: staff and annotator. staff=full access + mode selector, annotator=annotator view only
USER_CREDENTIALS = {"staff": "123123", "annotator": "123123"}
SESSIONS = {}  # session_id -> {user, expires}
SESSION_COOKIE = "annotator_session"
SESSION_DAYS = 30

scripts_dir = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, scripts_dir)

try:
    import psycopg2
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login — SQL Annotator</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #0f1419; --bg-card: #1a1f26; --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d; --accent: #3b82f6; --radius: 8px; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--fg); margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem; width: 100%; max-width: 360px; }
    h1 { font-size: 1.25rem; margin: 0 0 1.5rem 0; }
    label { display: block; font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); margin-bottom: 0.375rem; text-transform: uppercase; }
    input[type="text"], input[type="password"] { width: 100%; padding: 0.625rem 0.75rem; background: var(--bg); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.9375rem; margin-bottom: 1rem; }
    input:focus { outline: none; border-color: var(--accent); }
    .row { margin-bottom: 1rem; }
    .row label { display: inline; text-transform: none; font-weight: 400; }
    .row input { width: auto; margin: 0 0.5rem 0 0; }
    button { width: 100%; padding: 0.75rem; background: var(--accent); color: #fff; border: none; border-radius: 6px; font-size: 0.9375rem; font-weight: 600; cursor: pointer; }
    button:hover { background: #2563eb; }
    .err { color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>SQL Annotator</h1>
    <form method="post" action="/login">
      <label>Username</label>
      <input type="text" name="user" placeholder="staff or annotator" required autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" placeholder="••••••••" required autocomplete="current-password">
      <div class="row">
        <input type="checkbox" name="stay" id="stay" value="1" checked>
        <label for="stay">Stay logged in (30 days)</label>
      </div>
      <button type="submit">Log in</button>
      <p id="err" class="err"></p>
    </form>
  </div>
  <script>
    const params = new URLSearchParams(window.location.search);
    if (params.get('err')) document.getElementById('err').textContent = params.get('err');
  </script>
</body>
</html>
"""

try:
    from label_studio_adapter import _get_api_key, _ls_request
except ImportError:
    def _get_api_key():
        return os.getenv("LABEL_STUDIO_API_KEY") or os.getenv("LABEL_STUDIO_USER_TOKEN", "")

    def _ls_request(method, path, json_data=None):
        try:
            url = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080").rstrip("/")
            api_key = _get_api_key()
            req = Request(
                f"{url}{path}",
                data=json.dumps(json_data).encode() if json_data else None,
                headers={"Authorization": f"Token {api_key}", "Content-Type": "application/json"},
                method=method,
            )
            with urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode()) if r.length else {}
        except Exception as e:
            return -1, {"error": str(e)}


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SQL Annotator — Workbench</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f1419; --bg-card: #1a1f26; --bg-hover: #242b33;
      --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d;
      --accent: #3b82f6; --accent-hover: #2563eb;
      --success: #22c55e; --warning: #eab308; --error: #ef4444;
      --radius: 8px; --radius-sm: 6px;
      --shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 0; line-height: 1.5; font-size: 14px; }
    .app { max-width: 1400px; margin: 0 auto; padding: 0 1.5rem 2rem; }
    .header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
    .header h1 { font-size: 1.125rem; font-weight: 600; color: var(--fg); margin: 0; letter-spacing: -0.02em; }
    .header-sub { font-size: 0.8125rem; color: var(--fg-muted); margin-top: 0.25rem; }
    .header-sub a { color: var(--accent); text-decoration: none; }
    .header-sub a:hover { text-decoration: underline; }
    .toolbar { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
    .row { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: flex-end; }
    select, button { padding: 0.5rem 0.875rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: var(--radius-sm); cursor: pointer; font-size: 0.875rem; font-family: inherit; }
    select:hover, button:hover:not(:disabled) { background: var(--bg-hover); border-color: var(--fg-muted); }
    button.primary { background: var(--accent); color: #fff; border-color: var(--accent); font-weight: 500; }
    button.primary:hover:not(:disabled) { background: var(--accent-hover); }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    label { display: block; font-size: 0.75rem; font-weight: 500; color: var(--fg-muted); margin-bottom: 0.375rem; text-transform: uppercase; letter-spacing: 0.04em; }
    textarea, input[type="text"] { width: 100%; padding: 0.625rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: var(--radius-sm); font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace; font-size: 0.8125rem; }
    textarea:focus, input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 2px rgba(59,130,246,0.2); }
    textarea { min-height: 100px; resize: vertical; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.25rem; margin-bottom: 1rem; box-shadow: var(--shadow); }
    .card-title { font-size: 0.8125rem; font-weight: 600; color: var(--fg); margin-bottom: 0.75rem; }
    #msg { font-size: 0.875rem; padding: 0.5rem 0; }
    #msg.err { color: var(--error); }
    #msg.ok { color: var(--success); }
    .nav { display: flex; gap: 0.5rem; margin-top: 1.25rem; }
    .mode-row { margin-bottom: 1rem; }
    .mode-row label { display: inline; margin-right: 1rem; text-transform: none; font-weight: 400; }
    .mode-row input { margin-right: 0.375rem; }
    .admin-bar { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.3); border-radius: var(--radius); padding: 0.75rem 1rem; margin-bottom: 1rem; }
    .admin-bar label { font-weight: 500; color: var(--accent); text-transform: none; }
    .query-list { max-height: 320px; overflow-y: auto; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-card); }
    .query-list .q-row { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.625rem 1rem; border-bottom: 1px solid var(--border); cursor: pointer; font-size: 0.875rem; }
    .query-list .q-row:last-child { border-bottom: none; }
    .query-list .q-row:hover { background: var(--bg-hover); }
    .query-list .q-row.fixed { background: rgba(34,197,94,0.08); border-left: 3px solid var(--success); }
    .task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.75rem; max-height: 70vh; overflow-y: auto; padding: 0.25rem 0; }
    .task-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s; }
    .task-card:hover { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
    .task-card.active { border-color: var(--accent); background: rgba(59,130,246,0.06); box-shadow: 0 0 0 2px rgba(59,130,246,0.3); }
    .task-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
    .task-card-title { font-weight: 600; font-size: 0.9375rem; color: var(--fg); }
    .task-card-preview { font-size: 0.8125rem; color: var(--fg-muted); line-height: 1.4; margin-bottom: 0.75rem; max-height: 2.8em; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .task-card-badges { display: flex; flex-wrap: wrap; gap: 0.375rem; margin-bottom: 0.75rem; }
    .task-card-open { width: 100%; padding: 0.5rem 0.75rem; font-size: 0.8125rem; background: var(--accent); color: #fff; border: none; border-radius: var(--radius-sm); cursor: pointer; font-weight: 500; }
    .task-card-open:hover { background: var(--accent-hover); }
    .badge { display: inline-flex; align-items: center; padding: 0.2rem 0.5rem; font-size: 0.6875rem; font-weight: 600; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.03em; }
    .badge-completed { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-progress { background: rgba(59,130,246,0.2); color: var(--accent); }
    .badge-queued { background: rgba(139,148,158,0.2); color: var(--fg-muted); }
    .badge-error { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-accepted { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-rejected { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-fixed { background: rgba(59,130,246,0.2); color: var(--accent); }
    .layout-2col { display: grid; grid-template-columns: 320px 1fr; gap: 1.5rem; }
    @media (max-width: 900px) { .layout-2col { grid-template-columns: 1fr; } }
    .progress-bar { height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; margin-top: 0.5rem; }
    .progress-bar-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.2s; }
    .section-label { font-size: 0.6875rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .validation-status { padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; }
    .validation-status.valid { background: rgba(34,197,94,0.15); color: var(--success); border: 1px solid rgba(34,197,94,0.4); }
    .validation-status.invalid { background: rgba(239,68,68,0.15); color: var(--error); border: 1px solid rgba(239,68,68,0.4); }
    .pipeline-tracker { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.8125rem; }
    .pipeline-tracker .pipeline-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .pipeline-tracker .pipeline-row:last-child { margin-bottom: 0; }
    .pipeline-tracker .pipeline-label { color: var(--fg-muted); font-weight: 500; margin-right: 0.25rem; min-width: 4.5rem; }
    .pipeline-tracker .pipeline-stage { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(139,148,158,0.15); color: var(--fg); }
    .pipeline-tracker .pipeline-stage .count { font-weight: 600; color: var(--accent); }
    .pipeline-tracker .pipeline-arrow { color: var(--fg-muted); font-size: 0.7rem; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
  </style>
</head>
<body>
  <div class="app">
    <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
      <label for="mode-select">Mode</label>
      <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
    </div>
    <div class="view-selector">
      <label for="view-select">View</label>
      <select id="view-select" onchange="if(this.value) window.location.href=this.value">
        <option value="/staff">Staff</option>
        <option value="/">Annotator</option>
        <option value="/admin/tasks">Task Board</option>
        <option value="/dashboard">Dashboard</option>
        <option value="/suite">Full Suite</option>
        <option value="/customer">Customer Portal</option>
      </select>
    </div>
    <div class="header">
    <div>
      <h1>SQL Annotator</h1>
      <p class="header-sub"><a href="/dashboard">Dashboard</a> · <a href="/suite">Full Suite</a> · <a href="/customer">Customer Portal</a> · queries.json master. <a href="https://scale.com/docs/pro-or-tasks-tab" target="_blank" rel="noopener">Scale Tasks</a> · <a href="https://outlier.ai" target="_blank" rel="noopener">Outlier</a> · <a href="/logout">Log out</a></p>
    </div>
    <div class="toolbar"></div>
  </div>

  <div class="admin-bar">
    <label><input type="checkbox" id="admin" /> Admin</label>
    <a href="/admin/tasks" style="margin-left:1rem;color:var(--accent);font-size:0.85rem;text-decoration:none;">Open task board (30 queries)</a>
    <span style="margin-left:1rem;color:var(--fg-muted);font-size:0.85rem;">— Independent task submissions, Accept/Fix/Reject</span>
  </div>

  <div class="mode-row">
    <label><input type="radio" name="mode" value="json" checked> queries.json</label>
    <label><input type="radio" name="mode" value="ls"> Label Studio</label>
  </div>

  <div id="json-row" class="row">
    <div>
      <label id="source-label">Source (queries.json)</label>
      <select id="source" title="Choose which db-N to annotate"><option value="template">Loading...</option></select>
    </div>
    <div>
      <label>Query</label>
      <select id="task" disabled><option>Load source first</option></select>
    </div>
    <div style="align-self:flex-end;">
      <button id="load-json">Load</button>
      <button id="export-csv" title="Export to Excel CSV">Export CSV</button>
      <button id="export-json" title="Export JSON">Export JSON</button>
      <button id="export-md" title="Export to queries.md">Export MD</button>
    </div>
  </div>

  <div id="tasks-tab-filters" class="row" style="margin-top:0.5rem;">
    <div>
      <label>Task Status</label>
      <select id="filter-task-status">
        <option value="">All</option>
        <option value="Queued">Queued</option>
        <option value="In Progress">In Progress</option>
        <option value="Completed">Completed</option>
        <option value="Error">Error</option>
        <option value="Canceled">Canceled</option>
        <option value="Redo">Redo</option>
      </select>
    </div>
    <div>
      <label>Audit Status</label>
      <select id="filter-audit-status">
        <option value="">All</option>
        <option value="Ready to Audit">Ready to Audit</option>
        <option value="Accepted">Accepted</option>
        <option value="Fixed">Fixed</option>
        <option value="Rejected">Rejected</option>
      </select>
    </div>
  </div>

  <div id="admin-fix-panel" style="display:none;" class="layout-2col">
    <div class="card">
      <div class="section-label">30 independent task submissions — click a card to open</div>
      <div id="pipeline-tracker" class="pipeline-tracker" style="display:none;"></div>
      <div id="task-progress" style="font-size:0.75rem;color:var(--fg-muted);margin-bottom:0.5rem;"></div>
      <div class="progress-bar" id="task-progress-bar" style="display:none;"><div class="progress-bar-fill" id="task-progress-fill" style="width:0%"></div></div>
      <div id="query-list" class="query-list"></div>
      <div id="task-grid" class="task-grid" style="display:none;"></div>
    </div>
    <div id="admin-form-slot"></div>
  </div>

  <div id="ls-row" class="row" style="display:none;">
    <div>
      <label>Project</label>
      <select id="project" disabled><option>Loading...</option></select>
    </div>
    <div id="ls-seed-source-wrap" style="display:none;">
      <label>Seed from (Admin)</label>
      <select id="ls-seed-source"><option value="template">Loading...</option></select>
    </div>
    <div>
      <label>Task</label>
      <select id="ls-task" disabled><option>Select project first</option></select>
    </div>
    <div style="align-self:flex-end;">
      <button id="refresh" disabled>Refresh</button>
      <button id="seed" title="Create project and import">Seed</button>
    </div>
  </div>

  <div id="form" style="display:none;">
    <div class="section-label" style="margin-top:1rem;">Annotation</div>
    <div class="card">
      <label>Question (queries.md)</label>
      <textarea id="question" rows="3"></textarea>
    </div>
    <div class="card">
      <label>SQL (edit if needed)</label>
      <textarea id="sql" rows="12"></textarea>
    </div>
    <div class="card">
      <label>Evidence (chain-of-thought)</label>
      <textarea id="evidence" rows="5"></textarea>
    </div>
    <div class="section-label">Metadata</div>
    <div class="card" style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div><label>Difficulty</label><select id="difficulty"><option value="simple">simple</option><option value="moderate">moderate</option><option value="challenging">challenging</option></select></div>
      <div><label>Query category</label><input type="text" id="query_category" placeholder="e.g. aggregation, window/ranking"></div>
    </div>
    <div class="card">
      <label>Tables used (comma-separated)</label>
      <input type="text" id="tables_used" placeholder="e.g. patients, diagnoses">
    </div>
    <div class="card">
      <label>Expected output</label>
      <textarea id="expected_output" rows="3" placeholder="e.g. [[7.3]] or [['Emergency', 142]]"></textarea>
    </div>
    <div class="card">
      <label>Actual output (run query locally)</label>
      <div class="row" style="margin-bottom:0.5rem;">
        <button id="validate-sql" type="button" title="Validate SQL against live database">Validate SQL</button>
        <button id="run-query" type="button">Run query</button>
        <button id="use-as-expected" type="button" disabled>Use as expected output</button>
      </div>
      <div id="validation-status" class="validation-status" style="display:none;"></div>
      <textarea id="actual_output" rows="4" readonly placeholder="Click Run query to execute against local PostgreSQL (PG_* env)"></textarea>
    </div>
    <div class="section-label">Scale-style status</div>
    <div class="card" style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div><label>Task Status</label><select id="task_status"><option value="Queued">Queued</option><option value="In Progress">In Progress</option><option value="Completed">Completed</option><option value="Error">Error</option><option value="Canceled">Canceled</option><option value="Redo">Redo</option></select></div>
      <div><label>Audit Status</label><select id="audit_status"><option value="Ready to Audit">Ready to Audit</option><option value="Accepted">Accepted</option><option value="Fixed">Fixed</option><option value="Rejected">Rejected</option></select></div>
    </div>
    <div class="nav">
      <button class="primary" id="submit">Submit annotation</button>
      <button id="next">Next task</button>
    </div>
  </div>

  <p id="msg"></p>

  <script>
    const api = (path, opts = {}) => fetch('/api' + path, { headers: { 'Content-Type': 'application/json' }, ...opts }).then(r => r.json());
    const $ = id => document.getElementById(id);
    const msg = (t, cls) => { const m = $('msg'); m.textContent = t; m.className = cls || ''; };

    let tasks = [], currentTask = null;

    async function loadSources() {
      const data = await api('/sources');
      const sources = data.sources || ['template'];
      const opts = sources.map(s => `<option value="${s}">${s}</option>`).join('');
      $('source').innerHTML = opts;
      if ($('ls-seed-source')) $('ls-seed-source').innerHTML = opts;
    }
    let mode = 'json';
    let admin = false;

    function isJsonMode() { return mode === 'json'; }
    function isAdmin() { return admin; }

    const formOriginalParent = $('form')?.parentElement;
    const formOriginalNext = $('form')?.nextElementSibling;
    function applyAdminState() {
      admin = $('admin').checked;
      $('source-label').textContent = admin ? 'Database to annotate' : 'Source (queries.json)';
      $('ls-seed-source-wrap').style.display = (admin && !isJsonMode()) ? 'block' : 'none';
      $('admin-fix-panel').style.display = (admin && isJsonMode() && tasks.length) ? 'block' : 'none';
      $('submit').textContent = admin ? 'Save (fix)' : 'Submit annotation';
      const taskWrap = document.querySelector('#task')?.closest('div');
      if (taskWrap) taskWrap.style.display = admin ? 'none' : 'block';
      const slot = $('admin-form-slot');
      if (admin && tasks.length && slot && $('form')) { slot.appendChild($('form')); slot.style.minWidth = '0'; }
      else if ((!admin || !tasks.length) && formOriginalParent && $('form') && $('form').parentElement !== formOriginalParent) { formOriginalParent.insertBefore($('form'), formOriginalNext); }
      if (admin && isJsonMode() && tasks.length) renderQueryList();
    }
    $('admin').onchange = applyAdminState;

    function escapeHtml(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }
    function taskBadgeClass(s) {
      if (!s) return 'badge-queued';
      const v = (s + '').toLowerCase();
      if (v.includes('completed')) return 'badge-completed';
      if (v.includes('progress')) return 'badge-progress';
      if (v.includes('error')) return 'badge-error';
      return 'badge-queued';
    }
    function auditBadgeClass(s) {
      if (!s) return '';
      const v = (s + '').toLowerCase();
      if (v.includes('accepted')) return 'badge-accepted';
      if (v.includes('rejected')) return 'badge-rejected';
      if (v.includes('fixed')) return 'badge-fixed';
      return '';
    }
    function openTaskFromGrid(idx) {
      $('task').value = idx;
      showTask();
      $('form').style.display = 'block';
      document.querySelectorAll('.task-card.active').forEach(c => c.classList.remove('active'));
      const card = document.querySelector(`.task-card[data-idx="${idx}"]`);
      if (card) card.classList.add('active');
      document.querySelector(`#task-grid .task-card[data-idx="${idx}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    function renderPipelineTracker(tasks, elId) {
      const el = document.getElementById(elId);
      if (!el || !tasks || !tasks.length) { if (el) el.style.display = 'none'; return; }
      const TASK_STAGES = ['Queued','In Progress','Completed','Error','Canceled','Redo'];
      const AUDIT_STAGES = ['Ready to Audit','Accepted','Fixed','Rejected'];
      const taskCounts = {}; TASK_STAGES.forEach(s=>taskCounts[s]=0);
      const auditCounts = {}; AUDIT_STAGES.forEach(s=>auditCounts[s]=0);
      tasks.forEach(t=>{
        const ts = t.task_status || 'Completed';
        taskCounts[ts] = (taskCounts[ts]||0)+1;
        const as = t.audit_status || 'Ready to Audit';
        auditCounts[as] = (auditCounts[as]||0)+1;
      });
      const taskHtml = TASK_STAGES.map(s=>`<span class="pipeline-stage">${s} <span class="count">${taskCounts[s]||0}</span></span>`).join('<span class="pipeline-arrow">→</span>');
      const auditHtml = AUDIT_STAGES.map(s=>`<span class="pipeline-stage">${s} <span class="count">${auditCounts[s]||0}</span></span>`).join('<span class="pipeline-arrow">→</span>');
      el.innerHTML = '<div class="pipeline-row"><span class="pipeline-label">Task</span>'+taskHtml+'</div><div class="pipeline-row"><span class="pipeline-label">Audit</span>'+auditHtml+'</div>';
      el.style.display = 'block';
    }
    function renderQueryList() {
      const list = $('query-list');
      const grid = $('task-grid');
      const useGrid = admin && tasks.length > 5;
      list.style.display = useGrid ? 'none' : 'block';
      grid.style.display = useGrid ? 'block' : 'none';
      if (useGrid) {
        const ft = filteredTasks();
        const ftIdx = ft.map(t => tasks.indexOf(t));
        grid.innerHTML = ftIdx.map((origIdx) => {
          const t = tasks[origIdx];
          const qid = t.question_id || origIdx + 1;
          const preview = (t.question || '').slice(0, 80) + ((t.question || '').length > 80 ? '...' : '');
          const ts = t.task_status || 'Completed';
          const as = t.audit_status || 'Ready to Audit';
          const tsCls = taskBadgeClass(ts);
          const asCls = auditBadgeClass(as);
          return `<div class="task-card" data-idx="${origIdx}"><div class="task-card-header"><span class="task-card-title">Query ${qid}</span></div><div class="task-card-preview">${escapeHtml(preview)}</div><div class="task-card-badges"><span class="badge ${tsCls}">${escapeHtml(ts)}</span>${asCls ? `<span class="badge ${asCls}">${escapeHtml(as)}</span>` : ''}</div><button class="task-card-open" data-idx="${origIdx}">Open</button></div>`;
        }).join('');
        grid.querySelectorAll('.task-card').forEach(card => {
          const idx = parseInt(card.dataset.idx, 10);
          card.onclick = (e) => { if (!e.target.classList.contains('task-card-open') && !isNaN(idx)) openTaskFromGrid(idx); };
        });
        grid.querySelectorAll('.task-card-open').forEach(btn => {
          btn.onclick = (e) => { e.stopPropagation(); const idx = parseInt(btn.dataset.idx, 10); if (!isNaN(idx)) openTaskFromGrid(idx); };
        });
      } else {
        list.innerHTML = tasks.map((t, i) => {
          const qid = t.question_id || i + 1;
          const preview = (t.question || '').slice(0, 50) + ((t.question || '').length > 50 ? '...' : '');
          const ts = t.task_status || 'Completed';
          const as = t.audit_status || 'Ready to Audit';
          const tsCls = taskBadgeClass(ts);
          const asCls = auditBadgeClass(as);
          return `<div class="q-row" data-idx="${i}"><div style="flex:1;min-width:0;"><span style="font-weight:500;">Query ${qid}</span><span style="color:var(--fg-muted);margin-left:0.25rem;">${escapeHtml(preview)}</span></div><div style="display:flex;gap:0.375rem;flex-shrink:0;"><span class="badge ${tsCls}">${escapeHtml(ts)}</span>${asCls ? `<span class="badge ${asCls}">${escapeHtml(as)}</span>` : ''}<button class="fix-btn" data-idx="${i}" style="padding:0.25rem 0.5rem;font-size:0.75rem;">Open</button></div></div>`;
        }).join('');
        list.querySelectorAll('.q-row').forEach(row => {
          const idx = parseInt(row.dataset.idx, 10);
          row.onclick = () => { if (!isNaN(idx)) { openTaskFromGrid(idx); list.querySelectorAll('.q-row').forEach(r => r.classList.remove('fixed')); row.classList.add('fixed'); } };
        });
        list.querySelectorAll('.fix-btn').forEach(btn => {
          btn.onclick = (e) => { e.stopPropagation(); const idx = parseInt(btn.dataset.idx, 10); if (!isNaN(idx)) { openTaskFromGrid(idx); list.querySelectorAll('.q-row').forEach(r => r.classList.remove('fixed')); btn.closest('.q-row')?.classList.add('fixed'); } };
        });
      }
      const completed = tasks.filter(t => (t.task_status || '').toLowerCase().includes('completed')).length;
      const prog = $('task-progress');
      const progBar = $('task-progress-bar');
      const progFill = $('task-progress-fill');
      if (prog) prog.textContent = `${completed} / ${tasks.length} completed`;
      if (progBar) progBar.style.display = tasks.length ? 'block' : 'none';
      if (progFill && tasks.length) progFill.style.width = (100 * completed / tasks.length) + '%';
      renderPipelineTracker(tasks, 'pipeline-tracker');
    }

    document.querySelectorAll('input[name="mode"]').forEach(r => {
      r.onchange = () => {
        mode = r.value;
        $('json-row').style.display = isJsonMode() ? 'flex' : 'none';
        $('ls-row').style.display = isJsonMode() ? 'none' : 'flex';
        $('ls-seed-source-wrap').style.display = (admin && !isJsonMode()) ? 'block' : 'none';
        $('admin-fix-panel').style.display = 'none';
        if (isJsonMode()) { tasks = []; currentTask = null; $('form').style.display = 'none'; }
        else loadProjects().then(() => $('project').value && loadLsTasks());
      };
    });

    function filteredTasks() {
      const ts = $('filter-task-status')?.value || '';
      const as = $('filter-audit-status')?.value || '';
      if (!ts && !as) return tasks;
      return tasks.filter(t => {
        if (ts && (t.task_status || 'Completed') !== ts) return false;
        if (as && (t.audit_status || 'Ready to Audit') !== as) return false;
        return true;
      });
    }
    function refreshTaskSelect() {
      const ft = filteredTasks();
      const sel = $('task');
      const ftIdx = ft.map(t => tasks.indexOf(t));
      sel.innerHTML = ftIdx.map((origIdx) => {
        const t = tasks[origIdx];
        return `<option value="${origIdx}">Query ${t.question_id || origIdx+1}: ${(t.question || '').slice(0, 50)}...</option>`;
      }).join('') || '<option>No queries</option>';
      sel.disabled = !tasks.length;
      sel.onchange = showTask;
      if (ft.length) { sel.selectedIndex = 0; showTask(); }
      if (admin && tasks.length) renderQueryList();
    }
    $('filter-task-status').onchange = refreshTaskSelect;
    $('filter-audit-status').onchange = refreshTaskSelect;

    async function doLoadQueries() {
      const src = $('source').value;
      msg('Loading...');
      const data = await api('/queries?source=' + encodeURIComponent(src));
      if (data.error) { msg(data.error, 'err'); return; }
      tasks = data.queries || [];
      refreshTaskSelect();
      applyAdminState();
      if (admin && tasks.length) $('admin-fix-panel').style.display = 'block';
      if (tasks.length) msg('Loaded ' + tasks.length + ' queries', 'ok');
      else msg('No queries found', 'err');
    }
    $('load-json').onclick = doLoadQueries;
    $('source').onchange = () => { if (admin && isJsonMode() && $('source').value && $('source').value !== 'template') doLoadQueries(); };

    async function doExport(format) {
      const src = $('source').value;
      const url = '/api/export?source=' + encodeURIComponent(src) + '&format=' + format;
      try {
        const r = await fetch(url);
        if (!r.ok) { const e = await r.json().catch(() => ({})); msg(e.error || 'Export failed', 'err'); return; }
        const blob = await r.blob();
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = format === 'md' ? 'queries.md' : 'submissions_' + src.replace(/-/g, '_') + '.' + (format === 'csv' ? 'csv' : 'json');
        a.click();
        URL.revokeObjectURL(a.href);
        msg('Exported ' + src, 'ok');
      } catch (e) { msg(e.message || 'Export failed', 'err'); }
    }
    $('export-csv').onclick = () => doExport('csv');
    $('export-json').onclick = () => doExport('json');
    $('export-md').onclick = () => doExport('md');

    async function loadProjects() {
      const data = await api('/projects');
      const projects = data.projects || [];
      const sel = $('project');
      sel.innerHTML = projects.map(p => `<option value="${p.id}">${p.title || p.id}</option>`).join('') || '<option>No projects</option>';
      sel.disabled = false;
      sel.onchange = () => loadLsTasks();
      $('refresh').disabled = false;
      $('refresh').onclick = () => loadProjects().then(() => loadLsTasks());
      $('seed').onclick = async () => {
        const src = (admin && $('ls-seed-source')) ? $('ls-seed-source').value : 'template';
        $('seed').disabled = true;
        msg('Seeding project from ' + src + '...');
        const r = await api('/seed?source=' + encodeURIComponent(src), { method: 'POST' });
        $('seed').disabled = false;
        if (r.error) { msg(r.error, 'err'); return; }
        msg('Project created. Refreshing...', 'ok');
        await loadProjects();
        $('project').selectedIndex = 0;
        loadLsTasks();
      };
    }

    async function loadLsTasks() {
      const pid = $('project').value;
      if (!pid) return;
      const data = await api('/tasks?project=' + pid);
      tasks = data.tasks || [];
      const sel = $('ls-task');
      sel.innerHTML = tasks.map(t => `<option value="${t.id}">Task ${t.id} (q${(t.data && t.data.question_id) || '?'})</option>`).join('') || '<option>No tasks</option>';
      sel.disabled = false;
      sel.onchange = showLsTask;
      if (tasks.length) { sel.selectedIndex = 0; showLsTask(); }
    }

    function getTaskData(t) {
      if (isJsonMode() && typeof t === 'object') return t;
      return (t && t.data) || {};
    }

    function showTask() {
      const idx = parseInt($('task').value, 10);
      currentTask = tasks[idx];
      if (currentTask == null) { $('form').style.display = 'none'; return; }
      const d = getTaskData(currentTask);
      const tables = d.tables_used;
      $('question').value = d.question || '';
      $('sql').value = d.SQL || d.sql || '';
      $('evidence').value = d.evidence || '';
      $('difficulty').value = d.difficulty || 'moderate';
      $('query_category').value = d.query_category || '';
      $('tables_used').value = Array.isArray(tables) ? tables.join(', ') : (tables || '');
      $('expected_output').value = d.expected_output || '';
      $('task_status').value = d.task_status || 'Completed';
      $('audit_status').value = d.audit_status || 'Ready to Audit';
      $('actual_output').value = '';
      $('use-as-expected').disabled = true;
      const vs = $('validation-status');
      if (vs) { vs.style.display = 'none'; vs.textContent = ''; }
      $('form').style.display = 'block';
    }

    function showLsTask() {
      const tid = $('ls-task').value;
      currentTask = tasks.find(t => String(t.id) === tid);
      if (!currentTask) { $('form').style.display = 'none'; return; }
      showTask();
    }

    async function submit() {
      if (!currentTask) return;
      $('submit').disabled = true;
      msg('Submitting...');

      if (isJsonMode()) {
        const payload = {
          source: $('source').value,
          question_id: currentTask.question_id,
          question: $('question').value,
          SQL: $('sql').value,
          evidence: $('evidence').value,
          difficulty: $('difficulty').value,
          query_category: $('query_category').value,
          tables_used: $('tables_used').value.split(',').map(s => s.trim()).filter(Boolean),
          expected_output: $('expected_output').value,
          task_status: $('task_status').value,
          audit_status: $('audit_status').value
        };
        const result = await api('/annotate', { method: 'POST', body: JSON.stringify(payload) });
        $('submit').disabled = false;
        if (result.error) { msg(result.error, 'err'); return; }
        msg('Saved to queries.json', 'ok');
        const idx = tasks.findIndex(t => t === currentTask);
        if (idx >= 0 && idx < tasks.length - 1) { $('task').selectedIndex = idx + 1; showTask(); }
        return;
      }

      const result = await api('/tasks/' + currentTask.id + '/annotations', {
        method: 'POST',
        body: JSON.stringify({
          result: [
            { from_name: 'sql', to_name: 'question', type: 'textarea', value: { text: [$('sql').value] } },
            { from_name: 'evidence', to_name: 'question', type: 'textarea', value: { text: [$('evidence').value] } },
            { from_name: 'difficulty', to_name: 'question', type: 'choices', value: { choices: [$('difficulty').value] } }
          ],
          was_cancelled: false
        })
      });
      $('submit').disabled = false;
      if (result.error) { msg(result.error, 'err'); return; }
      msg('Annotation submitted.', 'ok');
      const idx = tasks.findIndex(t => String(t.id) === String(currentTask.id));
      if (idx >= 0 && idx < tasks.length - 1) { $('ls-task').selectedIndex = idx + 1; showLsTask(); }
    }

    $('next').onclick = () => {
      if (isJsonMode()) {
        const sel = $('task');
        if (sel.selectedIndex < tasks.length - 1) { sel.selectedIndex++; showTask(); }
        else msg('No more tasks.', '');
      } else {
        const sel = $('ls-task');
        if (sel.selectedIndex < tasks.length - 1) { sel.selectedIndex++; showLsTask(); }
        else msg('No more tasks.', '');
      }
    };

    $('submit').onclick = submit;

    $('validate-sql').onclick = async () => {
      const src = $('source').value;
      const sql = $('sql').value;
      const vs = $('validation-status');
      vs.style.display = 'none';
      if (!src || !sql) { msg('Select source and load a query first.', 'err'); return; }
      if (src === 'template') { msg('template has no database; use db-1..db-16.', 'err'); return; }
      $('validate-sql').disabled = true;
      msg('Validating against live database...');
      try {
        const r = await api('/execute', { method: 'POST', body: JSON.stringify({ source: src, sql }) });
        $('validate-sql').disabled = false;
        vs.style.display = 'block';
        if (r.error) {
          vs.className = 'validation-status invalid';
          vs.textContent = '✗ Invalid: ' + (r.error || 'Execution failed');
          msg('Validation failed', 'err');
        } else {
          vs.className = 'validation-status valid';
          vs.textContent = '✓ Valid — ' + (r.row_count ?? 0) + ' rows returned';
          msg('SQL validated successfully', 'ok');
        }
      } catch (e) {
        $('validate-sql').disabled = false;
        vs.style.display = 'block';
        vs.className = 'validation-status invalid';
        vs.textContent = '✗ Invalid: ' + (e.message || e);
        msg(e.message || e, 'err');
      }
    };

    $('run-query').onclick = async () => {
      const src = $('source').value;
      const sql = $('sql').value;
      if (!src || !sql) { msg('Select source and load a query first.', 'err'); return; }
      if (src === 'template') { msg('template has no database; use db-1..db-16.', 'err'); return; }
      $('run-query').disabled = true;
      msg('Running query...');
      try {
        const r = await api('/execute', { method: 'POST', body: JSON.stringify({ source: src, sql }) });
        $('run-query').disabled = false;
        if (r.error) { $('actual_output').value = 'Error: ' + r.error; msg(r.error, 'err'); return; }
        const str = JSON.stringify(r.rows || []);
        $('actual_output').value = str;
        $('use-as-expected').disabled = false;
        msg('Query returned ' + (r.row_count || 0) + ' rows.', 'ok');
      } catch (e) {
        $('run-query').disabled = false;
        $('actual_output').value = 'Error: ' + (e.message || e);
        msg(e.message || e, 'err');
      }
    };

    $('use-as-expected').onclick = () => {
      const v = $('actual_output').value.trim();
      if (v) { $('expected_output').value = v; msg('Copied to expected output.', 'ok'); }
    };

    (async function initAuthView() {
      const me = await fetch('/api/me').then(r=>r.json()).catch(()=>({}));
      const mode = me.mode || 'annotator';
      const canSwitch = !!me.canSwitchMode;
      const sel = document.getElementById('view-select');
      const modeWrap = document.getElementById('mode-selector-wrap');
      const modeSelect = document.getElementById('mode-select');
      if (modeWrap && modeSelect && canSwitch) {
        modeWrap.style.display = 'flex';
        modeSelect.value = mode;
        modeSelect.onchange = async () => {
          await fetch('/api/set-mode', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({mode: modeSelect.value}) });
          location.reload();
        };
      }
      if (sel && mode === 'annotator') {
        const adminPaths = ['/dashboard', '/suite', '/customer'];
        for (let i = sel.options.length - 1; i >= 0; i--) {
          if (adminPaths.includes(sel.options[i].value)) sel.remove(i);
        }
      }
      if (sel) {
        const p = window.location.pathname;
        const map = { '/':'/', '/index.html':'/', '/annotate':'/', '/admin':'/', '/dashboard':'/dashboard', '/staff':'/staff', '/admin/tasks':'/admin/tasks', '/suite':'/suite', '/customer':'/customer' };
        const v = map[p] || p;
        for (let i=0;i<sel.options.length;i++) { if (sel.options[i].value===v) { sel.selectedIndex=i; break; } }
      }
    })();
    (async () => {
      if (window.location.pathname === '/admin') { $('admin').checked = true; applyAdminState(); }
      await loadSources();
      const urlSource = new URLSearchParams(window.location.search).get('source');
      if (urlSource && Array.from($('source').options).some(o => o.value === urlSource)) { $('source').value = urlSource; }
      if (isJsonMode()) {
        if (admin) {
          if (!urlSource) {
            const db1 = Array.from($('source').options).find(o => o.value.startsWith('db-'));
            if (db1) { $('source').value = db1.value; }
          }
          await doLoadQueries();
          $('source').focus();
        } else await doLoadQueries();
      } else loadProjects().then(() => $('project').value && loadLsTasks());
    })();
  </script>
  </div>
</body>
</html>
"""

# Dedicated tasks page with accordion UI (separate page for task submissions)
TASKS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Task Board — 30 Queries</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f1419; --bg-card: #1a1f26; --bg-hover: #242b33;
      --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d;
      --accent: #3b82f6; --accent-hover: #2563eb;
      --success: #22c55e; --warning: #eab308; --error: #ef4444;
      --radius: 8px; --radius-sm: 6px; --shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 0; line-height: 1.5; font-size: 14px; }
    .app { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem 2rem; }
    .header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
    .header h1 { font-size: 1.125rem; font-weight: 600; margin: 0; }
    .header-sub { font-size: 0.8125rem; color: var(--fg-muted); margin-top: 0.25rem; }
    .header-sub a { color: var(--accent); text-decoration: none; }
    .header-sub a:hover { text-decoration: underline; }
    .row { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: flex-end; }
    select, button { padding: 0.5rem 0.875rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: var(--radius-sm); cursor: pointer; font-size: 0.875rem; font-family: inherit; }
    select:hover, button:hover:not(:disabled) { background: var(--bg-hover); border-color: var(--fg-muted); }
    button.primary { background: var(--accent); color: #fff; border-color: var(--accent); font-weight: 500; }
    button.primary:hover:not(:disabled) { background: var(--accent-hover); }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    label { display: block; font-size: 0.75rem; font-weight: 500; color: var(--fg-muted); margin-bottom: 0.375rem; text-transform: uppercase; letter-spacing: 0.04em; }
    textarea, input[type="text"] { width: 100%; padding: 0.625rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: var(--radius-sm); font-family: ui-monospace, monospace; font-size: 0.8125rem; }
    textarea:focus, input:focus { outline: none; border-color: var(--accent); }
    textarea { min-height: 100px; resize: vertical; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.25rem; margin-bottom: 1rem; box-shadow: var(--shadow); }
    .section-label { font-size: 0.6875rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .validation-status { padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; }
    .validation-status.valid { background: rgba(34,197,94,0.15); color: var(--success); border: 1px solid rgba(34,197,94,0.4); }
    .validation-status.invalid { background: rgba(239,68,68,0.15); color: var(--error); border: 1px solid rgba(239,68,68,0.4); }
    .badge { display: inline-flex; align-items: center; padding: 0.2rem 0.5rem; font-size: 0.6875rem; font-weight: 600; border-radius: 4px; text-transform: uppercase; }
    .badge-completed { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-progress { background: rgba(59,130,246,0.2); color: var(--accent); }
    .badge-queued { background: rgba(139,148,158,0.2); color: var(--fg-muted); }
    .badge-error { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-accepted { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-rejected { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-fixed { background: rgba(59,130,246,0.2); color: var(--accent); }
    .accordion { border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-card); overflow: hidden; }
    .accordion-item { border-bottom: 1px solid var(--border); }
    .accordion-item:last-child { border-bottom: none; }
    .accordion-header { display: flex; align-items: center; justify-content: space-between; padding: 0.875rem 1rem; cursor: pointer; transition: background 0.15s; }
    .accordion-header:hover { background: var(--bg-hover); }
    .accordion-header.open { background: rgba(59,130,246,0.08); border-left: 3px solid var(--accent); }
    .accordion-header-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
    .accordion-chevron { color: var(--fg-muted); font-size: 0.875rem; transition: transform 0.2s; flex-shrink: 0; }
    .accordion-item.open .accordion-chevron { transform: rotate(90deg); }
    .accordion-body { display: none; padding: 0 1rem 1rem; border-top: 1px solid var(--border); }
    .accordion-item.open .accordion-body { display: block; }
    .accordion-body-inner { padding-top: 1rem; }
    .pipeline-tracker { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.8125rem; }
    .pipeline-tracker .pipeline-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .pipeline-tracker .pipeline-row:last-child { margin-bottom: 0; }
    .pipeline-tracker .pipeline-label { color: var(--fg-muted); font-weight: 500; margin-right: 0.25rem; min-width: 4.5rem; }
    .pipeline-tracker .pipeline-stage { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(139,148,158,0.15); color: var(--fg); }
    .pipeline-tracker .pipeline-stage .count { font-weight: 600; color: var(--accent); }
    .pipeline-tracker .pipeline-arrow { color: var(--fg-muted); font-size: 0.7rem; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    #msg { font-size: 0.875rem; padding: 0.5rem 0; }
    #msg.err { color: var(--error); }
    #msg.ok { color: var(--success); }
  </style>
</head>
<body>
  <div class="app">
  <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
    <label for="mode-select">Mode</label>
    <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
  </div>
  <div class="view-selector">
    <label for="view-select">View</label>
    <select id="view-select" onchange="if(this.value) window.location.href=this.value">
      <option value="/staff">Staff</option>
      <option value="/">Annotator</option>
      <option value="/admin/tasks">Task Board</option>
      <option value="/dashboard">Dashboard</option>
      <option value="/suite">Full Suite</option>
      <option value="/customer">Customer Portal</option>
    </select>
  </div>
  <div class="header">
    <div>
      <h1>Task Board — 30 Queries</h1>
      <p class="header-sub"><a href="/dashboard">Dashboard</a> · <a href="/">Annotator</a> · <a href="/suite">Full Suite</a> · Independent task submissions, Accept/Fix/Reject</p>
    </div>
  </div>

  <div class="row">
    <div>
      <label>Database</label>
      <select id="source"><option value="template">Loading...</option></select>
    </div>
    <div style="align-self:flex-end;">
      <button id="load">Load 30 queries</button>
    </div>
  </div>

  <div id="accordion-wrap" style="display:none;">
    <div id="pipeline-tracker" class="pipeline-tracker" style="display:none;"></div>
    <div class="section-label">Select and expand a task to edit</div>
    <div id="accordion" class="accordion"></div>
  </div>

  <div id="form-container" style="display:none;">
    <div id="task-form" class="card" style="margin-top:1rem;">
      <div class="section-label">Annotation</div>
      <label>Question</label>
      <textarea id="question" rows="3"></textarea>
      <label>SQL</label>
      <textarea id="sql" rows="10"></textarea>
      <div class="row" style="margin-bottom:0.5rem;">
        <button id="validate-sql" type="button">Validate SQL</button>
        <button id="run-query" type="button">Run query</button>
        <button id="use-as-expected" type="button" disabled>Use as expected output</button>
      </div>
      <div id="validation-status" class="validation-status" style="display:none;"></div>
      <label>Actual output</label>
      <textarea id="actual_output" rows="3" readonly></textarea>
      <label>Expected output</label>
      <textarea id="expected_output" rows="2"></textarea>
      <div class="row" style="margin-top:1rem;">
        <div><label>Task Status</label><select id="task_status"><option value="Queued">Queued</option><option value="In Progress">In Progress</option><option value="Completed">Completed</option><option value="Error">Error</option></select></div>
        <div><label>Audit Status</label><select id="audit_status"><option value="Ready to Audit">Ready to Audit</option><option value="Accepted">Accepted</option><option value="Fixed">Fixed</option><option value="Rejected">Rejected</option></select></div>
      </div>
      <div style="margin-top:1rem;">
        <button class="primary" id="submit">Save (fix)</button>
      </div>
    </div>
  </div>

  <p id="msg"></p>

  <script>
    const api = (path, opts = {}) => fetch('/api' + path, { headers: { 'Content-Type': 'application/json' }, ...opts }).then(r => r.json());
    const $ = id => document.getElementById(id);
    const msg = (t, cls) => { const m = $('msg'); m.textContent = t; m.className = cls || ''; };

    let tasks = [], currentIdx = -1;

    function taskBadgeClass(s) {
      if (!s) return 'badge-queued';
      const v = (s + '').toLowerCase();
      if (v.includes('completed')) return 'badge-completed';
      if (v.includes('progress')) return 'badge-progress';
      if (v.includes('error')) return 'badge-error';
      return 'badge-queued';
    }
    function auditBadgeClass(s) {
      if (!s) return '';
      const v = (s + '').toLowerCase();
      if (v.includes('accepted')) return 'badge-accepted';
      if (v.includes('rejected')) return 'badge-rejected';
      if (v.includes('fixed')) return 'badge-fixed';
      return '';
    }
    function escapeHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

    function renderPipelineTracker(tasks, elId) {
      const el = document.getElementById(elId);
      if (!el || !tasks || !tasks.length) { if (el) el.style.display = 'none'; return; }
      const TASK_STAGES = ['Queued','In Progress','Completed','Error','Canceled','Redo'];
      const AUDIT_STAGES = ['Ready to Audit','Accepted','Fixed','Rejected'];
      const taskCounts = {}; TASK_STAGES.forEach(s=>taskCounts[s]=0);
      const auditCounts = {}; AUDIT_STAGES.forEach(s=>auditCounts[s]=0);
      tasks.forEach(t=>{
        const ts = t.task_status || 'Completed';
        taskCounts[ts] = (taskCounts[ts]||0)+1;
        const as = t.audit_status || 'Ready to Audit';
        auditCounts[as] = (auditCounts[as]||0)+1;
      });
      const taskHtml = TASK_STAGES.map(s=>'<span class="pipeline-stage">'+s+' <span class="count">'+(taskCounts[s]||0)+'</span></span>').join('<span class="pipeline-arrow">→</span>');
      const auditHtml = AUDIT_STAGES.map(s=>'<span class="pipeline-stage">'+s+' <span class="count">'+(auditCounts[s]||0)+'</span></span>').join('<span class="pipeline-arrow">→</span>');
      el.innerHTML = '<div class="pipeline-row"><span class="pipeline-label">Task</span>'+taskHtml+'</div><div class="pipeline-row"><span class="pipeline-label">Audit</span>'+auditHtml+'</div>';
      el.style.display = 'block';
    }

    async function loadSources() {
      const data = await api('/sources');
      const sources = data.sources || ['template'];
      $('source').innerHTML = sources.map(s => `<option value="${s}">${s}</option>`).join('');
    }

    async function doLoad() {
      const src = $('source').value;
      msg('Loading...');
      const data = await api('/queries?source=' + encodeURIComponent(src));
      if (data.error) { msg(data.error, 'err'); return; }
      tasks = data.queries || [];
      if (!tasks.length) { msg('No queries found', 'err'); return; }
      msg('Loaded ' + tasks.length + ' queries', 'ok');
      renderPipelineTracker(tasks, 'pipeline-tracker');
      renderAccordion();
      $('accordion-wrap').style.display = 'block';
      const db1 = Array.from($('source').options).find(o => o.value.startsWith('db-'));
      if (db1) $('source').value = db1.value;
    }

    function renderAccordion() {
      const acc = $('accordion');
      acc.innerHTML = tasks.map((t, i) => {
        const qid = t.question_id ?? i + 1;
        const preview = (t.question || '').slice(0, 60) + ((t.question || '').length > 60 ? '...' : '');
        const ts = t.task_status || 'Completed';
        const as = t.audit_status || 'Ready to Audit';
        return `<div class="accordion-item" data-idx="${i}">
          <div class="accordion-header">
            <div class="accordion-header-left">
              <span class="accordion-chevron">▶</span>
              <span style="font-weight:600;">Query ${qid}</span>
              <span style="color:var(--fg-muted);font-size:0.8125rem;">${escapeHtml(preview)}</span>
              <span class="badge badge-ts ${taskBadgeClass(ts)}">${escapeHtml(ts)}</span>
              <span class="badge badge-as ${auditBadgeClass(as) || 'badge-queued'}">${escapeHtml(as)}</span>
            </div>
          </div>
          <div class="accordion-body"><div class="accordion-body-inner" data-idx="${i}"></div></div>
        </div>`;
      }).join('');

      acc.querySelectorAll('.accordion-header').forEach(h => {
        h.onclick = () => {
          const item = h.closest('.accordion-item');
          const idx = parseInt(item.dataset.idx, 10);
          const wasOpen = item.classList.contains('open');
          acc.querySelectorAll('.accordion-item').forEach(it => it.classList.remove('open'));
          if (!wasOpen) {
            item.classList.add('open');
            currentIdx = idx;
            showFormInAccordion(idx);
          } else {
            currentIdx = -1;
            $('form-container').style.display = 'none';
          }
        };
      });
    }

    function showFormInAccordion(idx) {
      const t = tasks[idx];
      if (!t) return;
      $('question').value = t.question || '';
      $('sql').value = t.SQL || t.sql || '';
      $('expected_output').value = t.expected_output || '';
      $('task_status').value = t.task_status || 'Completed';
      $('audit_status').value = t.audit_status || 'Ready to Audit';
      $('actual_output').value = '';
      $('use-as-expected').disabled = true;
      const vs = $('validation-status');
      if (vs) { vs.style.display = 'none'; vs.textContent = ''; }

      const slot = document.querySelector(`.accordion-body-inner[data-idx="${idx}"]`);
      const form = $('form-container');
      if (slot) {
        slot.appendChild(form);
        form.style.display = 'block';
      }
    }

    async function submit() {
      if (currentIdx < 0) return;
      const t = tasks[currentIdx];
      $('submit').disabled = true;
      msg('Saving...');
      const payload = {
        source: $('source').value,
        question_id: t.question_id,
        question: $('question').value,
        SQL: $('sql').value,
        expected_output: $('expected_output').value,
        task_status: $('task_status').value,
        audit_status: $('audit_status').value
      };
      const result = await api('/annotate', { method: 'POST', body: JSON.stringify(payload) });
      $('submit').disabled = false;
      if (result.error) { msg(result.error, 'err'); return; }
      msg('Saved', 'ok');
      Object.assign(t, { question: payload.question, SQL: payload.SQL, expected_output: payload.expected_output, task_status: payload.task_status, audit_status: payload.audit_status });
      renderPipelineTracker(tasks, 'pipeline-tracker');
      const item = document.querySelector(`.accordion-item[data-idx="${currentIdx}"]`);
      if (item) {
        const tsBadge = item.querySelector('.badge-ts');
        const asBadge = item.querySelector('.badge-as');
        if (tsBadge) { tsBadge.textContent = payload.task_status; tsBadge.className = 'badge badge-ts ' + taskBadgeClass(payload.task_status); }
        if (asBadge) { asBadge.textContent = payload.audit_status; asBadge.className = 'badge badge-as ' + (auditBadgeClass(payload.audit_status) || 'badge-queued'); }
      }
    }

    $('load').onclick = doLoad;
    $('submit').onclick = submit;

    $('validate-sql').onclick = async () => {
      const src = $('source').value, sql = $('sql').value;
      const vs = $('validation-status');
      vs.style.display = 'none';
      if (!src || !sql || src === 'template') { msg('Select db-N and load queries.', 'err'); return; }
      $('validate-sql').disabled = true;
      try {
        const r = await api('/execute', { method: 'POST', body: JSON.stringify({ source: src, sql }) });
        $('validate-sql').disabled = false;
        vs.style.display = 'block';
        if (r.error) { vs.className = 'validation-status invalid'; vs.textContent = '✗ Invalid: ' + (r.error || 'Execution failed'); msg(r.error, 'err'); }
        else { vs.className = 'validation-status valid'; vs.textContent = '✓ Valid — ' + (r.row_count ?? 0) + ' rows'; msg('Valid', 'ok'); }
      } catch (e) {
        $('validate-sql').disabled = false;
        vs.style.display = 'block';
        vs.className = 'validation-status invalid';
        vs.textContent = '✗ Invalid: ' + (e.message || e);
        msg(e.message || e, 'err');
      }
    };

    $('run-query').onclick = async () => {
      const src = $('source').value, sql = $('sql').value;
      if (!src || !sql || src === 'template') { msg('Select db-N and load queries.', 'err'); return; }
      $('run-query').disabled = true;
      try {
        const r = await api('/execute', { method: 'POST', body: JSON.stringify({ source: src, sql }) });
        $('run-query').disabled = false;
        if (r.error) { $('actual_output').value = 'Error: ' + r.error; msg(r.error, 'err'); return; }
        $('actual_output').value = JSON.stringify(r.rows || []);
        $('use-as-expected').disabled = false;
        msg('Query returned ' + (r.row_count || 0) + ' rows.', 'ok');
      } catch (e) {
        $('run-query').disabled = false;
        $('actual_output').value = 'Error: ' + (e.message || e);
        msg(e.message || e, 'err');
      }
    };

    $('use-as-expected').onclick = () => {
      const v = $('actual_output').value.trim();
      if (v) { $('expected_output').value = v; msg('Copied to expected output.', 'ok'); }
    };

    (async function initAuthView(){const me=await fetch('/api/me').then(r=>r.json()).catch(()=>({}));const mode=me.mode||'annotator';const canSwitch=!!me.canSwitchMode;const sel=document.getElementById('view-select');const modeWrap=document.getElementById('mode-selector-wrap');const modeSelect=document.getElementById('mode-select');if(modeWrap&&modeSelect&&canSwitch){modeWrap.style.display='flex';modeSelect.value=mode;modeSelect.onchange=async()=>{await fetch('/api/set-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:modeSelect.value})});location.reload();}}if(sel&&mode==='annotator'){['/dashboard','/suite','/customer'].forEach(p=>{for(let i=sel.options.length-1;i>=0;i--)if(sel.options[i].value===p)sel.remove(i);});}if(sel){const p=window.location.pathname;const v={'/dashboard':'/dashboard','/staff':'/staff','/':'/','/admin/tasks':'/admin/tasks','/suite':'/suite','/customer':'/customer'}[p]||p;for(let i=0;i<sel.options.length;i++)if(sel.options[i].value===v){sel.selectedIndex=i;break;}}})();
    (async () => {
      await loadSources();
      const db1 = Array.from($('source').options).find(o => o.value.startsWith('db-'));
      if (db1) { $('source').value = db1.value; await doLoad(); }
    })();
  </script>
  </div>
</body>
</html>
"""

# Dashboard hub page
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard — SQL Annotator</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #0f1419; --bg-card: #1a1f26; --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d; --accent: #3b82f6; --radius: 8px; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 2rem; line-height: 1.5; }
    .container { max-width: 1000px; margin: 0 auto; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    .sub { color: var(--fg-muted); font-size: 0.9rem; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; text-decoration: none; color: inherit; display: block; transition: border-color 0.15s; }
    .card:hover { border-color: var(--accent); }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
    .card p { font-size: 0.8125rem; color: var(--fg-muted); margin: 0; }
    .nav { margin-bottom: 2rem; }
    .nav a { color: var(--accent); text-decoration: none; font-size: 0.875rem; margin-right: 1rem; }
    .nav a:hover { text-decoration: underline; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
  </style>
</head>
<body>
  <div class="container">
  <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
    <label for="mode-select">Mode</label>
    <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
  </div>
  <div class="view-selector">
    <label for="view-select">View</label>
    <select id="view-select" onchange="if(this.value) window.location.href=this.value">
      <option value="/staff">Staff</option>
      <option value="/">Annotator</option>
      <option value="/admin/tasks">Task Board</option>
      <option value="/dashboard">Dashboard</option>
      <option value="/suite">Full Suite</option>
      <option value="/customer">Customer Portal</option>
    </select>
  </div>
  <div class="nav">
    <a href="/staff">Staff</a>
    <a href="/">Annotator</a>
    <a href="/admin/tasks">Task Board</a>
    <a href="/suite">Full Suite</a>
    <a href="/customer">Customer Portal</a>
    <a href="/logout">Log out</a>
  </div>
  <h1>Dashboard</h1>
  <p class="sub">SQL annotation workbench — hub for annotator, task board, and database suite</p>
  <div class="grid">
    <a href="/staff" class="card">
      <h2>Staff</h2>
      <p>Internal tools for annotators — Annotator, Task Board, pipeline.</p>
    </a>
    <a href="/" class="card">
      <h2>Annotator</h2>
      <p>Load queries, annotate SQL, validate against live databases. queries.json mode and Label Studio.</p>
    </a>
    <a href="/admin/tasks" class="card">
      <h2>Task Board</h2>
      <p>30 independent task submissions. Accordion view, Accept/Fix/Reject workflow.</p>
    </a>
    <a href="/suite" class="card">
      <h2>Full Suite</h2>
      <p>All databases (db-1 through db-N). Documentation links and query counts.</p>
    </a>
    <a href="/customer" class="card">
      <h2>Customer Portal</h2>
      <p>Scale-style customer view: task filters, visualizations, export CSV/JSON.</p>
    </a>
  </div>
  </div>
  <script>(async function initAuthView(){const me=await fetch('/api/me').then(r=>r.json()).catch(()=>({}));const mode=me.mode||'annotator';const canSwitch=!!me.canSwitchMode;const sel=document.getElementById('view-select');const modeWrap=document.getElementById('mode-selector-wrap');const modeSelect=document.getElementById('mode-select');if(modeWrap&&modeSelect&&canSwitch){modeWrap.style.display='flex';modeSelect.value=mode;modeSelect.onchange=async()=>{await fetch('/api/set-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:modeSelect.value})});location.reload();}}if(sel&&mode==='annotator'){['/dashboard','/suite','/customer'].forEach(p=>{for(let i=sel.options.length-1;i>=0;i--)if(sel.options[i].value===p)sel.remove(i);});}if(sel){const p=window.location.pathname;const v={'/dashboard':'/dashboard','/staff':'/staff','/':'/','/admin/tasks':'/admin/tasks','/suite':'/suite','/customer':'/customer'}[p]||p;for(let i=0;i<sel.options.length;i++)if(sel.options[i].value===v){sel.selectedIndex=i;break;}}})();</script>
</body>
</html>
"""

# Staff hub page — internal annotator tools
STAFF_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Staff — SQL Annotator</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #0f1419; --bg-card: #1a1f26; --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d; --accent: #3b82f6; --radius: 8px; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 2rem; line-height: 1.5; }
    .container { max-width: 1000px; margin: 0 auto; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    .sub { color: var(--fg-muted); font-size: 0.9rem; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; text-decoration: none; color: inherit; display: block; transition: border-color 0.15s; }
    .card:hover { border-color: var(--accent); }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
    .card p { font-size: 0.8125rem; color: var(--fg-muted); margin: 0; }
    .nav { margin-bottom: 2rem; }
    .nav a { color: var(--accent); text-decoration: none; font-size: 0.875rem; margin-right: 1rem; }
    .nav a:hover { text-decoration: underline; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
  </style>
</head>
<body>
  <div class="container">
  <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
    <label for="mode-select">Mode</label>
    <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
  </div>
  <div class="view-selector">
    <label for="view-select">View</label>
    <select id="view-select" onchange="if(this.value) window.location.href=this.value">
      <option value="/staff">Staff</option>
      <option value="/">Annotator</option>
      <option value="/admin/tasks">Task Board</option>
      <option value="/dashboard">Dashboard</option>
      <option value="/suite">Full Suite</option>
      <option value="/customer">Customer Portal</option>
    </select>
  </div>
  <div class="nav">
    <a href="/">Annotator</a>
    <a href="/admin/tasks">Task Board</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/customer">Customer Portal</a>
  </div>
  <h1>Staff</h1>
  <p class="sub">Internal tools for annotators — workbench, task board, and pipeline</p>
  <div class="grid">
    <a href="/" class="card">
      <h2>Annotator</h2>
      <p>Load queries, annotate SQL, validate against live databases. queries.json mode and Label Studio.</p>
    </a>
    <a href="/admin/tasks" class="card">
      <h2>Task Board</h2>
      <p>30 independent task submissions. Accordion view, Accept/Fix/Reject workflow.</p>
    </a>
    <a href="/dashboard" class="card">
      <h2>Dashboard</h2>
      <p>Full hub — annotator, task board, suite, and customer portal.</p>
    </a>
  </div>
  </div>
  <script>(async function initAuthView(){const me=await fetch('/api/me').then(r=>r.json()).catch(()=>({}));const mode=me.mode||'annotator';const canSwitch=!!me.canSwitchMode;const sel=document.getElementById('view-select');const modeWrap=document.getElementById('mode-selector-wrap');const modeSelect=document.getElementById('mode-select');if(modeWrap&&modeSelect&&canSwitch){modeWrap.style.display='flex';modeSelect.value=mode;modeSelect.onchange=async()=>{await fetch('/api/set-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:modeSelect.value})});location.reload();}}if(sel&&mode==='annotator'){['/dashboard','/suite','/customer'].forEach(p=>{for(let i=sel.options.length-1;i>=0;i--)if(sel.options[i].value===p)sel.remove(i);});}if(sel){const p=window.location.pathname;const v={'/dashboard':'/dashboard','/staff':'/staff','/':'/','/admin/tasks':'/admin/tasks','/suite':'/suite','/customer':'/customer'}[p]||p;for(let i=0;i<sel.options.length;i++)if(sel.options[i].value===v){sel.selectedIndex=i;break;}}})();</script>
</body>
</html>
"""

# Full suite page — all databases
SUITE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Full Suite — All Databases</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root { --bg: #0f1419; --bg-card: #1a1f26; --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d; --accent: #3b82f6; --radius: 8px; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 2rem; line-height: 1.5; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    .sub { color: var(--fg-muted); font-size: 0.9rem; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; text-decoration: none; color: inherit; display: block; transition: border-color 0.15s; }
    .card:hover { border-color: var(--accent); }
    .card .id { display: inline-block; background: rgba(59,130,246,0.2); color: var(--accent); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
    .card p { font-size: 0.8125rem; color: var(--fg-muted); margin: 0; }
    .nav { margin-bottom: 2rem; }
    .nav a { color: var(--accent); text-decoration: none; font-size: 0.875rem; margin-right: 1rem; }
    .nav a:hover { text-decoration: underline; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    #loading { color: var(--fg-muted); }
  </style>
</head>
<body>
  <div class="container">
  <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
    <label for="mode-select">Mode</label>
    <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
  </div>
  <div class="view-selector">
    <label for="view-select">View</label>
    <select id="view-select" onchange="if(this.value) window.location.href=this.value">
      <option value="/staff">Staff</option>
      <option value="/">Annotator</option>
      <option value="/admin/tasks">Task Board</option>
      <option value="/dashboard">Dashboard</option>
      <option value="/suite">Full Suite</option>
      <option value="/customer">Customer Portal</option>
    </select>
  </div>
  <div class="nav">
    <a href="/dashboard">Dashboard</a>
    <a href="/">Annotator</a>
    <a href="/admin/tasks">Task Board</a>
    <a href="/customer">Customer Portal</a>
  </div>
  <h1>Full Suite</h1>
  <p class="sub">All databases with queries.json — production databases for annotation and validation</p>
  <div id="grid" class="grid"><span id="loading">Loading...</span></div>
  </div>
  <script>
    (async function initAuthView(){const me=await fetch('/api/me').then(r=>r.json()).catch(()=>({}));const mode=me.mode||'annotator';const canSwitch=!!me.canSwitchMode;const sel=document.getElementById('view-select');const modeWrap=document.getElementById('mode-selector-wrap');const modeSelect=document.getElementById('mode-select');if(modeWrap&&modeSelect&&canSwitch){modeWrap.style.display='flex';modeSelect.value=mode;modeSelect.onchange=async()=>{await fetch('/api/set-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:modeSelect.value})});location.reload();}}if(sel&&mode==='annotator'){['/dashboard','/suite','/customer'].forEach(p=>{for(let i=sel.options.length-1;i>=0;i--)if(sel.options[i].value===p)sel.remove(i);});}if(sel){const p=window.location.pathname;const v={'/dashboard':'/dashboard','/staff':'/staff','/':'/','/admin/tasks':'/admin/tasks','/suite':'/suite','/customer':'/customer'}[p]||p;for(let i=0;i<sel.options.length;i++)if(sel.options[i].value===v){sel.selectedIndex=i;break;}}})();
    const DB_NAMES = { "db-1":"Chat Messaging", "db-2":"Filling Station Retail", "db-3":"Hierarchical Orders", "db-4":"SharedAI Models", "db-5":"POS Retail", "db-6":"Weather Consulting", "db-7":"Maritime Shipping", "db-8":"Job Market", "db-9":"Shipping Intelligence", "db-10":"Marketing Intelligence", "db-11":"Parking Intelligence", "db-12":"Credit Card & Rewards", "db-13":"AI Benchmark", "db-14":"Cloud Instance Cost", "db-15":"Electricity & Solar", "db-16":"Flood Risk", "template":"Template" };
    fetch('/api/sources').then(r=>r.json()).then(d=>{
      const sources = (d.sources||[]).filter(s=>s!=='template');
      document.getElementById('loading').style.display='none';
      const grid = document.getElementById('grid');
      grid.innerHTML = sources.map(s=>{
        const name = DB_NAMES[s] || s;
        return '<a href="/customer?source='+encodeURIComponent(s)+'" class="card"><span class="id">'+s+'</span><h2>'+name+'</h2><p>30 queries · PostgreSQL</p></a>';
      }).join('') || '<p style="color:var(--fg-muted)">No databases found</p>';
    }).catch(()=>{ document.getElementById('loading').textContent='Failed to load'; });
  </script>
</body>
</html>
"""

# Customer-facing portal (Scale-style): filters, visualizations, export
CUSTOMER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Customer Portal — Task Overview</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root { --bg: #0f1419; --bg-card: #1a1f26; --fg: #e6edf3; --fg-muted: #8b949e; --border: #30363d; --accent: #3b82f6; --radius: 8px; --success: #22c55e; --warning: #eab308; --error: #ef4444; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--fg); margin: 0; padding: 2rem; line-height: 1.5; }
    .container { max-width: 1200px; margin: 0 auto; }
    .nav { margin-bottom: 2rem; }
    .nav a { color: var(--accent); text-decoration: none; font-size: 0.875rem; margin-right: 1rem; }
    .nav a:hover { text-decoration: underline; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    .sub { color: var(--fg-muted); font-size: 0.9rem; margin-bottom: 1.5rem; }
    .row { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: flex-end; }
    select, button { padding: 0.5rem 0.875rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; cursor: pointer; font-size: 0.875rem; font-family: inherit; }
    select:hover, button:hover:not(:disabled) { background: #242b33; border-color: var(--fg-muted); }
    button.primary { background: var(--accent); color: #fff; border-color: var(--accent); font-weight: 500; }
    button.primary:hover:not(:disabled) { background: #2563eb; }
    label { display: block; font-size: 0.7rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin-bottom: 0.25rem; }
    .viz-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .viz-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }
    .viz-card h3 { font-size: 0.8125rem; font-weight: 600; margin: 0 0 0.75rem 0; color: var(--fg-muted); }
    .viz-canvas { position: relative; height: 200px; }
    .task-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    .task-table th, .task-table td { padding: 0.625rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
    .task-table th { color: var(--fg-muted); font-weight: 500; }
    .task-table tr:hover { background: rgba(255,255,255,0.02); }
    .badge { display: inline-block; padding: 0.2rem 0.5rem; font-size: 0.6875rem; font-weight: 600; border-radius: 4px; }
    .badge-completed { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-progress { background: rgba(59,130,246,0.2); color: var(--accent); }
    .badge-queued { background: rgba(139,148,158,0.2); color: var(--fg-muted); }
    .badge-error { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-accepted { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-rejected { background: rgba(239,68,68,0.2); color: var(--error); }
    .badge-fixed { background: rgba(59,130,246,0.2); color: var(--accent); }
    .badge-audit { background: rgba(139,148,158,0.2); color: var(--fg-muted); }
    .table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: var(--radius); margin-top: 1rem; }
    #loading { color: var(--fg-muted); }
    .export-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
    .pipeline-tracker { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.8125rem; }
    .pipeline-tracker .pipeline-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .pipeline-tracker .pipeline-row:last-child { margin-bottom: 0; }
    .pipeline-tracker .pipeline-label { color: var(--fg-muted); font-weight: 500; margin-right: 0.25rem; min-width: 4.5rem; }
    .pipeline-tracker .pipeline-stage { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(139,148,158,0.15); color: var(--fg); }
    .pipeline-tracker .pipeline-stage .count { font-weight: 600; color: var(--accent); }
    .pipeline-tracker .pipeline-arrow { color: var(--fg-muted); font-size: 0.7rem; }
    .view-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--border); }
    .view-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
    .view-selector select { padding: 0.4rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; font-size: 0.875rem; cursor: pointer; }
    .view-selector select:hover { border-color: var(--accent); }
    .mode-selector { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
    .mode-selector label { font-size: 0.75rem; font-weight: 600; color: var(--fg-muted); text-transform: uppercase; margin: 0; }
  </style>
</head>
<body>
  <div class="container">
  <div id="mode-selector-wrap" class="mode-selector" style="display:none;">
    <label for="mode-select">Mode</label>
    <select id="mode-select"><option value="annotator">Annotator</option><option value="admin">Admin</option></select>
  </div>
  <div class="view-selector">
    <label for="view-select">View</label>
    <select id="view-select" onchange="if(this.value) window.location.href=this.value">
      <option value="/staff">Staff</option>
      <option value="/">Annotator</option>
      <option value="/admin/tasks">Task Board</option>
      <option value="/dashboard">Dashboard</option>
      <option value="/suite">Full Suite</option>
      <option value="/customer">Customer Portal</option>
    </select>
  </div>
  <div class="nav">
    <a href="/dashboard">Dashboard</a>
    <a href="/suite">Full Suite</a>
    <a href="/logout">Log out</a>
  </div>
  <h1>Customer Portal</h1>
  <p class="sub">Task overview, visualizations, and export — Scale-style customer view</p>

  <div class="row">
    <div>
      <label>Database</label>
      <select id="source"><option value="template">Loading...</option></select>
    </div>
    <div>
      <label>Task Status</label>
      <select id="filter-task"><option value="">All</option><option value="Completed">Completed</option><option value="In Progress">In Progress</option><option value="Queued">Queued</option><option value="Error">Error</option><option value="Canceled">Canceled</option><option value="Redo">Redo</option></select>
    </div>
    <div>
      <label>Audit Status</label>
      <select id="filter-audit"><option value="">All</option><option value="Ready to Audit">Ready to Audit</option><option value="Accepted">Accepted</option><option value="Fixed">Fixed</option><option value="Rejected">Rejected</option></select>
    </div>
    <div style="align-self:flex-end;">
      <button id="load">Load tasks</button>
    </div>
  </div>

  <div class="export-row">
    <button class="primary" id="export-csv">Export CSV</button>
    <button class="primary" id="export-json">Export JSON</button>
  </div>

  <div id="pipeline-tracker" class="pipeline-tracker" style="display:none;"></div>

  <div id="viz-section" style="display:none;">
    <div class="viz-row">
      <div class="viz-card">
        <h3>Task Status</h3>
        <div class="viz-canvas"><canvas id="chart-task"></canvas></div>
      </div>
      <div class="viz-card">
        <h3>Audit Status</h3>
        <div class="viz-canvas"><canvas id="chart-audit"></canvas></div>
      </div>
      <div class="viz-card">
        <h3>Completion Progress</h3>
        <div class="viz-canvas"><canvas id="chart-progress"></canvas></div>
      </div>
    </div>
  </div>

  <div id="table-section" style="display:none;">
    <h3 style="font-size:0.9375rem;margin-bottom:0.5rem;">Tasks</h3>
    <div class="table-wrap">
      <table class="task-table" id="task-table"></table>
    </div>
  </div>

  <p id="loading">Select database and click Load tasks.</p>
  </div>

  <script>
    const api = (path, opts) => fetch('/api' + path, { headers: { 'Content-Type': 'application/json' }, ...opts }).then(r => r.json());
    const $ = id => document.getElementById(id);
    let tasks = [];
    let chartTask = null, chartAudit = null, chartProgress = null;

    function badgeClass(s, type) {
      const v = (s||'').toLowerCase();
      if (type === 'task') {
        if (v.includes('completed')) return 'badge-completed';
        if (v.includes('progress')) return 'badge-progress';
        if (v.includes('error')) return 'badge-error';
        return 'badge-queued';
      }
      if (v.includes('accepted')) return 'badge-accepted';
      if (v.includes('rejected')) return 'badge-rejected';
      if (v.includes('fixed')) return 'badge-fixed';
      return 'badge-audit';
    }

    async function loadSources() {
      const d = await api('/sources');
      const src = d.sources || ['template'];
      $('source').innerHTML = src.map(s => '<option value="'+s+'">'+s+'</option>').join('');
    }

    function filtered() {
      const ft = $('filter-task').value, fa = $('filter-audit').value;
      if (!ft && !fa) return tasks;
      return tasks.filter(t => {
        if (ft && (t.task_status || 'Completed') !== ft) return false;
        if (fa && (t.audit_status || 'Ready to Audit') !== fa) return false;
        return true;
      });
    }

    function renderPipelineTracker() {
      const ft = filtered();
      const el = $('pipeline-tracker');
      if (!el || !tasks.length) { if (el) el.style.display = 'none'; return; }
      const TASK_STAGES = ['Queued','In Progress','Completed','Error','Canceled','Redo'];
      const AUDIT_STAGES = ['Ready to Audit','Accepted','Fixed','Rejected'];
      const taskCounts = {}; TASK_STAGES.forEach(s=>taskCounts[s]=0);
      const auditCounts = {}; AUDIT_STAGES.forEach(s=>auditCounts[s]=0);
      ft.forEach(t=>{
        const ts = t.task_status || 'Completed';
        taskCounts[ts] = (taskCounts[ts]||0)+1;
        const as = t.audit_status || 'Ready to Audit';
        auditCounts[as] = (auditCounts[as]||0)+1;
      });
      const taskHtml = TASK_STAGES.map(s=>'<span class="pipeline-stage">'+s+' <span class="count">'+(taskCounts[s]||0)+'</span></span>').join('<span class="pipeline-arrow">→</span>');
      const auditHtml = AUDIT_STAGES.map(s=>'<span class="pipeline-stage">'+s+' <span class="count">'+(auditCounts[s]||0)+'</span></span>').join('<span class="pipeline-arrow">→</span>');
      el.innerHTML = '<div class="pipeline-row"><span class="pipeline-label">Task</span>'+taskHtml+'</div><div class="pipeline-row"><span class="pipeline-label">Audit</span>'+auditHtml+'</div>';
      el.style.display = 'block';
    }

    function renderCharts() {
      const ft = filtered();
      const taskCounts = {}; const auditCounts = {};
      ft.forEach(t => {
        const ts = t.task_status || 'Completed';
        taskCounts[ts] = (taskCounts[ts]||0) + 1;
        const as = t.audit_status || 'Ready to Audit';
        auditCounts[as] = (auditCounts[as]||0) + 1;
      });
      const colors = { Completed:'#22c55e', 'In Progress':'#3b82f6', Queued:'#8b949e', Error:'#ef4444', Accepted:'#22c55e', Rejected:'#ef4444', Fixed:'#3b82f6', 'Ready to Audit':'#8b949e' };
      if (chartTask) chartTask.destroy();
      if (chartAudit) chartAudit.destroy();
      if (chartProgress) chartProgress.destroy();
      chartTask = new Chart($('chart-task'), { type: 'doughnut', data: { labels: Object.keys(taskCounts), datasets: [{ data: Object.values(taskCounts), backgroundColor: Object.keys(taskCounts).map(k=>colors[k]||'#6b7280') }] }, options: { responsive: true, maintainAspectRatio: false } });
      chartAudit = new Chart($('chart-audit'), { type: 'doughnut', data: { labels: Object.keys(auditCounts), datasets: [{ data: Object.values(auditCounts), backgroundColor: Object.keys(auditCounts).map(k=>colors[k]||'#6b7280') }] }, options: { responsive: true, maintainAspectRatio: false } });
      const completed = ft.filter(t=>(t.task_status||'').toLowerCase().includes('completed')).length;
      const total = ft.length;
      chartProgress = new Chart($('chart-progress'), { type: 'bar', data: { labels: ['Completed','Remaining'], datasets: [{ data: [completed, Math.max(0,total-completed)], backgroundColor: ['#22c55e','#3b82f6'] }] }, options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { max: total } } } });
    }

    function renderTable() {
      const ft = filtered();
      const html = '<thead><tr><th>Query</th><th>Question</th><th>Task Status</th><th>Audit Status</th></tr></thead><tbody>' +
        ft.map(t => {
          const qid = t.question_id ?? '?';
          const q = (t.question||'').slice(0, 60) + ((t.question||'').length > 60 ? '...' : '');
          const ts = t.task_status || 'Completed';
          const as = t.audit_status || 'Ready to Audit';
          const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
          return '<tr><td>Query '+qid+'</td><td>'+esc(q)+'</td><td><span class="badge '+badgeClass(ts,'task')+'">'+esc(ts)+'</span></td><td><span class="badge '+badgeClass(as,'audit')+'">'+esc(as)+'</span></td></tr>';
        }).join('') + '</tbody>';
      $('task-table').innerHTML = html;
    }

    async function doLoad() {
      const src = $('source').value;
      $('loading').textContent = 'Loading...';
      const d = await api('/queries?source=' + encodeURIComponent(src));
      if (d.error) { $('loading').textContent = d.error; return; }
      tasks = d.queries || [];
      $('loading').style.display = 'none';
      $('viz-section').style.display = 'block';
      $('table-section').style.display = 'block';
      const refresh = () => { renderPipelineTracker(); renderCharts(); renderTable(); };
      refresh();
      $('filter-task').onchange = refresh;
      $('filter-audit').onchange = refresh;
    }

    function doExport(format) {
      const src = $('source').value;
      if (!src) return;
      window.location.href = '/api/export?source=' + encodeURIComponent(src) + '&format=' + format;
    }

    $('load').onclick = doLoad;
    $('export-csv').onclick = () => doExport('csv');
    $('export-json').onclick = () => doExport('json');

    (async function initAuthView(){const me=await fetch('/api/me').then(r=>r.json()).catch(()=>({}));const mode=me.mode||'annotator';const canSwitch=!!me.canSwitchMode;const sel=document.getElementById('view-select');const modeWrap=document.getElementById('mode-selector-wrap');const modeSelect=document.getElementById('mode-select');if(modeWrap&&modeSelect&&canSwitch){modeWrap.style.display='flex';modeSelect.value=mode;modeSelect.onchange=async()=>{await fetch('/api/set-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:modeSelect.value})});location.reload();}}if(sel&&mode==='annotator'){['/dashboard','/suite','/customer'].forEach(p=>{for(let i=sel.options.length-1;i>=0;i--)if(sel.options[i].value===p)sel.remove(i);});}if(sel){const p=window.location.pathname;const v={'/dashboard':'/dashboard','/staff':'/staff','/':'/','/admin/tasks':'/admin/tasks','/suite':'/suite','/customer':'/customer'}[p]||p;for(let i=0;i<sel.options.length;i++)if(sel.options[i].value===v){sel.selectedIndex=i;break;}}})();
    (async () => {
      await loadSources();
      const urlSource = new URLSearchParams(window.location.search).get('source');
      if (urlSource && Array.from($('source').options).some(o => o.value === urlSource)) {
        $('source').value = urlSource;
        await doLoad();
      } else {
        const db1 = Array.from($('source').options).find(o => o.value.startsWith('db-'));
        if (db1) $('source').value = db1.value;
      }
    })();
  </script>
</body>
</html>
"""


def _discover_database_sources() -> list[str]:
    """Discover all databases with queries.json in source/ and template."""
    sources = ["template"]
    source_dir = Path(root_dir) / "source"
    if not source_dir.exists():
        return sources
    def _db_sort_key(p):
        if not p.name.startswith("db-"):
            return (1, p.name)
        try:
            n = int(p.name.replace("db-", ""))
            return (0, n)
        except ValueError:
            return (0, 999)
    for d in sorted(source_dir.iterdir(), key=_db_sort_key):
        if not d.is_dir() or not d.name.startswith("db-"):
            continue
        for base in ["app/QUERIES", "QUERIES"]:
            if (d / base / "queries.json").exists():
                sources.append(d.name)
                break
        else:
            if (Path(root_dir) / d.name / "queries" / "queries.json").exists():
                sources.append(d.name)
    return sources


def _get_queries_json_path(source: str) -> Path | None:
    """Resolve queries.json path for source (template, db-1, db-2, ...)."""
    if source.lower() == "template":
        return Path(root_dir) / "template" / "queries.json"
    db_num = source.replace("db-", "").strip()
    try:
        n = int(db_num)
    except ValueError:
        return None
    for base in ["app/QUERIES", "QUERIES"]:
        p = Path(root_dir) / "source" / f"db-{n}" / base / "queries.json"
        if p.exists():
            return p
    p = Path(root_dir) / f"db-{n}" / "queries" / "queries.json"
    if p.exists():
        return p
    return None


def _get_queries_md_path(source: str) -> Path | None:
    """Resolve queries.md path for source (same dir as queries.json)."""
    jp = _get_queries_json_path(source)
    if not jp:
        return None
    return jp.parent / "queries.md"


def _queries_to_md(queries: list[dict], source: str) -> str:
    """Convert queries list to queries.md format (template style). Preserves preamble if queries.md exists."""
    def _render_queries_section():
        lines = ["## Queries\n"]
        for q in queries:
            n = q.get("question_id", q.get("number", 0))
            diff = q.get("difficulty", "moderate")
            cat = q.get("query_category", "aggregation")
            lines.append(f"### Query {n} — {diff} / {cat}\n")
            out = {
                "db_id": q.get("db_id", source),
                "question_id": n,
                "question": q.get("question", ""),
                "SQL": q.get("SQL", q.get("sql", "")),
                "evidence": q.get("evidence", ""),
                "difficulty": diff,
                "query_category": cat,
                "tables_used": q.get("tables_used", []),
                "schema_context": q.get("schema_context", {}),
                "expected_output": q.get("expected_output", ""),
            }
            lines.append("```json")
            lines.append(json.dumps(out, indent=2, ensure_ascii=False))
            lines.append("```\n")
        return "\n".join(lines)

    md_path = _get_queries_md_path(source)
    if md_path and md_path.exists():
        content = md_path.read_text(encoding="utf-8")
        if "## Queries" in content:
            preamble = content.split("## Queries", 1)[0].rstrip()
            return preamble + "\n\n" + _render_queries_section()
    try:
        from queries_md_template_formatter import format_queries_md_template
        return format_queries_md_template(queries, db_id=source, db_name=f"{source} — Query Documentation")
    except ImportError:
        return f"# {source} — Query Documentation\n\n" + _render_queries_section()


def _execute_query_locally(source: str, sql: str, limit: int = 100) -> tuple[list[list], str | None]:
    """Execute SQL against local PostgreSQL. Returns (rows as list of lists, error)."""
    if not PG_AVAILABLE:
        return [], "psycopg2 not installed"
    if source.lower() == "template":
        return [], "template has no database; use db-1..db-16 for execution"
    db_num = source.replace("db-", "").strip()
    try:
        n = int(db_num)
    except ValueError:
        return [], f"Invalid source: {source}"
    db_name = f"db{n}"
    base_port = os.environ.get("PG_BASE_PORT")
    if base_port:
        port = int(base_port) + n - 1
    else:
        port = int(os.environ.get("PG_PORT", "5432"))
    try:
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            port=port,
            database=db_name,
            user=os.environ.get("PG_USER") or os.environ.get("USER") or "postgres",
            password=os.environ.get("PG_PASSWORD", ""),
        )
    except Exception as e:
        return [], f"Connection failed: {e}"
    q = sql.strip().rstrip(";")
    # Only add LIMIT if query doesn't already have one (handles \nLIMIT 100, LIMIT 100, etc.)
    if not re.search(r"\bLIMIT\s+\d+\s*$", q, re.IGNORECASE):
        q = f"{q} LIMIT {limit}"
    try:
        with conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
        conn.close()
        out = [[str(c) if c is not None else "" for c in row] for row in rows]
        return out, None
    except Exception as e:
        conn.close()
        return [], str(e)[:500]


def _load_queries_from_json(source: str) -> tuple[list[dict], str | None]:
    """Load query items from queries.json. Returns (queries, error)."""
    path = _get_queries_json_path(source)
    if not path or not path.exists():
        return [], f"Not found: {source}"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        queries = [x for x in data if isinstance(x, dict) and "question_id" in x]
    else:
        queries = data.get("queries", data.get("data", {}).get("queries", []))
    return queries, None


def _parse_cookies(header: str) -> dict:
    out = {}
    for part in (header or "").split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            out[k.strip()] = v.strip()
    return out


class AnnotatorHandler(BaseHTTPRequestHandler):
    def _check_auth(self):
        """Returns (username, None) on success, or (None, True) if redirect to login was sent."""
        cookies = _parse_cookies(self.headers.get("Cookie", ""))
        sid = cookies.get(SESSION_COOKIE)
        if not sid or sid not in SESSIONS:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return None, True
        sess = SESSIONS[sid]
        if sess["expires"] < time.time():
            del SESSIONS[sid]
            self.send_response(302)
            self.send_header("Location", "/login?err=Session+expired")
            self.end_headers()
            return None, True
        return sess["user"], None

    def _get_view_mode(self) -> str:
        """Staff can have annotator|admin. Annotator role always annotator."""
        cookies = _parse_cookies(self.headers.get("Cookie", ""))
        return cookies.get("view_mode", "annotator")

    def _annotator_forbidden(self, path: str, user: str, view_mode: str) -> bool:
        """True if not allowed: annotator role or staff in annotator mode cannot access admin-only paths."""
        if user == "staff" and view_mode == "admin":
            return False
        if path == "/customer":
            return True
        if path.startswith("/api/export"):
            return True
        if path == "/dashboard" or path == "/suite":
            return True
        return False

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode("utf-8"))
            return
        if parsed.path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly")
            self.send_header("Set-Cookie", "view_mode=; Path=/; Max-Age=0")
            self.end_headers()
            return
        user, sent_redirect = self._check_auth()
        if sent_redirect:
            return
        view_mode = self._get_view_mode()
        if self._annotator_forbidden(parsed.path, user, view_mode):
            self.send_response(403)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Forbidden: annotator cannot access this page")
            return
        def _send_html(body):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        if parsed.path in ("/", "/index.html", "/annotate", "/admin"):
            _send_html(HTML)
            return
        if parsed.path == "/admin/tasks":
            _send_html(TASKS_HTML)
            return
        if parsed.path == "/dashboard":
            _send_html(DASHBOARD_HTML)
            return
        if parsed.path == "/staff":
            _send_html(STAFF_HTML)
            return
        if parsed.path == "/suite":
            _send_html(SUITE_HTML)
            return
        if parsed.path == "/customer":
            _send_html(CUSTOMER_HTML)
            return
        if parsed.path.startswith("/api/"):
            if parsed.path == "/api/me":
                mode = self._get_view_mode()
                self._json({
                    "user": user,
                    "role": user,
                    "mode": mode,
                    "canSwitchMode": user == "staff",
                })
                return
            self._handle_api_get(parsed)
            return
        self.send_response(404)
        self.end_headers()

    def _handle_api_get(self, parsed):
        path = parsed.path[len("/api"):]
        qs = parse_qs(parsed.query)
        try:
            if path == "/sources":
                sources = _discover_database_sources()
                self._json({"sources": sources})
                return
            if path == "/queries" and "source" in qs:
                source = qs["source"][0]
                queries, err = _load_queries_from_json(source)
                if err:
                    self._json({"error": err}, 404)
                    return
                self._json({"queries": queries})
                return
            if path == "/export" and "source" in qs:
                source = qs["source"][0]
                fmt = (qs.get("format") or ["csv"])[0]
                queries, err = _load_queries_from_json(source)
                if err:
                    self._json({"error": err}, 404)
                    return
                if fmt == "json":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Disposition", f'attachment; filename="submissions_{source.replace("-", "_")}.json"')
                    self.end_headers()
                    self.wfile.write(json.dumps({"queries": queries}, indent=2, ensure_ascii=False).encode("utf-8"))
                    return
                if fmt == "md":
                    md_content = _queries_to_md(queries, source)
                    md_path = _get_queries_md_path(source)
                    if md_path and source.lower().startswith("db-"):
                        try:
                            md_path.write_text(md_content, encoding="utf-8")
                        except Exception:
                            pass
                    self.send_response(200)
                    self.send_header("Content-Type", "text/markdown")
                    self.send_header("Content-Disposition", f'attachment; filename="queries.md"')
                    self.end_headers()
                    self.wfile.write(md_content.encode("utf-8"))
                    return
                # CSV (Excel sheet structure)
                EXCEL_COLUMNS = [
                    "question_id", "db_id", "question", "SQL", "evidence", "difficulty",
                    "query_category", "tables_used", "expected_output",
                    "task_status", "audit_status", "created_at", "updated_at",
                ]
                def row_from_query(q):
                    tables = q.get("tables_used", [])
                    tables_str = ", ".join(tables) if isinstance(tables, list) else str(tables)
                    return {
                        "question_id": q.get("question_id", ""),
                        "db_id": q.get("db_id", source),
                        "question": q.get("question", ""),
                        "SQL": q.get("SQL", q.get("sql", "")),
                        "evidence": q.get("evidence", ""),
                        "difficulty": q.get("difficulty", ""),
                        "query_category": q.get("query_category", ""),
                        "tables_used": tables_str,
                        "expected_output": q.get("expected_output", ""),
                        "task_status": q.get("task_status", "Completed"),
                        "audit_status": q.get("audit_status", "Ready to Audit"),
                        "created_at": q.get("created_at", ""),
                        "updated_at": q.get("updated_at", ""),
                    }
                buf = io.StringIO()
                w = csv.DictWriter(buf, fieldnames=EXCEL_COLUMNS, extrasaction="ignore")
                w.writeheader()
                for q in queries:
                    w.writerow(row_from_query(q))
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", f'attachment; filename="submissions_{source.replace("-", "_")}.csv"')
                self.end_headers()
                self.wfile.write(buf.getvalue().encode("utf-8"))
                return
            if path == "/projects":
                status, data = _ls_request("GET", "/api/projects/")
                if status not in (200, 201):
                    self._json({"error": data.get("error", data)}, 500)
                    return
                projects = data if isinstance(data, list) else data.get("results", data.get("data", []))
                self._json({"projects": projects})
                return
            if path == "/tasks" and "project" in qs:
                pid = qs["project"][0]
                status, data = _ls_request("GET", f"/api/tasks/?project={pid}")
                if status not in (200, 201):
                    self._json({"error": data.get("error", data)}, 500)
                    return
                task_list = data.get("tasks", data.get("data", []))
                self._json({"tasks": task_list})
                return
        except Exception as e:
            self._json({"error": str(e)[:200]}, 500)
            return
        self._json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/login":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                form = parse_qs(body)
            except Exception:
                self.send_response(302)
                self.send_header("Location", "/login?err=Invalid+request")
                self.end_headers()
                return
            user = (form.get("user") or [""])[0].strip()
            pw = (form.get("password") or [""])[0]
            stay = (form.get("stay") or [""])[0] == "1"
            if user not in USER_CREDENTIALS or USER_CREDENTIALS[user] != pw:
                self.send_response(302)
                self.send_header("Location", "/login?err=Invalid+username+or+password")
                self.end_headers()
                return
            sid = secrets.token_urlsafe(32)
            max_age = SESSION_DAYS * 86400 if stay else 86400
            SESSIONS[sid] = {"user": user, "expires": time.time() + max_age}
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}={sid}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Lax")
            self.end_headers()
            return
        if parsed.path == "/api/set-mode":
            user, sent_redirect = self._check_auth()
            if sent_redirect:
                return
            if user != "staff":
                self._json({"error": "Only staff can set mode"}, 403)
                return
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body) if body else {}
            except Exception:
                self._json({"error": "Invalid JSON"}, 400)
                return
            mode = (payload.get("mode") or "annotator").lower()
            if mode not in ("annotator", "admin"):
                mode = "annotator"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", f"view_mode={mode}; Path=/; Max-Age=2592000; SameSite=Lax")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "mode": mode}).encode("utf-8"))
            return
        user, sent_redirect = self._check_auth()
        if sent_redirect:
            return
        if parsed.path == "/api/annotate":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body) if body else {}
            except Exception as e:
                self._json({"error": str(e)[:200]}, 400)
                return
            source = payload.get("source")
            question_id = payload.get("question_id")
            if not source or question_id is None:
                self._json({"error": "source and question_id required"}, 400)
                return
            path = _get_queries_json_path(source)
            if not path or not path.exists():
                self._json({"error": f"Not found: {source}"}, 404)
                return
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                self._json({"error": str(e)[:200]}, 500)
                return
            if isinstance(data, list):
                queries = data
                idx = next((i for i, q in enumerate(queries) if isinstance(q, dict) and q.get("question_id") == question_id), -1)
            else:
                queries = list(data.get("queries", data.get("data", {}).get("queries", [])))
                idx = next((i for i, q in enumerate(queries) if isinstance(q, dict) and q.get("question_id") == question_id), -1)
            if idx < 0:
                self._json({"error": f"question_id {question_id} not found"}, 404)
                return
            q = queries[idx]
            q["question"] = payload.get("question", q.get("question", ""))
            q["SQL"] = payload.get("SQL", q.get("SQL", q.get("sql", "")))
            q["sql"] = q["SQL"]
            q["evidence"] = payload.get("evidence", q.get("evidence", ""))
            q["difficulty"] = payload.get("difficulty", q.get("difficulty", "moderate"))
            q["query_category"] = payload.get("query_category", q.get("query_category", ""))
            q["tables_used"] = payload.get("tables_used", q.get("tables_used", []))
            q["expected_output"] = payload.get("expected_output", q.get("expected_output", ""))
            if "task_status" in payload:
                q["task_status"] = payload["task_status"]
            if "audit_status" in payload:
                q["audit_status"] = payload["audit_status"]
            if isinstance(data, list):
                data = queries
            else:
                if "queries" in data:
                    data["queries"] = queries
                elif "data" in data and "queries" in data["data"]:
                    data["data"]["queries"] = queries
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            self._json({"ok": True})
            return
        if parsed.path == "/api/seed":
            qs = parse_qs(parsed.query)
            source = qs.get("source", ["template"])[0]
            try:
                from label_studio_adapter import export_tasks
            except ImportError:
                self._json({"error": "label_studio_adapter not found"}, 500)
                return
            tasks, err = export_tasks(source)
            if err or not tasks:
                self._json({"error": err or "No tasks"}, 500)
                return
            config_path = os.path.join(root_dir, "template", "label_studio_config.xml")
            config = ""
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    config = f.read()
            status, resp = _ls_request("POST", "/api/projects", {"title": f"db-workbench-{source}", "label_config": config})
            if status not in (200, 201) or "id" not in resp:
                self._json({"error": resp.get("error", resp)}, 500)
                return
            pid = resp["id"]
            status2, _ = _ls_request("POST", f"/api/projects/{pid}/import", tasks)
            if status2 not in (200, 201):
                self._json({"error": f"Import failed: {status2}"}, 500)
                return
            self._json({"ok": True, "project_id": pid})
            return
        if parsed.path.startswith("/api/tasks/") and "/annotations" in parsed.path:
            parts = parsed.path[len("/api"):].split("/")
            # /api/tasks/123/annotations
            if len(parts) >= 4 and parts[1] == "tasks" and parts[3] == "annotations":
                tid = parts[2]
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    payload = json.loads(body) if body else {}
                    status, data = _ls_request("POST", f"/api/tasks/{tid}/annotations", payload)
                    if status in (200, 201):
                        self._json({"ok": True})
                    else:
                        self._json({"error": data.get("error", data)}, status if status > 0 else 500)
                except Exception as e:
                    self._json({"error": str(e)[:200]}, 500)
                return
        if parsed.path == "/api/execute":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                payload = json.loads(body) if body else {}
                source = payload.get("source")
                sql = payload.get("sql") or payload.get("SQL", "")
                # #region agent log
                try:
                    import time
                    (Path(root_dir) / ".cursor").mkdir(parents=True, exist_ok=True)
                    with open(Path(root_dir) / ".cursor" / "debug.log", "a") as f:
                        f.write(json.dumps({"timestamp": int(time.time()*1000), "location": "annotator_app:execute:entry", "message": "execute", "data": {"source": source, "sql_len": len(sql or ""), "PG_AVAILABLE": PG_AVAILABLE}, "hypothesisId": "H1"}) + "\n")
                except Exception:
                    pass
                # #endregion
                if not source or not sql:
                    self._json({"error": "source and sql required"}, 400)
                    return
                rows, err = _execute_query_locally(source, sql)
                # #region agent log
                try:
                    import time
                    with open(Path(root_dir) / ".cursor" / "debug.log", "a") as f:
                        f.write(json.dumps({"timestamp": int(time.time()*1000), "location": "annotator_app:execute:result", "message": "execute_result", "data": {"err": (err or "")[:100], "row_count": len(rows) if not err else 0}, "hypothesisId": "H1"}) + "\n")
                except Exception:
                    pass
                # #endregion
                if err:
                    self._json({"error": err, "rows": []})
                    return
                self._json({"rows": rows, "row_count": len(rows)})
            except Exception as e:
                self._json({"error": str(e)[:200]}, 500)
            return
        self.send_response(404)
        self.end_headers()

    def _json(self, obj, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

    def log_message(self, format, *args):
        pass  # quiet


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Annotator app for Label Studio")
    ap.add_argument("--port", type=int, default=8766, help="Port (default 8766)")
    ap.add_argument("--host", default="0.0.0.0", help="Host (default 0.0.0.0 for all interfaces)")
    args = ap.parse_args()

    url = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
    print(f"Annotator app: http://localhost:{args.port}/ and http://localhost:{args.port}/annotate")
    print(f"  queries.json mode: Load/save directly (no Label Studio required)")
    if _get_api_key():
        print(f"  Label Studio: {url}")
    else:
        print(f"  Label Studio: set LABEL_STUDIO_API_KEY or LABEL_STUDIO_USER_TOKEN for LS mode")
    print("  Run on different ports for multiple annotators on one host.")
    HTTPServer((args.host, args.port), AnnotatorHandler).serve_forever()


if __name__ == "__main__":
    main()
