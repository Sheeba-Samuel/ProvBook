// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
'use strict';


import {
  nbformat
} from '@jupyterlab/coreutils';

import {
  Panel, Widget
} from '@phosphor/widgets';

import {
  RenderMimeRegistry
} from '@jupyterlab/rendermime';

import {
  defaultSanitizer
} from '@jupyterlab/apputils';

import {
  IDiffEntry
} from 'nbdime/lib/diff/diffentries';

import {
  NotebookDiffModel
} from 'nbdime/lib/diff/model';

import {
  NotebookDiffWidget
} from 'nbdime/lib/diff/widget';

import {
  requestDiff
} from './request';

import {
  getBaseUrl, getConfigOption, toggleSpinner, toggleShowUnchanged,
  markUnchangedRanges
} from './common';

import {
  exportDiff
} from './staticdiff';

import {
  rendererFactories
} from './rendermime';

let diffWidget: NotebookDiffWidget | null = null;

const prefixes = ['git:', 'checkpoint:'];

function hasPrefix(candidate: string): boolean {
  for (let p of prefixes) {
    if (candidate.slice(0, p.length) === p) {
      return true;
    }
  }
  return false;
}

function stripPrefix(s: string): string {
  for (let p of prefixes) {
    if (s.slice(0, p.length) === p) {
      return s.slice(p.length);
    }
  }
  return s;
}


/**
 * Show the diff as represented by the base notebook and a list of diff entries
 */
function showDiff(data: {base: nbformat.INotebookContent, diff: IDiffEntry[]}): Promise<void> {


  let rendermime = new RenderMimeRegistry({
    initialFactories: rendererFactories,
    sanitizer: defaultSanitizer,
  });

  let nbdModel = new NotebookDiffModel(data.base, data.diff);
  let nbdWidget = new NotebookDiffWidget(nbdModel, rendermime);

  let root = document.getElementById('nbdime-root');
  if (!root) {
    throw new Error('Missing root element "nbidme-root"');
  }
  root.innerHTML = '';
  let panel = new Panel();
  panel.id = 'main';
  Widget.attach(panel, root);
  panel.addWidget(nbdWidget);
  let work = nbdWidget.init();
  work.then(() => {
    window.onresize = () => { panel.update(); };
  });
  diffWidget = nbdWidget;
  return work;
}



function compare(base: string, remote: string | undefined, cell_index: number, base_selected_execution:number, remote_selected_execution: number, baseUrl:string, pushHistory: boolean | 'replace') {
  toggleSpinner(true);
  getDiff(base, remote, cell_index, base_selected_execution, remote_selected_execution, baseUrl);
  if (pushHistory) {
    let uri = window.location.pathname;
    base = stripPrefix(base);
    uri = '?base=' + encodeURIComponent(base);
    if (remote) {
      uri += '&remote=' + encodeURIComponent(remote);
    }
    editHistory(pushHistory, {base, remote},
      'Diff: "' + base + '" vs "' + remote + '"', uri);
  }
}

function editHistory(pushHistory: boolean | 'replace', statedata: any, title: string, url?: string): void {
  if (pushHistory === true) {
    history.pushState(statedata, title, url);
  } else if (pushHistory === 'replace') {
    history.replaceState(statedata, title, url);
  }
}


/**
 * Calls `requestDiff` with our response handlers
 */
export
function getDiff(base: string, remote: string | undefined, cell_index: number, base_selected_execution:number, remote_selected_execution: number, baseUrl:string) {  
  requestDiff(base, remote, cell_index, base_selected_execution, remote_selected_execution, baseUrl, onDiffRequestCompleted, onDiffRequestFailed);
}

/**
 * Callback for a successfull diff request
 */
function onDiffRequestCompleted(data: any) {
  let layoutWork = showDiff(data);

  layoutWork.then(() => {
    let exportBtn = document.getElementById('nbdime-export') as HTMLButtonElement;
    exportBtn.style.display = 'initial';
    toggleSpinner(false);
    markUnchangedRanges();
  });
}

/**
 * Callback for a failed diff request
 */
function onDiffRequestFailed(response: string) {
  console.log('Diff request failed.');
  let root = document.getElementById('nbdime-root');
  if (!root) {
    throw new Error('Missing root element "nbidme-root"');
  }
  root.innerHTML = '<pre>' + response + '</pre>';
  diffWidget = null;
  toggleSpinner(false);
}
/**
 *
 */
export
function initializeDiff() {
  
  // If arguments supplied in config, run diff directly:
  let base = getConfigOption('base');
  let remote = getConfigOption('remote');
  let cell_index = getConfigOption('cell_index');
  let base_selected_execution = getConfigOption('base_selected_execution');
  let remote_selected_execution = getConfigOption('remote_selected_execution');
  let baseUrl = getConfigOption('baseurl');
  if (base && (remote || hasPrefix(base))) {
    compare(base, remote, cell_index, base_selected_execution, remote_selected_execution, baseUrl, 'replace');
  }

  let exportBtn = document.getElementById('nbdime-export') as HTMLButtonElement;
  exportBtn.onclick = exportDiff;

  let hideUnchangedChk = document.getElementById('nbdime-hide-unchanged') as HTMLInputElement;
  hideUnchangedChk.onchange = () => {
    toggleShowUnchanged(!hideUnchangedChk.checked);
  };
}
