const assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm');
const source=fs.readFileSync('3DWET/app/static/js/app.js','utf8');
const section=(start,end)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));
const elements={
 'ac-method':{value:'scipy'},'ac-iterations':{value:2},'ac-objective':{value:'rmse'},
 'ac-points':{selectedOptions:[{value:'station-2'}]},'ac-progress':{innerHTML:''},
 'ac-progress-detail':{innerHTML:''},'ac-max-simulations':{value:'100'}
};
const check={dataset:{module:'POM',param:'kDMinW'},closest:()=>({querySelector:s=>({value:s.includes('min')?1:2})})};
let payload;
const context=vm.createContext({state:{activeCase:'Test',calibPointsLoaded:true,calibJobId:'j'},
 $:id=>elements[id],document:{querySelectorAll:()=>[check]},toast:()=>{},
 setInterval:()=>1,clearInterval:()=>{},ModelDates:{formatText:s=>s},
 api:async(url,options)=>{if(options){payload=options.body;return {job_id:'j'};}
 return {status:'completed',progress:1,history:[],result:{best_params:[],best_objective:0}};}
});
vm.runInContext(section('async function startAutoCal()', 'async function stopAutoCal()'),context);
(async()=>{
 await context.startAutoCal();assert.deepEqual(Array.from(payload.point_ids),['station-2']);
 await context.pollAutoCalStatus();assert.match(elements['ac-progress-detail'].innerHTML,/0\.0000/);
 assert.doesNotMatch(elements['ac-progress-detail'].innerHTML,/NaN/);
 console.log('calibration UI: selected station payload and zero objective rendering PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
