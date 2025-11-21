#!/usr/bin/env python3
"""
Data Validation Script

Validates the structure and quality of scraped content.
Ensures all required fields are present and content meets quality standards.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from colorama import init, Fore, Style

# Initialize colorama
init()

# Directories
SCRIPT_DIR = Path(__file__).parent
RAW_DATA_DIR = SCRIPT_DIR.parent / "data" / "raw"

# Validation rules
REQUIRED_FIELDS = ["id", "title", "category", "content", "tags"]
OPTIONAL_FIELDS = ["source", "url", "difficulty", "timestamp"]
MIN_CONTENT_LENGTH = 100
MAX_CONTENT_LENGTH = 50000
MIN_TAGS = 1
MAX_TAGS = 10

VALID_CATEGORIES = [
    "scalability", "performance", "databases", "api-design",
    "architecture", "security", "caching", "messaging",
    "storage", "networking"
]

VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced"]


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    filename: str
    field: str
    message: str
    type: str  # 'error' or 'warning'


@dataclass
class ValidationResults:
    """Tracks validation results"""
    errors: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    passed: int = 0
    failed: int = 0

    def add_error(self, filename: str, field: str, message: str):
        """Add an error"""
        self.errors.append(ValidationIssue(filename, field, message, "error"))

    def add_warning(self, filename: str, field: str, message: str):
        """Add a warning"""
        self.warnings.append(ValidationIssue(filename, field, message, "warning"))

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def print_summary(self):
        """Print validation results"""
        print(f"\n{Fore.CYAN}📊 Validation Results{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}✅ Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Failed: {self.failed}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Warnings: {len(self.warnings)}{Style.RESET_ALL}\n")

        if self.errors:
            print(f"{Fore.RED}❌ ERRORS:{Style.RESET_ALL}\n")
            for err in self.errors:
                print(f"   {Fore.RED}File: {err.filename}{Style.RESET_ALL}")
                print(f"   {Fore.RED}Field: {err.field}{Style.RESET_ALL}")
                print(f"   {Fore.RED}Issue: {err.message}{Style.RESET_ALL}\n")

        if self.warnings:
            print(f"{Fore.YELLOW}⚠️  WARNINGS:{Style.RESET_ALL}\n")
            for warn in self.warnings:
                print(f"   {Fore.YELLOW}File: {warn.filename}{Style.RESET_ALL}")
                print(f"   {Fore.YELLOW}Field: {warn.field}{Style.RESET_ALL}")
                print(f"   {Fore.YELLOW}Issue: {warn.message}{Style.RESET_ALL}\n")

        if not self.errors and not self.warnings:
            print(f"{Fore.GREEN}🎉 All validations passed!{Style.RESET_ALL}\n")


def validate_content(filename: str, data: Dict, results: ValidationResults) -> bool:
    """
    Validate a single content item
    
    Args:
        filename: Name of the file being validated
        data: Content data dictionary
        results: ValidationResults object to track issues
    
    Returns:
        bool: True if valid, False otherwise
    """
    is_valid = True

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            results.add_error(filename, field, f"Missing required field: {field}")
            is_valid = False

    if not is_valid:
        return False  # Skip further validation if required fields missing

    # Validate ID format
    if not re.match(r'^[a-z0-9-]+$', data["id"]):
        results.add_error(
            filename, "id",
            "ID must contain only lowercase letters, numbers, and hyphens"
        )
        is_valid = False

    # Validate title
    title_len = len(data["title"])
    if title_len < 10 or title_len > 200:
        results.add_warning(
            filename, "title",
            f"Title length should be between 10-200 characters (current: {title_len})"
        )

    # Validate category
    if data["category"] not in VALID_CATEGORIES:
        results.add_warning(
            filename, "category",
            f"Category '{data['category']}' is not in predefined list. "
            f"Consider using: {', '.join(VALID_CATEGORIES)}"
        )

    # Validate content length
    content_len = len(data["content"])
    if content_len < MIN_CONTENT_LENGTH:
        results.add_error(
            filename, "content",
            f"Content too short: {content_len} characters (minimum: {MIN_CONTENT_LENGTH})"
        )
        is_valid = False
    elif content_len > MAX_CONTENT_LENGTH:
        results.add_error(
            filename, "content",
            f"Content too long: {content_len} characters (maximum: {MAX_CONTENT_LENGTH})"
        )
        is_valid = False

    # Validate tags
    if not isinstance(data["tags"], list):
        results.add_error(filename, "tags", "Tags must be an array")
        is_valid = False
    else:
        tags_count = len(data["tags"])
        if tags_count < MIN_TAGS:
            results.add_error(
                filename, "tags",
                f"Too few tags: {tags_count} (minimum: {MIN_TAGS})"
            )
            is_valid = False
        elif tags_count > MAX_TAGS:
            results.add_warning(
                filename, "tags",
                f"Many tags: {tags_count} (recommended maximum: {MAX_TAGS})"
            )

        # Check for empty tags
        empty_tags = [tag for tag in data["tags"] if not tag or not tag.strip()]
        if empty_tags:
            results.add_error(filename, "tags", "Contains empty tags")
            is_valid = False

        # Check for duplicate tags
        if len(data["tags"]) != len(set(data["tags"])):
            results.add_warning(filename, "tags", "Contains duplicate tags")

    # Validate optional fields if present
    if "difficulty" in data and data["difficulty"] not in VALID_DIFFICULTIES:
        results.add_warning(
            filename, "difficulty",
            f"Difficulty '{data['difficulty']}' should be one of: {', '.join(VALID_DIFFICULTIES)}"
        )

    if "url" in data and data["url"] and not data["url"].startswith("http"):
        results.add_warning(
            filename, "url",
            "URL should start with http:// or https://"
        )

    if "timestamp" in data and data["timestamp"]:
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            results.add_error(filename, "timestamp", "Invalid timestamp format")
            is_valid = False

    return is_valid


def validate_all_content() -> ValidationResults:
    """
    Validate all content files
    
    Returns:
        ValidationResults: Validation results
    """
    print(f"{Fore.CYAN}🔍 Starting content validation...{Style.RESET_ALL}\n")

    if not RAW_DATA_DIR.exists():
        print(f"{Fore.RED}❌ Error: Directory not found: {RAW_DATA_DIR}{Style.RESET_ALL}")
        exit(1)

    files = [f for f in RAW_DATA_DIR.glob("*.json") if f.name != "index.json"]

    if not files:
        print(f"{Fore.RED}❌ Error: No JSON files found to validate{Style.RESET_ALL}")
        exit(1)

    print(f"{Fore.BLUE}📁 Found {len(files)} files to validate{Style.RESET_ALL}\n")

    results = ValidationResults()

    for filepath in files:
        filename = filepath.name
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                results.add_error(filename, "file", f"Invalid JSON: {e}")
                results.failed += 1
                continue

            is_valid = validate_content(filename, data, results)

            if is_valid:
                print(f"{Fore.GREEN}✅ {filename}{Style.RESET_ALL}")
                results.passed += 1
            else:
                print(f"{Fore.RED}❌ {filename}{Style.RESET_ALL}")
                results.failed += 1

        except Exception as e:
            print(f"{Fore.RED}❌ Error processing {filename}: {e}{Style.RESET_ALL}")
            results.failed += 1

    return results


def generate_report() -> Dict:
    """
    Generate validation report with statistics
    
    Returns:
        Dict: Report data
    """
    results = ValidationResults()

    files = [f for f in RAW_DATA_DIR.glob("*.json") if f.name != "index.json"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "totalFiles": len(files),
        "passed": 0,
        "failed": 0,
        "categories": {},
        "difficulties": {},
        "totalContent": 0,
        "avgContentLength": 0,
        "totalTags": set()
    }

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if validate_content(filepath.name, data, results):
                report["passed"] += 1
            else:
                report["failed"] += 1

            # Collect statistics
            category = data.get("category", "unknown")
            report["categories"][category] = report["categories"].get(category, 0) + 1

            if "difficulty" in data:
                diff = data["difficulty"]
                report["difficulties"][diff] = report["difficulties"].get(diff, 0) + 1

            report["totalContent"] += len(data.get("content", ""))
            
            for tag in data.get("tags", []):
                report["totalTags"].add(tag)

        except Exception:
            report["failed"] += 1

    if files:
        report["avgContentLength"] = round(report["totalContent"] / len(files))
    report["totalTags"] = len(report["totalTags"])

    # Save report
    report_path = RAW_DATA_DIR / "validation-report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{Fore.BLUE}📄 Validation report saved to: {report_path}{Style.RESET_ALL}")

    return report


def main():
    """Main execution"""
    import sys
    
    results = validate_all_content()
    results.print_summary()

    if "--report" in sys.argv:
        report = generate_report()
        print(f"\n{Fore.CYAN}📈 Statistics:{Style.RESET_ALL}")
        print(f"   Total content: {report['totalContent']:,} characters")
        print(f"   Average length: {report['avgContentLength']:,} characters")
        print(f"   Unique tags: {report['totalTags']}")
        print(f"   Categories: {', '.join(report['categories'].keys())}")

    return 0 if not results.has_errors() else 1


if __name__ == "__main__":
    exit(main())