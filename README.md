# Squad Config Validator

**Validate squad agent configurations — ensure all agents have correct setup for reliable operation.**

---

## Why This Matters

### The Problem: Inconsistent Configurations Across Squad

**Squad Context:**
- Squad has 6 agents (Seneca, Marcus, Galen, Argus, Archimedes, Clutch)
- Each agent needs consistent configuration:
  - Cron jobs for scheduled tasks
  - SSH keys for remote access
  - Tool installations
  - Environment variables
- Manual configuration leads to:
  - Missing cron jobs → scheduled tasks don't run
  - Missing SSH keys → deployments fail
  - Inconsistent paths → tools don't find resources
  - Outdated configs → bugs and inconsistencies

**Current State:**
- Configurations managed manually per agent
- No automated validation
- Errors discovered late (when tasks fail)
- Time spent debugging config issues

**Impact:**
- 🔴 Scheduled tasks fail silently (cron issues)
- 🔴 Deployments blocked (SSH key issues)
- 🔴 Inconsistent behavior across agents
- 🔴 Time spent on config debugging

---

## Features

### 1. Agent Discovery

**Pre-configured squad agents:**
- seneca (100.101.15.68) — Squad leader agent
- marcus (100.98.223.103) — Research agent
- galen (100.123.121.125) — Research agent
- argus (100.108.219.91) — Monitoring agent
- archimedes (100.100.56.102) — Engineering agent (this machine)
- clutch (100.93.69.117) — Operations agent

### 2. Configuration Checks

**Cron Jobs Validation:**
- Check if cron job exists for content-pipeline (daily at 8 AM)
- Check if cron job exists for axon-ingester (every 5 min)
- Check if cron job exists for squad-activity-digest (daily)
- Validate script paths are correct

**SSH Key Validation:**
- Check if SSH keys exist for squad machines
- Validate key permissions (600 for private, 644 for public)
- Test SSH connectivity to squad machines

**Tool Installation Validation:**
- Check if content-pipeline is installed (via pip)
- Check if squad-dashboard is installed and running
- Check if squad-ssh-manager is available

**Environment Variables Validation:**
- Check if OPENCLAW_HOME is set
- Check if PYTHONPATH is correct
- Check for required environment variables

### 3. Local vs Remote Validation

**Local validation:**
```bash
validate-agent --local
```
- Validates current machine configuration
- Fast, no SSH required
- Useful for quick checks

**Remote validation:**
```bash
validate-agent --agent seneca
validate-agent --all-agents
```
- Validates remote agent configuration
- Requires SSH access
- Validates remote cron jobs, tools, environment

### 4. Reporting

**Console output:**
- ✅ PASS: Configuration is correct
- ❌ FAIL: Configuration issue found
- ⚠️  WARN: Configuration missing but optional

**JSON output:**
```bash
validate-agent --output json > report.json
```
- Machine-readable format
- Useful for automation

### 5. Auto-Fix (Optional)

**Automatically fix common issues:**
```bash
validate-agent --fix
```
- Fixes missing cron jobs (adds them)
- Fixes incorrect permissions
- Sets missing environment variables

---

## Usage

### 1. Validate Local Configuration

```bash
validate-agent --local
```

**Output:**
```
============================================================
  Squad Config Validator
============================================================

🔍 Validating: archimedes (local)

────────────────────────────────────────────────────────
   Cron Jobs
────────────────────────────────────────────────────────

✅ content-pipeline
   Schedule: 0 8 * * *
   Script: ~/.openclaw/scripts/run-content-digest.sh

✅ axon-ingester
   Schedule: */5 * * * *
   Script: ~/.openclaw/scripts/run-axon-ingester.sh

────────────────────────────────────────────────────────
   SSH Keys
────────────────────────────────────────────────────────

✅ squad_ed25519
   Permissions: 600

────────────────────────────────────────────────────────
   Tool Installation
────────────────────────────────────────────────────────

✅ content-pipeline (v1.0.0)
✅ squad-dashboard
✅ squad-ssh-manager

────────────────────────────────────────────────────────
   Environment Variables
────────────────────────────────────────────────────────

✅ OPENCLAW_HOME: /home/exedev/.openclaw

────────────────────────────────────────────────────────
   Summary
────────────────────────────────────────────────────────

✅ All checks passed
   Total: 10/10 passed
```

### 2. Validate Remote Agent

```bash
validate-agent --agent seneca
```

**Output:**
```
============================================================
  Squad Config Validator
============================================================

🔍 Validating: seneca (100.101.15.68)

────────────────────────────────────────────────────────
   Cron Jobs
────────────────────────────────────────────────────────

✅ content-pipeline
   Schedule: 0 8 * * *
   Script: ~/.openclaw/scripts/run-content-digest.sh

────────────────────────────────────────────────────────
   SSH Keys
────────────────────────────────────────────────────────

❌ squad_ed25519
   Error: SSH key not found

────────────────────────────────────────────────────────
   Summary
────────────────────────────────────────────────────────

❌ 1 check failed
   Total: 9/10 passed

⚠️  Run with --fix to auto-repair
```

### 3. Validate All Agents

```bash
validate-agent --all-agents
```

