#!/usr/bin/env python3
"""
Squad Config Validator - Validates squad agent configurations.

Ensures all agents have correct setup for reliable operation:
- Cron jobs for scheduled tasks
- SSH keys for remote access
- Tool installations
- Environment variables

Usage:
    python3 main.py --local
    python3 main.py --agent seneca
    python3 main.py --all-agents
    python3 main.py --agent seneca --fix
    python3 main.py --local --output json
"""

import os
import sys
import subprocess
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Squad agent configuration
SQUAD_AGENTS = {
    "seneca": "100.101.15.68",
    "marcus": "100.98.223.103",
    "galen": "100.123.121.125",
    "argus": "100.108.219.91",
    "archimedes": "100.100.56.102",
    "clutch": "100.93.69.117"
}

# Required cron jobs
REQUIRED_CRONS = {
    "content-pipeline": {
        "schedule": "0 8 * * *",
        "script": "~/.openclaw/scripts/run-content-digest.sh"
    },
    "axon-ingester": {
        "schedule": "0 * * * *",
        "script": "~/.openclaw/scripts/run-axon-auto-ingester.sh"
    }
}

# Required tools (Python packages)
REQUIRED_PYTHON_TOOLS = [
    "squad-content-pipeline"
]

# Required workspace tools (local directories)
REQUIRED_WORKSPACE_TOOLS = [
    # squad-dashboard - archived 2026-05-10, not actively used
]

# Required environment variables (optional)
OPTIONAL_ENV_VARS = [
    "OPENCLAW_HOME"
]

# SSH key configuration
SSH_KEY_NAME = "squad_ed25519"


