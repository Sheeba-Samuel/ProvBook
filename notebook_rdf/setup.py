#from distutils.core import setup
from setuptools import setup

setup(
    name="notebook_rdf",
    version="1.0.0",
    description="Convert jupyter notebook to RDF and back.",
    packages=["notebook_rdf"],
    author="Sheeba Samuel",
    author_email="sheeba.samuel@uni-jena.de",
    license='MIT',
    entry_points={'console_scripts': ['notebook_rdf = notebook_rdf.__main__:app', ]},
)
