const path = require('path');
const Mocha = require('mocha');

const mocha = new Mocha({ ui: 'tdd', timeout: 60000 });

const tests = [
  path.resolve(__dirname, 'extension.test.js'),
  path.resolve(__dirname, 'analyze.test.js'),
];

tests.forEach((f) => mocha.addFile(f));

mocha.run((failures) => {
  process.exitCode = failures ? 1 : 0;
});
