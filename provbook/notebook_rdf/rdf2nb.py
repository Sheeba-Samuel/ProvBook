#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

import io
import os
import os.path

from rdflib import Graph
import nbformat
import nbformat.v4.nbbase as nbbase
import argparse

def get_cell_source(rdfgraph, cell_index):
    for row in sorted(rdfgraph.query(
        'select ?cell ?source ?source_value where { ?cell repr:hasIndex ' + cell_index + ' .' \
        '?cell p-plan:hasInputVar ?source . ?source rdf:value ?source_value }'
            )):
        return row.source_value

def get_cell_output(rdfgraph, cell_index):
    output = []
    for row in sorted(rdfgraph.query(
        'select * where { \
            ?cell repr:hasIndex ' + cell_index + ' . \
            OPTIONAL { ?cell p-plan:hasOutputVar ?output  . \
            OPTIONAL { ?output rdf:value ?output_value  } . \
            OPTIONAL { ?output repr:hasType ?output_type } . \
            OPTIONAL { ?output repr:hasErrorName ?output_errorname } . \
            OPTIONAL { ?output repr:hasErrorTraceback ?output_errortraceback } . \
            OPTIONAL { ?output repr:hasExecutionCount ?execution_count } . } . } '
        )):
            if row.output_type:
                output_type = str(row.output_type)
                output = {
                    'output_type' : str(row.output_type),
                }

                output_value = str(row.output_value)
                if output_type == 'execute_result' or output_type == 'display_data':
                    repr_output = 'repr:' + row.output.split('#')[1]

                    output['data'] = {}
                    for suboutput_row in sorted(rdfgraph.query(
                        'select * where { ' + repr_output + ' repr:hasSubOutput ?suboutput . \
                            ?suboutput rdf:value ?output_value . \
                            ?suboutput repr:hasDataType ?output_datatype } '
                    )):

                        output_value = str(suboutput_row.output_value)
                        output_datatype = str(suboutput_row.output_datatype)

                        output['data'].update({
                            output_datatype: output_value
                        })
                    if (row.output_value):
                        output['data'] = {
                            output_datatype : output_value
                        }
                    output['metadata'] = {}

                    if row.execution_count:
                        output['execution_count'] = int(row.execution_count)
                elif output_type == 'stream':
                    output['name'] = 'stdout'
                    output['text'] = output_value
                elif output_type == 'error':
                    output['ename'] = row.output_errorname
                    output['evalue'] = output_value
                    output['traceback'] = []#row.output_errortraceback
                return output


def create_cells(rdfgraph, cell, cell_index, **kwargs):
    provenance_metadata = create_provenance(rdfgraph, cell, cell_index)
    cell_type = str(kwargs['cell_type'])
    source = get_cell_source(rdfgraph, cell_index)
    if source:
        kwargs['source'] = source
    kwargs['metadata'] = provenance_metadata
    if cell_type == 'code':
        output = get_cell_output(rdfgraph, cell_index)
        if output:
            output = create_cell_output(**output)
        if output:
            kwargs['outputs'] = [output]
        else:
            kwargs['outputs'] = []
        notebook_cell = nbbase.new_code_cell(**kwargs)
    elif cell_type == 'markdown':
        notebook_cell = nbbase.new_markdown_cell(**kwargs)
    elif cell_type == 'raw':
        notebook_cell = nbbase.new_raw_cell(**kwargs)

    return notebook_cell

