const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/index.ts',
  output: {
    path: path.resolve(__dirname, '..', '..', 'provbook', 'webapp', 'static'),
    filename: "provbookdiff.js",
    publicPath: "./static/"
  },
  bail: true,
  devtool: 'source-map',
  module: {
    rules: [
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.ipynb$/, type: 'json' },
      { test: /\.ts$/, loader: 'ts-loader' },
      { test: /\.js$/, loader: "source-map-loader", exclude: [/node_modules/, /build/, /__test__/] },
      { test: /\.html$/, loader: 'file-loader' },
      // jquery-ui loads some images
      { test: /\.(jpg|png|gif)$/, loader: 'file-loader' },
      // required to load font-awesome
      { test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/, loader: 'url-loader?limit=10000&mimetype=application/font-woff' },
      { test: /\.woff(\?v=\d+\.\d+\.\d+)?$/, loader: 'url-loader?limit=10000&mimetype=application/font-woff' },
      { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, loader: 'url-loader?limit=10000&mimetype=application/octet-stream' },
      { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, loader: 'file-loader' },
      { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, loader: 'url-loader?limit=10000&mimetype=image/svg+xml' }
    ],
  },
  resolve: {
    // Add '.ts' and '.tsx' as resolvable extensions.
    extensions: [".webpack.js", ".web.js", ".ts", ".js"]
  }

}
