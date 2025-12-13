import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class DataValidator:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.config_path = self.root / "config" / "content_index.yaml"
        self.data_path = self.root / "data" / "programs"

    def validate_all(self):
        """Main validation routine."""
        logger.info("Starting Systematic Data Review (Comprehensive)...")

        # 1. Load Index
        if not self.config_path.exists():
            logger.error(f"❌ Config index not found at {self.config_path}")
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f)

        programs_list = index_data.get("programs", [])
        programs_count = len(programs_list) if programs_list else 0
        logger.info(f"ℹ️ Found {programs_count} programs in index.")

        results = {
            "missing_files": [],
            "issues": {},  # code -> list of issues
        }

        # 2. Iterate and Validate
        valid_count = 0
        for entry in programs_list:
            code = entry.get("code")
            rel_path = entry.get("path")
            full_path = self.root / rel_path

            if not full_path.exists():
                logger.error(f"❌ File missing for {code}: {rel_path}")
                results["missing_files"].append(code)
                continue

            program_issues = []
            try:
                with open(full_path, "r", encoding="utf-8") as pf:
                    prog_data = yaml.safe_load(pf)
                    program = prog_data.get("program", {})

                    if not program:
                        program_issues.append("Structure: Root 'program' key missing")
                    else:
                        # --- Basic Fields ---
                        for field in [
                            "code",
                            "title",
                            "degree_level",
                            "faculty",
                            "language_of_instruction",
                            "duration_semesters",
                            "ects_total",
                        ]:
                            if not program.get(field):
                                program_issues.append(f"Basic: Missing '{field}'")

                        # --- Intakes ---
                        intakes = program.get("intakes", [])
                        if not intakes:
                            program_issues.append("Intakes: Missing or empty")
                        else:
                            for intake in intakes:
                                if not intake.get("term") or not intake.get(
                                    "application_window"
                                ):
                                    program_issues.append(
                                        "Intakes: Incomplete intake data"
                                    )

                        # --- Portal ---
                        portal = program.get("application_portal", {})
                        if not portal or not portal.get("url"):
                            program_issues.append("Portal: Missing application URL")

                        # --- Contacts ---
                        contacts = program.get("contacts", {})
                        if not contacts:
                            program_issues.append("Contacts: Missing section")
                        elif not contacts.get("admissions_email"):
                            program_issues.append("Contacts: Missing admissions email")

                        # --- Eligibility ---
                        eligibility = program.get("eligibility", {})
                        if not eligibility:
                            program_issues.append("Eligibility: Missing section")
                        else:
                            if not eligibility.get("academic_background"):
                                program_issues.append(
                                    "Eligibility: Missing academic background"
                                )
                            if not eligibility.get("language_requirements"):
                                program_issues.append(
                                    "Eligibility: Missing language requirements"
                                )

                        # --- Fees ---
                        fees = program.get("fees", {})
                        if not fees:
                            program_issues.append("Fees: Missing section")
                        elif not any(fees.values()):  # Check if any category has data
                            program_issues.append("Fees: All fee categories empty")

                        # --- Documents ---
                        docs = program.get("required_documents", {})
                        if not docs:
                            program_issues.append("Docs: Missing section")
                        elif not docs.get("international_non_eu"):
                            program_issues.append(
                                "Docs: Missing International requirements"
                            )

                        # --- Policies ---
                        policies = program.get("policies", {})
                        if not policies:
                            program_issues.append("Policies: Missing section")

            except Exception as e:
                logger.error(f"⚠️ Error parsing {code}: {e}")
                program_issues.append(f"Parse Error: {e}")

            if program_issues:
                results["issues"][code] = program_issues
            else:
                valid_count += 1

        # 3. Report
        self._print_report(results, valid_count)

    def _print_report(self, results: Dict, valid_count: int):
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE DATA REVIEW REPORT")
        print("=" * 60)
        total = valid_count + len(results["missing_files"]) + len(results["issues"])
        print(f"📂 Total Programs Scanned: {total}")
        print(
            f"✅ Fully Valid Programs:   {valid_count} ({(valid_count / total if total > 0 else 0) * 100:.1f}%)"
        )
        print(f"❌ Programs with Issues:    {len(results['issues'])}")
        print(f"🚫 Missing Files:          {len(results['missing_files'])}")
        print("-" * 60)

        if results["issues"]:
            print("\n⚠️  DETAILED ISSUES BY PROGRAM:")
            for code, issues in results["issues"].items():
                print(f"\n🔹 {code}:")
                for issue in issues:
                    print(f"   - {issue}")

        if results["missing_files"]:
            print("\n🚫 MISSING FILES:")
            for f in results["missing_files"]:
                print(f"   - {f}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    validator = DataValidator()
    validator.validate_all()
