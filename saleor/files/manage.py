#!/usr/bin/env python

{%- set store = salt['pillar.get']('saleor:server:store:'+store_name) %}

import os
import sys
from os.path import abspath, dirname, join, normpath

import django
from django.core.management import execute_from_command_line

path = '/srv/saleor'
sys.path.append(
    join(path, 'stores', '{{ store_name }}', 'venv', 'lib', 'python3.5', 'site-packages'))
{%- if store.source is defined and store.source.engine == 'git' %}
sys.path.append(join(path, 'stores', '{{ store_name }}', 'saleor'))
{%- endif %}
sys.path.append(join(path, 'stores', '{{ store_name }}', 'site'))
{%- if store.saleor is defined %}
sys.path.append(join(path, 'stores', '{{ store_name }}', 'source'))
sys.path.append(join(path, 'stores', '{{ store_name }}', 'venv', 'src'))
{% else %}
sys.path.append(join(path, 'source'))
sys.path.append(join(path, 'venv', 'src'))
{% endif %}
if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    django.setup()
    execute_from_command_line(sys.argv)
