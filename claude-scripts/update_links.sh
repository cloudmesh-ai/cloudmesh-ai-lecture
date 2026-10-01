#!/bin/bash

FILES=("docs/lecture/dates.md" "docs/lecture/dates-table.md")

declare -A REPLACEMENTS=(
    ["/section/cloud/other-architecture-with-vmon-mac.md"]="/section/cloud/architecture/other-architecture-with-vmon-mac.md"
    ["/section/cloud/other-architecture-with-vmon-windows.md"]="/section/cloud/architecture/other-architecture-with-vmon-windows.md"
    ["/section/cloud/openstack-heat-fast-api-project-wide-access.md"]="/section/cloud/openstack/openstack-heat-fast-api-project-wide-access.md"
    ["/section/cloud/openstack-heat-fastapi.md"]="/section/cloud/openstack/openstack-heat-fastapi.md"
    ["/section/container/docker.md"]="/section/container/foundations/docker.md"
    ["/section/container/kubernetes.md"]="/section/container/orchestration/kubernetes.md"
    ["/section/container/kubernetes-local.md"]="/section/container/orchestration/kubernetes-local.md"
    ["/section/container/apptainer.md"]="/section/container/foundations/apptainer.md"
    ["/section/container/podman.md"]="/section/container/foundations/podman.md"
    ["/section/container/podman-and-co.md"]="/section/container/foundations/podman-and-co.md"
    ["/section/llm/llm-cpu-all.md"]="/section/llm/hardware/llm-cpu-all.md"
    ["/section/llm/llm-jetstream.md"]="/section/llm/hardware/llm-jetstream.md"
    ["/section/llm/llm-spark.md"]="/section/llm/hardware/llm-spark.md"
    ["/section/llm/llm-amsc.md"]="/section/llm/hardware/llm-amsc.md"
)

for file in "${FILES[@]}"; do
    echo "Updating $file..."
    for old in "${!REPLACEMENTS[@]}"; do
        new=${REPLACEMENTS[$old]}
        sed -i '' "s|$old|$new|g" "$file"
    done
done
