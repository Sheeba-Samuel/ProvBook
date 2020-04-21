// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
'use strict';

import {
  initializeDiff
} from './app/diff';

import {
  closeTool, getConfigOption, handleError, toolClosed
} from './app/common';


import 'codemirror/lib/codemirror.css';
import '@jupyterlab/codemirror/style/index.css';

import '@phosphor/widgets/style/index.css';
import '@phosphor/dragdrop/style/index.css';

import '@jupyterlab/application/style/materialcolors.css';
import '@jupyterlab/theme-light-extension/static/index.css';
import '@jupyterlab/notebook/style/index.css';
import '@jupyterlab/cells/style/index.css';
import '@jupyterlab/rendermime/style/index.css';
import '@jupyterlab/codemirror/style/index.css';

import 'nbdime/lib/common/collapsible.css';
import 'nbdime/lib/upstreaming/flexpanel.css';
import 'nbdime/lib/common/dragpanel.css';
import 'nbdime/lib/styles/variables.css';
import 'nbdime/lib/styles/common.css';
import 'nbdime/lib/styles/diff.css';
import 'nbdime/lib/styles/merge.css';

import './app/common.css';
import './app/diff.css';


/** */
function initialize() {
  let closable = getConfigOption('closable');
  let type: 'diff' ;
  if (document.getElementById('provbookdiff')) {
    initializeDiff();
    type = 'diff';
  }

  let closeBtn = document.getElementById('nbdime-close') as HTMLButtonElement;
  if (closable) {
    let close = (ev: Event, unloading=false) => {
      if (!unloading) {
        return closeTool();
      }
      return null;
    };
    closeBtn.onclick = close;

    window.onbeforeunload = (ev: Event) => {
      if (!toolClosed) {
        return close(ev, true);
      }
    };

    window.onunload = (ev: Event) => {
      if (!toolClosed) {
          closeTool();
      }
    };

    closeBtn.style.display = 'initial';
  }
}

window.onload = initialize;
window.onerror = handleError;
