"""Setup configuration for the GTM Opportunity Agent."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gtm-opportunity-agent",
    version="1.0.0",
    author="GTM Team",
    author_email="gtm@company.com",
    description="Proactive AI agent for sales opportunity intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "temporalio>=1.6.0",
        "llama-index>=0.10.0",
        "arcade-ai>=0.1.0",
        "pydantic>=2.7.0",
        "typer>=0.12.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.27.0",
        "ddtrace>=2.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.2.0",
            "black>=24.4.0",
            "isort>=5.13.0",
        ],
        "anthropic": [
            "llama-index-llms-anthropic>=0.1.0",
        ],
        "ollama": [
            "llama-index-llms-ollama>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gtm-agent=main:app",
        ],
    },
) 