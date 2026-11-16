let sessionId=crypto.randomUUID(), sequence=0, seconds=0, visits=1, cursor=null;
let queue=[], sentClicks=[], samples=[], enabled=false, sending=false;
const checkbox=document.getElementById('analytics-consent');
try { visits=Math.min(1000000,Number(localStorage.getItem('atelier-visits')||0)+1); if(!Number.isFinite(visits))visits=1; localStorage.setItem('atelier-visits',String(visits)); } catch {}
checkbox?.addEventListener('change',()=>{enabled=checkbox.checked;});
document.addEventListener('click',event=>{
  if(!enabled || queue.length>=30)return;
  const control=event.target.closest('button,a,select,summary,input[type="checkbox"]');
  if(control)queue.push((control.id||control.getAttribute('href')||control.tagName).slice(0,80));
});
document.addEventListener('pointermove',event=>{
  if(!enabled)return;
  cursor=[Math.max(0,Math.min(1000,Math.round(event.clientX/document.documentElement.clientWidth*1000))), Math.max(0,Math.min(1000,Math.round((event.clientY+scrollY)/document.documentElement.scrollHeight*1000)))];
},{passive:true});
setInterval(async()=>{
  if(!enabled || document.hidden)return;
  seconds++;
  if(sending)return;
  const points=cursor?[cursor]:[], clicks=queue.splice(0,30);
  const data={session_id:sessionId,sequence:++sequence,time_on_page:seconds,visits,clicks,pointer_samples:points,layout:document.documentElement.clientWidth<641?'mobile':'desktop'};
  sending=true;
  try {
    const response=await fetch('/api/behavior-metrics',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),keepalive:true});
    if(!response.ok)throw new Error('metrics');
    sentClicks=(sentClicks.concat(clicks)).slice(-100);samples=(samples.concat(points)).slice(-60);
  } catch {queue=(clicks.concat(queue)).slice(-30);} finally {sending=false;}
},1000);
export function getMetrics(){if(!enabled)return {time_on_page:0,visits:1,clicks:[],pointer_samples:[],technical:{}};return {time_on_page:seconds,visits,clicks:sentClicks.slice(-100),pointer_samples:samples.slice(-60),technical:{language:navigator.language,viewport:`${innerWidth}x${innerHeight}`,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone||'',user_agent:navigator.userAgent.slice(0,300)}};}
