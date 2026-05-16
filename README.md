# Squad Config Validator

Validates OpenSeneca squad agent configurations for best practices and common issues.

## Installation

```bash
pip install squad-config-validator
```

## Usage

```bash
# Validate all configs
squad-config-validator

# Validate specific directory
squad-config-validator --dir /path/to/configs
```

## Features

- Validates JSON syntax and structure
- Checks for required configuration keys
- Verifies agent name formatting
- Validates cron schedules
- Checks tool paths exist
- Detects API key placeholders
- Generates health scores (0-100)
- Saves individual and summary reports

## Output

Reports are saved to `~/.openclaw/workspace/outputs/`:
- `squad-config-validator-{agent_name}.json` - Individual reports
- `squad-config-validator-summary.json` - Summary statistics

## Priority

PRIORITY 4 for Archimedes squad. Helps identify configuration issues and improves adoption tracker data quality.