def run_command(cmd: List[str], check: bool = True, capture: bool = True, timeout: int = 30) -> Tuple[int, str, str]:
    """Run a command and return returncode, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except Exception as e:
        return 1, "", str(e)


def check_cron_jobs(agent: str = "local", fix: bool = False) -> Dict:
    """Check required cron jobs."""
    result = {
        "status": "PASS",
        "items": []
    }

    if agent == "local":
        # Check local crontab
        _, crontab_output, _ = run_command(["crontab", "-l"], check=False)
    else:
        # Check remote crontab via SSH
        ip = SQUAD_AGENTS[agent]
        _, crontab_output, _ = run_command(
            ["ssh", ip, "crontab -l"],
            check=False,
            timeout=10
        )

    for job_name, job_config in REQUIRED_CRONS.items():
        item = {
            "name": job_name,
            "status": "FAIL",
            "schedule": job_config["schedule"],
            "script": job_config["script"],
            "error": None
        }

        # Check if cron job exists
        if job_config["script"] in crontab_output:
            item["status"] = "PASS"
        elif job_config["schedule"] in crontab_output and "content-digest" in crontab_output:
            item["status"] = "PASS"
        elif "axon-auto-ingester" in crontab_output and job_name == "axon-ingester":
            item["status"] = "PASS"
        else:
            item["error"] = f"Cron job not found for {job_name}"
            result["status"] = "FAIL"

            # Auto-fix if enabled
            if fix and agent == "local":
                try:
                    # Add cron job
                    _, current_crontab, _ = run_command(["crontab", "-l"], check=False)
                    new_crontab = f"{current_crontab}\n{job_config['schedule']} {job_config['script']}\n"
                    subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
                    item["status"] = "PASS"
                    item["error"] = None
                    item["fixed"] = True
                    print(f"  ✅ Added cron job: {job_name}")
                except Exception as e:
                    item["error"] = f"Failed to add cron job: {str(e)}"

        result["items"].append(item)

    return result


def check_ssh_keys(agent: str = "local", fix: bool = False) -> Dict:
    """Check SSH keys."""
    result = {
        "status": "PASS",
        "items": []
    }

    private_key_path = Path.home() / ".ssh" / SSH_KEY_NAME
    public_key_path = Path.home() / ".ssh" / f"{SSH_KEY_NAME}.pub"

    if agent != "local":
        # For remote agents, just check if we can SSH to them
        ip = SQUAD_AGENTS[agent]
        returncode, _, _ = run_command(
            ["ssh", "-o", "ConnectTimeout=5", ip, "echo", "ok"],
            check=False
        )
        item = {
            "name": SSH_KEY_NAME,
            "status": "PASS" if returncode == 0 else "FAIL",
            "error": None if returncode == 0 else f"Cannot SSH to {agent}"
        }
        result["items"].append(item)
        if returncode != 0:
            result["status"] = "FAIL"
        return result

    # Check local SSH keys
    item = {
        "name": SSH_KEY_NAME,
        "status": "FAIL",
        "path": str(private_key_path),
        "permissions": None,
        "error": None
    }

    if private_key_path.exists():
        # Check permissions
        stat = private_key_path.stat()
        perms = oct(stat.st_mode)[-3:]
        item["permissions"] = perms

        if perms == "600":
            item["status"] = "PASS"
        else:
            item["error"] = f"Incorrect permissions: {perms} (should be 600)"
            result["status"] = "FAIL"

            # Auto-fix if enabled
            if fix:
                try:
                    private_key_path.chmod(0o600)
                    item["status"] = "PASS"
                    item["error"] = None
                    item["fixed"] = True
                    print(f"  ✅ Fixed permissions for {SSH_KEY_NAME}")
                except Exception as e:
                    item["error"] = f"Failed to fix permissions: {str(e)}"
    else:
        item["error"] = "SSH key not found"
        result["status"] = "FAIL"

        # Auto-fix if enabled
        if fix:
            try:
                # Generate SSH key
                subprocess.run(
                    ["ssh-keygen", "-t", "ed25519", "-f", str(private_key_path), "-N", ""],
                    check=True
                )
                private_key_path.chmod(0o600)
                item["status"] = "PASS"
                item["error"] = None
                item["fixed"] = True
                print(f"  ✅ Generated SSH key: {SSH_KEY_NAME}")
            except Exception as e:
                item["error"] = f"Failed to generate SSH key: {str(e)}"

    result["items"].append(item)
    return result


def check_tools(agent: str = "local") -> Dict:
    """Check required tools are installed."""
    result = {
        "status": "PASS",
        "items": []
    }

    # Check Python packages
    for tool in REQUIRED_PYTHON_TOOLS:
        item = {
            "name": tool,
            "status": "FAIL",
            "version": None,
            "error": None,
            "type": "pip"
        }

        if agent == "local":
            # Check local pip installation
            returncode, stdout, _ = run_command(
                ["pip", "show", tool],
                check=False
            )
            if returncode == 0:
                item["status"] = "PASS"
                # Extract version
                for line in stdout.split('\n'):
                    if line.startswith("Version:"):
                        item["version"] = line.split(":", 1)[1].strip()
                        break
            else:
                item["error"] = "Tool not installed via pip"
                result["status"] = "FAIL"
        else:
            # Check remote pip installation
            ip = SQUAD_AGENTS[agent]
            returncode, stdout, _ = run_command(
                ["ssh", ip, f"pip show {tool}"],
                check=False,
                timeout=10
            )
            if returncode == 0:
                item["status"] = "PASS"
                for line in stdout.split('\n'):
                    if line.startswith("Version:"):
                        item["version"] = line.split(":", 1)[1].strip()
                        break
            else:
                item["error"] = "Tool not installed via pip"
                result["status"] = "FAIL"

        result["items"].append(item)

    # Check workspace tools (local directories)
    workspace = Path.home() / ".openclaw" / "workspace" / "tools"
    for tool in REQUIRED_WORKSPACE_TOOLS:
        item = {
            "name": tool,
            "status": "FAIL",
            "version": None,
            "error": None,
            "type": "workspace"
        }

        if agent == "local":
            tool_path = workspace / tool
            if tool_path.exists() and tool_path.is_dir():
                item["status"] = "PASS"
                # Check if there's a package.json or main.py
                if (tool_path / "package.json").exists():
                    item["type"] = "node"
                elif (tool_path / "main.py").exists():
                    item["type"] = "python"
                elif (tool_path / "server.js").exists():
                    item["type"] = "node"
            else:
                item["error"] = f"Workspace tool not found: {tool}"
                result["status"] = "FAIL"
        else:
            # Check remote workspace tool
            ip = SQUAD_AGENTS[agent]
            tool_path = f"~/.openclaw/workspace/tools/{tool}"
            returncode, _, _ = run_command(
                ["ssh", ip, f"test -d {tool_path}"],
                check=False,
                timeout=10
            )
            if returncode == 0:
                item["status"] = "PASS"
            else:
                item["error"] = f"Workspace tool not found: {tool}"
                result["status"] = "FAIL"

        result["items"].append(item)

    return result


def check_environment(agent: str = "local") -> Dict:
    """Check optional environment variables."""
    result = {
        "status": "PASS",
        "items": []
    }

    for var_name in OPTIONAL_ENV_VARS:
        item = {
            "name": var_name,
            "status": "PASS",  # Optional vars default to PASS
            "value": None,
            "error": None,
            "optional": True
        }

        if agent == "local":
            value = os.environ.get(var_name)
        else:
            ip = SQUAD_AGENTS[agent]
            _, value, _ = run_command(
                ["ssh", ip, f"echo ${var_name}"],
                check=False,
                timeout=10
            )
            value = value.strip() if value else None

        if value:
            item["value"] = value
        else:
            # Optional vars don't fail the check
            item["status"] = "WARN"
            item["error"] = f"Optional environment variable not set: {var_name}"

        result["items"].append(item)

    return result


def validate_agent(agent: str, fix: bool = False) -> Dict:
    """Validate a single agent's configuration."""
    print(f"\n{'─' * 60}")
    print(f"🔍 Validating: {agent}")
    if agent != "local":
        print(f"   IP: {SQUAD_AGENTS.get(agent, 'unknown')}")
    print(f"{'─' * 60}\n")

    results = {
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "cron_jobs": check_cron_jobs(agent, fix),
            "ssh_keys": check_ssh_keys(agent, fix),
            "tools": check_tools(agent),
            "environment": check_environment(agent)
        },
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }

    # Calculate summary
    for check_name, check_result in results["checks"].items():
        for item in check_result["items"]:
            results["summary"]["total"] += 1
            if item["status"] == "PASS":
                results["summary"]["passed"] += 1
            elif item.get("optional"):
                # Optional warnings don't count as failures
                pass
            else:
                results["summary"]["failed"] += 1

    return results


