// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
'use strict';

import {
  JSONObject
} from '@phosphor/coreutils';

import {
  URLExt
} from '@jupyterlab/coreutils/lib/url';

import {
  ServerConnection
} from '@jupyterlab/services';


function urlRStrip(target: string): string {
  if (target.slice(-1) === '/') {
    return target.slice(0, -1);
  }
  return target;
}


export
function handleError(response: Response): Promise<Response> | Response {
  if (!response.ok) {
    if (response.status === 500 && response.body) {
      return response.text().then((body) => {
        throw new Error(body);
      });
    }
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response;
}


/**
 * Make a POST request passing a JSON argument and receiving a JSON result.
 */
export
function requestJsonPromise(url: string, argument: any): Promise<JSONObject> {
  let request = {
      method: 'POST',
      body: JSON.stringify(argument),
    };
  let settings = ServerConnection.makeSettings();
  return ServerConnection.makeRequest(url, request, settings)
    .then(handleError)
    .then((response) => {
      return response.json();
    });
}

/**
 * Make a POST request passing a JSON argument and receiving a JSON result.
 */
export
function requestJson(url: string, argument: any, callback: (result: any) => void, onError: (result: any) => void): void {
  let promise = requestJsonPromise(url, argument);
  promise.then((data) => {
    callback(data);
  }, (error: ServerConnection.NetworkError | ServerConnection.ResponseError) => {
    onError(error.message);
  });
}

/**
 * Make a diff request for the given base/remote specifiers (filenames)
 */
export
function requestDiff(
    base: string, remote: string | undefined, cell_index: number, base_selected_execution:number, remote_selected_execution: number,
    baseUrl: string,
    onComplete: (result: any) => void,
    onFail: (result: any) => void): void {
  requestJson(URLExt.join(window.location.origin, window.location.pathname, 'api/diff'),
              {base, remote, cell_index, base_selected_execution, remote_selected_execution},
              onComplete,
              onFail);
}
