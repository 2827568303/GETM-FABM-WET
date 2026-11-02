const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const helper = '3DWET/app/static/js/model_dates.js';
assert.ok(fs.existsSync(helper), 'year + ordinal-day conversion module must exist');
const context = vm.createContext({console, Date});
vm.runInContext(fs.readFileSync(helper, 'utf8'), context);
const D = vm.runInContext('ModelDates', context);
for (const [iso, ordinal] of [
    ['2023-01-01', '2023-DOY001'], ['2023-12-31', '2023-DOY365'],
    ['2024-02-28', '2024-DOY059'], ['2024-02-29', '2024-DOY060'],
    ['2024-03-01', '2024-DOY061'], ['2024-12-31', '2024-DOY366'],
    ['2025-01-01', '2025-DOY001'], ['1900-03-01', '1900-DOY060'],
    ['2000-02-29', '2000-DOY060'], ['0099-01-01', '0099-DOY001'],
]) {
    assert.equal(D.format(iso), ordinal);
    assert.equal(D.toIso(ordinal), iso);
}
assert.equal(D.format('2024-02-29 12:34:56'), '2024-DOY060 12:34:56');
assert.equal(D.toIso('2024-DOY060 12:34:56', {time:true}), '2024-02-29 12:34:56');
assert.equal(D.toIso('2024-060', {time:true}), '2024-02-29 00:00:00');
assert.equal(D.format('2024-03-01T00:30:00+08:00'), '2024-DOY060 16:30:00');
assert.equal(D.format('2024/02/29'), '2024-DOY060');
assert.equal(D.format('2024/2/29'), '2024-DOY060', 'legacy padded and unpadded imports');
assert.equal(D.format('2/29/2024'), '2024-DOY060', 'legacy US CSV date');
assert.equal(D.format('20240229'), '2024-DOY060', 'legacy compact date');
assert.equal(D.format('2024-02-29T12:34:56.125Z'), '2024-DOY060 12:34:56.125');
assert.equal(D.format('2020-01-01 00:20:00.785733'), '2020-DOY001 00:20:00.785733');
assert.equal(D.format('2024-12-31T23:59:59.999999Z'), '2024-DOY366 23:59:59.999999');
assert.equal(D.toIso('2025-DOY001 00:00:00.000001+01:00'), '2024-12-31 23:00:00.000001');
assert.equal(D.formatText('时刻 2020-01-01 00:20:00.785733'), '时刻 2020-DOY001 00:20:00.785733');
assert.equal(D.parse('2020-01-01 00:00:00.785733').date.getUTCMilliseconds(), 785);
for (const bad of ['2023-DOY366', '2024-DOY000', '2024-DOY367', '2023-02-29',
    '2024-02-30', '2024-13-01', '2024-DOY060 24:00:00', '2024-DOY060 12:60:00',
    '0000-DOY001', '2024-DOY060 junk']) {
    assert.equal(D.parse(bad), null, bad);
    assert.throws(() => D.toIso(bad), /DOY/);
}
assert.equal(D.format('第 3 帧'), '第 3 帧', 'non-calendar model coordinates are preserved');
assert.equal(D.format(12.5), 12.5);
assert.equal(D.formatText('INFO 2024-02-29 12:00:00 -> 2025-01-01'),
    'INFO 2024-DOY060 12:00:00 -> 2025-DOY001');
assert.deepEqual(Array.from(D.chartLabels(['2024-02-28', '2024-02-29', '2024-03-01'])),
    ['2024-DOY059', '2024-DOY060', '2024-DOY061']);
const axis = D.plotlyAxis(['2024-02-28', '2024-02-29', '2024-03-02']);
assert.equal(axis.x[1] - axis.x[0], 86400000);
assert.equal(axis.x[2] - axis.x[1], 172800000, 'heatmaps retain real unequal time spacing');
assert.equal(axis.axis.type, 'linear', 'Plotly must not regenerate month ticks');
assert.deepEqual(Array.from(axis.axis.ticktext), ['2024-DOY059', '2024-DOY060', '2024-DOY062']);
assert.equal(D.plotlyAxis([0, 1, 2]).axis.type, 'category');
for (const year of [1900, 2000, 2023, 2024]) {
    const stop = Date.UTC(year + 1, 0, 1);
    for (let stamp = Date.UTC(year, 0, 1); stamp < stop; stamp += 86400000) {
        const iso = new Date(stamp).toISOString().slice(0,10);
        assert.equal(D.toIso(D.format(iso)), iso, 'every calendar day roundtrips: ' + iso);
    }
}
vm.runInContext(fs.readFileSync('3DWET/app/static/js/calibration_metrics.js', 'utf8'), context);
assert.equal(context.pairObsSim([{time:'2024-DOY060 12:00:00',value:8}],
    {times:['2024-02-29 12:00:00'],values:[9]}, 1).length, 1, 'metrics pair ordinal and legacy timestamps');
assert.equal(context.pairObsSim([{time:'2024-02-29T12:00:00Z',value:8}],
    {times:['2024-02-29 12:00:00'],values:[9]}, 1).length, 1, 'naive model time and UTC agree in any timezone');
assert.equal(context.pairObsSim([{time:'2023-DOY366',value:8}],
    {times:['2024-01-01'],values:[9]}, 86400).length, 0, 'invalid dates cannot affect metrics');
console.log('model dates: ordinal conversions, validation, UTC and chart spacing PASS');
