from setuptools import setup

setup(
   name='Mailing',
   version='1.0',
   description='Implements the Gmail API to send mails',
   author='Yorben Joosen',
   author_email='webmaster@ingeniumua.be',
   packages=['Mailing'],   # same as name
   install_requires=['google'],  # external packages as dependencies
)