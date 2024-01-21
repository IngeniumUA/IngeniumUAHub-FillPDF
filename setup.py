from setuptools import setup

setup(
    name="Mailing",
    version="11.0",
    description="Implements the Gmail API to send mails",
    author="Yorben Joosen",
    author_email="webmaster@ingeniumua.be",
    packages=["Mailing"],  # same as name
    install_requires=[
        "google",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-auth-httplib2",
        "googleapis-common-protos",
    ],  # external packages as dependencies
)
