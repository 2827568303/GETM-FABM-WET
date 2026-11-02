const assert=require('node:assert/strict');
const fs=require('node:fs');
const source=fs.readFileSync('3DWET/app/static/js/ecology_network.js','utf8');

assert.match(source,/function modelGroup\(/,'network nodes need model family classification');
assert.match(source,/phytoplankton:[^\n]*藻类/,'phytoplankton instances should be identified as algae');
assert.match(source,/fish:[^\n]*鱼类/,'fish instances should be identified as fish');
assert.match(source,/data-network-filter="ecology"/,'provide an ecology-only view');
assert.match(source,/data-network-filter="water_quality"/,'provide a water-quality-only view');
assert.match(source,/api\('\/api\/ecology\/network'/,'network view must load real case data');
assert.match(source,/api\('\/api\/ecology\/network',\{method:'POST',body\}\)/,'node edits must save to the existing API');
assert.match(source,/个物种实例/,'show counts of actual instances by family');
assert.match(source,/id="en-view-foodweb"[^>]*>食性配置分层图/,'provide a separate actual-coupling configured-food-web view');
for (const step of ['第 1 步 · 选择模型族','第 2 步 · 选择来源','第 3 步 · 设置初始状态','第 4 步 · 命名并预览']) assert.ok(source.includes(step),`instance wizard includes ${step}`);
assert.match(source,/box\.id='ecology-network-editor'/,'reuse one stable editor section as the direct-navigation target');
assert.match(source,/id="ecology-network-heading" tabindex="-1"/,'provide a programmatically focusable accessible destination');
const html=fs.readFileSync('3DWET/app/templates/index.html','utf8');
assert.match(html,/data-page="ecology"[^>]*>.*?生态网络与食物网/,'expose the ecology editor in model configuration navigation');
const app=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
assert.match(app,/page === 'ecology' \? 'gridstudio' : page/,'route the shortcut through the existing grid studio page');
assert.match(app,/heading\.scrollIntoView\(\{block: 'start'\}\)/,'land on the ecology editor itself');
assert.match(app,/heading\.focus\(\{preventScroll: true\}\)/,'move keyboard focus to the editor heading');
assert.equal((source.match(/id='ecology-network-editor'/g)||[]).length,1,'do not create a second editor instance');

console.log('ecology network routing, accessible focus target, and single editor instance PASS');