def create_provenance(rdfgraph, cell,  cell_index, **kwargs):
    provenance_metadata = {}

    repr_cell = 'repr:' + cell.split('#')[1]
    for row in sorted(rdfgraph.query(
            'select ?execution ?endedAtTime ?startedAtTime ?executionTime ?source ?source_value where { ' + repr_cell + ' rdf:type p-plan:Step . \
            ?execution p-plan:correspondsToStep ' + repr_cell + '  . \
            ?execution prov:endedAtTime ?endedAtTime  . \
            ?execution prov:startedAtTime ?startedAtTime  . \
            ?execution repr:executionTime ?executionTime  . \
            ?execution prov:used ?source . \
            OPTIONAL { ?source rdf:value ?source_value } . \
            } '
    )):
        if 'provenance' not in provenance_metadata:
            provenance_metadata['provenance'] = []
        execution = 'repr:' + row.execution.split('#')[1]
        output = []
        output_provenance = []
        for output_row in sorted(rdfgraph.query(
            'select * where { ' + execution + ' prov:generated ?output . \
            ?output repr:hasType ?output_type . \
            OPTIONAL { ?output rdf:value ?output_value } . \
            OPTIONAL { ?output repr:hasErrorName ?output_errorname } . \
            OPTIONAL { ?output repr:hasErrorTraceback ?output_errortraceback } . \
            OPTIONAL { ?output repr:hasExecutionCount ?execution_count } . } '
        )):
            output_type = str(output_row.output_type)
            output = {
                'output_type' : str(output_row.output_type),
            }
            output_value = str(output_row.output_value)
            if output_type == 'execute_result' or output_type == 'display_data':
                repr_output = 'repr:' + output_row.output.split('#')[1]

                output['data'] = {}
                for suboutput_row in sorted(rdfgraph.query(
                    'select * where { ' + repr_output + ' repr:hasSubOutput ?suboutput . \
                        ?suboutput rdf:value ?output_value . \
                        ?suboutput repr:hasDataType ?output_datatype } '
                )):
                    if suboutput_row:
                        output_value = str(suboutput_row.output_value)
                        output_datatype = str(suboutput_row.output_datatype)

                        output['data'].update({
                            output_datatype: output_value
                        })
                    else:
                        output['data'] = {
                            output_datatype : output_value
                        }
                        output['metadata'] = {}
                        if row.execution_count:
                            output['execution_count'] = int(output_row.execution_count)
            elif output_type == 'stream':
                output['name'] = 'stdout'
                output['text'] = output_value
            elif output_type == 'error':
                output['ename'] = output_row.output_errorname
                output['evalue'] = output_value
                output['traceback'] = []#row.output_errortraceback
            output_provenance.append(output)

        provenance_metadata['provenance'].append({
            'end_time': row.endedAtTime,
            'start_time': row.startedAtTime,
            'execution_time': row.executionTime,
            'source': row.source_value,
            'outputs': output_provenance
            }
        )
    return provenance_metadata

def create_cell_output(**output):
    if output:
        output = nbbase.new_output(**output)
        return output
    else:
        return

def get_notebook_cells(rdfgraph):
    notebook_cells = []
    for row in rdfgraph.query(
            'select ?cell ?cell_type ?cell_index ?cell_execution_count where { \
            ?cell rdf:type p-plan:Step . \
            ?cell repr:hasCellType ?cell_type . \
            ?cell repr:hasIndex ?cell_index . \
            OPTIONAL { ?cell repr:hasExecutionCount ?cell_execution_count } . \
        } ORDER BY xsd:integer(?cell_index)'
    ):
        kwargs = {
            'cell_type': str(row.cell_type),
        }
        if row.cell_execution_count:
            kwargs['execution_count'] = int(row.cell_execution_count)
        cells = create_cells(rdfgraph, row.cell, row.cell_index, **kwargs)
        notebook_cells.append(cells)

    return notebook_cells

def get_notebook_metadata(rdfgraph):
    metadata = {}

    for row in sorted(rdfgraph.query(
        'select * where { \
            ?notebook rdf:type repr:Notebook . \
            OPTIONAL { ?notebook repr:hasKernelDisplayName ?kernel_display_name } . \
            OPTIONAL { ?notebook repr:hasKernelName ?kernel_name } . \
            OPTIONAL { ?notebook prov:wasAttributedTo ?agent } .\
            OPTIONAL { ?notebook repr:hasProgrammingLanguage ?programminglanguage } . \
            OPTIONAL { ?notebook repr:hasProgrammingLanguageExtension ?programminglanguage_extension } . \
            OPTIONAL { ?notebook repr:hasProgrammingLanguageVersion ?programminglanguage_version } . \
        }'
    )):
        if row.kernel_display_name:
            metadata['kernelspec'] = {
                'display_name' : str(row.kernel_display_name),
                'name' : str(row.kernel_name),
            }
        if row.programminglanguage:
            metadata['language_info'] = {
                'file_extension' : str(row.programminglanguage_extension),
                'name' : str(row.programminglanguage),
                'version' : str(row.programminglanguage_version),
            }
        if row.agent and 'authors' not in metadata:
            metadata['authors'] = []
        if row.agent:
            metadata['authors'].append({'name' : str(row.agent)})
    return metadata



def convert_rdf_to_notebook(args):
    infile = args.input_file

    input_file = os.path.basename(infile)
    notebook_name, extension = os.path.splitext(input_file)
    input_file_directory = os.path.dirname(infile)
    output_file_extension = 'ipynb'
    output_file = os.path.join(input_file_directory, notebook_name + "_rdf2nb." + output_file_extension)
    print("Converting RDF file {0} to notebook {1}".format(input_file,output_file))

    notebook = io.open(infile).read()
    g = Graph()
    nbrdf = g.parse(infile, format="turtle")
    nbconvert_rdf = get_notebook_cells(nbrdf)
    metadata = get_notebook_metadata(nbrdf)
    nb = nbbase.new_notebook(cells=nbconvert_rdf, metadata=metadata)
    validate_result = nbbase.validate(nb)
    with io.open(output_file, 'w', encoding='utf-8') as fout:
        nbformat.write(nb, fout, version=max(nbformat.versions))
        return nb
