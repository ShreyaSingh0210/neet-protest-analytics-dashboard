from flask import Flask, render_template_string, send_from_directory, abort
import os
import pandas as pd
import config

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>NEET Protest Analytics</title>
<h1>NEET Protest Analytics Dashboard</h1>
<p>This small web app provides a quick preview of the dataset and links to the dashboard files stored in the repository.</p>
<h2>Dataset (preview)</h2>
{% if table_html %}
  {{ table_html|safe }}
{% else %}
  <p>No dataset found. Please place the CSV at <code>{{ data_path }}</code>.</p>
{% endif %}

<h2>Dashboard</h2>
<ul>
{% for f in dashboards %}
  <li><a href="/dashboard/{{ f }}">{{ f }}</a></li>
{% endfor %}
</ul>
"""


@app.route("/")
def index():
    data_path = config.DATA_FILE
    table_html = None
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
            # show a concise preview
            table_html = df.head(10).to_html(classes="table table-striped", index=False)
        except Exception:
            table_html = None

    dashboards = []
    if os.path.isdir(config.DASHBOARD_DIR):
        dashboards = [f for f in os.listdir(config.DASHBOARD_DIR) if os.path.isfile(os.path.join(config.DASHBOARD_DIR, f))]

    return render_template_string(TEMPLATE, table_html=table_html, data_path=data_path, dashboards=dashboards)


@app.route('/data')
def download_data():
    # Serve the dataset file if present
    data_path = config.DATA_FILE
    data_dir = os.path.dirname(data_path) or '.'
    filename = os.path.basename(data_path)
    if os.path.exists(data_path):
        return send_from_directory(data_dir, filename, as_attachment=True)
    abort(404)


@app.route('/dashboard/<path:filename>')
def get_dashboard(filename):
    # Serve dashboard files from the dashboard folder
    safe_dir = os.path.abspath(config.DASHBOARD_DIR)
    requested = os.path.abspath(os.path.join(safe_dir, filename))
    if not requested.startswith(safe_dir):
        abort(403)
    if os.path.exists(requested) and os.path.isfile(requested):
        return send_from_directory(config.DASHBOARD_DIR, filename, as_attachment=True)
    abort(404)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
