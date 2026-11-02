const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../app/templates/index.html'), 'utf8');
for (const kind of ['viz2d', 'viz3d']) {
  const select = html.match(new RegExp(`<select id="${kind}-speed"[\\s\\S]*?</select>`));
  assert.ok(select, `${kind} playback speed control exists`);
  const values = [...select[0].matchAll(/<option value="([^"]+)"/g)].map(match => Number(match[1]));
  assert.ok(values.includes(8), `${kind} exposes an 8 fps target`);
  assert.ok(values.includes(12), `${kind} exposes a 12 fps target`);
}
