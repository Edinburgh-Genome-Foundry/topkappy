import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('topkappy/version.py').read()) # loads __version__

setup(
    name='topkappy',
    version=__version__,
    author='Zulko',
    url='https://github.com/Edinburgh-Genome-Foundry/topkappy',
    description='Pythonic wrapper for the Kappa language (bio simulations)',
    long_description=open('pypi-readme.rst').read(),
    license='MIT',
    keywords="simulation biology modeling complex kappa binding",
    packages=find_packages(exclude='docs'),
    install_requires=['kappy', 'networkx', 'matplotlib', 'numpy',
                      'termcolor'])
