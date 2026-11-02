const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {test}=require('node:test');
function environment() {
    const canvases=[],downloads=[],renders=[],imageCalls=[],elements=new Map();
    function canvas(width=0,height=0) {
        const c={width,height,text:[],images:[],gradients:[]},ctx={font:'16px sans-serif',textAlign:'left',fillStyle:'',
            measureText(text){return {width:Array.from(String(text)).length*(parseFloat(this.font)||16)*.6};},
            fillText(text,x,y){c.text.push({text,x,y,font:this.font,width:this.measureText(text).width,align:this.textAlign});},
            fillRect(){},drawImage(...args){c.images.push(args);},createLinearGradient(){const stops=[];c.gradients.push(stops);return {addColorStop:(...args)=>stops.push(args)};}};
        c.getContext=()=>ctx;c.toBlob=fn=>fn({canvas:c});canvases.push(c);return c;
    }
    function element(id){if(!elements.has(id))elements.set(id,{value:'temp',options:[],style:{},dataset:{},setAttribute(){},replaceChildren(){},appendChild(){}});return elements.get(id);}
    const source=canvas(361,300);source._scientificMetadata={shape:[2,2],wetMask:[[true,false],[true,true]],coordinate_mode:'projected',xc:[100,200],yc:[500,700]};
    elements.set('viz2d-canvas',source);elements.set('viz3d-plotly',{_fullLayout:{scene:{camera:{eye:{x:2,y:1,z:1}}}},data:[]});
    const context=vm.createContext({console,state:{activeCasePath:'A',activeCase:'CASE_'+ '研究湖泊'.repeat(30),caseRevision:1},
        window:{StudioIcons:{node:()=>({})},Image:class {set src(value){this.url=value;queueMicrotask(()=>this.onload());}},
            Plotly:{toImage:async(graph,options)=>{imageCalls.push({graph,options});return 'data:image/png;base64,test';},downloadImage:async()=>{}},
            ScientificHeatmap:{draw:(c,data,opts)=>{renders.push({c,data,opts});}}},
        document:{readyState:'loading',getElementById:element,addEventListener(){},createElement:type=>type==='canvas'?canvas():type==='a'?{click(){downloads.push(this);}}:{style:{},dataset:{},appendChild(){}},querySelectorAll:()=>[]},
        URL:{createObjectURL:blob=>{downloads.blob=blob;return 'blob:export';},revokeObjectURL(){}},setTimeout:()=>{},queueMicrotask,ModelDates:{format:x=>x}});
    for(const name of ['scientific_style','scientific_workspace'])vm.runInContext(fs.readFileSync('3DWET/app/static/js/'+name+'.js','utf8'),context);
    const meta={variable:'macrophytes_sD_PV_raw_identity',label:'FULL_LABEL_'+ '沉水植物库存科学说明'.repeat(20),units:'g DW m-3',
        date:'2026-12-31 23:59:30',time:7,level:4,ve:100,field:[[0,null],[-1,2]],min:-1,max:2,
        detail:'Original grid 6×14×21 · Sampling stride 1×1×1 · Transparent layers blend colours',
        range:context.window.ScientificStyle.resolve({caseKey:'A',variable:'temp',min:-1,max:2})};
    meta.range.mode='locked';
    return {context,w:context.window.ScientificWorkspace,meta,source,canvases,downloads,renders,imageCalls};
}
function checkHeader(e,out) {
    const text=out.text.map(x=>x.text).join('');
    for(const expected of [e.meta.variable,e.meta.label,e.meta.units,e.context.state.activeCase,e.meta.date,e.meta.detail,'4','100','locked','-1','2'])assert.ok(text.includes(expected),`full export metadata missing: ${expected}`);
    const header=out.text.filter(x=>x.y<out.images[0][2]);
    assert.ok(header.length>6,'long scientific metadata wraps into a dynamic header');
    assert.ok(header.every(x=>x.x+x.width<=out.width-20),'every header line fits the canvas');
}
test('2D exports redraw original values and trusted wet geometry at useful resolution with full wrapped metadata',async()=>{
    const e=environment();e.w.publish('viz2d',e.meta);await e.w.exportFigure('viz2d');
    assert.equal(e.renders.length,1,'export must redraw the original field instead of enlarging a mobile bitmap');
    const rendered=e.renders[0];assert.strictEqual(rendered.data,e.meta.field);assert.ok(rendered.c.width>=1000);assert.ok(rendered.c.height>=600);
    assert.strictEqual(rendered.opts.wetMask,e.source._scientificMetadata.wetMask);assert.strictEqual(rendered.opts.xc,e.source._scientificMetadata.xc);
    assert.equal(rendered.opts.min,-1);assert.equal(rendered.opts.max,2);assert.equal(rendered.opts.pixelRatio,1);
    const out=e.downloads.blob.canvas;checkHeader(e,out);assert.strictEqual(out.images[0][0],rendered.c);
});
test('3D exports composite the current-camera image with complete metadata without changing the live graph',async()=>{
    const e=environment();e.w.publish('viz3d',e.meta);await e.w.exportFigure('viz3d');
    assert.equal(e.imageCalls.length,1,'use toImage to preserve the existing graph and its camera');
    assert.equal(e.imageCalls[0].options.width,1600);assert.equal(e.imageCalls[0].options.height,1000);
    const out=e.downloads.blob.canvas;checkHeader(e,out);assert.equal(out.images[0][0].url,'data:image/png;base64,test');
    assert.equal(e.imageCalls[0].graph.data.length,0,'export never replaces live traces');
});
test('an asynchronous 3D export rejects a superseded displayed result instead of mixing its image and metadata',async()=>{
    const e=environment();let release;e.context.window.Plotly.toImage=(graph,options)=>{e.imageCalls.push({graph,options});return new Promise(r=>release=r);};
    e.w.publish('viz3d',e.meta);const pending=e.w.exportFigure('viz3d');
    assert.equal(e.imageCalls.length,1);e.w.publish('viz3d',{...e.meta,time:8,date:'2027-01-01 00:00:30'});release('data:image/png;base64,test');
    await assert.rejects(pending,/changed|变化|重新/);assert.equal(e.downloads.length,0);
});
test('a new 3D rendering request invalidates export even before its metadata is published',async()=>{
    const e=environment();let release;const graph=e.context.document.getElementById('viz3d-plotly');
    graph._viz3dStatus={phase:'ready'};
    e.context.window.Plotly.toImage=()=>new Promise(r=>release=r);
    e.w.publish('viz3d',e.meta);const pending=e.w.exportFigure('viz3d');
    graph._viz3dStatus={phase:'loading'};release('data:image/png;base64,test');
    await assert.rejects(pending,/changed|变化|重新/);assert.equal(e.downloads.length,0);
});

test('custom export data and legend retain exact positioned class boundaries from the displayed result',async()=>{
    const e=environment(),style=e.context.window.ScientificStyle;
    style.set('A','temp',{palette:'custom',stops:[[0,'#000000'],[.25,'#ff0000'],[1,'#ffffff']],mapping:'discrete',classes:3,reverse:true,nanColor:'#123456'});
    e.meta.range=style.resolve({caseKey:'A',variable:'temp',min:-1,max:2});
    e.w.publish('viz2d',e.meta);await e.w.exportFigure('viz2d');
    assert.deepEqual(e.renders[0].opts.style,e.meta.range,'the original field renderer receives the full transfer function');
    assert.deepEqual(JSON.parse(JSON.stringify(e.downloads.blob.canvas.gradients[0])),JSON.parse(JSON.stringify(e.meta.range.colorscale)),
        'the exported legend uses actual class boundaries, including duplicated step positions');
});
