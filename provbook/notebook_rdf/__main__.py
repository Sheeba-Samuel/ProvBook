#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

from __future__ import absolute_import
import argparse
from .nb2rdf import NBToRDFConverter
from .rdf2nb import convert_rdf_to_notebook
import sys
import os

examples = """
Example usage of notebook_rdf
-------------------------
Convert your notebook to RDF
    python3.5 notebook_rdf --from notebook your_notebook.ipynb --to RDF
    python3.5 notebook_rdf your_notebook.ipynb
Convert your RDF to notebook
    python3.5 notebook_rdf --from RDF notebook_rdf.ttl --to notebook
    python3.5 notebook_rdf notebook_rdf.ttl
"""


def command_line_parser():
    description = "Convert Jupyter Notebook to RDF and back to Jupyter Notebook."
    example_use = """Example: python3.5 notebook_rdf --from notebook your_notebook.ipynb --to RDF
                  """
    parser = argparse.ArgumentParser(description=description,
                                     epilog=example_use)
    parser.add_argument('input_file',
                        help="The input file",
                        nargs="?",
                        default='-')
    parser.add_argument('-o', '--output',
                    help=("output file, (default STDOUT). "
                          "If flag used but no file given, use "
                          "the name of the input file to "
                          "determine the output filename. "
                          "This will OVERWRITE if input and output "
                          "formats are the same."),
                    nargs="?",
                    default='-',
                    const='')
    parser.add_argument('--from',
                        dest='informat',
                        choices=('notebook', 'RDF'),
                        help=("The format to convert from, defaults to notebook "
                              "or file extension"))
    parser.add_argument('--to',
                        dest='outformat',
                        choices=('notebook', 'RDF'),
                        help=("The format to convert to, defaults to RDF "
                              "or file extension"))
    parser.add_argument('--examples',
                        help=('Show example usage'),
                        action='store_true')

    return parser

def file_extension_detect(filename):
    """Determine if file is notebook or RDF,
    based on the file extension.
    """
    _, extension = os.path.splitext(filename)
    rdf_exts = ['.ttl', '.nt', '.jsonld', '.json']
    nb_exts = ['.ipynb']
    if extension in rdf_exts:
        return 'RDF'
    elif extension in nb_exts:
        return 'notebook'
    else:
        return None


def main(args, help=''):
    if args.examples:
        print(examples)
        sys.exit()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit()

    informat = args.informat or file_extension_detect(args.input_file) or 'notebook'
    if args.outformat:
        outformat = args.outformat
    elif informat == 'notebook':
        outformat = 'RDF'
    else:
        outformat = 'notebook'
    if informat=='notebook' and outformat=='RDF':
        nbtordfconverter = NBToRDFConverter()
        nbtordfconverter.convert_notebook_to_rdf(args)
    if informat=='RDF' and outformat=='notebook':
        convert_rdf_to_notebook(args)

def app():
    parser = command_line_parser()
    args = parser.parse_args()
    main(args, help=parser.format_help())

if __name__ == '__main__':
    app()
