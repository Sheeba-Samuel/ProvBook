#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

from __future__ import print_function

import json
import os

from jinja2 import ChoiceLoader, FileSystemLoader

from notebook.utils import url_path_join, to_os_path
from tornado.web import HTTPError, escape, authenticated, gen
import nbformat

from .nbdimeserver import (
    template_path,
    static_path,
    NbdimeHandler,
    ApiDiffHandler,
)


class ProvBookDiffHandler(NbdimeHandler):

    @authenticated
    def get(self):

        args= {}
        base = self.get_argument('base', '')
        base_selected_execution = int(self.get_argument('base_selected_execution', ''))
        remote_selected_execution = int(self.get_argument('remote_selected_execution', ''))
        cell_index = self.get_argument('cell_index', '')
        args['base'] = base
        args['remote'] = base
        args['baseurl'] = 'provbookdiff'
        args['cell_index'] = cell_index
        args['base_selected_execution'] = base_selected_execution
        args['remote_selected_execution'] = remote_selected_execution
        self.write(self.render_template(
            'provbookdiff.html',
            config_data=args,
        ))


def _load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app

    env = web_app.settings['jinja2_env']

    env.loader = ChoiceLoader([
        env.loader,
        FileSystemLoader(template_path),
    ])

    web_app.settings['static_path'].append(static_path)

    params = {
        'nbdime_relative_base_url': 'provbookdiff',
        'closable': False,
    }
    handlers = [
        (r'/provbookdiff/api/diff', ApiDiffHandler, params),
        (r'/provbookdiff', ProvBookDiffHandler, params),
    ]

    # Prefix routes with base_url:
    base_url = web_app.settings.get('base_url', '/')
    handlers = [(url_path_join(base_url, h[0]), h[1], h[2]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
