import os
import sys
import argparse
import subprocess
import json
import time

from analytics.service import AnalyticsService


class HealingTestRunner:

    def __init__(self):

        self.analytics = AnalyticsService()

    def run_tests(self, test_path=None, verbose=True):

        project_root = os.path.dirname(os.path.abspath(__file__))

        venv_python = os.path.join(project_root, "venv", "bin", "python")

        if not os.path.exists(venv_python):
            raise Exception("Virtual environment python not found")

        cmd = [venv_python, "-m", "pytest"]

        if verbose:
            cmd.extend(["-s", "-v"])

        if test_path:
            cmd.append(test_path)

        print(f"\n[Runner] Executing: {' '.join(cmd)}\n")

        result = subprocess.run(
            cmd,
            cwd=project_root
        )

        return result.returncode

    def print_healing_summary(self):

        stats = self.analytics.get_stats()

        print("\n========== Healing Summary ==========\n")

        print(f"Total Healings      : {stats['total_healings']}")
        print(f"Successful Healings : {stats['successful_healings']}")
        print(f"Failed Healings     : {stats['failed_healings']}")
        print(f"Success Rate        : {stats['success_rate']:.2%}")

        print("\n=====================================\n")

    def clean_memory(self):

        dirs = ["healing_memory", "healing_reports", "healing_backups"]

        for d in dirs:

            if os.path.exists(d):

                for f in os.listdir(d):

                    path = os.path.join(d, f)

                    if os.path.isfile(path):

                        os.remove(path)

        print("[Runner] Healing memory cleaned.")

    def run(self, args):

        if args.clean:

            self.clean_memory()

        exit_code = self.run_tests(args.test)

        self.print_healing_summary()

        return exit_code


def main():

    parser = argparse.ArgumentParser(
        description="AI Self-Healing Automation Test Runner"
    )

    parser.add_argument(
        "--test",
        help="Run specific test file or folder",
        required=False
    )

    parser.add_argument(
        "--clean",
        help="Clean healing memory before execution",
        action="store_true"
    )

    args = parser.parse_args()

    runner = HealingTestRunner()

    exit_code = runner.run(args)

    sys.exit(exit_code)


if __name__ == "__main__":

    main()
