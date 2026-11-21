import dns.exception
import dns.resolver


class DnsChecker:
    """Resolve A, AAAA, MX, NS, and CNAME records for a domain."""

    def __init__(self, timeout: float = 3.0):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout

    def _query(self, domain: str, record_type: str):
        try:
            answers = self.resolver.resolve(domain, record_type, raise_on_no_answer=False)
            return [str(answer).rstrip(".") for answer in answers]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.NoAnswer, dns.exception.Timeout):
            return []
        except dns.resolver.LifetimeTimeout:
            return []

    def check(self, domain: str) -> dict:
        a = self._query(domain, "A")
        aaaa = self._query(domain, "AAAA")
        mx = self._query(domain, "MX")
        ns = self._query(domain, "NS")
        cname = self._query(domain, "CNAME")
        return {
            "a": a,
            "aaaa": aaaa,
            "mx": mx,
            "ns": ns,
            "cname": cname,
            "exists": bool(a or aaaa or mx or ns or cname),
        }
