import os
import requests
import urllib.parse
from typing import Dict, Optional, Any


class PrometheusClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url or os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        self.timeout = timeout

    def _query(self, promql: str) -> Optional[Dict[str, Any]]:
        encoded = urllib.parse.quote(promql, safe="")
        url = f"{self.base_url}/api/v1/query?query={encoded}"
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            print(resp.json())
            return resp.json()
        except requests.RequestException:
            return None

    def _extract_single_value(self, data: Dict[str, Any]) -> Optional[float]:
        try:
            value = data["data"]["result"][0]["value"][1]
            return 0 if value == 'NaN' else float(value)  # Check for NaN (NaN != NaN)
        except Exception:
            return None

    def cpu_usage_percentage(self, pod_regex: str, window: str = "5m") -> Optional[float]:
        query = f"""
        avg(
          100 * (
            sum by(pod)(
              rate(container_cpu_usage_seconds_total{{pod=~"{pod_regex}"}}[{window}])
            )
            /
            sum by(pod)(
              kube_pod_container_resource_limits{{resource="cpu", pod=~"{pod_regex}"}}
            )
          )
        )
        """
        data = self._query(query)
        return self._extract_single_value(data) if data else None

    def request_rate_by_instance(
        self,
        job: str = "fastapi",
        exclude_handler: str = "/metrics",
        window: str = "1m",
    ) -> Dict[str, Optional[float]]:
        query = (
            f'sum by (instance) (rate(http_requests_total{{job="{job}", handler!="{exclude_handler}"}}[{window}]))'
        )
        data = self._query(query)
        results = {}
        if not data:
            return results
        for item in data.get("data", {}).get("result", []):
            instance = item.get("metric", {}).get("instance", "<unknown>")
            try:
                results[instance] = float(item["value"][1])
            except Exception:
                results[instance] = None
        return results

    def p99_latency(
        self,
        handler: str,
        job: str = "fastapi-pods",
        window: str = "5m",
        quantile: float = 0.99,
    ) -> Optional[float]:
        query = f"""
        histogram_quantile(
          {quantile},
          sum by (le, handler) (
            rate(http_request_duration_seconds_bucket{{job="{job}", handler="{handler}"}}[{window}])
          )
        )
        """
        data = self._query(query)
        return self._extract_single_value(data) if data else None


if __name__ == "__main__":
    client = PrometheusClient()
    print(client.p99_latency("/heroes/{hero_id}"))