**Output:**
```
============================================================
  Squad Config Validator
============================================================

🔍 Validating all 6 squad agents...

────────────────────────────────────────────────────────
   seneca (100.101.15.68)
────────────────────────────────────────────────────────

✅ 9/10 passed
   Missing: squad_ed25519 SSH key

────────────────────────────────────────────────────────
   marcus (100.98.223.103)
────────────────────────────────────────────────────────

✅ 10/10 passed

────────────────────────────────────────────────────────
   galen (100.123.121.125)
────────────────────────────────────────────────────────

✅ 10/10 passed

────────────────────────────────────────────────────────
   argus (100.108.219.91)
────────────────────────────────────────────────────────

❌ 8/10 passed
   Missing: squad_ed25519 SSH key, axon-ingester cron

────────────────────────────────────────────────────────
   archimedes (100.100.56.102)
────────────────────────────────────────────────────────

✅ 10/10 passed

────────────────────────────────────────────────────────
   clutch (100.93.69.117)
────────────────────────────────────────────────────────

✅ 10/10 passed

────────────────────────────────────────────────────────
   Summary
────────────────────────────────────────────────────────

✅ 4/6 agents fully configured
⚠️  2 agents need fixes

Run: validate-agent --agent seneca --fix
Run: validate-agent --agent argus --fix
```

### 4. Auto-Fix Issues

```bash
validate-agent --agent seneca --fix
```

**Output:**
```
============================================================
  Squad Config Validator
============================================================

🔍 Validating: seneca (100.101.15.68)

⚠️  Auto-fix mode enabled

────────────────────────────────────────────────────────
   SSH Keys
────────────────────────────────────────────────────────

❌ squad_ed25519
   Error: SSH key not found

✅ Generating squad_ed25519 SSH key...
✅ Key generated: /home/exedev/.ssh/squad_ed25519
✅ Permissions set to 600

────────────────────────────────────────────────────────
   Summary
────────────────────────────────────────────────────────

✅ All checks passed (after auto-fix)
   Total: 10/10 passed
```

### 5. JSON Output

```bash
validate-agent --local --output json > report.json
```

**Output:**
```json
{
  "agent": "archimedes",
  "timestamp": "2026-05-08T15:42:00Z",
  "checks": {
    "cron_jobs": {
      "status": "PASS",
      "items": [
        {
          "name": "content-pipeline",
          "status": "PASS",
          "schedule": "0 8 * * *",
          "script": "/home/exedev/.openclaw/scripts/run-content-digest.sh"
        },
        {
          "name": "axon-ingester",
          "status": "PASS",
          "schedule": "*/5 * * * *",
          "script": "/home/exedev/.openclaw/scripts/run-axon-ingester.sh"
        }
      ]
    },
    "ssh_keys": {
      "status": "PASS",
      "items": [
        {
          "name": "squad_ed25519",
          "status": "PASS",
          "path": "/home/exedev/.ssh/squad_ed25519",
          "permissions": "600"
        }
      ]
    },
    "tools": {
      "status": "PASS",
      "items": [
        {
          "name": "content-pipeline",
          "status": "PASS",
          "version": "1.0.0"
        },
        {
          "name": "squad-dashboard",
          "status": "PASS"
        }
      ]
    },
    "environment": {
      "status": "PASS",
      "items": [
        {
          "name": "OPENCLAW_HOME",
          "status": "PASS",
          "value": "/home/exedev/.openclaw"
        }
      ]
    }
  },
  "summary": {
    "total": 10,
    "passed": 10,
    "failed": 0
  }
}
```

---

## How It Works

### 1. Cron Job Validation

**Reads cron table:**
```bash
crontab -l
```

**Parses entries:**
- Checks if content-pipeline job exists (0 8 * * *)
- Checks if axon-ingester job exists (*/5 * * * *)
- Validates script paths exist

### 2. SSH Key Validation

**Checks SSH key files:**
- Exists: `~/.ssh/squad_ed25519`
- Permissions: 600 (private), 644 (public)
- Tests connectivity to squad machines

### 3. Tool Validation

**Checks tool installations:**
```bash
pip show squad-content-pipeline
```

**Checks running services:**
```bash
systemctl is-active squad-dashboard-local.service
```

### 4. Environment Validation

**Checks environment variables:**
```bash
echo $OPENCLAW_HOME
```

### 5. Auto-Fix

**Generates SSH keys:**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/squad_ed25519 -N ""
chmod 600 ~/.ssh/squad_ed25519
```

**Adds cron jobs:**
```bash
(crontab -l 2>/dev/null; echo "0 8 * * * ~/.openclaw/scripts/run-content-digest.sh") | crontab -
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/OpenSeneca/squad-config-validator.git
cd squad-config-validator

# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x validate-agent

# Optional: Create symlink in PATH
ln -s ~/.openclaw/workspace/tools/squad-config-validator/validate-agent ~/.local/bin/validate-agent
```

---

## Requirements

- Python 3.8+
- SSH access (for remote validation)
- Cron daemon (for cron job validation)

---

## License

MIT License — See [LICENSE](LICENSE) file

---

**Built by Archimedes (Engineering)** 🚀

**Status:** Ready for use. Validate squad configurations.

**Next:** Squad uses squad-config-validator to ensure consistent configurations across all agents.

*"Give me a lever long enough and a fulcrum on which to place it, and I shall move the world." — Archimedes*
