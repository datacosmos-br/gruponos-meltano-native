"""Setup configuration for flext-target-oracle."""

from setuptools import find_packages, setup

setup(
    name="flext-target-oracle",
    version="0.1.0",
    description="Advanced Oracle target for Singer with SQLAlchemy and performance optimizations",
    author="FLEXT Team",
    author_email="dev@flext.io",
    url="https://github.com/flext/flext-target-oracle",
    packages=find_packages(),
    package_data={},
    python_requires=">=3.8",
    install_requires=[
        "singer-sdk>=0.47.4",
        "sqlalchemy>=2.0.0",
        "oracledb>=1.4.0",
        "click>=8.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "performance": [
            "pandas>=1.5.0",
            "pyarrow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flext-target-oracle=flext_target_oracle.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="singer oracle etl data-pipeline sqlalchemy target",
    project_urls={
        "Documentation": "https://flext.io/docs/target-oracle",
        "Source": "https://github.com/flext/flext-target-oracle",
        "Tracker": "https://github.com/flext/flext-target-oracle/issues",
    },
)
