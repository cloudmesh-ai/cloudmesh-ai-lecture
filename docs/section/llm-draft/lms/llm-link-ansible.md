# Ansible


### 1. Inventory Configuration (`inventory.yaml`)

spark and white are defined in .ssh/config

```yaml
all:
  hosts:
    spark:
    white:
  children:
    cluster_nodes:
      hosts:
        spark:
        white:
```

---

### 2. LiteLLM Configuration Template (`templates/litellm-config.yaml.j2`)

```yaml
model_list:
  - model_name: mac/wen3.8-27b
    litellm_params:
      model: qwen/qwen3.8-27b
      api_base: http://localhost:1234/v1
      api_key: "not-needed"

  {% set openstack_llms = lookup('file', ansible_env.HOME + '/.config/openstack/llm_config.json') | from_json %}
  {% for model_key, model_data in openstack_llms.items() %}
  - model_name: {{ model_key }}
    litellm_params:
      model: {{ model_data.model_name | default('openai/' ~ model_key) }}
      api_base: {{ model_data.api_base }}
      api_key: "{{ model_data.api_key | default('not-needed') }}"
  {% endfor %}

general_settings:
  master_key: "{{ litellm_master_key | default(omit) }}"
```

---

### 3. Main Playbook (`playbook.yaml`)

```yaml
-- name: Deploy LiteLLM Config and Package
  hosts: cluster_nodes
  become: true
  vars:
    litellm_port: 4000
    litellm_master_key: "sk-optional-master-key"
    app_dir: /opt/litellm

  tasks:
    - name: Create application directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        mode: '0755'

    - name: Install LiteLLM proxy via pip3
      ansible.builtin.pip:
        name: "litellm[proxy]"
        executable: pip3
        state: present

    - name: Deploy LiteLLM configuration file from template
      ansible.builtin.template:
        src: templates/litellm-config.yaml.j2
        dest: "{{ app_dir }}/config.yaml"
        mode: '0644'
```


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the role of the `templates/litellm-config.yaml.j2` file in the Ansible deployment?"
    It is a Jinja2 template used to dynamically generate the LiteLLM configuration based on the remote host's `llm_config.json`.

??? question "Which Ansible module is used to install the `litellm[proxy]` package?"
    The `ansible.builtin.pip` module is used to ensure the `litellm[proxy]` package is installed on the cluster nodes.

??? question "How are the `spark` and `white` hosts defined in the inventory?"
    They are defined in `.ssh/config`, so the inventory just lists them by name.

