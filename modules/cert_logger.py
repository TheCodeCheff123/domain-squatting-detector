import requests


class CertificateTransparencyLogger:
    """Retrieve and normalize Certificate Transparency entries from crt.sh."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.endpoint = "https://crt.sh/"

    def query(self, domain: str, limit: int = 100) -> list[dict]:
        try:
            response = requests.get(
                self.endpoint,
                params={"q": f"%.{domain}", "output": "json"},
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        records = []
        for item in payload[:limit] if isinstance(payload, list) else []:
            records.append({
                "id": item.get("id"),
                "name_value": item.get("name_value"),
                "issuer_name": item.get("issuer_name"),
                "not_before": item.get("not_before"),
                "not_after": item.get("not_after"),
            })
        return records
