from __future__ import absolute_import
from __future__ import print_function

import os
import tempfile


import nbformat
import notebook_rdf
import argparse
from notebook_rdf import nb2rdf
from notebook_rdf import rdf2nb

sample_notebook = r"""{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Create IPython Notebooks from markdown\n",
    "\n",
    "This is a simple tool to convert markdown with code into an IPython\n",
    "Notebook.\n",
    "\n",
    "Usage:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "notedown input.md > output.ipynb"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "It is really simple and separates your markdown into code and not\n",
    "code. Code goes into code cells, not-code goes into markdown cells.\n",
    "\n",
    "Installation:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "pip install notedown"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 2
}"""


def test_notedown():
    """Integration test the whole thing."""

    # args = {
    #     'input_file': '/home/sheeba/notebookcode/notebook_rdf/examples/r-example.ipynb'
    # }
    args = {
        'input_file': '/home/sheeba/notebookcode/notebook_rdf/examples/rotorcraft_mixing.ipynb'
    }
    # args['input_file'] = 'example.ipynb'
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        help="The input file",
                        nargs="?",
                        default='-')
    args = parser.parse_args(args)
    # args.input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/r-example.ipynb'
    args.input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/rotorcraft_mixing.ipynb'
    print("parser_args", args)

    nbtordfConverter = nb2rdf.NBToRDFConverter()

    notebook_rdf = nbtordfConverter.convert_notebook_to_rdf(args)
    # print("notebook_rdf", notebook_rdf)

    # args.input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/r-example.ttl'
    args.input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/rotorcraft_mixing.ttl'


    rdf_notebook = rdf2nb.convert_rdf_to_notebook(args)
    # print("rdf_notebook", rdf_notebook)
    # input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/r-example.ipynb'
    # output_file = '/home/sheeba/notebookcode/notebook_rdf/examples/r-example_rdf2nb.ipynb'
    input_file = '/home/sheeba/notebookcode/notebook_rdf/examples/rotorcraft_mixing.ipynb'
    output_file = '/home/sheeba/notebookcode/notebook_rdf/examples/rotorcraft_mixing_rdf2nb.ipynb'
    from difflib import ndiff
    import difflib

    diff = difflib.unified_diff(open(input_file).readlines(),open(output_file).readlines())
    # print(''.join(diff))

    # print(difflib.SequenceMatcher(None, open(input_file).readlines(),open(output_file).readlines()))
    # diff = ndiff(open(input_file).readlines(),open(output_file).readlines())
    # print(''.join(diff))

    # nbtordf_result = notebook_rdf
    # print("nbtordf_result", nbtordf_result)
    # from difflib import ndiff
    # notebook = create_json_notebook(sample_markdown)
    # diff = ndiff(sample_notebook.splitlines(1), notebook.splitlines(1))
    # print('\n'.join(diff))
    # nt.assert_multi_line_equal(create_json_notebook(sample_markdown),
    #                            sample_notebook)

test_notedown()

class TestCommandLine(object):
    @property
    def default_args(self):
        parser = notebook_rdf.main.command_line_parser()
        return parser.parse_args()

    def run(self, args):
        notebook_rdf.main.main(args)

    def test_basic(self):
        args = self.default_args
        args.input_file = 'example.md'
        self.run(args)

    def test_reverse(self):
        args = self.default_args
        args.input_file = 'example.ipynb'
        self.run(args)

    def test_markdown_to_notebook(self):
        args = self.default_args
        args.input_file = 'example.md'
        args.informat = 'markdown'
        args.outformat = 'notebook'
        self.run(args)

    def test_markdown_to_markdown(self):
        args = self.default_args
        args.input_file = 'example.md'
        args.informat = 'markdown'
        args.outformat = 'markdown'
        self.run(args)

    def test_notebook_to_markdown(self):
        args = self.default_args
        args.input_file = 'example.ipynb'
        args.informat = 'notebook'
        args.outformat = 'markdown'
        self.run(args)

    def test_notebook_to_notebook(self):
        args = self.default_args
        args.input_file = 'example.ipynb'
        args.informat = 'notebook'
        args.outformat = 'notebook'
        self.run(args)
