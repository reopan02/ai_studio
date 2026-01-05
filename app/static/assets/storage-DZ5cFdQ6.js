var A=(f,d)=>()=>(d||f((d={exports:{}}).exports,d),d.exports);import{d as S,o as H,a as U,b as _,g as j,j as V}from"./runtime-dom.esm-bundler-D9CM_geE.js";import{g as T}from"./auth-DhJl3iPe.js";/* empty css                   */var P=A((q,u)=>{(function(f,d){typeof u=="object"&&u.exports?u.exports=d():f.StoragePage=d()})(typeof globalThis<"u"?globalThis:window,function(){function f(t,n){const s=`; ${typeof n=="string"?n:typeof document<"u"?document.cookie:""}`.split(`; ${t}=`);return s.length===2?s.pop().split(";").shift():null}function d(){const t=f("csrf_token");return t?{"X-CSRF-Token":t}:{}}function r(t){return String(t??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;")}async function p(t){const n=await t.text();try{const a=JSON.parse(n);return(a==null?void 0:a.detail)||n}catch{return n}}function y(t){t.innerHTML=`
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                    <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                <h3>暂无视频记录</h3>
                <p style="margin-top: 8px;">开始生成您的第一个视频吧</p>
                <a href="/video" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去生成视频 →</a>
            </div>
        `}function w(t,n){const a=typeof document<"u"?document.getElementById("videoCount"):null;a&&(a.textContent=`${n.length} 个视频`),t.innerHTML=n.map(e=>{const s=new Date(e.created_at).toLocaleString("zh-CN"),o=String(e.model||"").toLowerCase();let i="badge-default";o.includes("sora")?i="badge-sora2":o.includes("veo")?i="badge-veo":o.includes("seedance")&&(i="badge-seedance");const c=r(e.title||"未命名视频"),l=r(e.prompt||""),h=String(e.video_url||"");return`
                <div class="video-card">
                    <div class="video-thumb">
                        <video src="${h}" controls preload="metadata"></video>
                    </div>
                    <div class="video-info">
                        <div class="video-title">${c}</div>
                        <div class="video-meta">
                            <span class="badge ${i}">${r(e.model)}</span>
                            <span style="color: #94a3b8;">${r(s)}</span>
                        </div>
                        <div class="video-prompt" title="${l}">${l}</div>
                        <div class="video-actions">
                            <a href="${h}" download class="btn btn-secondary btn-sm" style="text-decoration: none; flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                                下载
                            </a>
                            <button onclick="StoragePage.deleteVideoAndReload('${r(e.id)}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                </div>
            `}).join("")}function k(t){t.innerHTML=`
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
                <h3>暂无图像记录</h3>
                <p style="margin-top: 8px;">开始编辑您的第一张图像吧</p>
                <a href="/image" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去图像编辑 →</a>
            </div>
        `}function $(t,n){const a=typeof document<"u"?document.getElementById("imageCount"):null;a&&(a.textContent=`${n.length} 张图像`),t.innerHTML=n.map(e=>{const s=new Date(e.created_at).toLocaleString("zh-CN"),o=r(e.title||"未命名图像"),i=r(e.prompt||""),c=String(e.image_url||""),l=r(e.id||""),h=c||(l?`/api/v1/images/${l}/data/0`:""),M=h?`<img src="${h}" alt="${o}" loading="lazy" />`:'<div style="color: #cbd5e1; font-size: 14px;">无预览</div>',B=(l?`/api/v1/images/${l}/data/0`:h)?`<button onclick="StoragePage.downloadImage('${l}', '${r(o)}')" class="btn btn-secondary btn-sm" style="flex: 1; justify-content: center;">
                       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                           <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                           <polyline points="7 10 12 15 17 10"/>
                           <line x1="12" y1="15" x2="12" y2="3"/>
                       </svg>
                       下载
                   </button>`:"";return`
                <div class="video-card">
                    <div class="video-thumb">
                        ${M}
                    </div>
                    <div class="video-info">
                        <div class="video-title">${o}</div>
                        <div class="video-meta">
                            <span class="badge badge-default">${r(e.model)}</span>
                            <span style="color: #94a3b8;">${r(s)}</span>
                        </div>
                        <div class="video-prompt" title="${i}">${i}</div>
                        <div class="video-actions">
                            ${B}
                            <button onclick="StoragePage.deleteImageAndReload('${l}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                </div>
            `}).join("")}async function v({fetchFn:t,gridEl:n,onUnauthorized:a}={}){const e=n||(typeof document<"u"?document.getElementById("storageGrid"):null),s=typeof document<"u"?document.getElementById("videoCount"):null,o=t||(typeof fetch<"u"?fetch:null);if(!e)throw new Error("storageGrid not found");if(!o)throw new Error("fetch is not available");try{const i=await o("/api/v1/videos",{credentials:"include"});if(!i.ok){if(i.status===401){typeof a=="function"&&a();return}throw new Error(await p(i)||"Failed to load videos")}const c=await i.json();if(s&&(s.textContent=c.length===0?"暂无记录":`${c.length} 个视频`),!Array.isArray(c)||c.length===0){y(e);return}w(e,c)}catch(i){e.innerHTML=`<div class="empty-state" style="color: #dc2626; grid-column: 1/-1;"><h3>加载失败</h3><p>${r((i==null?void 0:i.message)||String(i))}</p></div>`,s&&(s.textContent="加载失败")}}async function m({fetchFn:t,gridEl:n,onUnauthorized:a}={}){const e=n||(typeof document<"u"?document.getElementById("imageGrid"):null),s=t||(typeof fetch<"u"?fetch:null);if(!e)throw new Error("imageGrid not found");if(!s)throw new Error("fetch is not available");try{const o=await s("/api/v1/images",{credentials:"include"});if(!o.ok){if(o.status===401){typeof a=="function"&&a();return}throw new Error(await p(o)||"Failed to load images")}const i=await o.json();if(!Array.isArray(i)||i.length===0){k(e);return}$(e,i)}catch(o){e.innerHTML=`<div class="empty-state" style="color: var(--error-color);">Load failed: ${r((o==null?void 0:o.message)||String(o))}</div>`}}async function x(t,{fetchFn:n,confirmFn:a,onDeleted:e}={}){const s=n||(typeof fetch<"u"?fetch:null);if(!s)throw new Error("fetch is not available");const o=a||(typeof confirm<"u"?confirm:null);if(o&&!o("确定要删除这条记录吗？"))return;const i=await s(`/api/v1/videos/${encodeURIComponent(t)}`,{method:"DELETE",credentials:"include",headers:{...d()}});if(!i.ok)throw new Error(await p(i)||"删除失败");typeof e=="function"&&e()}async function b(t,{fetchFn:n,confirmFn:a,onDeleted:e}={}){const s=n||(typeof fetch<"u"?fetch:null);if(!s)throw new Error("fetch is not available");const o=a||(typeof confirm<"u"?confirm:null);if(o&&!o("Delete this record?"))return;const i=await s(`/api/v1/images/${encodeURIComponent(t)}`,{method:"DELETE",credentials:"include",headers:{...d()}});if(!i.ok)throw new Error(await p(i)||"Delete failed");typeof e=="function"&&e()}async function C(t){try{await x(t),await v({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})}catch(n){typeof alert=="function"&&alert((n==null?void 0:n.message)||"删除出错")}}async function E(t){try{await b(t),await m({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})}catch(n){typeof alert=="function"&&alert((n==null?void 0:n.message)||"Delete failed")}}async function L(t,n){if(t)try{const a=`/api/v1/images/${t}/data/0`,e=await fetch(a,{credentials:"include"});if(!e.ok)throw new Error("下载失败");const s=await e.blob(),o=e.headers.get("content-type")||"image/png",i=o.includes("jpeg")?"jpg":o.includes("webp")?"webp":o.includes("gif")?"gif":"png",c=URL.createObjectURL(s),l=document.createElement("a");l.href=c,l.download=`${n||"image"}.${i}`,document.body.appendChild(l),l.click(),document.body.removeChild(l),URL.revokeObjectURL(c)}catch(a){typeof alert=="function"&&alert((a==null?void 0:a.message)||"下载失败")}}function I(){typeof document>"u"||document.addEventListener("DOMContentLoaded",()=>{v({onUnauthorized:()=>{window.location.href="/login?next=/storage"}}),m({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})})}return{getCookie:f,csrfHeaders:d,loadVideos:v,loadImages:m,deleteVideo:x,deleteImage:b,deleteVideoAndReload:C,deleteImageAndReload:E,downloadImage:L,init:I,_test:{escapeHtml:r,readError:p,renderEmpty:y,renderVideos:w}}});const z={class:"storage-page"},R=S({__name:"storage-page",setup(f){return H(async()=>{window.StoragePage&&(window.StoragePage.loadVideos({onUnauthorized:()=>{window.location.href="/login?next=/storage"}}),window.StoragePage.loadImages({onUnauthorized:()=>{window.location.href="/login?next=/storage"}}));const d=document.getElementById("adminLink");if(d)try{const r=await T();r!=null&&r.is_admin&&(d.style.display="inline-flex")}catch{}}),(d,r)=>(_(),U("div",z,[...r[0]||(r[0]=[j('<div class="container"><header class="storage-header"><div class="storage-header-left"><a href="/" class="btn btn-secondary" style="text-decoration:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> 返回主页 </a><h1>我的存储库</h1></div><div class="header-actions"><a href="/admin" class="btn btn-secondary" id="adminLink" style="display:none;text-decoration:none;"> Admin </a><a href="/video" class="btn btn-secondary"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> 返回生成页 </a></div></header><section class="section"><div class="section-header"><div style="display:flex;align-items:center;gap:12px;"><div class="section-title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg> 视频生成记录 </div><span class="section-count" id="videoCount">加载中...</span></div></div><div id="storageGrid" class="storage-grid"><div class="empty-state"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg><h3>加载中...</h3></div></div></section><section class="section"><div class="section-header"><div style="display:flex;align-items:center;gap:12px;"><div class="section-title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 图像生成记录 </div><span class="section-count" id="imageCount">加载中...</span></div></div><div id="imageGrid" class="storage-grid"><div class="empty-state"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg><h3>加载中...</h3></div></div></section></div>',1)])]))}}),g=globalThis.StoragePage;g!=null&&g.init&&g.init();V(R).mount("#app")});export default P();
