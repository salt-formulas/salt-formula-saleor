{%- if store.bind is defined and store.bind.port is defined %}
{%- set store_bind_port = store.bind.port %}
{%- else %}
{%- set store_bind_port = 8000 %}
{%- endif %}

{%- set store_dir = '/srv/saleor/stores/' + store_name %}

saleor_{{ store_name }}_dirs:
  file.directory:
  - names:
    - {{ store_dir }}/site
  - mode: 775
  - makedirs: true
  - group: saleor
  - user: saleor
  - require:
    - user: saleor

{%- if store.saleor is defined %}

saleor_{{ store_name }}_source:
  git.latest:
  - name: {{ store.saleor.address }}
  - rev: {{ store.saleor.revision }}
  - target: {{ store_dir }}/source
  - user: saleor
  - require:
    - file: saleor_{{ store_name }}_dirs

{{ store_dir }}/venv:
  virtualenv.manage:
  - python: python3
  - require:
    - git: saleor_{{ store_name }}_source

pip-{{ store_name }}-upgrade1:
  pip.installed:
  - name: pip==10
  - bin_env: {{ store_dir }}/venv/bin/pip

pip-{{ store_name }}-upgrade2:
  pip.installed:
  - requirements: {{ store_dir }}/source/requirements.txt
  - bin_env: {{ store_dir }}/venv/bin/pip

{% for plugin_name, plugin in store.get('plugins', {}).iteritems() %}
{% if not plugin.get('site', false) %}
{{ plugin_name }}_{{ store_name }}_req:
  pip.installed:
  {%- if 'source' in plugin and plugin.source.get('engine', 'git') == 'git' %}
  - editable: {{ plugin.source.address }}
  {%- elif 'source' in plugin and plugin.source.engine == 'pip' %}
  - name: {{ plugin_name }} {%- if plugin.version is defined %}=={{ plugin.version }}{% endif %}
    {%- if plugin.source.address is defined %}
  - index_url: {{ plugin.source.get('address', 'http://pypi.python.org') }}
  - trusted_host: {{ index_url.replace('https://', '').replace('/simple/', '') }}
    {%- endif %}
    {%- if not plugin.version is defined %}
  - pre_releases: True
    {%- endif %}
  {%- endif %}
  - bin_env: {{ store_dir }}/venv/bin/pip
  - exists_action: w
  - process_dependency_links: True
{% endif %}
{% endfor %}

{% else %}

{% for plugin_name, plugin in store.get('plugins', {}).iteritems() %}
{% if not plugin.get('site', false) %}
{{ plugin_name }}_{{ store_name }}_req:
  pip.installed:
  {%- if 'source' in plugin and plugin.source.get('engine', 'git') == 'git' %}
  - editable: {{ plugin.source.address }}
  {%- elif 'source' in plugin and plugin.source.engine == 'pip' %}
  - name: {{ plugin_name }} {%- if plugin.version is defined %}=={{ plugin.version }}{% endif %}
    {%- if plugin.source.address is defined %}
  - index_url: {{ plugin.source.get('address', 'http://pypi.python.org') }}
  - trusted_host: {{ index_url.replace('https://', '').replace('/simple/', '') }}
    {%- endif %}
    {%- if not plugin.version is defined %}
  - pre_releases: True
    {%- endif %}
  {%- endif %}
  - bin_env: /srv/saleor/venv/bin/pip
  - exists_action: w
  - process_dependency_links: True
{% endif %}
{% endfor %}

{%- endif %}

pip-{{ store_name }}-gunicorn:
  pip.installed:
  - name: gunicorn
  - bin_env: /srv/saleor/venv/bin/pip

{{ store_dir }}/site/settings.py:
  file.managed:
  - source: salt://saleor/files/settings.py
  - template: jinja
  - mode: 644
  - defaults:
    store_name: "{{ store_name }}"
  - require:
    - file: saleor_{{ store_name }}_dirs

{{ store_dir }}/site/manage.py:
  file.managed:
  - source: salt://saleor/files/manage.py
  - template: jinja
  - mode: 644
  - defaults:
    store_name: "{{ store_name }}"
  - require:
    - file: saleor_{{ store_name }}_dirs

{{ store_dir }}/site/wsgi.py:
  file.managed:
  - source: salt://saleor/files/wsgi.py
  - template: jinja
  - mode: 644
  - defaults:
    store_name: "{{ store_name }}"
  - require:
    - file: saleor_{{ store_name }}_dirs

saleor_{{ store_name }}_service_file:
  file.managed:
  - name: /etc/systemd/system/saleor-{{ store_name }}.service
  - source: salt://saleor/files/saleor.service
  - template: jinja
  - defaults:
    store_name: "{{ store_name }}"
    port: {{ store_bind_port }}
  - user: root
  - mode: 644
  - require:
    - pip: pip-{{ store_name }}-gunicorn

npm_{{ store_name }}_install:
  cmd.run:
  - name: sudo npm update; sudo npm install npm@latest -g; sudo npm install node-sass; sudo npm install; sudo npm audit fix; sudo npm run build-assets; sudo npm run build-emails
  - cwd: {{ store_dir }}/source
  - require:
    - file: saleor_{{ store_name }}_dirs

saleor_{{ store_name }}_migrate_database:
  cmd.run:
  - name: source {{ store_dir }}/venv/bin/activate; {{ store_dir }}/venv/bin/python manage.py migrate
  - cwd: {{ store_dir }}/site
  - require:
    - file: saleor_{{ store_name }}_dirs
    - file: {{ store_dir }}/site/settings.py
