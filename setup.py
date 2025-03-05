from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cherry",
    version="0.1.0",
    author="Cherry Team",
    author_email="author@example.com",
    description="AI Orchestration Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github