#!/usr/bin/env python3
"""
Squad Config Validator - Validates OpenSeneca squad agent configurations
Checks for best practices, common issues, and generates health scores.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class ConfigValidator:
    """Validates OpenSeneca squad configuration files."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.score = 100
        self.max_deductions = 0

    def validate_config(self, config_path: str) -> Dict:
        """Validate a single configuration file."""
        config = self._load_config(config_path)
        if not config:
            return self._generate_report(config_path, config)

        # Run validation checks
        self._check_required_keys(config)
        self._check_agent_name_format(config)
        self._check_cron_schedule(config)
        self._check_tool_paths(config)
        self._check_api_keys(config)
        self._check_logging_config(config)

        return self._generate_report(config_path, config)

    def _load_config(self, config_path: str) -> Dict:
        """Load and parse configuration file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.issues.append(f"Config file not found: {config_path}")
            self.score -= 20
            self.max_deductions += 20
            return {}
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in {config_path}: {str(e)}")
            self.score -= 30
            self.max_deductions += 30
            return {}

    def _check_required_keys(self, config: Dict):
        """Check for required configuration keys."""
        required_keys = ['agent_name', 'role', 'heartbeat_interval']
        missing = [k for k in required_keys if k not in config]
        if missing:
            self.issues.append(f"Missing required keys: {', '.join(missing)}")
            self.score -= 15
            self.max_deductions += 15

    def _check_agent_name_format(self, config: Dict):
        """Check agent name follows naming convention."""
        if 'agent_name' not in config:
            return
        name = config['agent_name']
        if not name.lower() in ['seneca', 'marcus', 'galen', 'archimedes', 'argus']:
            self.warnings.append(f"Agent name '{name}' not in standard squad names")

    def _check_cron_schedule(self, config: Dict):
        """Check cron schedule is reasonable."""
        if 'cron_schedule' in config:
            schedule = config['cron_schedule']
            if not schedule or schedule == "* * * * *":
                self.issues.append("Cron schedule too frequent or missing")
                self.score -= 10
                self.max_deductions += 10

    def _check_tool_paths(self, config: Dict):
        """Check tool paths are valid."""
        if 'tool_paths' in config:
            for tool, path in config['tool_paths'].items():
                if not os.path.exists(path):
                    self.warnings.append(f"Tool path not found: {tool} -> {path}")

    def _check_api_keys(self, config: Dict):
        """Check API keys are properly configured."""
        if 'api_keys' in config:
            for service, key in config['api_keys'].items():
                if not key or key == 'your_api_key_here':
                    self.issues.append(f"API key placeholder for {service}")
                    self.score -= 10
                    self.max_deductions += 10

    def _check_logging_config(self, config: Dict):
        """Check logging configuration."""
        if 'logging' in config:
            if 'level' not in config['logging']:
                self.warnings.append("Logging level not specified")

    def _generate_report(self, config_path: str, config: Dict) -> Dict:
        """Generate validation report."""
        # Calculate final score (0-100)
        final_score = max(0, min(100, self.score))

        return {
            "config_file": config_path,
            "agent_name": config.get('agent_name', 'unknown'),
            "score": final_score,
            "max_score": 100,
            "deductions": self.max_deductions,
            "issues_count": len(self.issues),
            "warnings_count": len(self.warnings),
            "issues": self.issues,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat()
        }


def validate_all_configs(config_dir: str) -> List[Dict]:
    """Validate all configs in directory."""
    config_path = Path(config_dir)
    if not config_path.exists():
        print(f"Config directory not found: {config_dir}")
        return []

    results = []
    for config_file in sorted(config_path.glob("**/*.json")):
        validator = ConfigValidator()
        report = validator.validate_config(str(config_file))
        results.append(report)

    return results


def generate_summary(results: List[Dict]) -> Dict:
    """Generate summary statistics."""
    if not results:
        return {"total": 0, "avg_score": 0}

    total = len(results)
    avg_score = sum(r['score'] for r in results) / total
    failing = len([r for r in results if r['score'] < 70])
    passing = len([r for r in results if r['score'] >= 70])

    return {
        "total_configs": total,
        "average_score": round(avg_score, 1),
        "passing_configs": passing,
        "failing_configs": failing,
        "total_issues": sum(r['issues_count'] for r in results),
        "total_warnings": sum(r['warnings_count'] for r in results)
    }


def save_reports(results: List[Dict], output_dir: str):
    """Save validation reports to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save individual reports
    for report in results:
        agent_name = report['agent_name']
        report_file = output_path / f"squad-config-validator-{agent_name}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

    # Save summary
    summary = generate_summary(results)
    summary_file = output_path / "squad-config-validator-summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Reports saved to: {output_dir}")
    print(f"Summary: {summary}")


def main():
    """Main entry point."""
    config_dir = os.path.expanduser("~/.openclaw/workspace/configs")
    output_dir = os.path.expanduser("~/.openclaw/workspace/outputs")

    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Squad Config Validator")
            print("Validates OpenSeneca squad agent configurations")
            print("")
            print("Usage:")
            print("  squad-config-validator [options]")
            print("")
            print("Options:")
            print("  --help     Show this help message")
            print("  --dir DIR  Specify config directory (default: ~/.openclaw/workspace/configs)")
            return

        if sys.argv[1] == "--dir":
            if len(sys.argv) > 2:
                config_dir = sys.argv[2]
            else:
                print("Error: --dir requires a directory path")
                return

    results = validate_all_configs(config_dir)

    if results:
        save_reports(results, output_dir)
    else:
        print("No config files found or validation failed")


if __name__ == "__main__":
    main()