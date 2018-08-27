#!/usr/bin/env python

{%- set store = salt['pillar.get']('saleor:server:store:'+store_name) %}

import os
import sys
from os.path import abspath, dirname, join, normpath

import django
import django.core.handlers.wsgi
from django.core.management import execute_from_command_line

path = '/srv/saleor'
sys.path.append(
    join(path, 'stores', '{{ store_name }}', 'lib', 'python2.7', 'site-packages'))
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

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()


application = django.core.handlers.wsgi.WSGIHandler()
