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
  - requirements: {{ store_dir }}/source/requirements.txt
  - python: python3
  - require:
    - git: saleor_{{ store_name }}_source

npm_{{ store_name }}_install:
  cmd.run:
  - name: sudo npm install; sudo npm run build-assets; sudo npm run build-emails
  - cwd: {{ store_dir }}/source
  - require:
    - file: saleor_{{ store_name }}_dirs

{%- endif %}

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

saleor_{{ store_name }}migrate_database:
  cmd.run:
  - name: source {{ store_dir }}/venv/bin/activate; {{ store_dir }}/venv/bin/python manage.py migrate
  - cwd: {{ store_dir }}/site
  - require:
    - file: saleor_{{ store_name }}_dirs
    - file: {{ store_dir }}/site/settings.py
