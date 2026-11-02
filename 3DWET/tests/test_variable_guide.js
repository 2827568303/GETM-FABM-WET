const assert = require('node:assert/strict');
const guide = require('../app/static/js/variable_guide.js');
assert.match(guide.formatReference({kind:'standard',lower:5,unit:'mg/L'}), /≥ 5/);
assert.match(guide.formatReference({kind:'unset'}), /未设置/);
const standard = guide.assess([null, 3, 5, 8, NaN], {kind:'standard',lower:5});
assert.equal(standard.count, 3);
assert.equal(standard.outside, 1);
assert.equal(standard.status, 'warning');
const initial = guide.assess([8,12], {kind:'initial',value:5});
assert.equal(initial.delta,5);
assert.equal(initial.status,'reference'); // Initial state is not a health threshold.
assert.equal(guide.assess([null,NaN],{kind:'standard',upper:1}).status,'empty');
assert.equal(guide.assess([1],{kind:'unset'}).status,'unset');
console.log('Variable guide: missing values, lower bounds, initial comparison PASS');
