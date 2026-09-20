
## Jinja2 + Ansible – The Native Templating Engine  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).  

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

The dictionary `extra_services` becomes available to any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a tiny Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.





## Jinja2 + Ansible – The Native Templating Engine  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).  

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

The dictionary `extra_services` becomes available to any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a tiny Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.



**Jinja2 + Ansible – The Native Templating Engine**  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).  

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

`extra_services` becomes a dictionary you can reference in any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a small Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.





## Jinja2 + Ansible – The Native Templating Engine  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).  

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

The dictionary `extra_services` becomes available to any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a tiny Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.



**Jinja2 + Ansible – The Native Templating Engine**  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).  

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

`extra_services` becomes a dictionary you can reference in any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a small Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.



## Jinja2 + Ansible – The Native Templating Engine  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

The dictionary `extra_services` becomes available to any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

The following two‑step Python snippet shows how the same Jinja2 template can be rendered outside of Ansible (useful for quick ad‑hoc checks or for generating artefacts in a custom CI step).  

**Step 1 – Install Jinja2 in the execution environment**





## Jinja2 + Ansible – The Native Templating Engine  

Ansible is built on Jinja2. Every time you write `{{ … }}` you are invoking the Jinja2 engine. Mastering this integration lets you:

* generate any text‑based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,  
* keep configuration DRY with macros and template inheritance,  
* safely inject external data and secrets, and  
* test‑drive the rendering as part of a CI pipeline.

Below is a practical, “from‑scratch‑to‑production” guide that shows how to:

1. **Structure templates and data** in a role.  
2. **Leverage built‑in filters, tests, and the `jinja2_native` mode** for proper data types.  
3. **Create reusable macros** and **template inheritance** to avoid duplication.  
4. **Inject external data (JSON/YAML) and secrets** safely.  
5. **Test and lint** the rendered output as part of a CI pipeline.  

---  

### !!! note Learning Objectives  

- Understand the directory layout for an Ansible role that uses Jinja2 templates.  
- Write Jinja2 templates that consume Ansible facts, role defaults, and host‑specific variables.  
- Use macros, includes, and inheritance to keep templates DRY.  
- Apply the `jinja2_native` configuration to preserve native Python types.  
- Create custom filter plugins and reference them from templates.  
- Render templates safely with secrets coming from Ansible Vault or lookup plugins.  
- Validate rendered artefacts with unit tests, `yamllint`, and `ansible‑lint` in a CI workflow.  

---  

### 1️⃣ Directory Layout – A Typical Role  

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest‑precedence defaults
├─ vars/
│   └─ main.yml          # role‑specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as‑is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial – macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

---  

### 2️⃣ A Full‑Featured Jinja2 Template for Nginx  

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration – rendered by Ansible/Jinja2
   ------------------------------------------------- #}
{% from "_helpers.j2" import render_upstream %}

