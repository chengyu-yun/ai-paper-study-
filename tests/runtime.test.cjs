const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
function workspace(fn) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ai-study-test-'));
  try { return fn(temp); } finally { fs.rmSync(temp, { recursive: true, force: true }); }
}
function node(script, args) { return spawnSync(process.execPath, [path.join(root, script), ...args], { encoding: 'utf8' }); }
test('render a self-contained Chinese reading with math, SVG, actual section links and source toggles', () => workspace(temp => {
  const out = path.join(temp, 'reading.html');
  const result = node('scripts/render-reading.cjs', [path.join(root, 'examples/demo/reading.md'), out]);
  assert.equal(result.status, 0, result.stderr);
  const html = fs.readFileSync(out, 'utf8');
  for (const expected of ['AI PAPER STUDY', 'class="katex"', 'data:image/svg+xml;base64,', 'data:font/woff2;base64,', 'connect-src', 'show-sources', '<details']) assert.ok(html.includes(expected), expected);
  for (const link of html.matchAll(/href="#(section-\d+)"/g)) assert.ok(html.includes('id="' + link[1] + '"'));
  assert.equal((html.match(/<h2 id="section-/g) || []).length, 10);
  assert.ok(!/<(?:img|script)[^>]+src=["']https?:/.test(html));
}));
test('renderer refuses missing images without replacing the source or an existing output', () => workspace(temp => {
  const input = path.join(temp, 'source.md');
  const source = '<!-- paper-reading-lang: zh-CN -->\n# Test\n## Test\n![missing](missing.png)\n';
  fs.writeFileSync(input, source);
  assert.notEqual(node('scripts/render-reading.cjs', [input, input]).status, 0);
  assert.equal(fs.readFileSync(input, 'utf8'), source);
  const out = path.join(temp, 'existing.html'); fs.writeFileSync(out, 'keep');
  assert.notEqual(node('scripts/render-reading.cjs', [input, out]).status, 0);
  assert.equal(fs.readFileSync(out, 'utf8'), 'keep');
  assert.notEqual(node('scripts/render-reading.cjs', [input, path.join(temp, 'new.html')]).status, 0);
  assert.ok(!fs.existsSync(path.join(temp, 'new.html')));
}));
test('initializer creates an editable ten-section draft and preserves an existing directory', () => workspace(temp => {
  const out = path.join(temp, 'new');
  const result = node('scripts/init-study.cjs', ['--out', out, '--title', '测试论文', '--paper', 'paper.pdf']);
  assert.equal(result.status, 0, result.stderr);
  const source = fs.readFileSync(path.join(out, 'reading.md'), 'utf8');
  assert.ok(source.includes('未完成草稿'));
  assert.equal((source.match(/^## /gm) || []).length, 10);
  assert.notEqual(node('scripts/init-study.cjs', ['--out', out, '--title', 'overwrite']).status, 0);
  assert.equal(fs.readFileSync(path.join(out, 'reading.md'), 'utf8'), source);
}));
test('runtime package includes dependencies metadata, attribution, working example and verified checksums', () => workspace(temp => {
  const out = path.join(temp, 'package');
  const result = node('scripts/pack-skill.cjs', ['--out', out]);
  assert.equal(result.status, 0, result.stderr);
  const manifest = JSON.parse(fs.readFileSync(path.join(out, 'manifest.json'), 'utf8'));
  for (const item of manifest.files) {
    const content = fs.readFileSync(path.join(out, item.path));
    assert.equal(content.length, item.bytes);
    assert.equal(crypto.createHash('sha256').update(content).digest('hex'), item.sha256);
  }
  assert.ok(fs.existsSync(path.join(out, 'licenses/paper-reading-MIT.txt')));
  assert.ok(fs.existsSync(path.join(out, 'scripts/pdf_tools.py')));
  assert.ok(!fs.existsSync(path.join(out, 'node_modules')));
}));
test('PDF extraction, matching, Chinese annotations, note pagination and source preservation', () => {
  const candidates = process.env.PYTHON ? [process.env.PYTHON] : process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  let executable;
  for (const candidate of candidates) if (spawnSync(candidate, ['-c', 'import pymupdf']).status === 0) { executable = candidate; break; }
  assert.ok(executable, 'Install PyMuPDF or set PYTHON');
  const result = spawnSync(executable, ['-X', 'utf8', path.join(root, 'tests/test_pdf_tools.py')], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stdout + result.stderr);
});
