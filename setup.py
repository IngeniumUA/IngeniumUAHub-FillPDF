from setuptools import setup

setup(
    name="FillPDF",
    version="5.0",
    description="Used to automatically fill PDF's",
    author="Yorben Joosen",
    author_email="webmaster@ingeniumua.be",
    packages=["FillPDF"],  # same as name
    install_requires=[
        "pypdf",
    ],  # external packages as dependencies
)
