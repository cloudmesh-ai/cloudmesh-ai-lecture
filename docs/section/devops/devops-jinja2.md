# Jinja 2 (for ansible and others)

## Learning Objectives

!!! info "Learning Objectives"
    - Understand the directory layout for an Ansible role that uses Jinja2 templates.
    - Write Jinja2 templates that consume Ansible facts, role defaults, and host-specific variables.
    - Use macros, includes, and inheritance to keep templates DRY.
    - Apply the `jinja2_native` configuration to preserve native Python types.
    - Create custom filter plugins and reference them from templates.
    - Render templates safely with secrets coming from Ansible Vault or lookup plugins.
    - Validate rendered artefacts with unit tests, `yamllint`, and `ansible-lint` in a CI workflow.

## Overview

Ansible is built on Jinja2. Every time you write `{{ ... }}` you are invoking the Jinja2 engine. Understanding this integration allows you to:

- generate any text-based artefact (YAML, JSON, INI, Dockerfile, etc.) from inventory, facts, and variables,
- keep configuration DRY with macros and template inheritance,
- safely inject external data and secrets, and
- test-drive the rendering as part of a CI pipeline.

## Core Sections

### Directory Layout

A typical Ansible role that utilizes Jinja2 templates follows a specific directory structure to separate static files from dynamic templates and default variables.

```
myapp/
├─ defaults/
│   └─ main.yml          # lowest-precedence defaults
├─ vars/
│   └─ main.yml          # role-specific variables
├─ files/
│   └─ static/nginx.conf # static file copied as-is
├─ templates/
│   ├─ nginx.conf.j2
│   ├─ systemd.service.j2
│   └─ _helpers.j2       # partial - macros & shared filters
├─ tasks/
│   └─ main.yml
├─ meta/
│   └─ main.yml
└─ tests/
    ├─ inventory
    └─ test.yml          # simple playbook for CI validation
```

The `_helpers.j2` file holds reusable macros that other templates can import, keeping the code DRY.

### Jinja2 Templates for Nginx

Templates allow for dynamic configuration generation based on the target host's attributes and defined variables.

**`templates/nginx.conf.j2`**

```jinja
{# -------------------------------------------------
   Nginx configuration - rendered by Ansible/Jinja2
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

The following table summarizes the key Jinja2 constructs used in the example:

| Feature | Syntax | Benefit |
|---------|--------|---------|
| Macro import | `{% from "_helpers.j2" import render_upstream %}` | Centralizes upstream generation, reusable by many services. |
| Filters with defaults | `{{ ansible_processor_vcpus \| default(2) }}` | Guarantees a sensible value even when the fact is missing. |
| Conditional block | `{% if ssl_enabled %}` ... `{% endif %}` | Enables the same template for HTTP-only or HTTPS services. |
| Variables from facts | `{{ ansible_processor_vcpus }}` | Leverages automatically gathered host facts. |

### Helper Partials and Reusable Macros

Macros are the Jinja2 equivalent of functions, allowing you to encapsulate repetitive logic.

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

### Supplying Data to Templates

Ansible provides multiple layers of variable precedence to supply data to Jinja2 templates.

#### Role Defaults

Located in `defaults/main.yml`, these provide the lowest precedence values.

```yaml
nginx_user: nginx
nginx_log_dir: /var/log/nginx
nginx_run_dir: /var/run/nginx
nginx_conf_dir: /etc/nginx
listen_port: 80
ssl_enabled: false
```

#### Host-Specific Overrides

Located in `host_vars/web01.yml`, these override defaults for specific targets.

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

#### External Data Loading

You can load JSON or YAML files at runtime using the `include_vars` module.

```yaml
# tasks/main.yml
- name: Load extra service definitions
  include_vars:
    file: "{{ playbook_dir }}/files/services.json"
    name: extra_services
```

The dictionary `extra_services` then becomes available to any subsequent template.

### Rendering Templates in a Playbook

The `template` module is used to render a `.j2` file and upload it to the target host.

**`tasks/main.yml`**

```yaml
- name: Render nginx.conf from template
  template:
    src: nginx.conf.j2
    dest: "{{ nginx_conf_dir }}/nginx.conf"
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx

- name: Render systemd service unit
  template:
    src: systemd.service.j2
    dest: /etc/systemd/system/myapp.service
    mode: "0644"
  notify: Reload systemd
```

### Preserving Python Types with `jinja2_native`

By default, Jinja2 renders everything as strings. To preserve booleans, integers, and lists (essential for generating JSON), enable `jinja2_native` in `ansible.cfg`.

```ini
[defaults]
jinja2_native = True
```

### Custom Filter Plugins

Custom filters extend the Jinja2 vocabulary with Python functions.

**`filter_plugins/custom_filters.py`**

```python
def slugify(value):
    """Convert any string to a DNS-compatible slug."""
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

