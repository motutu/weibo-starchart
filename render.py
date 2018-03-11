#!/usr/bin/env python3

import csv

import jinja2


STYLE_TEMPLATE = jinja2.Template('''\
{% if id -%}

{% if vertical_header -%}
#{{ id }} tr > td:nth-child(1) { background: #dbf1ff; font-weight: bold; }
#{{ id }} tr > td:nth-child(2n+3) { background: #e8e8e8; }
{% else -%}
#{{ id }} thead > tr { background: #dbf1ff; font-weight: bold; }
#{{ id }} tbody > tr:nth-child(even) { background: #e8e8e8; }
{% endif -%}

{% for rownum in highlighted_rows -%}
#{{ id }} tbody > tr:nth-child({{ rownum }}) > td { background: #addfff !important; }
{% endfor -%}

{% for rownum in thick_bordered_rows -%}
#{{ id }} tr:nth-child({{ rownum }}) > td { border-bottom: 3px solid #000; }
{% endfor -%}

{% endif -%}
''')

TABLE_TEMPLATE = jinja2.Template('''\
<table{% if id %} id="{{ id }}"{% endif %}>
  {% if header -%}
  <thead>
    <tr>
      {% for cell in header -%}
      <th>{{ cell }}</th>
      {% endfor -%}
    </tr>
  </thead>
  {% endif -%}
  <tbody>
    {% for row in body -%}
    {% if not cutoff_row or loop.index <= cutoff_row -%}
    <tr>
      {% for cell in row -%}
      <td>{{ cell }}</td>
      {% endfor -%}
    </tr>
    {% endif -%}
    {% endfor -%}
  </tbody>
</table>''')

HTML_TEMPLATE = jinja2.Template('''\
<!DOCTYPE html>
<html>
<head>
  <style>
    body { margin: 0; font: 16px Times, "Songti SC", serif; }
    table { border-collapse: collapse; margin: 20px; }
    table, th, td { border: 1px solid #bbb; }
    th, td { padding: 1px 5px; text-align: center; white-space: nowrap; }
    {% for style in styles -%}
    {{ style|indent(4) }}
    {% endfor -%}
  </style>
</head>
<body>
  {% for table in tables -%}
  {{ table|indent(2) }}
  {% endfor -%}
</body>
</html>
''')


def load_csv(csvfile):
    with open(csvfile, encoding='utf-8') as csvfile:
        return [row for row in csv.reader(csvfile)]


# entries are (id, csvfile, **style_opts) tuples.
def render_csvs(entries):
    style_html_list = []
    table_html_list = []
    for id_, csvfile, style_opts in entries:
        style_opts = style_opts or {}
        table = load_csv(csvfile)
        header = None if style_opts.get('vertical_header') else table[0]
        body = table if style_opts.get('vertical_header') else table[1:]
        style_html_list.append(STYLE_TEMPLATE.render(id=id_, **style_opts))
        table_html_list.append(TABLE_TEMPLATE.render(id=id_, header=header, body=body, **style_opts))
    return HTML_TEMPLATE.render(styles=style_html_list, tables=table_html_list)
