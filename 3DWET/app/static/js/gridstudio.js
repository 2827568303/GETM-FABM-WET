/* Grid and case-scoped points share one revision-checked editing session. */
(() => {
  let current=null, selected=new Map(), busy=false, gesture=null, pendingCell=null;
  let view={zoom:1,x:0,y:0}, geometry={x:0,y:0,cell:1};
  const page=document.createElement('div');page.id='page-gridstudio';page.className='page';
  page.innerHTML=`<div class="page-header"><div class="page-title">交互网格与湖点位</div><p class="page-desc">编辑水深、河口、测站和源点。修改先进入会话，保存后写入当前案例。下方生态网络显示真实 FABM 耦合。</p></div>
  <div class="editor-message" id="ge-message">加载案例后开始编辑。</div>
  <div class="editor-toolbar"><button class="btn" id="ge-load">加载 / 刷新</button><button class="btn" id="ge-undo">${StudioIcons.svg('undo')} 撤销</button><button class="btn" id="ge-redo">${StudioIcons.svg('redo')} 重做</button><button class="btn" id="ge-select-all">全选水域</button><button class="btn" id="ge-clear">清除选择</button><button class="btn btn-primary" id="ge-save">保存到案例</button><button class="btn" id="ge-reset">放弃编辑</button></div>
  <div class="grid-workspace"><div class="grid-canvas-wrap"><canvas id="ge-canvas" aria-label="湖泊网格与点位画布"></canvas></div><div class="card editor-info">
  <div><b>网格属性</b><p id="ge-stats">尚未加载</p><p id="ge-selection">已选择 0 格</p><label for="ge-mode">画布操作</label><select id="ge-mode"><option value="select">选择网格</option><option value="point">点选新建 / 移动点位</option><option value="pan">平移视图</option></select></div>
  <div><label for="ge-brush">画笔半径 / 格</label><input id="ge-brush" type="number" min="0" max="15" value="0"><label for="ge-depth">目标水深 / m</label><input id="ge-depth" type="number" min="0.001" step="0.1" value="3"><button class="btn" id="ge-apply">设置水深</button><button class="btn" id="ge-land">设为陆地</button><button class="btn" id="ge-smooth">平滑选区</button></div>
  <div><b>点位快捷编辑</b><label for="ge-point">现有点位</label><select id="ge-point"></select><label for="ge-name">名称</label><input id="ge-name" maxlength="80" placeholder="河口用英文名称"><label for="ge-kind">类型 / 流量方向</label><select id="ge-kind"><option value="monitor">测站</option><option value="source">源点（空间标记）</option><option value="inflow">入湖河口（正流量）</option><option value="outflow">出湖河口（负流量）</option><option value="signed">河口（保留原流量符号）</option></select><label for="ge-calibration">关联已有校准测站</label><select id="ge-calibration"></select><details><summary>显式绑定官方观测站（选择此网格即为模型单元映射，不代表真实坐标系）</summary><label for="ge-lake-id">观测湖泊 ID</label><input id="ge-lake-id" maxlength="200"><label for="ge-station-id">观测站位 ID</label><input id="ge-station-id" maxlength="200"><label for="ge-observation-point-id">观测点 ID（需与导入记录 point_id 一致）</label><input id="ge-observation-point-id" maxlength="200"></details><p id="ge-location">点选一个水格指定位置。</p><button class="btn" id="ge-point-apply">应用点位</button><button class="btn" id="ge-point-delete">删除点位</button><button class="btn" id="ge-calibration-open">打开校准</button></div>
  <p>滚轮缩放；中键、Shift 拖动或平移模式移动视图。点位模式下可拖动标记。河口改名同步流量列；方向按正负绝对值保存。新河口的流量须在输入数据页配置。测站/源点采用1起始网格坐标，源点标记本身不自动生成模型负荷。</p></div></div>`;
  document.querySelector('.content-area').append(page);
  const el=id=>document.getElementById('ge-'+id),canvas=el('canvas');canvas.dataset.nativeViewport='true';
  const norm=p=>String(p||'').replace(/\\/g,'/').toLowerCase();
  function active(){return current&&norm(current.case_path)===norm(state.activeCasePath);}
  function message(text,error=false){el('message').textContent=text;el('message').style.color=error?'var(--danger)':'';}
  function points(){return current?[...current.rivers.map((p,i)=>({...p,key:'r:'+i,river_index:i})),...(current.points||[]).map(p=>({...p,key:'p:'+p.id}))]:[];}
  function chosen(){return points().find(p=>p.key===el('point').value);}
  function coords(i,j){return [geometry.x+(i-.5)*geometry.cell,geometry.y+(current.ny-j+.5)*geometry.cell];}
  function draw(){
    const rect=canvas.getBoundingClientRect(),ratio=window.devicePixelRatio||1;
    if(rect.width<1||rect.height<1)return;
    canvas.width=Math.max(1,Math.round(rect.width*ratio));canvas.height=Math.max(1,Math.round(rect.height*ratio));
    const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);ctx.fillStyle='#102d3d';ctx.fillRect(0,0,rect.width,rect.height);
    if(!current)return;
    const cell=Math.max(.001,Math.min((rect.width-36)/current.nx,(rect.height-36)/current.ny)*view.zoom);
    const ox=(rect.width-cell*current.nx)/2+view.x,oy=(rect.height-cell*current.ny)/2+view.y;geometry={x:ox,y:oy,cell};
    const minI=Math.max(0,Math.floor(-ox/cell)),maxI=Math.min(current.nx,Math.ceil((rect.width-ox)/cell));
    const minJ=Math.max(0,current.ny-Math.ceil((rect.height-oy)/cell)),maxJ=Math.min(current.ny,current.ny-Math.floor(-oy/cell));
    for(let j=minJ;j<maxJ;j++)for(let i=minI;i<maxI;i++){const v=current.depth[j][i];
      ctx.fillStyle=v>0?`hsl(${174+25*v/(current.max_depth||1)},${55+15*v/(current.max_depth||1)}%,${64-36*v/(current.max_depth||1)}%)`:'#284452';
      ctx.fillRect(ox+i*cell,oy+(current.ny-1-j)*cell,Math.max(.4,cell-(cell>7?1:0)),Math.max(.4,cell-(cell>7?1:0)));
    }
    ctx.fillStyle='#ffe491aa';selected.forEach(([i,j])=>ctx.fillRect(ox+i*cell,oy+(current.ny-1-j)*cell,cell,cell));
    points().forEach(p=>{const [x,y]=coords(p.i,p.j),valid=current.depth[p.j-1]?.[p.i-1]>0;
      ctx.beginPath();ctx.arc(x,y,Math.max(5,Math.min(11,cell*.3)),0,Math.PI*2);ctx.fillStyle=!valid?'#ff334d':p.key.startsWith('r:')?'#ff9588':p.kind==='source'?'#c6a2ff':'#ffdf7a';ctx.fill();
      if(p.key===el('point').value){ctx.lineWidth=2;ctx.strokeStyle='#fff';ctx.stroke();}
      ctx.font='11px sans-serif';ctx.fillStyle='#fff';ctx.fillText(p.name,x+9,y-7);
    });
    el('selection').textContent=`已选择 ${selected.size} 格`;
  }
  function option(value,text){const o=document.createElement('option');o.value=value;o.textContent=text;return o;}
  function selectPoint(){const p=chosen();pendingCell=p?[p.i-1,p.j-1]:null;
    el('name').value=p?.name||'';el('kind').value=p?.kind||'monitor';el('calibration').value=p?.calibration_id||'';
    el('lake-id').value=p?.lake_id||'';el('station-id').value=p?.station_id||'';el('observation-point-id').value=p?.observation_point_id||'';
    el('location').textContent=p?`位置 (${p.i}, ${p.j}) · ${current.depth[p.j-1]?.[p.i-1]>0?'有效水格':'无效位置，保存前请移动'}`:'点选一个水格指定位置。';draw();}
  function show(s,keep=true){const key=keep?el('point').value:'';current=s;
    el('stats').textContent=`${s.nx} × ${s.ny} · ${s.water_cells} 水格 · 最大水深 ${s.max_depth.toFixed(2)} m`;
    el('undo').disabled=!s.can_undo;el('redo').disabled=!s.can_redo;
    el('point').replaceChildren(option('','＋ 新建点位'),...points().map(p=>option(p.key,`${p.name} (${p.i}, ${p.j})`)));
    if(points().some(p=>p.key===key))el('point').value=key;
    el('calibration').replaceChildren(option('','不关联'),...(s.calibration_candidates||[]).map(p=>option(p.id,p.name+' · '+p.id)));
    message(s.backup?`已保存，原文件备份：${s.backup}`:s.dirty?'有未保存修改，点击“保存到案例”写入。':'已加载。选择点位或网格开始编辑。');selectPoint();
  }
  async function load(){if(busy)return;busy=true;const identity=norm(state.activeCasePath);
    if(window.loadEcologyNetwork)window.loadEcologyNetwork();
    try{const s=await api('/api/grid/editor');if(identity!==norm(state.activeCasePath))return;
      if(s.error){current=null;message(s.error,true);draw();return;}
      if(!current||norm(s.case_path)!==norm(current.case_path)){selected.clear();view={zoom:1,x:0,y:0};}show(s);
    }catch(e){message('加载失败：'+e.message,true);}finally{busy=false;}}
  async function command(action,extra={}){if(busy||!current)return;if(!active()){message('案例已切换，请重新加载',true);return;}busy=true;
    const identity=norm(state.activeCasePath);try{const s=await api('/api/grid/edit',{method:'POST',body:{case_path:current.case_path,revision:current.revision,action,...extra}});
      if(identity!==norm(state.activeCasePath))return;if(s.error){message(s.error,true);return;}show(s);
    }catch(e){message('操作失败：'+e.message,true);}finally{busy=false;}}
  function cellAt(e){const r=canvas.getBoundingClientRect();return [Math.floor((e.clientX-r.left-geometry.x)/geometry.cell),current.ny-1-Math.floor((e.clientY-r.top-geometry.y)/geometry.cell)];}
  function valid([i,j]){return i>=0&&j>=0&&i<current.nx&&j<current.ny;}
  function pick(e){if(!active()||busy)return;const [i,j]=cellAt(e),radius=Math.max(0,Math.min(15,parseInt(el('brush').value)||0));
    for(let y=j-radius;y<=j+radius;y++)for(let x=i-radius;x<=i+radius;x++)if(valid([x,y]))selected.set(`${x},${y}`,[x,y]);draw();}
  function setLocation(cell){pendingCell=cell;selected.clear();selected.set(cell.join(','),cell);el('location').textContent=`待应用位置 (${cell[0]+1}, ${cell[1]+1}) · ${current.depth[cell[1]][cell[0]]>0?'有效水格':'陆格，请选择水域'}`;draw();}
  function applyPoint(cell=pendingCell,dragged=false){const p=chosen(),kind=dragged?p.kind:el('kind').value;
    if(!cell&&selected.size===1)cell=[...selected.values()][0];if(!cell){message('请先点选一个水格',true);return;}
    const river=['inflow','outflow','signed'].includes(kind);
    if(p&&river!==p.key.startsWith('r:')){message('现有河口与测站/源点不能直接互换，请新建点位',true);return;}
    command(river?(p?'river_update':'river_add'):'point',{cells:[cell],name:dragged?p.name:el('name').value,kind,
      ...(river?{river_index:p?.river_index}:{point_id:p?.id,calibration_id:dragged?p.calibration_id:el('calibration').value,
        lake_id:el('lake-id').value,station_id:el('station-id').value,observation_point_id:el('observation-point-id').value})});}
  canvas.addEventListener('pointerdown',e=>{if(!active()||busy)return;canvas.setPointerCapture(e.pointerId);
    if(e.button===1||e.shiftKey||el('mode').value==='pan'){gesture={type:'pan',x:e.clientX,y:e.clientY};return;}
    if(el('mode').value==='point'){const r=canvas.getBoundingClientRect(),hit=points().find(p=>{const [x,y]=coords(p.i,p.j);return Math.hypot(e.clientX-r.left-x,e.clientY-r.top-y)<12;});
      if(hit){el('point').value=hit.key;selectPoint();gesture={type:'point',start:[hit.i-1,hit.j-1],cell:[hit.i-1,hit.j-1]};}
      else{const cell=cellAt(e);if(valid(cell))setLocation(cell);}return;}
    gesture={type:'select'};pick(e);
  });
  canvas.addEventListener('pointermove',e=>{if(!gesture||!current)return;
    if(gesture.type==='pan'){view.x+=e.clientX-gesture.x;view.y+=e.clientY-gesture.y;gesture.x=e.clientX;gesture.y=e.clientY;draw();}
    else if(gesture.type==='select')pick(e);else{const cell=cellAt(e);if(valid(cell)){gesture.cell=cell;setLocation(cell);}}});
  canvas.addEventListener('pointerup',()=>{const ended=gesture;gesture=null;if(ended?.type==='point'&&ended.cell.join(',')!==ended.start.join(','))applyPoint(ended.cell,true);});
  canvas.addEventListener('pointercancel',()=>gesture=null);
  function zoom(factor,x,y){if(!current)return;const r=canvas.getBoundingClientRect();x??=r.width/2;y??=r.height/2;
    const before=view.zoom;view.zoom=Math.max(.5,Math.min(30,before*factor));const k=view.zoom/before;
    view.x=k*view.x+(1-k)*(x-r.width/2);view.y=k*view.y+(1-k)*(y-r.height/2);draw();}
  canvas.addEventListener('wheel',e=>{if(e.ctrlKey||!current)return;e.preventDefault();const r=canvas.getBoundingClientRect();zoom(Math.exp(-e.deltaY*.001),e.clientX-r.left,e.clientY-r.top);},{passive:false});
  el('load').onclick=load;el('undo').onclick=()=>command('undo');el('redo').onclick=()=>command('redo');
  el('clear').onclick=()=>{selected.clear();draw();};el('select-all').onclick=()=>{if(!current)return;current.depth.forEach((row,j)=>row.forEach((v,i)=>{if(v>0)selected.set(`${i},${j}`,[i,j]);}));draw();};
  el('apply').onclick=()=>command('depth',{cells:[...selected.values()],value:Number(el('depth').value)});
  el('land').onclick=()=>command('land',{cells:[...selected.values()]});el('smooth').onclick=()=>command('smooth',{cells:[...selected.values()]});el('save').onclick=()=>command('save');
  el('point').onchange=selectPoint;el('point-apply').onclick=()=>applyPoint();
  el('point-delete').onclick=()=>{const p=chosen();if(p)command(p.key.startsWith('r:')?'river_delete':'point_delete',{river_index:p.river_index,point_id:p.id});};
  el('calibration-open').onclick=async()=>{const p=chosen(),identity=norm(state.activeCasePath);navigate('calibrate');await initCalibrate();
    if(identity===norm(state.activeCasePath)&&p?.calibration_id){document.getElementById('cal-point-select').value=p.calibration_id;document.getElementById('cal-data-point').value=p.calibration_id;}};
  el('reset').onclick=async()=>{if(current&&await window.confirmStudio('放弃本次网格与点位修改，重新读取磁盘文件？'))command('reload');};
  window.resizeGridStudio=draw;window.resetGridStudioView=()=>{view={zoom:1,x:0,y:0};draw();};
  if(window.ViewControls)ViewControls.registerCanvas(canvas,{reset:window.resetGridStudioView,resize:draw,zoom});else new ResizeObserver(draw).observe(canvas);
  window.initGridStudio=load;
})();
