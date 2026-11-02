// A draft is local to this dialog. Only Apply writes the selected case/variable.
(function(root){
    'use strict';
    const palettes=[['lake','湖蓝'],['cividis','Cividis'],['viridis','Viridis'],['blueRed','蓝—红'],['custom','自定义']];
    const text=value=>root.StudioI18n?.t(value) || value;
    const message=problem=>text(/Color nodes require/.test(problem.message)
        ? '颜色节点必须按位置递增，不能重复；首尾位置为 0% 和 100%。'
        : /Classes must/.test(problem.message) ? '级数须为 2 到 20 的整数。'
        : /(?:Incomplete|Invalid) color configuration/.test(problem.message) ? '色标方案不完整或格式不正确。'
        : problem.name==='SyntaxError' ? '无法读取方案，请选择有效的 JSON 色标文件。' : problem.message);
    const toHex=value=>value.startsWith('#') ? value : '#'+value.match(/\d+/g).map(v=>Number(v).toString(16).padStart(2,'0')).join('');
    function open(kind){
        const workspace=root.ScientificWorkspace,style=root.ScientificStyle;
        const context=workspace?.colorContext?.(kind);
        if(!context?.variable || !style)return;
        document.getElementById('scientific-colormap-editor')?.close();
        const trigger=document.activeElement,dialog=document.createElement('dialog');
        dialog.id='scientific-colormap-editor';dialog.setAttribute('aria-labelledby','colormap-title');
        dialog.innerHTML=`<form method="dialog">
            <div class="colormap-heading"><h2 id="colormap-title">编辑色标</h2><button type="button" data-action="close" aria-label="关闭色标编辑器">×</button></div>
            <p data-field="identity"></p>
            <div class="colormap-preview" data-field="preview" role="img" aria-label="色标预览"></div>
            <div class="colormap-options">
                <label>配色方案<select data-field="palette"></select></label>
                <label class="colormap-check"><input type="checkbox" data-field="reverse">反转色标</label>
                <label>显示方式<select data-field="mapping"><option value="continuous">连续渐变</option><option value="discrete">等宽分级</option></select></label>
                <label>级数<input type="number" min="2" max="20" step="1" data-field="classes"></label>
                <label>水域缺测颜色<input type="color" data-field="missing"></label>
            </div>
            <p class="colormap-note">按数值从小到大设置颜色节点；插值方式为 RGB。当前数值范围保持不变。</p>
            <div class="colormap-nodes" data-field="nodes"></div>
            <button type="button" data-action="add">增加颜色节点</button>
            <p class="colormap-error" data-field="error" role="status" aria-live="polite"></p>
            <div class="colormap-actions">
                <button type="button" data-action="import">导入方案</button>
                <input type="file" accept=".json,application/json" data-field="file" hidden>
                <button type="button" data-action="export">导出方案</button>
                <span></span><button type="button" data-action="close">取消</button>
                <button type="button" class="btn-primary" data-action="apply">应用</button>
            </div>
        </form>`;
        document.body.appendChild(dialog);
        const field=name=>dialog.querySelector(`[data-field="${name}"]`);
        const action=name=>dialog.querySelector(`[data-action="${name}"]`);
        let draft=style.get(context.caseKey,context.variable);
        const nodes=field('nodes'),error=field('error');
        const actualValue=position=>Number.isFinite(context.range?.min) && Number.isFinite(context.range?.max)
            ? String(Number((context.range.min*(1-position)+context.range.max*position).toPrecision(8))) : '';
        field('identity').textContent=`${context.label || context.variable}${context.units?' · '+context.units:''}`;
        for(const [value,label] of palettes){const option=document.createElement('option');option.value=value;option.textContent=text(label);field('palette').appendChild(option);}
        function baseNodes(){
            return draft.palette==='custom' ? draft.stops.map(node=>[...node])
                : style.colorscale({...draft,reverse:false,mapping:'continuous'}).map(([t,color])=>[t,toHex(color)]);
        }
        function read(){
            const stops=[...nodes.children].map(row=>{
                const raw=row.querySelector('input[type="number"]').value;
                if(!raw.trim())throw Error(text('请填写所有颜色节点位置。'));
                return [Number(raw)/100,row.querySelector('input[type="color"]').value];
            });
            return style.validateConfig({...draft,palette:field('palette').value,stops,
                reverse:field('reverse').checked,mapping:field('mapping').value,
                classes:Number(field('classes').value),nanColor:field('missing').value});
        }
        function preview(){
            field('classes').disabled=field('mapping').value!=='discrete';
            try{
                const value=read();
                field('preview').style.background=`linear-gradient(to right,${style.colorscale(value).map(([t,color])=>`${color} ${t*100}%`).join(',')})`;
                [...nodes.children].forEach((row,i)=>row.querySelector('.colormap-value').textContent=actualValue(value.stops[i][0]));
                error.textContent='';return value;
            }catch(problem){error.textContent=message(problem);return null;}
        }
        function renderNodes(stops){
            nodes.replaceChildren();
            stops.forEach(([position,color],i)=>{
                const row=document.createElement('div');row.className='colormap-node';
                const label=document.createElement('label');label.textContent=text(`节点 ${i+1} (%)`);
                const input=document.createElement('input');input.type='number';input.min='0';input.max='100';input.step='any';input.value=String(position*100);
                input.disabled=i===0 || i===stops.length-1;input.setAttribute('aria-label',`颜色节点位置 ${i+1} (%)`);label.appendChild(input);
                const colorInput=document.createElement('input');colorInput.type='color';colorInput.value=color;colorInput.setAttribute('aria-label',`颜色节点 ${i+1}`);
                const actual=document.createElement('span');actual.className='colormap-value';
                actual.textContent=actualValue(position);
                const remove=document.createElement('button');remove.type='button';remove.textContent=text('移除');remove.disabled=input.disabled;
                remove.setAttribute('aria-label',`移除颜色节点 ${i+1}`);
                const changed=()=>{field('palette').value='custom';preview();};
                input.addEventListener('input',changed);colorInput.addEventListener('input',changed);
                remove.addEventListener('click',()=>{
                    const value=preview();if(!value)return;value.stops.splice(i,1);draft=value;draft.palette='custom';render();
                });
                row.append(label,colorInput,actual,remove);nodes.appendChild(row);
            });
            action('add').disabled=stops.length>=32;
        }
        function render(){
            field('palette').value=draft.palette;field('reverse').checked=draft.reverse;
            field('mapping').value=draft.mapping;field('classes').value=String(draft.classes);field('missing').value=draft.nanColor;
            renderNodes(baseNodes());preview();
        }
        field('palette').addEventListener('change',()=>{
            const value=preview();if(!value)return;draft=value;draft.palette=field('palette').value;render();
        });
        for(const name of ['reverse','mapping','classes','missing'])field(name).addEventListener('input',preview);
        action('add').addEventListener('click',()=>{
            const value=preview();if(!value || value.stops.length>=32)return;
            let slot=0;for(let i=1;i<value.stops.length-1;i++)
                if(value.stops[i+1][0]-value.stops[i][0]>value.stops[slot+1][0]-value.stops[slot][0])slot=i;
            const position=(value.stops[slot][0]+value.stops[slot+1][0])/2;
            const color=toHex(style.color(position,{...value,reverse:false,mapping:'continuous'}));
            value.stops.splice(slot+1,0,[position,color]);value.palette='custom';draft=value;render();
        });
        dialog.querySelectorAll('[data-action="close"]').forEach(button=>button.addEventListener('click',()=>dialog.close()));
        dialog.addEventListener('close',()=>{dialog.remove();trigger?.focus({preventScroll:true});},{once:true});
        dialog.addEventListener('keydown',event=>{
            if(event.key!=='Tab')return;
            const controls=[...dialog.querySelectorAll('button,input,select')].filter(el=>!el.disabled && !el.hidden && el.getClientRects().length);
            const first=controls[0],last=controls.at(-1);
            if(event.shiftKey && document.activeElement===first){event.preventDefault();last?.focus();}
            else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first?.focus();}
        });
        dialog.querySelector('form').addEventListener('submit',event=>event.preventDefault());
        action('apply').addEventListener('click',()=>{
            const value=preview();if(!value)return;
            const now=workspace.colorContext(kind);
            if(now.caseKey!==context.caseKey || now.variable!==context.variable || now.revision!==context.revision){
                error.textContent=text('当前案例或变量已变化，请关闭后重新编辑。');return;
            }
            style.importConfig(context.caseKey,context.variable,{version:2,style:value});
            dialog.close();workspace.refresh(kind);
        });
        action('import').addEventListener('click',()=>field('file').click());
        field('file').addEventListener('change',async()=>{
            try{
                const file=field('file').files[0];if(!file)return;
                if(file.size>65536)throw Error(text('方案文件不能超过 64 KB。'));
                const payload=JSON.parse(await file.text());if(!dialog.open)return;
                if(payload?.version!==2)throw Error(text('不支持的色标方案版本。'));
                draft=style.validateConfig(payload.style,true);render();
            }catch(problem){error.textContent=message(problem);}
            finally{field('file').value='';}
        });
        action('export').addEventListener('click',()=>{
            const value=preview();if(!value)return;
            const url=URL.createObjectURL(new Blob([JSON.stringify({version:2,style:value},null,2)],{type:'application/json'}));
            const link=document.createElement('a');link.href=url;link.download='3dwet-colormap.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
        });
        render();dialog.showModal();
    }
    function bind(){document.querySelectorAll('[data-colormap-edit]').forEach(button=>button.addEventListener('click',()=>open(button.dataset.colormapEdit)));}
    root.ScientificColormapEditor={open};
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind,{once:true});else bind();
})(typeof window!=='undefined'?window:globalThis);
