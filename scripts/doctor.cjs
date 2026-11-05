#!/usr/bin/env node
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.join(__dirname, '..');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ai-paper-study-'));
let failed = false;
try {
  if (Number(process.versions.node.split('.')[0]) < 20 || (Number(process.versions.node.split('.')[0]) === 20 && Number(process.versions.node.split('.')[1]) < 18)) throw Error('Node.js 20.18+ required');
  for (const name of ['marked', 'katex']) require.resolve(name);
  const output = path.join(temp, 'demo.html');
  const result = spawnSync(process.execPath, [path.join(__dirname, 'render-reading.cjs'), path.join(root, 'examples/demo/reading.md'), output], { encoding: 'utf8' });
  if (result.status !== 0) throw Error(result.stderr || result.stdout);
  const html = fs.readFileSync(output, 'utf8');
  for (const text of ['class="katex"', 'href="#section-1"', 'data:image/svg+xml;base64,', 'data:font/woff2;base64,', 'AI PAPER STUDY']) {
    if (!html.includes(text)) throw Error('Missing rendered feature: ' + text);
  }
  console.log('OK: offline HTML, Chinese content, equations, embedded flow diagram, fonts and navigation.');
  const candidates = process.env.PYTHON ? [process.env.PYTHON] : process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  let found = false;
  for (const executable of candidates) {
    const check = spawnSync(executable, ['-c', 'import pymupdf; print(pymupdf.VersionBind)'], { encoding: 'utf8' });
    if (check.status === 0) { console.log('OK: PyMuPDF ' + check.stdout.trim() + ' (' + executable + ')'); found = true; break; }
  }
  if (!found) {
    console.error('PDF tools unavailable: run python -m pip install -r requirements.txt; or set PYTHON to your interpreter.');
    failed = true;
  }
  console.log('This is a tool check using a teaching example, not a paper-reading or comprehension test.');
} catch (error) { console.error(error.message); failed = true; }
finally { fs.rmSync(temp, { recursive: true, force: true }); }
if (failed) process.exitCode = 1;
