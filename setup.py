from setuptools import setup, find_packages

setup(
    name="FillPDF",
    version="64.0",
    description="Used to automatically fill PDF's",
    author="Yorben Joosen",
    author_email="webmaster@ingeniumua.be",
    packages=find_packages(),  # same as name
    include_package_data=True,
    package_data={"FillPDF": ["templates/*.*"]},
    install_requires=[
        "pypdf",
        "Pillow",
        "reportlab"
    ],  # external packages as dependencies
)