user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include       {{ nginx_conf_dir }}/mime.types;
    default_type  application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate     {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    {{ render_upstream(upstream_name, upstream_servers) }}

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};

        location / {
            proxy_pass http://{{ upstream_name }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

Key constructs:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralises upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` … `{% endif %}` | Enables the same template for HTTP‑only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts – no extra variables required. |

---  

### 3️⃣ Helper Partial – Reusable Macros & Custom Filters  

**`templates/_helpers.j2`**

```jinja
{# -----------------------------------------------------------------
   Helper macros and shared filters used across multiple templates.
   ----------------------------------------------------------------- #}

{% macro render_upstream(name, servers) -%}
upstream {{ name }} {
{% for s in servers %}
    server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
{% endfor %}
}
{%- endmacro %}
```

You can extend this file with additional macros (`render_location`, `render_ssl_block`, …).

---  

### 4️⃣ Supplying Data – Vars, Group‑Vars, & External Files  

#### 4.1 Role defaults (`defaults/main.yml`)

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### 4.2 Host‑specific overrides (`host_vars/web01.yml`)  

```yaml
listen_port: 443
ssl_enabled: true
ssl_cert_path: /etc/ssl/certs/web01.crt
ssl_key_path: /etc/ssl/private/web01.key
upstream_name: app_backends
upstream_servers:
  - { host: 10.0.1.10, port: 8080, weight: 2 }
  - { host: 10.0.1.11, port: 8080 }
```

#### 4.3 Loading a JSON/YAML file at runtime  

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

`extra_services` becomes a dictionary you can reference in any later template, e.g., `{{ extra_services.api.endpoint }}`.

---  

### 5️⃣ Rendering the Template in a Playbook  

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx                # classic handler pattern

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

The `template` module automatically supplies **all variables** (inventory, facts, defaults, etc.) to the Jinja2 engine.

---  

### 6️⃣ Enabling `jinja2_native` – Preserve Python Types  

Add the following to `ansible.cfg`:

```ini
[defaults]
jinja2_native = True
```

Now booleans, integers, and lists are rendered as native Python types, which is essential when generating JSON or when a downstream tool expects true data types.

---  

### 7️⃣ Custom Filters – Extending Jinja2 in Ansible  

Create a filter plugin inside the role:

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS‑compatible slug."""
    import re
    value = value.lower()
    value = re.sub(r'[^a-z0-9-]+', '-', value)
    return value.strip('-')

class FilterModule(object):
    def filters(self):
        return {
            'slugify': slugify,
        }
```

Use it in a template:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

Ansible automatically discovers plugins placed in `filter_plugins/` (or any directory referenced by `ANSIBLE_FILTER_PLUGINS`).

---  

### 8️⃣ Testing & Linting Templates  

#### 8.1 Unit tests with **`ansible-test`** (or plain `pytest`)

```yaml
# tests/test_nginx_template.yml
- hosts: localhost
  gather_facts: false
  vars:
    nginx_user: nginx
    nginx_log_dir: /tmp/log
    nginx_run_dir: /tmp/run
    listen_port: 8080
    ssl_enabled: false
  tasks:
    - name: Render template to a temporary file
      template:
        src: ../templates/nginx.conf.j2
        dest: /tmp/rendered-nginx.conf
    - name: Verify expected line exists
      command: grep -q '^listen 8080;' /tmp/rendered-nginx.conf
      changed_when: false
```

Run in CI:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

If the playbook exits with `0`, the template rendered correctly with the supplied variables.

#### 8.2 Linting with **`yamllint`** after rendering  

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

Add these steps to your CI pipeline to **fail early** on syntax errors.

---  

### 9️⃣ Demonstration – Rendering a Jinja2 Template with Python  

Below is a small Python snippet that mimics Ansible’s rendering process. It shows the final Nginx configuration for a host that enables SSL.  

```python
from jinja2 import Environment, StrictUndefined

template_str = """\
user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus | default(2) }};
error_log {{ nginx_log_dir }}/error.log warn;
pid {{ nginx_run_dir }}/nginx.pid;

events {
    worker_connections {{ worker_connections | default(1024) }};
}

http {
    include {{ nginx_conf_dir }}/mime.types;
    default_type application/octet-stream;

    {% if ssl_enabled %}
    ssl_certificate {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    {% endif %}

    upstream {{ upstream_name }} {
    {% for s in upstream_servers %}
        server {{ s.host }}:{{ s.port }}{% if s.weight %} weight={{ s.weight }}{% endif %};
    {% endfor %}
    }

    server {
        listen {{ listen_port }};
        server_name {{ server_name | default('_') }};
    }
}
"""

context = {
    "nginx_user": "nginx",
    "nginx_log_dir": "/var/log/nginx",
    "nginx_run_dir": "/var/run/nginx",
    "ansible_processor_vcpus": 4,
    "worker_connections": 2048,
    "nginx_conf_dir": "/etc/nginx",
    "ssl_enabled": True,
    "ssl_cert_path": "/etc/ssl/certs/web01.crt",
    "ssl_key_path": "/etc/ssl/private/web01.key",
    "upstream_name": "app_backends",
    "upstream_servers": [
        {"host": "10.0.1.10", "port": 8080, "weight": 2},
        {"host": "10.0.1.11", "port": 8080}
    ],
    "listen_port": 443,
    "server_name": "example.com"
}

env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
rendered = env.from_string(template_str).render(**context)

print("=== Rendered Nginx configuration ===")
print(rendered.strip())
```

**Explanation of the output**

* The rendered configuration reflects the values from `context`.  
* SSL block appears because `ssl_enabled` is `True`.  
* The `upstream` stanza lists both backend servers, applying the optional `weight` attribute only to the first server.  
* All defaults (`ansible_processor_vcpus`, `worker_connections`) are overridden by explicit values, showing how Jinja2’s `default` filter works.

---  

### 📚 Assignments  

1. **Create a new role** named `mywebapp` that follows the directory layout shown above. Include a `templates/nginx.conf.j2` that uses at least two custom macros from `_helpers.j2`.  
2. **Write host‑specific variables** for three hosts (`app01`, `app02`, `app03`) that differ in `listen_port`, `ssl_enabled`, and the list of upstream servers. Run the role locally with `ansible-playbook -i inventory site.yml` and verify that three distinct `nginx.conf` files are produced.  
3. **Add a custom filter** `to_hostname` that converts any string to a legal DNS hostname (lower‑case, alphanumerics + hyphens). Use it in a `systemd.service.j2` template to generate a `Description=` line based on `inventory_hostname`.  
4. **Implement a CI job** (GitHub Actions, GitLab CI, or Jenkins) that runs:  
   * `ansible-playbook --check` on the test playbook,  
   * `yamllint` on the rendered files, and  
   * `ansible-lint` on the role.  
   Ensure the job fails if any step reports an error.  

---  

### 🧭 Self‑Assessment Checklist  

- [ ] I can locate the role’s `defaults`, `vars`, `templates`, and `tasks` directories and explain their purpose.  
- [ ] I have written a Jinja2 template that uses `default`, `if/else`, and a loop over a list of dictionaries.  
- [ ] I created a macro in `_helpers.j2` and imported it into another template with `{% from "_helpers.j2" import … %}`.  
- [ ] My `ansible.cfg` contains `jinja2_native = True` and I understand how that changes output types.  
- [ ] I developed a custom filter plugin, placed it in `filter_plugins/`, and used it successfully in a template.  
- [ ] I can run a unit test playbook that renders a template and validates a specific line with `grep`.  
- [ ] My CI pipeline runs rendering, linting, and `ansible‑lint` steps, and it fails when a template contains a syntax error.  

If you can answer “yes” to all the items, you have a solid grasp of using Jinja2 inside Ansible for production‑grade automation.