from setuptools import setup, find_packages

setup(
    name="script_runner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "rich==10.12.0",
        "typer==0.9.0",
        "click==8.1.3",
        "yaspin==2.1.0",
    ],
)