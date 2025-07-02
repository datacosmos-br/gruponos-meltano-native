"""Setup configuration for flext-target-oracle."""

from setuptools import find_packages, setup

setup(
    name="flext-target-oracle",
    version="0.1.0",
    description="Advanced Oracle target with SQLAlchemy and performance optimizations",
    author="FLEXT Framework",
    author_email="dev@flext.io",
    py_modules=["target", "sinks", "connectors"],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "singer-sdk>=0.44.0",
        "sqlalchemy>=2.0.0",
        "oracledb>=1.4.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "mypy>=1.0",
            "black>=22.0",
            "flake8>=5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "target-oracle = target:TargetOracle.cli",
            "flext-target-oracle = target:TargetOracle.cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
