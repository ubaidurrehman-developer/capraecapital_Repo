import unittest
import requests
import json
import csv
import io

BASE_URL = "http://127.0.0.1:8080"

class TestSaaSquatchPlatform(unittest.TestCase):

    def test_01_health_and_stats(self):
        res = requests.get(f"{BASE_URL}/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_leads", data)
        self.assertIn("verified_leads", data)
        self.assertIn("avg_icp_score", data)
        self.assertGreater(data["total_leads"], 0)

    def test_02_list_and_filter_leads(self):
        # Query with high ICP
        res = requests.get(f"{BASE_URL}/api/leads?min_icp=80&sort_by=icp_score&sort_dir=desc")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        leads = data.get("leads", [])
        self.assertGreater(len(leads), 0)
        for lead in leads:
            self.assertGreaterEqual(lead["icp_score"], 80)
            self.assertTrue(lead["domain"])
            self.assertTrue(lead["company_name"])

    def test_03_scrape_and_deduplicate(self):
        # Scrape a domain
        payload = {"url_or_domain": "zapier.com", "auto_enrich": True}
        res1 = requests.post(f"{BASE_URL}/api/leads/scrape", json=payload)
        self.assertEqual(res1.status_code, 200)
        lead1 = res1.json().get("lead")
        self.assertEqual(lead1["domain"], "zapier.com")
        self.assertTrue(lead1["ai_summary"])
        self.assertGreater(len(lead1["acquisition_signals"]), 0)

        # Scrape the same domain again (verifying deduplication)
        res2 = requests.post(f"{BASE_URL}/api/leads/scrape", json=payload)
        self.assertEqual(res2.status_code, 200)
        lead2 = res2.json().get("lead")
        self.assertEqual(lead1["domain"], lead2["domain"])

    def test_04_ai_outreach_generation(self):
        # Get any lead
        leads_res = requests.get(f"{BASE_URL}/api/leads")
        lead = leads_res.json()["leads"][0]
        lead_id = lead["id"]

        for outreach_type in ["pe_acquisition", "founder_to_founder", "saas_growth"]:
            payload = {
                "lead_id": lead_id,
                "outreach_type": outreach_type,
                "custom_angle": "Impressive market penetration in core segment"
            }
            res = requests.post(f"{BASE_URL}/api/leads/{lead_id}/outreach", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("subject", data)
            self.assertIn("body", data)
            self.assertIn("key_talking_points", data)
            self.assertIn("suggested_follow_up_days", data)
            self.assertIn(lead["company_name"], data["subject"])

    def test_05_csv_and_json_exports(self):
        # Test CSV export
        csv_res = requests.get(f"{BASE_URL}/api/export/csv")
        self.assertEqual(csv_res.status_code, 200)
        reader = csv.reader(io.StringIO(csv_res.text))
        header = next(reader)
        self.assertIn("domain", header)
        self.assertIn("icp_score", header)
        first_row = next(reader)
        self.assertTrue(len(first_row) > 5)

        # Test JSON export
        json_res = requests.get(f"{BASE_URL}/api/export/json")
        self.assertEqual(json_res.status_code, 200)
        leads_json = json_res.json()
        self.assertIsInstance(leads_json, list)
        self.assertGreater(len(leads_json), 0)

if __name__ == "__main__":
    unittest.main()
