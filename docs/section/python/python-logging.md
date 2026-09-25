# Logging and Monitoring for Distributed Cloud Systems

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Configure a production-ready logging system using the Python `logging` module.
    - Implement structured logging (JSON) to facilitate log aggregation in cloud environments.
    - Use logging filters to inject contextual information like `service_name` and `request_id`.
    - Integrate Python services with monitoring tools using the `prometheus_client` library.
    - Apply best practices for log levels, correlation IDs, and metric collection.

In a distributed cloud environment, a single request may traverse several services, containers, or serverless functions. When an error occurs, the only reliable source of information is the observability data emitted by each component:

- **Logging**: Records a chronological, immutable stream of events, errors, and diagnostic context.
- **Monitoring**: Aggregates numerical metrics (latency, error counts, resource usage) and raises alerts when thresholds are breached.

Together, these enable rapid root-cause analysis, performance baselines, compliance audit trails, and automated incident response.

---

## Core Logging Concepts

| Concept | Description |
|---------|-------------|
| **Logger hierarchy** | Loggers are named (e.g., `myapp.web`). Child loggers inherit configuration from their ancestors unless overridden. |
| **Handlers** | Destination for log records (console, file, network, cloud services). Multiple handlers can be attached to a logger. |
| **Formatters** | Convert a `LogRecord` into a string or structured payload (e.g., JSON). |
| **Levels** | Severity ordering: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| **Structured logging** | Emitting logs as JSON or key-value pairs makes them machine-readable, enabling downstream filtering and correlation. |

---

## Production-Ready Logging Configuration

A production-grade logging setup should satisfy these requirements:
- **JSON output**: For easy ingestion by log aggregation services (e.g., AWS CloudWatch, Google Cloud Logging, Elastic Stack).
- **Timed rotating files**: To bound disk usage and keep recent logs locally.
- **Separate handlers**: Human-readable output for the console and JSON for files.
- **Contextual information**: Automatic injection of `service_name` and `request_id` into every record.

```python
import logging
import logging.handlers
import json
import os
from datetime import datetime
import uuid

class JsonFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = {k: v for k, v in record.__dict__.items()
                  if k not in logging.LogRecord.__dict__ and k not in payload}
        if extra:
            payload.update(extra)
        return json.dumps(payload)

def configure_logging(service_name: str, log_dir: str = "logs"):
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.DEBUG)

    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_fmt)

    # File handler (JSON, rotate daily, keep 7 days)
    file_path = os.path.join(log_dir, f"{service_name}.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=file_path,
        when="midnight",
        backupCount=7,
        utc=True,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.service = service_name
            record.request_id = getattr(record, "request_id", str(uuid.uuid4()))
            return True

    logger.addFilter(ContextFilter())
    return logger

# Usage
logger = configure_logging("mycloudservice")
logger.info("Service initialized", extra={"port": 8080})
logger.error("Failed to process request", extra={"error_code": 502, "url": "/api/v1/resource"})
```

### Interpretation of JSON Logs

Each line in the resulting log file is a complete JSON object. This makes it trivial for aggregation platforms to parse and index. The `service` and `request_id` fields provide stable correlation keys across distributed components, while the file handler rotation ensures log volume remains bounded.

---

## Integrating Logs with Cloud Providers

| Cloud Provider | Recommended Sink | Typical Setup Steps |
|----------------|-----------------|--------------------|
| **AWS** | CloudWatch Logs | Install CloudWatch Agent and configure JSON log files as the source. |
| **Google Cloud** | Cloud Logging | Use `google-cloud-logging` library to create a `CloudLoggingHandler`. |
| **Azure** | Azure Monitor | Use `opencensus-ext-azure` exporter or Azure Monitor Agent. |
| **Kubernetes** | Loki / Fluent Bit | Ship logs via Fluent Bit with a JSON parser to Grafana. |

---

## Monitoring and Metrics Collection

