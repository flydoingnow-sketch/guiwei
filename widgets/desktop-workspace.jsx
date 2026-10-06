import { run } from 'uebersicht';
export const command = "/usr/bin/curl --noproxy '*' --max-time 3 -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18743/";
export const refreshFrequency = 10000;
export const initialState = { ready: false, generation: 0 };
export const updateState = (event, previousState = initialState) => {
  const ready = !event.error && String(event.output || '').trim() === '200';
  return { ready, generation: (previousState.generation || 0) + (ready && !previousState.ready ? 1 : 0) };
};
export const className = `top: 6vh; left: 23vw; width: 54vw; height: 92vh; pointer-events: auto;`;
const mouseBridge = action => {
  const bridge=window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.uebersicht;
  if(bridge) bridge.postMessage(action);
};
export const init = () => {
  window.addEventListener('mousemove', event => {
    const frame=document.querySelector('iframe[title="四象限工作台"]');
    if(!frame){mouseBridge('widgetLeave');return;}
    const rect=frame.getBoundingClientRect();
    const inside=event.clientX>=rect.left && event.clientX<=rect.right && event.clientY>=rect.top && event.clientY<=rect.bottom;
    mouseBridge(inside?'widgetEnter':'widgetLeave');
  });

  window.addEventListener('message', event => {
    if(event.origin !== 'http://127.0.0.1:18743' || !event.data) return;
    if(!Array.from(document.querySelectorAll('iframe')).some(frame => frame.contentWindow === event.source)) return;
    const bridge = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.uebersicht;
    if(event.data.type === 'workspace-hover' && bridge) bridge.postMessage('widgetEnter');
    if(event.data.type === 'workspace-focus') {
      if(bridge) bridge.postMessage('widgetEnter');
      run('/usr/bin/open -b tracesOf.Uebersicht');
    }
  });
};
export const render = ({ ready, generation }) => ready ? <iframe key={`recovery-${generation}`} title="四象限工作台" src="http://127.0.0.1:18743/#startup-recovery" onMouseEnter={() => mouseBridge('widgetEnter')} onMouseLeave={() => mouseBridge('widgetLeave')} style={{width:'100%',height:'100%',border:0,background:'transparent',pointerEvents:'auto'}} /> : <div style={{padding:24,color:'#bfceb1',background:'rgba(8,12,10,.92)',borderRadius:16}}>工作台正在启动，几秒后自动恢复…</div>;
