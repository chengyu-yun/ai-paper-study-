#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.join(__dirname, '..');
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--out')) throw Error('Use --out <new-directory>');
const out = path.resolve(args[1] || path.join(root, 'outputs/demo'));
if (fs.existsSync(out)) throw Error('Demo directory exists; choose a new --out directory');
const candidates = process.env.PYTHON ? [process.env.PYTHON] : process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
const python = candidates.find(exe => spawnSync(exe, ['-c', 'import pymupdf']).status === 0);
if (!python) throw Error('Install PyMuPDF or set PYTHON');
fs.mkdirSync(out, { recursive: true });
for (const [exe, argv] of [
  [process.execPath, [path.join(__dirname, 'render-reading.cjs'), path.join(root, 'examples/demo/reading.md'), path.join(out, 'reading.html')]],
  [python, ['-X', 'utf8', path.join(__dirname, 'demo_pdf.py'), '--out', out]],
]) {
  const result = spawnSync(exe, argv, { stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status || 1);
}
console.log('Open ' + path.join(out, 'reading.html') + ' or teaching-annotated.pdf.');
