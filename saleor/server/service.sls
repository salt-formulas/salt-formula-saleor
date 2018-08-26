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
  - requirements: /srv/saleor/source/requirements.txt
  - python: python3
  - require:
    - pkg: saleor_packages
    - git: saleor_common_source

saleor_npm_common_install:
  cmd.run:
  - name: npm install; npm run build-assets; npm run build-emails
  - cwd: /srv/saleor/source
  - require:
    - git: saleor_common_source

{%- endif %}

{%- endif %}
