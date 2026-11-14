import os
import re

oct15_content = """
- **[Core Container Philosophy](/section/container/foundations/containers.md)**
- **[Docker](/section/container/foundations/docker.md)**
- **[Podman](/section/container/foundations/podman.md)**
- **[Podman vs Docker](/section/container/foundations/podman-and-co.md)**
- **[Apptainer](/section/container/foundations/apptainer.md)**
- **[Container Tool Comparison](/section/container/container-tool-comparison.md)**
- **[Container Security](/section/container/security/container-security.md)**
- **[CI/CD Security](/section/container/security/containers-in-pipeline.md)**
- **[Kubernetes Deployment Pipelines](/section/devops/k8s-pipeline.md)**
- **[AI Workloads in Containers](/section/container/specialized/ai-containers.md)**
- **[Container Storage and Networking](/section/container/specialized/container-storage-networking.md)**
- **[Kubernetes Introduction](/section/container/orchestration/kubernetes.md)**
- **[Kubernetes Local Deployment](/section/container/orchestration/kubernetes-local.md)**
- **[HPA Autoscaling](/section/container/kubernetes-advanced/hpa-autoscaling.md)**
- **[RPS Autoscaling](/section/container/kubernetes-advanced/rps-autoscaling.md)**
- **[Helm](/section/container/specialized/helm.md)**
- **[OpenShift](/section/container/orchestration/openshift.md)**
- **[Orchestration Comparison](/section/container/orchestration/orchestration-comparison.md)**
- **[OpenStack Foundations](/section/cloud/openstack/openstack.md)**
- **[OpenStack and Containers](/section/container/openstack/openstack-containers.md)**
- **[Containers on Chameleon](/section/container/openstack/openstack-chameleon-containers.md)**
- **[Containers on Jetstream](/section/container/openstack/openstack-jetstream-container.md)**
- **[AI in Cloud](/section/cloud/topics/ai.md)**
 28 | - **[Kubernetes Grid](/lecture/assignments/project/kubernetes-grid.md)**
 29 | - **[Slurm AI](/section/slurm/slurm-ai.md)**
 30 | - **[PlantUML](/section/writing/plantuml.md)**
 31 | """

# Extract paths from oct15_content
linked_paths = re.findall(r'\[.*?\]\((.*?)\)', oct15_content)
# Normalize to full paths starting with docs/
normalized_linked = set()
for p in linked_paths:
    if p.startswith('/'):
        normalized_linked.add('docs' + p)
    else:
        normalized_linked.add('docs/' + p)

