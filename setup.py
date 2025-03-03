from setuptools import setup, find_packages

setup(
    name="fillpdf",
    version="75.0",
    description="Used to automatically fill PDF's",
    author="Yorben Joosen",
    author_email="webmaster@ingeniumua.be",
    packages=find_packages(),  # same as name
    include_package_data=True,
    package_data={"fillpdf": ["templates/*.*"]},
    install_requires=[
        "pypdf",
        "Pillow",
        "reportlab"
    ],  # external packages as dependencies
)