Use the custom filter in a template as follows:

```jinja
{{ inventory_hostname | slugify }}.example.com
```

### Testing and Linting Templates

#### Unit Testing with Playbooks

You can verify template rendering by running a local playbook that checks for expected strings in the output.

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

Execute the test in a CI pipeline:

```bash
ansible-playbook -i tests/inventory tests/test_nginx_template.yml --check
```

#### Post-Rendering Linting

Rendered files should be validated with tools like `yamllint` to ensure the resulting configuration is syntactically correct.

```yaml
- name: Lint rendered manifest
  command: yamllint /tmp/rendered-nginx.conf
  changed_when: false
```

### Demonstration: Rendering with Python

The following Python snippet mimics Ansible's rendering process, demonstrating how to use Jinja2 independently for ad-hoc checks.

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

## Summary Checklist

- [ ] I can locate the role's `defaults`, `vars`, `templates`, and `tasks` directories and explain their purpose.
- [ ] I have written a Jinja2 template that uses `default`, `if/else`, and a loop over a list of dictionaries.
- [ ] I created a macro in `_helpers.j2` and imported it into another template.
- [ ] My `ansible.cfg` contains `jinja2_native = True` and I understand how that changes output types.
- [ ] I developed a custom filter plugin, placed it in `filter_plugins/`, and used it successfully in a template.
- [ ] I can run a unit test playbook that renders a template and validates a specific line with `grep`.
- [ ] My CI pipeline runs rendering, linting, and `ansible-lint` steps.

## Assignments

!!! note "Assignment.1: Role Structure"
    Create a new role named `mywebapp` that follows the directory layout described in this chapter. Include a `templates/nginx.conf.j2` that uses at least two custom macros from `_helpers.j2`.

??? tip "Solution: Role Structure"
    The role should have `defaults/main.yml`, `vars/main.yml`, `templates/`, and `tasks/main.yml`. The `_helpers.j2` file should define macros (e.g., for SSL blocks or upstream definitions) which are then imported into `nginx.conf.j2` using `{% from "_helpers.j2" import ... %}`.

!!! note "Assignment.2: Host Variable Implementation"
    Write host-specific variables for three hosts (`app01`, `app02`, `app03`) that differ in `listen_port`, `ssl_enabled`, and the list of upstream servers. Run the role locally and verify that three distinct `nginx.conf` files are produced.

??? tip "Solution: Host Variable Implementation"
    Define variables in `host_vars/app01.yml`, `host_vars/app02.yml`, and `host_vars/app03.yml`. Use a playbook with the `template` module to render the configuration on each host.

!!! note "Assignment.3: Custom Filter Development"
    Add a custom filter `to_hostname` that converts any string to a legal DNS hostname (lower-case, alphanumerics + hyphens). Use it in a `systemd.service.j2` template to generate a `Description=` line based on `inventory_hostname`.

??? tip "Solution: Custom Filter Development"
    Implement the filter in `filter_plugins/custom_filters.py` using `re.sub` to replace non-alphanumeric characters with hyphens and calling `.lower()`.

!!! note "Assignment.4: CI Pipeline Integration"
    Implement a CI job that runs `ansible-playbook --check` on the test playbook, `yamllint` on the rendered files, and `ansible-lint` on the role. Ensure the job fails if any step reports an error.

??? tip "Solution: CI Pipeline Integration"
    In a GitHub Actions workflow, create steps that execute the three commands. Use the exit codes of the commands to determine the job's success or failure.

## References

- Ansible Documentation: [Template Module](https://docs.ansible.com/ansible/latest/collections/ansible.builtin/template_module.html)
- Jinja2 Documentation: [Template Designer Documentation](https://jinja.palletsprojects.com/)

## Self-Evaluation

??? note "What is the purpose of the `_helpers.j2` file in an Ansible role?"
    It serves as a partial template used to store reusable macros and shared logic, preventing duplication across multiple templates in the same role.

??? note "How does `jinja2_native = True` in `ansible.cfg` affect the output of a template?"
    It ensures that Python data types (like integers, booleans, and lists) are preserved in the rendered output rather than being converted to strings, which is critical when generating JSON or other structured data.

??? note "Where should custom Jinja2 filter plugins be placed for automatic discovery by Ansible?"
    They should be placed in a directory named `filter_plugins/` within the role's directory structure or in a path specified by the `ANSIBLE_FILTER_PLUGINS` environment variable.