# All files mentioning the keywords
all_files = """
docs/drafts/nvidia-pair-notuseful/alternative.md
docs/drafts/nvidia-pair-notuseful/ansible.md
docs/drafts/nvidia-pair-notuseful/best.md
docs/drafts/nvidia-pair-notuseful/install.md
docs/drafts/nvidia-pair-notuseful/local.md
docs/drafts/nvidia-pair-notuseful/machines.md
docs/drafts/nvidia-pair-notuseful/pair-1.md
docs/drafts/nvidia-pair-notuseful/pair-tutorial.md
docs/drafts/nvidia-pair-notuseful/start.md
docs/drafts/outdated/writing/bugs.md
docs/drafts/outdated/writing/projects-2.md
docs/drafts/outdated/writing/report.md
docs/drafts/section/cloud/arch-scheduling.md
docs/drafts/section/cloud/arch.md
docs/drafts/section/cloud/chameleon/faq-orig.md
docs/drafts/section/cloud/chameleon/faq.md
docs/drafts/section/cloud/cloud-foundry.md
docs/drafts/section/cloud/definition.md
docs/drafts/section/cloud/use-cases.md
docs/drafts/section/cloudmesh/python-cloudmesh.md
docs/drafts/section/deprecated/python-deprecated.md
docs/drafts/section/deprecated/python-install-pyenv.md
docs/drafts/section/numpy/numpy.md
docs/drafts/section/storage/introduction.md
docs/drafts/sections.md
docs/index.md
docs/lecture/01.1-syllabus.md
docs/lecture/01.2-contribute-lecture-notes.md
docs/lecture/02-cloud.md
docs/lecture/assignments/assignments.md
docs/lecture/assignments/ideas.md
docs/lecture/assignments/overview.md
docs/lecture/assignments/project/kubernetes-grid.md
docs/lecture/assignments/project/openstack_multicloud_vpn_student_project.md
docs/lecture/dates-table.md
docs/lecture/dates.md
docs/lecture/oct15 copy.md
docs/lecture/oct15.md
docs/new/llm/llm-aws.md
docs/new/llm/llm-azure.md
docs/new/llm/llm-google.md
docs/new/llm/llm-online-vs-hosted.md
docs/new/llm/llm-oracle.md
docs/new/llm/llm-what-can-you-do.md
docs/new/llm/tutorials/llm-aws.md
docs/new/llm/tutorials/llm-azure.md
docs/new/llm/tutorials/llm-google.md
docs/new/llm/tutorials/llm-online-vs-hosted.md
docs/new/llm/tutorials/llm-oracle.md
docs/new/llm/tutorials/llm-what-can-you-do.md
docs/section/accounts/local.md
docs/section/ai/aws-bedrock.md
docs/section/ai/calender-notify.md
docs/section/ai/multi/tt.md
docs/section/ai/openclaw/chapter-generator.md
docs/section/ai/openclaw/introduction.md
docs/section/ai/openclaw/nemoclaw.md
docs/section/ai/openclaw/non-devops.md
docs/section/ai/openclaw/openstack.md
docs/section/ai/openclaw/references.md
docs/section/ai/openclaw/vm-manager.md
docs/section/ai/todo-wrong-openrouter.md
docs/section/cloud/architecture/other-architecture-with-vmon-mac.md
docs/section/cloud/architecture/other-architecture-with-vmon-windows.md
docs/section/cloud/fundamentals/introduction.md
docs/section/cloud/fundamentals/virtual-machine-technologies.md
docs/section/cloud/fundamentals/virtualization-landscape.md
docs/section/cloud/fundamentals/virtualization-popularity.md
docs/section/cloud/fundamentals/virtualization.md
docs/section/cloud/openstack/devstack.md
docs/section/cloud/openstack/openstack.md
docs/section/cloud/openstack/storage/glance.md
docs/section/cloud/openstack/storage/overview.md
docs/section/cloud/openstack/storage/swift.md
docs/section/cloud/platforms/chameleon/reservation.md
docs/section/cloud/platforms/jetstream/jetstream-multi-appendix.md
docs/section/cloud/platforms/local/lima.md
docs/section/cloud/platforms/local/multipass.md
docs/section/cloud/platforms/local/vagrant.md
docs/section/cloud/platforms/local/virtualbox.md
docs/section/cloud/platforms/local/vm-status.md
docs/section/cloud/platforms/ornl/gemma4.md
docs/section/cloud/platforms/ornl/llm.md
docs/section/cloud/platforms/ornl/ssh-prox-interactivey.md
docs/section/cloud/platforms/ornl/ssh-proxy-slurm.md
docs/section/cloud/resources/presentation/virtualization.md
docs/section/cloud/resources/slides/virtualization-talk.md
docs/section/cloud/resources/unused_images/vm-mindmap.md
docs/section/cloud/topics/ai.md
docs/section/cloud/topics/cost.md
docs/section/cloud/vm-cloud/aws-boto-chapter.md
docs/section/cloud/vm-cloud/aws-install-chapter.md
docs/section/cloud/vm-cloud/azure install-chapter.md
docs/section/cloud/vm-cloud/azure-sdk-chapter.md
docs/section/cloud/vm-cloud/gcp-install-chapter.md
docs/section/cloud/vm-cloud/google-sdk-chapter.md
docs/section/cloud/vm-cloud/libcloud-chapter.md
docs/section/cloud/vm-cloud/oracle-chapter.md
docs/section/cloud/vm-cloud/oracle-sdk-chapter.md
docs/section/cloud/vm-cloud/tutorials/aws-boto-tutorial.md
docs/section/cloud/vm-cloud/tutorials/aws-install-tutorial.md
docs/section/cloud/vm-cloud/tutorials/azure install-tutorial.md
docs/section/cloud/vm-cloud/tutorials/azure-sdk-tutorial.md
docs/section/cloud/vm-cloud/tutorials/free-tutorial.md
docs/section/cloud/vm-cloud/tutorials/gcp-install-tutorial.md
docs/section/cloud/vm-cloud/tutorials/google-sdk-tutorial.md
docs/section/cloud/vm-cloud/tutorials/libcloud-tutorial.md
docs/section/cloud/vm-cloud/tutorials/oracle-sdk-tutorial.md
docs/section/cloud/vm-cloud/tutorials/oracle-tutorial.md
docs/section/container/CHAPTER.md
docs/section/container/container-todo.md
docs/section/container/container-tool-comparison.md
docs/section/container/foundations/apptainer.md
docs/section/container/foundations/containers.md
docs/section/container/foundations/docker.md
docs/section/container/foundations/podman-and-co.md
docs/section/container/foundations/podman.md
docs/section/container/kubernetes-advanced/hpa-autoscaling.md
docs/section/container/kubernetes-advanced/rps-autoscaling.md
docs/section/container/openstack/openstack-chameleon-containers.md
docs/section/container/openstack/openstack-containers.md
docs/section/container/openstack/openstack-jetstream-container.md
docs/section/container/orchestration/kubernetes-local.md
docs/section/container/orchestration/kubernetes.md
docs/section/container/orchestration/openshift.md
docs/section/container/orchestration/orchestration-comparison.md
docs/section/container/public-clouds/aws-containers.md
docs/section/container/public-clouds/azure-containers-docker.md
docs/section/container/public-clouds/azure-containers.md
docs/section/container/public-clouds/gcp-containers.md
docs/section/container/public-clouds/oci-containers.md
docs/section/container/security/container-security.md
docs/section/container/security/containers-in-pipeline.md
docs/section/container/specialized/ai-containers.md
docs/section/container/specialized/container-storage-networking.md
docs/section/container/specialized/helm.md
docs/section/devops/ai-devops.md
docs/section/devops/ansible.md
docs/section/devops/argocd.md
docs/section/devops/CHAPTER.md
docs/section/devops/circleci.md
docs/section/devops/DEV-OPS-TODO.md
docs/section/devops/devop-aws.md
docs/section/devops/devop-azure-monitor.md
docs/section/devops/devop-ci.md
docs/section/devops/devops-iac.md
docs/section/devops/devops-jinja2.md
docs/section/devops/devops-team.md
docs/section/devops/devops.md
docs/section/devops/example-devops-project.md
docs/section/devops/github-workflow-security.md
docs/section/devops/github-workflows.md
docs/section/devops/gitops-fundamentals.md
docs/section/devops/jenkins.md
docs/section/devops/k8s-pipeline.md
docs/section/devops/local-lab.md
docs/section/devops/make.md
docs/section/devops/terraform.md
docs/section/devops/travis.md
docs/section/edge/edge.md
docs/section/editors/vscode.md
docs/section/linux/linux-orig.md
docs/section/linux/linux.md
docs/section/linux/refcards.md
docs/section/linux/ubuntu-cheatsheet.md
docs/section/llm-draft/cline-skills-appendix.md
docs/section/llm-draft/langchain.md
docs/section/llm-draft/llm-service.md
docs/section/llm-draft/llm-spark.md
docs/section/llm-draft/openclaw.md
docs/section/llm-draft/skill-lecture-tutorial.md
docs/section/llm-draft/skills-llm-jetstream.bak.md
docs/section/llm/agents/langchain.md
docs/section/llm/cli/opencode-skills.md
docs/section/llm/hardware/llm-jetstream.md
docs/section/llm/hardware/llm-spark.md
docs/section/llm/hardware/openclaw.md
docs/section/llm/new/case-study-walk-through.md
docs/section/llm/new/CHAPTER.md
docs/section/llm/new/devops-pipelines-for-llms.md
docs/section/llm/new/hands-on-lab-blueprint.md
docs/section/llm/new/infrastructure-for-llms.md
docs/section/llm/new/llm-devops-capabilities-map copy.md
docs/section/llm/new/llms-as-cloud-native-services.md
docs/section/llm/new/security-governance-&-compliance.md
docs/section/llm/new/summary-&-quick-start-checklist.md
docs/section/llm/new/why-llms-matter-for-cloud-&-devops.md
docs/section/llm/services/llm-service.md
docs/section/llm/skills-llm-jetstream.bak.md
docs/section/llm/skills/cline-skills-appendix.md
docs/section/llm/skills/skill-lecture-tutorial.md
docs/section/python/language.md
docs/section/python/python-argparse.md
docs/section/python/python-click.md
docs/section/python/python-hatch-vs-uv.md
docs/section/python/python-intro.md
docs/section/python/python-logging.md
docs/section/python/python-pyproject.md
docs/section/python/python-queue.md
docs/section/python/python-testing.md
docs/section/python/python-type-hints.md
docs/section/python/python-uv.md
docs/section/rest-what-is-an-llm-service.md
docs/section/rest/rest.md
docs/section/slurm/slurm-ai.md
docs/section/writing/acm-markdown.md
docs/section/writing/blockdiag.md
docs/section/writing/overleaf.md
docs/section/writing/plantuml.md
"""

all_files_list = all_files.strip().split('\n')
missing_files = [f for f in all_files_list if f not in normalized_linked]

# Further filter missing_files: 
# 1. Only keep those in docs/section/ or docs/lecture/ (not drafts, not new, etc.)
# 2. Exclude oct15.md and its copy
final_list = []
for f in missing_files:
    if f.startswith('docs/drafts') or f.startswith('docs/new'):
        continue
    if 'oct15' in f:
        continue
    if f.startswith('docs/section') or f.startswith('docs/lecture'):
        final_list.append(f)

print('\n'.join(final_list))
