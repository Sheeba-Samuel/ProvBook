#!/usr/bin/env python
# coding: utf-8

# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

from __future__ import print_function

import io
import os
import sys
from glob import glob

from setuptools import setup, find_packages

from setupbase import (create_cmdclass, install_npm, ensure_targets,
    combine_commands, ensure_python, get_version)

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))


# Minimal Python version sanity check
ensure_python(('2.7', '>=3.4'))

# the name of the project
name = 'provbook'
version = get_version(pjoin(name, '_version.py'))

# Some paths
static_dir = pjoin(here, name, 'webapp', 'static')
packages_dir = pjoin(here, 'packages')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(static_dir, 'provbookdiff.js'),
]


package_data = {
    name: [
        'webapp/static/*.*',
        'webapp/templates/*.*',
        'notebook_ext/*.*',
    ]
}


data_spec = [
    ('share/jupyter/nbextensions/provbook',
     name + '/notebook_ext',
     '*'),
    ('etc/jupyter',
     'jupyter-config',
     '**/*.json'),
]


cmdclass = create_cmdclass('js', data_files_spec=data_spec)
cmdclass['js'] = combine_commands(
    install_npm(here, build_targets=jstargets, sources=packages_dir),
    ensure_targets(jstargets),
)

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup_args = dict(
    name            = name,
    description     = "Provenance and differencing of the Jupyter Notebook Execution",
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    version         = version,
    scripts         = glob(pjoin('scripts', '*')),
    cmdclass        = cmdclass,
    packages        = find_packages(here),
    package_data    = package_data,
    author          = 'Sheeba Samuel',
    author_email    = 'sheeba.samuel@uni-jena.de',
    url             = 'https://github.com/Sheeba-Samuel/',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Interactive', 'Provenance', 'Reproducibility', 'RDF', 'Jupyter'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Jupyter',
    ],
)


setuptools_args = {}
install_requires = setuptools_args['install_requires'] = [
    'nbformat',
    'six',
    'colorama',
    'tornado',
    'requests',
    'GitPython!=2.1.4, !=2.1.5, !=2.1.6',
    'notebook',
    'jinja2>=2.9',
    'jupyter',
    'nbdime',
    'rdflib'
]

extras_require = setuptools_args['extras_require'] = {
    'docs': [
        'sphinx',
        'recommonmark',
        'sphinx_rtd_theme'
    ],

    ':python_version == "2.7"': [
        'backports.shutil_which',
        'backports.functools_lru_cache',
    ],
}

setuptools_args['python_requires'] = '>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*'

if 'setuptools' in sys.modules:
    setup_args.update(setuptools_args)

    # force entrypoints with setuptools (needed for Windows, unconditional because of wheels)
    setup_args['entry_points'] = {
        'console_scripts': ['notebook_rdf = provbook.notebook_rdf.__main__:app',]
    }
    setup_args.pop('scripts', None)

    setup_args.update(setuptools_args)

if __name__ == '__main__':
    setup(**setup_args)