While logging captures *what happened*, metrics capture *how the system is behaving over time*. A typical Python metrics stack includes:

1. **Metrics library**: `prometheus_client` is the industry standard.
2. **Instrumentation points**: Measuring request latency, error counters, and resource usage.
3. **Exporter**: An HTTP endpoint (`/metrics`) that Prometheus scrapes.
4. **Dashboard/Alerting**: Grafana for visualization and Alertmanager for threshold alerts.

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

REQUEST_LATENCY = Histogram('http_request_duration_seconds',
                            'HTTP request latency in seconds',
                            ['method', 'endpoint'])
ERRORS_TOTAL = Counter('http_errors_total',
                        'Total number of HTTP errors',
                        ['method', 'endpoint', 'status'])

def handle_request(method, endpoint):
    start = time.time()
    try:
        # Actual request handling logic
        pass
    except Exception:
        ERRORS_TOTAL.labels(method=method, endpoint=endpoint, status='500').inc()
        raise
    finally:
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        handle_request('GET', '/api/v1/resource')
        time.sleep(1)
```

---

## Best Practices

| Area | Recommendation |
|------|----------------|
| **Log levels** | Use `DEBUG` for dev, `INFO` for normal ops, `WARNING` for recoverable issues, `ERROR` for failures, `CRITICAL` for crashes. |
| **Structured fields** | Include immutable identifiers (`request_id`, `trace_id`), service name, and version. |
| **Correlation** | Propagate `request_id` or `trace_id` via HTTP headers (e.g., `X-Request-ID`) and inject them via a logging filter. |
| **Retention** | Keep raw logs for a period required by compliance and archive older logs to object storage. |
| **Performance** | Use asynchronous handlers (e.g., `QueueHandler`) to prevent logging I/O from blocking requests. |
| **Security** | Sanitize sensitive data (passwords, tokens) before logging using a redaction filter. |
| **Alerting** | Base alerts on metrics; use log-based alerts sparingly. |
| **Testing** | Use `caplog` (pytest) to assert proper log emission in unit tests. |

---

## Common Pitfalls and Mitigations

| Pitfall | Mitigation |
|---------|------------|
| **Excessive log volume** | Log stack traces only for `ERROR`/`CRITICAL` levels and rotate files frequently. |
| **Inconsistent field names** | Define a shared logging schema and enforce it via code reviews. |
| **Blocking I/O** | Use a non-blocking queue (`logging.handlers.QueueHandler`) and a separate listener process. |
| **Missing correlation IDs** | Generate a UUID at the entry point and propagate it via headers. |
| **Over-reliance on logs** | Emit explicit metrics (counters, histograms) alongside logs. |

---

## Assignments

!!! note "Assignment: Observability Implementation"
    1. **Logging Setup**: Implement the `JsonFormatter` and `configure_logging` function in a Python project.
    2. **Correlation ID**: Create a middleware or decorator that generates a `request_id` and injects it into the logging context.
    3. **Metrics**: Integrate `prometheus_client` to track the number of requests and the average latency of a specific function.
    4. **Verification**: Run the service, generate logs, and verify that each log entry contains the same `request_id` for a a single request.

---

## Self-Evaluation

??? note "What is the difference between logging and monitoring in a distributed system?"
    Logging records a chronological stream of discrete events and errors (the "what happened"), while monitoring aggregates numerical metrics like latency and error rates to track system health (the "how is it performing").

??? note "What is 'structured logging' and why is it preferred for cloud-native applications?"
    Structured logging involves emitting logs as machine-readable formats (typically JSON) rather than plain text. This allows log aggregation tools to filter, query, and analyze logs efficiently based on specific fields.

??? note "How do correlation IDs (like `request_id`) facilitate troubleshooting in a microservices architecture?"
    A correlation ID is generated at the entry point of a request and propagated via HTTP headers to all downstream services. By including this ID in every log record, engineers can trace the entire lifecycle of a single request across multiple services.
