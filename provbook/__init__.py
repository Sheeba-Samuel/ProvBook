# coding: utf-8

# Author: Sheeba Samuel, <sheeba.samuel@uni-jena.de> https://github.com/Sheeba-Samuel

from __future__ import unicode_literals

from ._version import __version__

from nbdime.diffing import diff, diff_notebooks

def load_jupyter_server_extension(nb_server_app):
    # Wrap this here to avoid pulling in webapp in a normal run
    from .webapp.nb_server_extension import _load_jupyter_server_extension
    _load_jupyter_server_extension(nb_server_app)


def _jupyter_server_extension_paths():
    return [{
        "module": "provbook"
    }]


def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `nbdime` directory
        src="notebook_ext",
        # directory in the `nbextension/` namespace
        dest="provbook",
        # _also_ in the `nbextension/` namespace
        require="provbook/index")]


__all__ = [
    "__version__",
    "diff", "diff_notebooks",
    "load_jupyter_server_extension",
    ]
