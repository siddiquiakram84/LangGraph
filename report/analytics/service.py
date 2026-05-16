import os
import json


class AnalyticsService:

    REPORT_DIR = "healing_reports"

    def get_reports(self):

        reports = []

        if not os.path.exists(self.REPORT_DIR):
            return reports

        for file in os.listdir(self.REPORT_DIR):

            if file.endswith(".json"):

                with open(os.path.join(self.REPORT_DIR, file)) as f:

                    reports.append(json.load(f))

        return reports

    def get_stats(self):

        reports = self.get_reports()

        total = len(reports)

        success = sum(1 for r in reports if r.get("success"))

        return {

            "total_healings": total,

            "successful_healings": success,

            "failed_healings": total - success,

            "success_rate": success / total if total else 0
        }

    def get_allure_trends(self):

        if not os.path.exists("allure-results"):
            return {}

        return {

            "allure_results_present": True,

            "results_count":
                len(os.listdir("allure-results"))
        }
