{%- from "saleor/map.jinja" import server with context %}
{%- if server.enabled %}

{%- if salt['pillar.get']('store_name', False) %}

{%- set store_name = salt['pillar.get']('store_name') %}
{%- set store = salt['pillar.get']('saleor:server:store:'+store_name) %}
{% include "saleor/server/_store.sls" %}

{%- elif salt['pillar.get']('store_names', False) is iterable %}

{%- for store_name in salt['pillar.get']('store_names') %}
{%- set store = salt['pillar.get']('saleor:server:store:'+store_name) %}
{% include "saleor/server/_store.sls" %}
{%- endfor %}

{%- else %}

{%- for store_name, store in server.get('store', {}).iteritems() %}
{% include "saleor/server/_store.sls" %}
{%- endfor %}

{%- endif %}

{%- endif %}
