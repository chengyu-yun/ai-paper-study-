#!/usr/bin/env node
// Package runtime files and source attribution; leave dependencies to package managers.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
if (args.includes('--help')) { console.log('node scripts/pack-skill.cjs [--out <new-directory>]'); process.exit(0); }
try {
  if (args.length && (args.length !== 2 || args[0] !== '--out' || !args[1])) throw Error('Use --out <new-directory> or no arguments');
  const out = path.resolve(args[1] || path.join(root, 'dist/ai-paper-study'));
  if (fs.existsSync(out) || fs.existsSync(out + '.tar.gz')) throw Error('Output exists: ' + out);
  for (const name of ['scripts', 'assets', 'templates', 'references', 'agents', 'licenses', 'examples']) {
    const source = path.join(root, name);
    const relative = path.relative(source, out);
    if (!relative || (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative))) throw Error('Output cannot be inside runtime source directories');
  }
  if (out === root) throw Error('Output cannot be the project root');
  const selected = [];
  function collect(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const source = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) throw Error('Runtime symlink not supported: ' + source);
      if (entry.isDirectory()) collect(source);
      else if (!source.endsWith('.pyc') && !source.includes(path.sep + '__pycache__' + path.sep)) selected.push(source);
    }
  }
  for (const name of ['SKILL.md', 'README.md', 'package.json', 'package-lock.json', 'requirements.txt', 'THIRD_PARTY_NOTICES.md']) selected.push(path.join(root, name));
  if (fs.existsSync(path.join(root, 'LICENSE'))) selected.push(path.join(root, 'LICENSE'));
  for (const name of ['scripts', 'assets', 'templates', 'references', 'agents', 'licenses', 'examples']) collect(path.join(root, name));
  const manifest = [];
  for (const source of selected) {
    const relative = path.relative(root, source);
    const target = path.join(out, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    const content = fs.readFileSync(source);
    fs.writeFileSync(target, content);
    manifest.push({ path: relative.split(path.sep).join('/'), bytes: content.length, sha256: crypto.createHash('sha256').update(content).digest('hex') });
  }
  const pkgFile = path.join(out, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgFile, 'utf8'));
  delete pkg.scripts.test; delete pkg.scripts['pack:skill'];
  fs.writeFileSync(pkgFile, JSON.stringify(pkg, null, 2) + '\n');
  const packageRecord = manifest.find(item => item.path === 'package.json');
  const finalPackage = fs.readFileSync(pkgFile);
  Object.assign(packageRecord, { bytes: finalPackage.length, sha256: crypto.createHash('sha256').update(finalPackage).digest('hex') });
  fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify({ version: pkg.version, files: manifest }, null, 2) + '\n');
  const archive = spawnSync('tar', ['-czf', out + '.tar.gz', '-C', path.dirname(out), path.basename(out)], { encoding: 'utf8' });
  console.log('Packaged ' + manifest.length + ' files in ' + out);
  console.log(archive.status === 0 ? 'Archive: ' + out + '.tar.gz' : 'Archive unavailable; the directory is ready to copy.');
} catch (error) { console.error(error.message); process.exitCode = 1; }
