from setuptools import setup, find_packages

setup(
    name="squad-config-validator",
    version="1.0.0",
    description="Validates OpenSeneca squad agent configurations for best practices",
    author="Archimedes - OpenSeneca Squad",
    python_requires=">=3.8",
    py_modules=["main"],
    entry_points={
        "console_scripts": [
            "squad-config-validator=main:main",
        ],
    },
)