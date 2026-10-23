(() => {
  const svg=document.getElementById('network');
  const pause=document.getElementById('graph-motion');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const seeds=Object.fromEntries(Object.entries(positions).map(([id,p])=>[id,[...p]]));
  const homes=Object.fromEntries(Object.entries(seeds).map(([id,p])=>[id,[...p]]));
  const velocity=Object.fromEntries(S.nodes.map(n=>[n.id,[0,0]]));
  let nodes=[],edges=[],labels=[],focus=null,drag=null;
  let moving=!reduced.matches,visible=false,frameId=0,lastTime=0;

  function refreshElements(){
    nodes=[...svg.querySelectorAll('[data-node]')];
    edges=[...svg.querySelectorAll('.edge')];
    labels=[...svg.querySelectorAll('.edge-label')];
    paint();
    highlight(focus);
  }
  function paint(){
    for(const node of nodes){
      const p=positions[node.dataset.node];
      node.setAttribute('transform',`translate(${p[0]} ${p[1]})`);
    }
    for(const edge of edges){
      const a=positions[edge.dataset.source],b=positions[edge.dataset.target];
      const length=Math.max(1,Math.hypot(b[0]-a[0],b[1]-a[1]));
      const dx=(b[0]-a[0])/length*25,dy=(b[1]-a[1])/length*25;
      edge.setAttribute('x1',a[0]+dx);edge.setAttribute('y1',a[1]+dy);
      edge.setAttribute('x2',b[0]-dx);edge.setAttribute('y2',b[1]-dy);
    }
    for(const label of labels){
      const a=positions[label.dataset.source],b=positions[label.dataset.target];
      label.setAttribute('x',(a[0]+b[0])/2);label.setAttribute('y',(a[1]+b[1])/2-10);
    }
  }
  function highlight(id){
    focus=id;
    const near=new Set(id?[id]:[]);
    for(const edge of edges){
      const linked=!!id&&(edge.dataset.source===id||edge.dataset.target===id);
      edge.classList.toggle('connected',linked);
      if(linked){near.add(edge.dataset.source);near.add(edge.dataset.target)}
    }
    svg.classList.toggle('focus-mode',!!id);
    for(const node of nodes){node.classList.toggle('near',near.has(node.dataset.node));node.classList.toggle('focused',node.dataset.node===id)}
    for(const label of labels)label.classList.toggle('connected',!!id&&(label.dataset.source===id||label.dataset.target===id));
  }
  function bounds(p){p[0]=Math.max(42,Math.min(878,p[0]));p[1]=Math.max(42,Math.min(688,p[1]))}
  function tick(now){
    frameId=0;
    if(!moving||!visible||document.hidden)return;
    const dt=lastTime?Math.min((now-lastTime)/16.67,2):1;
    lastTime=now;
    const force=Object.fromEntries(S.nodes.map((n,i)=>{
      const p=positions[n.id],home=homes[n.id];
      return[n.id,[(home[0]+Math.sin(now*.00035+i*1.7)*5-p[0])*.008,(home[1]+Math.cos(now*.0003+i*1.4)*5-p[1])*.008]];
    }));
    for(let i=0;i<S.nodes.length;i++)for(let j=i+1;j<S.nodes.length;j++){
      const a=S.nodes[i].id,b=S.nodes[j].id,dx=positions[b][0]-positions[a][0],dy=positions[b][1]-positions[a][1],d=Math.max(1,Math.hypot(dx,dy));
      if(d<120){const f=(120-d)*.012;force[a][0]-=dx/d*f;force[a][1]-=dy/d*f;force[b][0]+=dx/d*f;force[b][1]+=dy/d*f}
    }
    for(const pair of S.study.pairs){
      const a=pair[0],b=pair[1],dx=positions[b][0]-positions[a][0],dy=positions[b][1]-positions[a][1],d=Math.max(1,Math.hypot(dx,dy));
      const rest=Math.hypot(homes[b][0]-homes[a][0],homes[b][1]-homes[a][1]),f=(d-rest)*.001;
      force[a][0]+=dx/d*f;force[a][1]+=dy/d*f;force[b][0]-=dx/d*f;force[b][1]-=dy/d*f;
    }
    for(const n of S.nodes){
      if(drag?.id===n.id)continue;
      const v=velocity[n.id],p=positions[n.id];
      for(let axis=0;axis<2;axis++){v[axis]=(v[axis]+force[n.id][axis]*dt)*Math.pow(.86,dt);p[axis]+=v[axis]*dt}
      bounds(p);
    }
    paint();
    frameId=requestAnimationFrame(tick);
  }
  function syncMotion(){
    if(frameId){cancelAnimationFrame(frameId);frameId=0}
    lastTime=0;
    pause.textContent=moving?'Pause motion':'Resume motion';
    pause.setAttribute('aria-pressed',String(moving));
    if(moving&&visible&&!document.hidden)frameId=requestAnimationFrame(tick);
  }
  function nodeAt(event){return event.target.closest('[data-node]')}
  function dragTo(event){
    const matrix=svg.getScreenCTM();if(!matrix)return;
    const point=new DOMPoint(event.clientX,event.clientY).matrixTransform(matrix.inverse());
    const p=positions[drag.id];p[0]=point.x;p[1]=point.y;bounds(p);
    velocity[drag.id]=[0,0];paint();
  }
  svg.addEventListener('pointerover',event=>{if(!drag){const node=nodeAt(event);if(node)highlight(node.dataset.node)}});
  svg.addEventListener('pointerout',event=>{if(!drag&&!event.relatedTarget?.closest?.('[data-node]'))highlight(null)});
  svg.addEventListener('pointerdown',event=>{
    const node=nodeAt(event);if(!node||event.button!==0)return;
    event.preventDefault();drag={id:node.dataset.node,pointer:event.pointerId};
    node.focus();svg.setPointerCapture(event.pointerId);svg.classList.add('is-dragging');highlight(drag.id);dragTo(event);
  });
  svg.addEventListener('pointermove',event=>{if(drag&&drag.pointer===event.pointerId)dragTo(event)});
  function finishDrag(event){
    if(!drag||drag.pointer!==event.pointerId)return;
    const released=drag.id;homes[released]=[...positions[released]];
    if(svg.hasPointerCapture(event.pointerId))svg.releasePointerCapture(event.pointerId);
    drag=null;svg.classList.remove('is-dragging');highlight(released);
  }
  svg.addEventListener('pointerup',finishDrag);svg.addEventListener('pointercancel',finishDrag);
  svg.addEventListener('focusin',event=>{const node=nodeAt(event);if(node)highlight(node.dataset.node)});
  svg.addEventListener('focusout',()=>{if(!drag)highlight(null)});
  svg.addEventListener('keydown',event=>{
    const node=nodeAt(event),shift={ArrowLeft:[-14,0],ArrowRight:[14,0],ArrowUp:[0,-14],ArrowDown:[0,14]}[event.key];
    if(!node||!shift)return;
    event.preventDefault();const id=node.dataset.node,p=positions[id];
    p[0]+=shift[0];p[1]+=shift[1];bounds(p);homes[id]=[...p];velocity[id]=[0,0];highlight(id);paint();
  });
  pause.addEventListener('click',()=>{moving=!moving;syncMotion()});
  document.getElementById('graph-reset').addEventListener('click',()=>{
    for(const n of S.nodes){positions[n.id]=[...seeds[n.id]];homes[n.id]=[...seeds[n.id]];velocity[n.id]=[0,0]}
    highlight(null);paint();
  });
  reduced.addEventListener('change',event=>{moving=!event.matches;syncMotion()});
  document.addEventListener('visibilitychange',syncMotion);
  new MutationObserver(refreshElements).observe(svg,{childList:true});
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;syncMotion()},{threshold:0}).observe(svg);
  if(moving)S.nodes.forEach((n,i)=>{positions[n.id][0]+=Math.sin(i*2.4)*18;positions[n.id][1]+=Math.cos(i*1.8)*14});
  refreshElements();syncMotion();
})();
