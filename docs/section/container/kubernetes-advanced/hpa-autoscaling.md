# Kubernetes Horizontal Pod Autoscaling (HPA)

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Implement a Horizontal Pod Autoscaler (HPA) based on CPU utilization.
    - Configure resource requests and limits required for HPA functionality.
    - Compare reactive CPU-based scaling with proactive Request-Per-Second (RPS) scaling using KEDA.
    - Analyze the cost and performance implications of autoscaling GPU-accelerated workloads.
    - Configure scaling behaviors to prevent "flapping" in production environments.
    - Integrate custom metrics for GPU-based autoscaling.

## Overview

The Horizontal Pod Autoscaler (HPA) automatically adjusts the number of pod replicas in a deployment to maintain a target resource utilization level. 

In AI workloads, GPU resources are extremely expensive. Over-provisioning (keeping 10 GPU pods running when only 2 are needed) wastes significant budget. Conversely, under-provisioning during a traffic spike leads to request timeouts and model crashes. HPA allows the cluster to be "elastic," scaling capacity up for peak demand and down to save costs during idle periods.

While Kubernetes can scale based on custom metrics using tools like Prometheus or KEDA, the standard approach is scaling based on CPU utilization. As request volume increases, CPU usage rises, triggering the HPA to instantiate additional pods.

## Core Sections

### Implementing CPU-Based Autoscaling

To implement HPA, the application must first define its resource requirements. HPA requires "requests" to calculate the current utilization percentage.

!!! info "Why this matters"
    In a production cluster, `requests` act as a "guarantee." If you request 100m CPU, Kubernetes ensures the pod is scheduled on a node that has at least 100m available. Without these requests, the HPA has no baseline; it cannot calculate "50% utilization" if it doesn't know what "100%" is.

#### 1. Deployment with Resource Constraints

The following manifest defines a web service with explicit resource requests and limits.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-service
  template:
    metadata:
      labels:
        app: web-service
    spec:
      containers:
      - name: web-app
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: web-service-svc
spec:
  selector:
    app: web-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

#### 2. Configuring the Horizontal Pod Autoscaler

The HPA object targets the deployment and defines the scaling boundaries (min/max replicas) and the target utilization.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

::: tip "The Utilization Buffer"
    Avoid setting `averageUtilization` to 80% or 90%. By the time the HPA detects the breach and the new pod finishes its "pull image" and "startup" phase, the existing pods may already be overwhelmed. A target of 50-60% provides a necessary buffer to handle the lag between the scaling trigger and the pod becoming ready.
:::

### The Scaling Lifecycle

The HPA operates in a continuous loop of observation and adjustment:

1. **Baseline State**: The application runs with the minimum defined replicas (e.g., 2 pods).
2. **Traffic Increase**: Incoming request volume increases, causing CPU usage to exceed the 50% target.
3. **Scale Out**: The Kubernetes Metrics Server detects high CPU usage, and the HPA controller increases the replica count. The load balancer distributes traffic across the new pods.
4. **Scale In**: As traffic decreases and CPU utilization falls below the target, the HPA reduces the replica count to conserve cluster resources.

::: warning "The Flapping Problem"
    "Flapping" occurs when a system scales up and down rapidly in a short window (e.g., scaling to 10 pods, then immediately back to 2). This causes instability and wastes resources. 
    
    To prevent this, use the `behavior` field in the HPA v2 specification to define `stabilizationWindowSeconds`. This forces the HPA to wait (e.g., 5 minutes) before scaling back down, ensuring the traffic dip is permanent and not just a momentary lull.
:::

### Proactive Scaling with KEDA and RPS

CPU-based scaling is reactive, as it waits for resource stress to occur. To scale proactively based on traffic volume, **KEDA (Kubernetes Event-driven Autoscaling)** is used.

#### KEDA Architecture

KEDA is an operator that extends HPA to allow scaling based on external events. For Request-Per-Second (RPS) scaling, KEDA queries a Prometheus server to determine the actual request rate.

![KEDA RPS Architecture](images/keda-rps-flow.png)

Figure 1: KEDA RPS Architecture. KEDA queries Prometheus for request rates and adjusts the HPA replica count accordingly.

#### Implementation Example (KEDA ScaledObject)

The following configuration scales the `web-service` based on a Prometheus query calculating the sum of requests per second over a 2-minute window.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: web-service-rps-scaler
spec:
  scaleTargetRef:
    name: web-service
  minReplicaCount: 2
  maxReplicaCount: 10
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus-server.monitoring.svc.cluster.local:9090
        metricName: http_requests_per_second
        query: sum(rate(http_requests_total{app="web-service"}[2m]))
        threshold: '100'
