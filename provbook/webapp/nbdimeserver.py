#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import logging
import os
import sys
from argparse import ArgumentParser

from six import string_types
from tornado import ioloop, web, escape, netutil, httpserver
import nbformat
from jinja2 import FileSystemLoader, Environment

import nbdime
from nbdime.utils import EXPLICIT_MISSING_FILE

from nbdime.args import add_generic_args, add_web_args

from notebook.base.handlers import IPythonHandler, APIHandler
from notebook import DEFAULT_STATIC_FILES_PATH
from notebook.utils import url_path_join
from notebook.log import log_request
from nbdime.webapp.nbdimeserver import NbdimeHandler, ApiCloseHandler

# TODO: See <notebook>/notebook/services/contents/handlers.py for possibly useful utilities:
#contents_manager
#ContentsHandler


_logger = logging.getLogger(__name__)


here = os.path.abspath(os.path.dirname(__file__))
static_path = os.path.join(here, 'static')
template_path = os.path.join(here, 'templates')


class ApiDiffHandler(NbdimeHandler, APIHandler):
    def post(self):
        base_nb = self.get_notebook_argument('base')
        body = json.loads(escape.to_unicode(self.request.body))        
        base_selected_execution = body['base_selected_execution']
        remote_selected_execution = body['remote_selected_execution']
        cell_index = body['cell_index']
        base_notebook = {}
        remote_notebook = {}
        base_notebook['metadata'] = base_nb['metadata']
        remote_notebook['metadata'] = base_nb['metadata']
        base_notebook['nbformat'] = base_nb['nbformat']
        remote_notebook['nbformat'] = base_nb['nbformat']
        base_notebook['nbformat_minor'] = base_nb['nbformat_minor']
        remote_notebook['nbformat_minor'] = base_nb['nbformat_minor']
        
        base_notebook['cells'] = []
        remote_notebook['cells'] = []
        
        for cell_i, cell_node in enumerate(base_nb['cells']):
            base_prov_obj = {}
            remote_prov_obj = {}
            if (int(cell_i) == int(cell_index)):
                if 'provenance' in cell_node['metadata']:
                    
                    provenance = cell_node['metadata']['provenance']
                    base_selected_execution_prov = provenance[base_selected_execution]
                    remote_selected_execution_prov = provenance[remote_selected_execution]  
                    base_prov_obj['source'] = base_selected_execution_prov['source']
                    remote_prov_obj['source'] = remote_selected_execution_prov['source']
                    base_prov_obj['outputs'] = base_selected_execution_prov['outputs']                
                    remote_prov_obj['outputs'] = remote_selected_execution_prov['outputs']
                    base_prov_obj['execution_count'] = cell_node['execution_count']                
                    remote_prov_obj['execution_count'] = cell_node['execution_count']
                    base_prov_obj['metadata'] = {}
                    remote_prov_obj['metadata'] = {}
                    base_prov_obj['cell_type'] = cell_node['cell_type']
                    remote_prov_obj['cell_type'] = cell_node['cell_type']
                    base_notebook['cells'] = [base_prov_obj]
                    remote_notebook['cells'] = [remote_prov_obj]
                    d = nbdime.diff(provenance[base_selected_execution], provenance[remote_selected_execution])
                else:
                    base_notebook = base_nb
                    remote_notebook = base_nb
        try:
            thediff = nbdime.diff_notebooks(base_notebook, remote_notebook)
        except Exception:
            nbdime.log.exception('Error diffing documents:')
            raise web.HTTPError(500, 'Error while attempting to diff documents')
        data = {
            'base': base_notebook,            
            'diff': thediff,
            }
        self.finish(data)

    def get_notebook_argument(self, argname):
        if 'difftool_args' in self.params:
            arg = self.params['difftool_args'][argname]
            if not isinstance(arg, string_types):
                # Assume arg is file-like
                arg.seek(0)
                return nbformat.read(arg, as_version=4)
            return self.read_notebook(arg)
        return super(ApiDiffHandler, self).get_notebook_argument(argname)


def make_app(**params):
    base_url = params.pop('base_url', '/')
    handlers = [
        (r'/api/diff', ApiDiffHandler, params),
        (r'/api/closetool', ApiCloseHandler, params),
        (r'/nb-static/mathjax/(.*)', web.StaticFileHandler, {
            'path': os.path.join(DEFAULT_STATIC_FILES_PATH, 'components', 'MathJax')
        })
        # Static handler will be added automatically
    ]
    if base_url != '/':
        prefix = base_url.rstrip('/')
        handlers = [
            (prefix + path, cls, params)
            for (path, cls, params) in handlers
        ]
    else:
        prefix = ''

    env = Environment(loader=FileSystemLoader([template_path]), autoescape=False)
    settings = {
        'log_function': log_request,
        'static_path': static_path,
        'static_url_prefix': prefix + '/static/',
        'template_path': [template_path],
        'base_url': base_url,
        'jinja2_env': env,
        'mathjax_url': prefix + '/nb-static/mathjax/MathJax.js',
        }

    if nbdime.utils.is_in_repo(nbdime.__file__):
        # don't cache when working from repo
        settings.update({
            # 'autoreload': True,
            'compiled_template_cache': False,
            'static_hash_cache': False,
            # 'serve_traceback': True,
            })

    app = web.Application(handlers, **settings)
    app.exit_code = 0
    return app


def init_app(on_port=None, closable=False, **params):
    _logger.debug('Using params: %s' % params)
    params.update({'closable': closable})
    port = params.pop('port', 0)
    ip = params.pop('ip', '127.0.0.1')
    app = make_app(**params)
    if port != 0:
        server = app.listen(port, address=ip)
        _logger.info('Listening on %s, port %d', ip, port)
    else:
        sockets = netutil.bind_sockets(0, ip)
        server = httpserver.HTTPServer(app)
        server.add_sockets(sockets)
        for s in sockets:
            _logger.info('Listening on %s, port %d', *s.getsockname()[:2])
            port = s.getsockname()[1]
    if on_port is not None:
        on_port(port)
    return app, server


def main_server(on_port=None, closable=False, **params):
    app, server = init_app(on_port, closable, **params)
    io_loop = ioloop.IOLoop.current()
    if sys.platform.startswith('win'):
        # workaround for tornado on Windows:
        # add no-op to wake every 5s
        # to handle signals that may be ignored by the inner loop
        pc = ioloop.PeriodicCallback(lambda : None, 5000)
        pc.start()
    io_loop.start()
    # Clean up after server:
    server.stop()
    return app.exit_code


def _build_arg_parser():
    """
    Creates an argument parser that lets the user specify a port
    and displays a help message.
    """
    description = 'Web interface for Nbdime.'
    parser = ArgumentParser(description=description)
    add_generic_args(parser)
    add_web_args(parser)
    return parser


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    arguments = _build_arg_parser().parse_args(args)
    return main_server(port=arguments.port,
                       ip=arguments.ip,
                       cwd=arguments.workdirectory,
                       base_url=arguments.base_url,
                      )


if __name__ == '__main__':
    sys.exit(main())
