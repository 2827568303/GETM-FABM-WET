// Native disclosure groups share the existing business-page navigation.
(() => {
    'use strict';
    const menu=document.querySelector('.nav-menu');
    const sidebar=document.getElementById('studio-navigation');
    const toggle=document.getElementById('studio-nav-toggle');
    const close=document.getElementById('studio-nav-close');
    const backdrop=document.getElementById('studio-nav-backdrop');
    const main=document.querySelector('.main-content');
    if(!menu || !sidebar || !toggle)return;
    const groups=[...menu.querySelectorAll('details[data-workflow]')];
    const narrow=window.matchMedia('(max-width: 720px), (max-width: 950px) and (max-height: 500px)');
    let drawer=false,previousInert=false;
    const focusable=()=>[...sidebar.querySelectorAll('summary,button,a,[tabindex="0"]')]
        .filter(el=>!el.disabled && !el.hidden && el.getClientRects().length>0);
    function closeDrawer(returnFocus=false) {
        if(!drawer)return;
        drawer=false;
        document.body.classList.toggle('studio-nav-open',false);
        toggle.setAttribute('aria-expanded','false');
        sidebar.setAttribute('role','navigation');
        sidebar.removeAttribute('aria-modal');
        if(backdrop)backdrop.hidden=true;
        if(main)main.inert=previousInert;
        if(returnFocus)toggle.focus();
        else main?.focus({preventScroll:true});
    }
    function openDrawer() {
        if(!narrow.matches || drawer)return;
        drawer=true;
        previousInert=!!main?.inert;
        if(main)main.inert=true;
        document.body.classList.toggle('studio-nav-open',true);
        toggle.setAttribute('aria-expanded','true');
        sidebar.setAttribute('role','dialog');
        sidebar.setAttribute('aria-modal','true');
        if(backdrop)backdrop.hidden=false;
        (focusable()[0] || close)?.focus();
    }
    function activate(page) {
        // Match the route against existing DOM values; never interpolate an
        // arbitrary route into a CSS selector.
        const leaves=[...menu.querySelectorAll('[data-page]')];
        const item=leaves.find(el=>el.dataset.page===page);
        if(!item)return;
        const selected=item.closest('details[data-workflow]');
        for(const group of groups)group.open=group===selected;
        for(const leaf of leaves) {
            if(leaf===item)leaf.setAttribute('aria-current','page');
            else leaf.removeAttribute('aria-current');
        }
        closeDrawer();
    }
    for(const group of groups)group.addEventListener('toggle',()=>{
        if(group.open)for(const other of groups)if(other!==group)other.open=false;
    });
    toggle.addEventListener('click',()=>drawer?closeDrawer(true):openDrawer());
    close?.addEventListener('click',()=>closeDrawer(true));
    backdrop?.addEventListener('click',()=>closeDrawer(true));
    document.addEventListener('keydown',event=>{
        if(!drawer)return;
        if(event.key==='Escape'){event.preventDefault();closeDrawer(true);return;}
        if(event.key!=='Tab')return;
        const items=focusable(),first=items[0],last=items.at(-1);
        if(!first){event.preventDefault();return;}
        if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
        else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
    });
    narrow.addEventListener('change',()=>{if(!narrow.matches)closeDrawer();});
    window.StudioNavigation={activate,closeDrawer};
    activate('dashboard');
})();
