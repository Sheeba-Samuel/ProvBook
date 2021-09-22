#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

import six
import io
import os
import os.path

from rdflib import URIRef, BNode, Literal, Namespace, Graph, plugin
from rdflib.serializer import Serializer
from rdflib.collection import Collection
from rdflib.namespace import RDF, XSD
from operator import itemgetter
import rdflib
import nbformat
import nbformat.v4.nbbase as nbbase
import argparse

class NBToRDFConverter():
    def __init__(self):
        self.g = Graph()
        self.pplan = Namespace("http://purl.org/net/p-plan/#")
        self.reproduce = Namespace("https://w3id.org/reproduceme#")
        self.prov = Namespace("http://www.w3.org/ns/prov/#")
        self.notebook = URIRef(self.reproduce["Notebook"])
        self.step = URIRef(self.pplan["Step"])
        self.variable = URIRef(self.pplan["Variable"])
        self.activity = URIRef(self.pplan["Activity"])
        self.cellexecution = URIRef(self.reproduce["CellExecution"])
        self.programminglanguage = URIRef(self.reproduce["Programminglanguage"])
        self.kernel = URIRef(self.reproduce["Kernel"])
        self.setting = URIRef(self.reproduce["Setting"])
        self.cell_execution_count = {}
        self.initialise_graph()

    def initialise_graph(self):
        self.g.bind('p-plan', self.pplan)
        self.g.bind('repr', self.reproduce)
        self.g.bind('prov', self.prov)

    def convert_notebook_metadata(self, notebook_name, notebook_metadata):
        notebook_node = URIRef(self.reproduce[notebook_name])

        self.g.add( (notebook_node, RDF.type, self.notebook) )
        if 'language_info' in notebook_metadata:
            language_info = notebook_metadata['language_info']
            self.g.add( (notebook_node, self.reproduce.hasProgrammingLanguage, Literal(language_info['name'])) ) if 'name' in language_info else None
            self.g.add( (notebook_node, self.reproduce.hasProgrammingLanguageVersion, Literal(language_info['version'])) ) if 'version' in language_info else None
            self.g.add( (notebook_node, self.reproduce.hasProgrammingLanguageExtension, Literal(language_info['file_extension'])) ) if 'file_extension' in language_info else None
        if 'kernelspec' in notebook_metadata:
            kernel_spec = notebook_metadata['kernelspec']
            self.g.add( (notebook_node, self.reproduce.hasKernelName, Literal(kernel_spec['name'])) ) if 'name' in kernel_spec else None
            self.g.add( (notebook_node, self.reproduce.hasKernelDisplayName, Literal(kernel_spec['display_name'])) ) if 'display_name' in kernel_spec else None
        if 'authors' in notebook_metadata:
            authors_list = notebook_metadata['authors']
            for author in authors_list:
                self.g.add( (notebook_node, self.prov.wasAttributedTo, URIRef(self.reproduce[author['name']])) ) if 'name' in author else None
                self.g.add( (URIRef(self.reproduce[author['name']]), RDF.type, self.prov["Agent"]) ) if 'name' in author else None

    def convert_code_cell_metadata(self, cell, cell_node, cell_index):
        self.cell_execution_count[cell] = cell_node.execution_count
        execution_count = Literal(cell_node.execution_count)
        output_execution_count = None
        output_val = None
        output_datatype = None
        error_name = None
        error_traceback = None
        if 'outputs' in cell_node and cell_node.outputs:
            for index, cell_node_output in enumerate(cell_node.outputs):
                output = URIRef(self.reproduce["Output" + str(cell_index)])
                output_type = cell_node_output.output_type
                self.g.add( (output, RDF.type, self.variable) )
                self.g.add( (cell, self.pplan.hasOutputVar, output) ) if output else None
                self.g.add( (output, self.reproduce.hasType, Literal(output_type)) ) if output_type else None
                if (output_type == 'execute_result' or output_type == 'display_data'):
                    output_index = 0
                    for key, value in cell_node_output.data.items():
                        output_datatype = key
                        output_val = value
                        suboutput = URIRef(self.reproduce["Output" + str(cell_index) + "Suboutput" + str(output_index)])

                        self.g.add( (output, self.reproduce.hasSubOutput, suboutput) )
                        self.g.add( (suboutput, self.reproduce.hasDataType, Literal(output_datatype)) )
                        self.g.add( (suboutput, RDF.value, Literal(output_val)) )
                        output_index = output_index + 1
                    if 'execution_count' in cell_node_output:
                        output_execution_count = cell_node_output.execution_count
                        if output_execution_count:
                            self.g.add( (output, self.reproduce.hasExecutionCount, Literal(output_execution_count)) )
                elif (output_type == 'stream'):
                    output_val = cell_node_output.text
                    output_variable_value = Literal(output_val)
                    self.g.add( (output, RDF.value, output_variable_value) ) if output_variable_value else None
                elif (output_type == 'error'):
                    output_val = cell_node_output.evalue
                    error_name = cell_node_output.ename
                    error_traceback = cell_node_output.traceback
                    output_variable_value = Literal(output_val)
                    self.g.add( (output, RDF.value, output_variable_value) ) if output_variable_value else None
                    self.g.add( (output, self.reproduce.hasErrorName, Literal(error_name)) ) if error_name else None
                    self.g.add( (output, self.reproduce.hasErrorTraceback, Literal(error_traceback)) ) if error_traceback else None

        self.g.add( (cell, self.reproduce.hasExecutionCount, Literal(cell_node['execution_count'])) ) if cell_node['execution_count'] else None

    def extract_output_from_cell(self, execution_activity, cell_index, prov_index, output):

        output_val = None
        output_datatype = None
        for output_index, out_val in enumerate(output):
            output_type = out_val.output_type
            execution_output = URIRef(self.reproduce["Cell" + str(cell_index) + "Execution" + str(prov_index) + "Output" + str(output_index)])
            self.g.add( (execution_activity, self.prov.generated, execution_output) ) if execution_output else None
            self.g.add( (execution_output, self.reproduce.hasType, Literal(output_type)) ) if output_type else None
            if (output_type == 'execute_result' or output_type == 'display_data'):
                output_index = 0
                for key, val in out_val.data.items():
                    output_datatype = key
                    output_val = val
                    execution_suboutput = URIRef(self.reproduce["Cell" + str(cell_index) + "Execution" + str(prov_index) + "Suboutput" + str(output_index)])

                    self.g.add( (execution_output, self.reproduce.hasSubOutput, execution_suboutput) )
                    self.g.add( (execution_suboutput, self.reproduce.hasDataType, Literal(output_datatype)) )
                    self.g.add( (execution_suboutput, RDF.value, Literal(output_val)) )
                    output_index = output_index + 1
            elif (output_type == 'stream'):
                output_val = output[output_index].text
                self.g.add( (execution_output, RDF.value, Literal(output_val)) ) if output_val else None
            elif (output_type == 'error'):
                output_val = output[output_index].evalue
                error_name = output[output_index].ename
                error_traceback = output[output_index].traceback
                self.g.add( (execution_output, RDF.value, Literal(output_val)) ) if output_val else None


    def convert_provenance_metadata(self, cell, cell_node, cell_index):
        for prov_index, provenance in enumerate(cell_node.metadata.provenance):
            start_time = provenance['start_time'] if 'start_time' in provenance else None
            end_time = provenance['end_time'] if 'end_time' in provenance else None
            source = provenance['source'] if 'source' in provenance else None
            source_entity = URIRef(self.reproduce["Cell" + str(cell_index) + "Execution" + str(prov_index) + "Source"]) if source else None
            execution_time = provenance['execution_time'] if 'execution_time' in provenance else None
            execution_activity = URIRef(self.reproduce["Cell" + str(cell_index) + "Execution" + str(prov_index)])

            output = self.extract_output_from_cell(execution_activity, cell_index, prov_index, provenance['outputs']) if 'outputs' in provenance else None

            self.g.add( (execution_activity, RDF.type, self.cellexecution) )
            self.g.add( (execution_activity, self.pplan.correspondsToStep, cell) )
            self.g.add( (execution_activity, self.prov.startedAtTime, Literal(start_time)) ) if start_time else None
            self.g.add( (execution_activity, self.prov.endedAtTime, Literal(end_time)) ) if end_time else None
            self.g.add( (execution_activity, self.reproduce.executionTime, Literal(execution_time)) ) if execution_time else None
            self.g.add( (execution_activity, self.prov.used, source_entity) ) if source else None
            self.g.add( (source_entity, RDF.value, Literal(source)) ) if source else None
            self.g.add( (execution_activity, self.prov.generated, Literal(output)) ) if output else None

    def convert_common_cell_metadata(self, cell, cell_node, cell_index):
        if 'provenance' in cell_node.metadata:
            self.convert_provenance_metadata(cell, cell_node, cell_index)

        self.g.add( (cell, RDF.type, self.step) )
        self.g.add( (cell, self.reproduce.hasIndex, Literal(cell_index, datatype=XSD.integer)) )
        self.g.add( (cell, self.reproduce.hasCellType, Literal(cell_node['cell_type'])) ) if cell_node['cell_type'] else None

        if 'source' in cell_node:
            source = URIRef(self.reproduce["Source" + str(cell_index)])
            source_variable_value = Literal(cell_node.source)
            self.g.add( (cell, self.pplan.hasInputVar, source) )
            self.g.add( (source, RDF.type, self.variable) )
            self.g.add( (source, RDF.value, source_variable_value) ) if source_variable_value else None



    def convert_cell_metadata(self, notebook_name, cell_data):
        notebook_node = URIRef(self.reproduce[notebook_name])
        for cell_index, cell_node in enumerate(cell_data):
            cell = URIRef(self.reproduce["Cell" + str(cell_index)])
            self.g.add( (cell, self.pplan.isStepOfPlan, notebook_node) )
            self.convert_common_cell_metadata(cell, cell_node, cell_index)
            if 'cell_type' in cell_node and cell_node.cell_type == 'code':
                self.convert_code_cell_metadata(cell, cell_node, cell_index)



    def convert_to_rdf(self, notebook_name, notebook_json):
        format = 'turtle'
        notebook_name = ''.join(nb_name for nb_name in notebook_name if nb_name.isalnum())
        for section in notebook_json:
            if section == 'cells':
                self.convert_cell_metadata(notebook_name, notebook_json[section])

            if section == 'metadata':
                self.convert_notebook_metadata(notebook_name, notebook_json[section])
        return self.g.serialize(format=format)


    def convert_notebook_to_rdf(self, args):
        infile = args.input_file
        notebook_file = os.path.basename(infile)
        notebook_name, extension = os.path.splitext(notebook_file)
        input_file_directory = os.path.dirname(infile)
        output_file_extension = 'ttl'
        output_file = os.path.join(input_file_directory, notebook_name + "." + output_file_extension)

        notebook = io.open(infile).read()
        notebook_json = nbformat.reads(notebook, as_version=4)
        nbconvert_rdf = self.convert_to_rdf(notebook_name, notebook_json)
        io.open(output_file, 'w').write(six.ensure_text(nbconvert_rdf))
        return nbconvert_rdf
