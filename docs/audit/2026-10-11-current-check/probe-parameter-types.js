const fs = require('node:fs'), vm = require('node:vm');
const source = fs.readFileSync('3DWET/app/static/js/app.js', 'utf8');
const sent = [];
const context = vm.createContext({state:{fabmModules:[],currentParams:[]},
  api:async(url, options)=>{sent.push(options.body);return {success:true}},
  $:()=>({textContent:''}),setTimeout:()=>{},toast:()=>{}});
vm.runInContext(source.slice(source.indexOf('async function saveParam('),
  source.indexOf('// ── Time Settings')), context);
(async()=>{
  for(const value of ['false','true','']) {
    await context.saveParam({value,dataset:{idx:'0'},classList:{remove(){}}},'m','p');
  }
  console.log(JSON.stringify(sent.map((row,i)=>({input:['false','true',''][i],
    sent_value:row.value,sent_type:typeof row.value})),null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
