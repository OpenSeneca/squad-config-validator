#!/usr/bin/env python3
"""
Setup script for squad-config-validator
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="squad-config-validator",
    version="1.0.0",
    description="Validate squad agent configurations — ensure all agents have correct setup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenSeneca",
    url="https://github.com/OpenSeneca/squad-config-validator",
    license="MIT",
    packages=find_packages(),
    py_modules=["main"],
    install_requires=[
        "paramiko>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "validate-agent=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
