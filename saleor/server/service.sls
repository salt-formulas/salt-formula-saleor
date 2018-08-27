{%- from "saleor/map.jinja" import server with context %}
{%- if server.enabled %}

saleor_packages:
  pkg.installed:
  - names: {{ server.pkgs }}

saleor_user:
  user.present:
  - name: saleor
  - system: true
  - home: {{ server.dir.base }}

saleor_dirs:
  file.directory:
  - names:
    - {{ server.dir.base }}
    - {{ server.dir.base }}/stores
    - {{ server.dir.scripts }}
    - {{ server.dir.logs }}
    - /run/saleor
  - user: saleor
  - group: saleor
  - mode: 755
  - makedirs: true
  - require:
    - user: saleor_user

{%- if server.source.saleor.engine == 'git' %}

saleor_common_source:
  git.latest:
  - name: {{ server.source.saleor.address }}
  - rev: {{ server.source.saleor.revision }}
  - target: {{ server.dir.base }}/source
  - user: saleor
  - require:
    - file: saleor_dirs

/srv/saleor/venv:
  virtualenv.manage:
  - python: python3
  - require:
    - pkg: saleor_packages
    - git: saleor_common_source

pip-upgrade1:
  pip.installed:
  - name: pip==10
  - bin_env: /srv/saleor/venv/bin/pip

pip-upgrade2:
  pip.installed:
  - requirements: /srv/saleor/source/requirements.txt
  - bin_env: /srv/saleor/venv/bin/pip


{%- endif %}

{%- endif %}
