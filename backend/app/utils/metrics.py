"""In-memory HTTP metrics for the Prometheus-compatible endpoint.

Purpose:
    Provide lightweight request counters and latency sums before a full metrics
    backend is introduced.
Responsibilities:
    Track route/method/status counts and expose Prometheus text format.
Dependencies:
    FastAPI request middleware.
Usage:
    app.middleware("http")(metrics_middleware)
    render_prometheus_metrics()
"""

import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from fastapi import Request, Response


_request_counts: dict[tuple[str, str, int], int] = defaultdict(int)
_request_latency_seconds: dict[tuple[str, str], list[float]] = defaultdict(list)


async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Record basic request counts and durations."""

    start = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start

    handler = request.scope.get("route").path if request.scope.get("route") else request.url.path
    _request_counts[(request.method, handler, response.status_code)] += 1
    _request_latency_seconds[(request.method, handler)].append(latency)
    return response


def render_prometheus_metrics() -> str:
    """Render currently tracked metrics in Prometheus text exposition format."""

    lines = [
        "# HELP http_requests_total Total number of HTTP requests.",
        "# TYPE http_requests_total counter",
    ]
    for (method, handler, status), count in sorted(_request_counts.items()):
        lines.append(
            f'http_requests_total{{method="{method}",handler="{handler}",status="{status}"}} {count}'
        )

    lines.extend(
        [
            "# HELP request_latency_seconds HTTP request latency in seconds.",
            "# TYPE request_latency_seconds summary",
        ]
    )
    for (method, handler), values in sorted(_request_latency_seconds.items()):
        count = len(values)
        total = sum(values)
        lines.append(f'request_latency_seconds_count{{method="{method}",handler="{handler}"}} {count}')
        lines.append(f'request_latency_seconds_sum{{method="{method}",handler="{handler}"}} {total:.6f}')

    return "\n".join(lines) + "\n"
