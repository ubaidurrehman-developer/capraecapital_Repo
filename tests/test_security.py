import unittest
import requests
import io
import csv

BASE_URL = "http://127.0.0.1:8080"

class TestSecurityProtections(unittest.TestCase):

    def test_01_security_headers_present(self):
        """Verify defense-in-depth HTTP security headers."""
        res = requests.get(f"{BASE_URL}/api/stats")
        self.assertEqual(res.status_code, 200)
        headers = res.headers
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("default-src 'self'", headers.get("Content-Security-Policy", ""))

    def test_02_ssrf_protection_blocks_private_and_loopback_ips(self):
        """Verify that SSRF attempts targeting localhost/private IPs are blocked."""
        restricted_targets = [
            "localhost",
            "127.0.0.1",
            "169.254.169.254",
            "0.0.0.0",
            "http://10.0.0.1",
            "http://192.168.1.1"
        ]
        for target in restricted_targets:
            res = requests.post(f"{BASE_URL}/api/leads/scrape", json={"url_or_domain": target})
            self.assertEqual(res.status_code, 400, f"Expected 400 for SSRF target {target}")
            self.assertTrue(
                "security" in res.text.lower() or "invalid" in res.text.lower() or "restricted" in res.text.lower()
            )

    def test_03_domain_syntax_validation(self):
        """Verify invalid domain syntax or command-injection-like inputs are rejected."""
        malformed_inputs = [
            "google.com; cat /etc/passwd",
            "test<script>alert(1)</script>.com",
            "../../../etc/hosts",
            "ftp://ftp.secure.com",
            ""
        ]
        for inp in malformed_inputs:
            res = requests.post(f"{BASE_URL}/api/leads/scrape", json={"url_or_domain": inp})
            self.assertEqual(res.status_code, 400)

    def test_04_sql_injection_defense_on_sorting(self):
        """Verify that SQL injection payloads in sort parameters are strictly blocked."""
        malicious_sort = "icp_score; DROP TABLE leads;--"
        res = requests.get(f"{BASE_URL}/api/leads?sort_by={malicious_sort}")
        # FastAPI query validation regex rejects invalid choices with 422 Unprocessable Entity
        self.assertEqual(res.status_code, 422)

    def test_05_csv_formula_injection_mitigation(self):
        """Verify that CSV cells starting with dangerous spreadsheet operators are neutralized."""
        from backend.main import sanitize_csv_cell
        self.assertEqual(sanitize_csv_cell("=1+1"), "'=1+1")
        self.assertEqual(sanitize_csv_cell("@SUM(A1:A10)"), "'@SUM(A1:A10)")
        self.assertEqual(sanitize_csv_cell("-5+2"), "'-5+2")
        self.assertEqual(sanitize_csv_cell("+cmd"), "'+cmd")
        self.assertEqual(sanitize_csv_cell("Safe Company Name"), "Safe Company Name")

if __name__ == "__main__":
    unittest.main()
