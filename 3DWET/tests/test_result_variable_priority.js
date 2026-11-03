const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const start=source.indexOf('function resultVariablePriority('),end=source.indexOf('\nfunction hasVerticalResultDimension',start);
const context=vm.createContext({});vm.runInContext(source.slice(start,end),context);
const rank=v=>context.resultVariablePriority(v);
test('F-column defaults are promoted only when a real output variable exists',()=>{
 for(const name of ['temp','salt','u','v','w','uu','vv','elev','abiotic_water_sO2W']) {
  assert.ok(rank({name,units:'g/m3'})<2,`${name} should stay with the always-available fields`);
 }
 for(const name of ['wet_fish_sD','wet_zoobenthos_sD','wet_zooplankton_sD']) {
  assert.ok(rank({name,units:'gDW/m3'})<2,`${name} biomass stays in the default list`);
 }
 for(const name of ['wet_totN','wet_totP','wet_chla','wet_totN_calculator_result','abiotic_water_sNH4W','abiotic_water_sNO3W','abiotic_water_sPO4W']) {
  assert.equal(rank({name,units:'g/m3'}),2,`${name} is stored and loaded on demand`);
 }
});
test('on-demand physical and diagnostic fields stay out of the default tier',()=>{
 for(const item of [
  {name:'PAR',zh_name:'光合有效辐射'},
  {name:'attenuation',zh_name:'光衰减系数'},
  {name:'oxygen_saturation',en_name:'Oxygen saturation'},
  {name:'hn',zh_name:'水层厚度'},
  {name:'cyanobacteria_chla',zh_name:'蓝藻叶绿素a'},
  {name:'diatoms_chla',zh_name:'硅藻叶绿素a'},
 ]) assert.equal(rank(item),2,`${item.name} should remain on-demand`);
});
test('transparency requires direct quantity metadata and metres; turbidity is not promoted',()=>{
 assert.equal(rank({name:'transparency',zh_name:'透明度',units:'m'}),1);
 assert.equal(rank({name:'transparency',zh_name:'透明度',units:'SD'}),2);
 assert.equal(rank({name:'turbidity',zh_name:'浊度',units:'NTU'}),2);
 assert.equal(rank({name:'tss',zh_name:'总悬浮物',units:'mg/L'}),1);
});
test('BOD output can be prioritized without treating the hO2BOD parameter as an output',()=>{
 assert.equal(rank({name:'BOD',zh_name:'生化需氧量',units:'mg/L'}),1);
 assert.equal(rank({name:'hO2BOD',units:'d-1'}),2);
});
test('sorting is stable within priorities and retains every actual variable',()=>{
 const values=[{name:'sediment_flux'},{name:'wet_zooplankton_sD'},{name:'temp'},{name:'unknown'},{name:'wet_chla'}];
 const sorted=Array.from(context.prioritizeResultVariables(values));
 assert.deepEqual(sorted.map(v=>v.name),['temp','wet_zooplankton_sD','sediment_flux','unknown','wet_chla']);
 assert.equal(new Set(sorted).size,values.length);
});

