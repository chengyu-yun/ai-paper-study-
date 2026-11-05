#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const args = process.argv.slice(2);
if (args.includes('--help')) {
  console.log('node scripts/init-study.cjs --out <new-directory> --title <title> [--paper <PDF-or-URL>]');
  process.exit(0);
}
try {
  const opts = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!['--out', '--title', '--paper'].includes(args[i]) || !args[i + 1] || args[i + 1].startsWith('--')) throw Error('Invalid arguments; use --help');
    if (opts[args[i]]) throw Error('Repeated option: ' + args[i]);
    opts[args[i]] = args[i + 1];
  }
  if (!opts['--out'] || !opts['--title']) throw Error('--out and --title are required');
  const out = path.resolve(opts['--out']);
  if (fs.existsSync(out)) throw Error('Directory exists; choose a new output directory: ' + out);
  const escape = value => value.replace(/[\r\n]/g, ' ').replace(/[\\`*_{}\[\]<>]/g, '\\$&');
  const template = fs.readFileSync(path.join(__dirname, '../templates/reading.md'), 'utf8');
  const content = template.replace('{{TITLE}}', () => escape(opts['--title'])).replace('{{PAPER}}', () => escape(opts['--paper'] || '原文未提供'));
  fs.mkdirSync(path.join(out, 'assets'), { recursive: true });
  fs.writeFileSync(path.join(out, 'reading.md'), content);
  fs.writeFileSync(path.join(out, 'notes.json'), JSON.stringify({ annotations: [] }, null, 2) + '\n');
  console.log('Created reading.md, assets/ and notes.json in ' + out);
  console.log('Draft only. Read the paper and author the explanation before rendering.');
} catch (error) { console.error(error.message); process.exitCode = 1; }
