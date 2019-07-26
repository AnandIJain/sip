from setuptools import setup

setup(
   name='sip',
   version='0.1',
   description='tools for RL sports betting',
   author='Anand Jain',
   author_email='anandj@uchicago.edu',
   packages=['sip'],  #same as name
   install_requires= \
           ['pandas', 'requests', 'bs4', 'numpy', 'gym'
           'torch', 'pickle', 'warnings', 'seaborn', 'sklearn',
           'matplotlib'] # external packages as dependencies
)