def print_results(results: Dict, output_format: str = "console"):
    """Print validation results."""
    if output_format == "json":
        print(json.dumps(results, indent=2))
        return

    # Console output
    agent = results["agent"]
    checks = results["checks"]
    summary = results["summary"]

    # Print each check category
    for check_name, check_result in checks.items():
        category_name = check_name.replace("_", " ").title()
        print(f"   {category_name}")
        print(f"   {'─' * 56}")

        for item in check_result["items"]:
            # Determine status icon based on status and optional flag
            if item["status"] == "PASS":
                status_icon = "✅"
            elif item.get("optional"):
                status_icon = "⚠️ "
            else:
                status_icon = "❌"

            name = item.get("name", "")
            status = item["status"]
            error = item.get("error")

            if status == "PASS":
                print(f"{status_icon} {name}")
                if item.get("version"):
                    print(f"   Version: {item['version']}")
                if item.get("schedule"):
                    print(f"   Schedule: {item['schedule']}")
                if item.get("script"):
                    print(f"   Script: {item['script']}")
                if item.get("permissions"):
                    print(f"   Permissions: {item['permissions']}")
                if item.get("value"):
                    print(f"   Value: {item['value']}")
                if item.get("fixed"):
                    print(f"   ✨ Auto-fixed")
            else:
                print(f"{status_icon} {name}")
                if error:
                    print(f"   Error: {error}")

        print()

    # Print summary
    print(f"   Summary")
    print(f"   {'─' * 56}")
    if summary["failed"] == 0:
        print(f"✅ All checks passed")
        print(f"   Total: {summary['passed']}/{summary['total']} passed")
    else:
        print(f"❌ {summary['failed']} check(s) failed")
        print(f"   Total: {summary['passed']}/{summary['total']} passed")
        if summary["passed"] + summary["failed"] > 0:
            print(f"\n⚠️  Run with --fix to auto-repair")

    # Count warnings
    warnings = 0
    for check_name, check_result in results["checks"].items():
        for item in check_result["items"]:
            if item.get("optional") and item["status"] == "WARN":
                warnings += 1

    if warnings > 0:
        print(f"\nℹ️  {warnings} optional check(s) skipped")


def main():
    parser = argparse.ArgumentParser(
        description="Squad Config Validator - Validate squad agent configurations"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Validate local configuration"
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=list(SQUAD_AGENTS.keys()),
        help="Validate specific remote agent"
    )
    parser.add_argument(
        "--all-agents",
        action="store_true",
        help="Validate all squad agents"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix common issues (local only)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["console", "json"],
        default="console",
        help="Output format"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Squad Config Validator")
    print("=" * 60)

    if args.all_agents:
        # Validate all agents
        print(f"\n🔍 Validating all {len(SQUAD_AGENTS)} squad agents...\n")

        all_results = []
        fully_configured = 0
        needs_fixes = 0

        for agent in SQUAD_AGENTS.keys():
            results = validate_agent(agent)
            print_results(results, args.output)
            all_results.append(results)

            if results["summary"]["failed"] == 0:
                fully_configured += 1
            else:
                needs_fixes += 1

        # Overall summary
        print(f"\n{'=' * 60}")
        print(f"   Overall Summary")
        print(f"{'=' * 60}")
        print(f"✅ {fully_configured}/{len(SQUAD_AGENTS)} agents fully configured")
        if needs_fixes > 0:
            print(f"⚠️  {needs_fixes} agent(s) need fixes")
            print(f"\nRun: python3 main.py --agent <name> --fix")

        # Return exit code
        if needs_fixes == 0:
            return 0
        else:
            return 1

    elif args.agent:
        # Validate specific agent
        results = validate_agent(args.agent, args.fix)
        print_results(results, args.output)

        # Return exit code based on results
        if results["summary"]["failed"] == 0:
            return 0
        else:
            return 1

    elif args.local:
        # Validate local configuration
        results = validate_agent("local", args.fix)
        print_results(results, args.output)

        # Return exit code based on results
        if results["summary"]["failed"] == 0:
            return 0
        else:
            return 1

    else:
        # Default: validate local
        results = validate_agent("local", args.fix)
        print_results(results, args.output)

        # Return exit code based on results
        if results["summary"]["failed"] == 0:
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())
