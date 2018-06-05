# notebook_rdf : Convert Jupyter Notebooks to RDF and the converted RDF back to Jupyter Notebooks

This utility converts Jupyter Notebooks to RDF. This is a command line utility which takes a notebook as input and generates RDF Turtle file. The RDF is generated using the REPRODUCE-ME ontology extended from W3C standard PROV-O and the P-Plan ontology. The RDF generated from the notebook can be converted back to a Jupyter Notebook.

## Install

```bash
cd notebook_rdf
python3 setup.py install
```

## Usage

Example usage of notebook_rdf

Convert your notebook to RDF
    python3.5 notebook_rdf your_notebook.ipynb
    or
    python3.5 notebook_rdf --from notebook your_notebook.ipynb --to RDF

Convert your RDF to notebook
    python3.5 notebook_rdf notebook_rdf.ttl
    or
    python3.5 notebook_rdf --from RDF notebook_rdf.ttl --to notebook
    
The example notebook converted to rdf and back to notebook is available in the examples directory.
