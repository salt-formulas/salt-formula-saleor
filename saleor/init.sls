{%- if pillar.saleor is defined %}
include:
{%- if pillar.saleor.server is defined %}
- saleor.server
{%- endif %}
{%- endif %}
