from setuptools import find_packages, setup
from os.path import abspath, basename, dirname, join, splitext
import codecs

def readme():
    """Read in and return the contents of the project's README.md file."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()
    
# Below two methods were pulled from:
# https://packaging.python.org/guides/single-sourcing-package-version/
def read(rel_path):
    """Open a file for reading from a given relative path."""
    here = abspath(dirname(__file__))
    with codecs.open(join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(version_file):
    """Extract a version number from the given file path."""
    for line in read(version_file).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    name='fernetvault',
    version=get_version("src/_version.py"),
    description="A file based secure vault",
    long_description=readme(),
    author='Luís Oliveira',
    url='https://github.com/charlieIT/fernetvault',
    license='MIT',
    packages=['fernetvault', 'fernetvault.crypto', 'fernetvault.models', 'fernetvault.ui'],
    #packages = find_packages(where="src"),
    package_dir={'fernetvault': 'src'},
    install_requires=[
        'cffi==1.16.0',
        'cryptography==41.0.7',
        'pycparser==2.21',
        'schedule==1.2.1'
    ],  # external dependencies
    entry_points={"console_scripts": ["fernetvault = fernetvault.fernetvault:main"]},
    classifiers=[  # see https://pypi.org/pypi?%3Aaction=list_classifiers
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
    ],
)