```

#### Comparison: CPU Scaling vs. RPS Scaling

| Feature | Standard HPA (CPU/Memory) | KEDA / Prometheus Adapter (RPS) |
| :--- | :--- | :--- |
| Metric Source | Internal (Metrics Server) | External (Prometheus/Event Source) |
| Scaling Logic | % of requested resources | Absolute values (e.g., 100 req/sec) |
| Responsiveness | Reactive | Proactive |
| Scaling Range | 1 to N | 0 to N (Scale-to-Zero via KEDA) |
| Primary Use Case | Compute-heavy workloads | I/O-bound or high-traffic services |

### Production Depth: GPU-Based Autoscaling

For AI workloads, CPU utilization is often a poor indicator of load. A model might be idle on the CPU but saturate the GPU VRAM or Compute cores.

!!! info "Why this matters"
    If you scale an LLM service based on CPU, you might find that the CPU stays at 10% while the GPU is at 100%, and the HPA never triggers. This results in massive latency for users despite having cluster capacity.

To solve this, you must use **Custom Metrics**. By installing the **NVIDIA Data Center GPU Manager (DCGM) Exporter**, you can expose GPU metrics to Prometheus. You then configure your HPA (via KEDA or the Prometheus Adapter) to scale based on `DCGM_FI_DEV_GPU_UTIL`.

## Summary Checklist

- [ ] Resource requests and limits are defined in the Deployment.
- [ ] Metrics Server is installed in the cluster.
- [ ] HPA target utilization is aligned with application performance profiles (includes a buffer).
- [ ] Max and min replica counts are set to prevent resource exhaustion.
- [ ] `stabilizationWindowSeconds` is configured to prevent flapping.
- [ ] Distinguish between reactive (CPU) and proactive (RPS/KEDA) scaling.
- [ ] Identify the correct metric (CPU vs GPU) for the specific AI workload.

## Assignments

!!! note "Assignment.1: Implementing HPA"
    Deploy the `web-service` and `web-service-hpa` provided in this chapter. Use a load testing tool (e.g., `hey` or `ab`) to generate traffic and observe the HPA scaling via `kubectl get hpa -w`.
    
    ??? tip "Solution: HPA Implementation"
        Apply both YAML manifests. Use `hey -z 2m -q 10 http://localhost:30007` to simulate load and watch the `REPLICAS` column in the `kubectl get hpa` output increase.

!!! note "Assignment.2: Scaling Sensitivity Analysis"
    Modify the HPA target utilization to 20% and observe how the scaling speed and replica count change compared to the 50% target.
    
    ??? tip "Solution: Sensitivity Analysis"
        Edit the `averageUtilization` field in the HPA manifest to 20. You will notice the cluster scales out much faster and maintains a higher number of pods for the same amount of traffic.

!!! note "Assignment.3: Designing a GPU Autoscaler"
    Draft a KEDA `ScaledObject` manifest that would scale an AI inference deployment based on a Prometheus query for `GPU_UTILIZATION > 70%`.
    
    ??? tip "Solution: GPU Autoscaler"
        The trigger type would be `prometheus`, and the query would target the DCGM metric `DCGM_FI_DEV_GPU_UTIL`. The threshold would be set to `70`.

## References

- Kubernetes HPA Documentation: [kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- KEDA Documentation: [keda.sh/docs/](https://keda.sh/docs/)
- Prometheus Adapter: [github.com/kubernetes-sigs/prometheus-adapter](https://github.com/kubernetes-sigs/prometheus-adapter)

## Self-Evaluation

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "Why are resource requests mandatory for CPU-based HPA?"
    HPA calculates utilization as a percentage of the requested resources. Without a defined request, the HPA cannot determine the current utilization percentage, as it has no baseline to compare the actual usage against.

??? question "What is the primary difference between Standard HPA and KEDA scaling?"
    Standard HPA is primarily reactive and relies on internal resource metrics (CPU/Memory), while KEDA is proactive and can scale based on external event sources and custom metrics, including the ability to scale to zero replicas.

??? question "In what scenario is RPS scaling preferred over CPU scaling?"
    RPS scaling is preferred for I/O-bound services where traffic spikes may cause latency increases or request queues to build up before the CPU usage significantly rises.

??? question "What is 'HPA Flapping' and how can it be mitigated?"
    Flapping is the rapid, repeated scaling up and down of pods due to small fluctuations in metrics. It is mitigated by configuring the `behavior` field in the HPA spec, specifically the `stabilizationWindowSeconds`, which forces the controller to wait before scaling in.

??? question "Why is a target utilization of 50-60% generally preferred over 90%?"
    Because pod startup is not instantaneous (image pulling, app initialization). A lower target provides a "headroom" buffer, allowing the existing pods to handle the load while new replicas are being provisioned.

??? question "Why is CPU-based HPA often insufficient for Large Language Model (LLM) inference services?"
    LLM inference is almost entirely GPU-bound. The CPU may remain largely idle while the GPU is fully saturated. An HPA based on CPU would fail to scale out during high load, leading to severe latency and timeouts.
