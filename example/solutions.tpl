{%- extends 'full.tpl' -%}

{%- block markdowncell scoped -%}
{%- if cell.metadata.written_answer -%}
<div class="cell border-box-sizing text_cell rendered">
{{ self.empty_in_prompt() }}
<div class="inner_cell" style="background-color: #beb; border: black solid 1px; -moz-border-radius: 10px; -webkit-border-radius: 10px; border-radius: 10px; -moz-box-shadow: 0px 0px 3px 3px #ccc; -webkit-box-shadow: 0px 0px 3px 3px #ccc; box-shadow: 0px 0px 3px 3px #ccc; padding: 1em">
<div class="text_cell_render border-box-sizing rendered_html">
{{ cell.source  | markdown2html | strip_files_prefix }}
</div>
</div>
</div>
{%- else -%}
{{ super() }}
{%- endif -%}
{%- endblock markdowncell -%}
