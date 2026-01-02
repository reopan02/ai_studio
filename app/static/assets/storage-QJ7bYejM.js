var L=(c,d)=>()=>(d||c((d={exports:{}}).exports,d),d.exports);import{d as B,o as I,c as A,a as H,f as _,g as S}from"./runtime-dom.esm-bundler-CzCxjph-.js";import{g as V}from"./auth-DhJl3iPe.js";/* empty css                   */var z=L((N,u)=>{const T={class:"storage-page"},j=B({__name:"storage-page",setup(c){return I(async()=>{const d=document.getElementById("adminLink");if(d)try{const a=await V();a!=null&&a.is_admin&&(d.style.display="inline-flex")}catch{}}),(d,a)=>(H(),A("div",T,[...a[0]||(a[0]=[_('<div class="container"><header class="storage-header"><div class="storage-header-left"><a href="/" class="btn btn-secondary" style="text-decoration:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> 返回主页 </a><h1>我的存储库</h1></div><div class="header-actions"><a href="/admin" class="btn btn-secondary" id="adminLink" style="display:none;text-decoration:none;"> Admin </a><a href="/video" class="btn btn-secondary"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"></path></svg> 返回生成页 </a></div></header><section class="section"><div class="section-header"><div style="display:flex;align-items:center;gap:12px;"><div class="section-title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg> 视频生成记录 </div><span class="section-count" id="videoCount">加载中...</span></div></div><div id="storageGrid" class="storage-grid"><div class="empty-state"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg><h3>加载中...</h3></div></div></section><section class="section"><div class="section-header"><div style="display:flex;align-items:center;gap:12px;"><div class="section-title"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 图像生成记录 </div><span class="section-count" id="imageCount">加载中...</span></div></div><div id="imageGrid" class="storage-grid"><div class="empty-state"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg><h3>加载中...</h3></div></div></section></div>',1)])]))}});(function(c,d){typeof u=="object"&&u.exports?u.exports=d():c.StoragePage=d()})(typeof globalThis<"u"?globalThis:window,function(){function c(t,n){const r=`; ${typeof n=="string"?n:typeof document<"u"?document.cookie:""}`.split(`; ${t}=`);return r.length===2?r.pop().split(";").shift():null}function d(){const t=c("csrf_token");return t?{"X-CSRF-Token":t}:{}}function a(t){return String(t??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;")}async function f(t){const n=await t.text();try{const s=JSON.parse(n);return(s==null?void 0:s.detail)||n}catch{return n}}function y(t){t.innerHTML=`
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" style="margin-bottom: 16px;">
                    <path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                <h3>暂无视频记录</h3>
                <p style="margin-top: 8px;">开始生成您的第一个视频吧</p>
                <a href="/video" style="color: #6366f1; text-decoration: none; margin-top: 12px; display: inline-block; font-weight: 500;">去生成视频 →</a>
            </div>
        `}function w(t,n){const s=typeof document<"u"?document.getElementById("videoCount"):null;s&&(s.textContent=`${n.length} 个视频`),t.innerHTML=n.map(e=>{const r=new Date(e.created_at).toLocaleString("zh-CN"),i=String(e.model||"").toLowerCase();let o="badge-default";i.includes("sora")?o="badge-sora2":i.includes("veo")?o="badge-veo":i.includes("seedance")&&(o="badge-seedance");const l=a(e.title||"未命名视频"),h=a(e.prompt||""),p=String(e.video_url||"");return`
                <div class="video-card">
                    <div class="video-thumb">
                        <video src="${p}" controls preload="metadata"></video>
                    </div>
                    <div class="video-info">
                        <div class="video-title">${l}</div>
                        <div class="video-meta">
                            <span class="badge ${o}">${a(e.model)}</span>
                            <span style="color: #94a3b8;">${a(r)}</span>
                        </div>
                        <div class="video-prompt" title="${h}">${h}</div>
                        <div class="video-actions">
                            <a href="${p}" download class="btn btn-secondary btn-sm" style="text-decoration: none; flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                                下载
                            </a>
                            <button onclick="StoragePage.deleteVideoAndReload('${a(e.id)}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
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
        `}function C(t,n){const s=typeof document<"u"?document.getElementById("imageCount"):null;s&&(s.textContent=`${n.length} 张图像`),t.innerHTML=n.map(e=>{const r=new Date(e.created_at).toLocaleString("zh-CN"),i=a(e.title||"未命名图像"),o=a(e.prompt||""),l=String(e.image_url||""),h=l?`<img src="${l}" alt="${i}" loading="lazy" />`:'<div style="color: #cbd5e1; font-size: 14px;">无预览</div>',p=l?`<a href="${l}" download class="btn btn-secondary btn-sm" style="text-decoration: none; flex: 1; justify-content: center;">
                       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                           <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                           <polyline points="7 10 12 15 17 10"/>
                           <line x1="12" y1="15" x2="12" y2="3"/>
                       </svg>
                       下载
                   </a>`:"";return`
                <div class="video-card">
                    <div class="video-thumb">
                        ${h}
                    </div>
                    <div class="video-info">
                        <div class="video-title">${i}</div>
                        <div class="video-meta">
                            <span class="badge badge-default">${a(e.model)}</span>
                            <span style="color: #94a3b8;">${a(r)}</span>
                        </div>
                        <div class="video-prompt" title="${o}">${o}</div>
                        <div class="video-actions">
                            ${p}
                            <button onclick="StoragePage.deleteImageAndReload('${a(e.id)}')" class="btn btn-secondary btn-sm danger" style="flex: 1; justify-content: center;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"/>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                </svg>
                                删除
                            </button>
                        </div>
                    </div>
                </div>
            `}).join("")}async function g({fetchFn:t,gridEl:n,onUnauthorized:s}={}){const e=n||(typeof document<"u"?document.getElementById("storageGrid"):null),r=typeof document<"u"?document.getElementById("videoCount"):null,i=t||(typeof fetch<"u"?fetch:null);if(!e)throw new Error("storageGrid not found");if(!i)throw new Error("fetch is not available");try{const o=await i("/api/v1/videos",{credentials:"include"});if(!o.ok){if(o.status===401){typeof s=="function"&&s();return}throw new Error(await f(o)||"Failed to load videos")}const l=await o.json();if(r&&(r.textContent=l.length===0?"暂无记录":`${l.length} 个视频`),!Array.isArray(l)||l.length===0){y(e);return}w(e,l)}catch(o){e.innerHTML=`<div class="empty-state" style="color: #dc2626; grid-column: 1/-1;"><h3>加载失败</h3><p>${a((o==null?void 0:o.message)||String(o))}</p></div>`,r&&(r.textContent="加载失败")}}async function m({fetchFn:t,gridEl:n,onUnauthorized:s}={}){const e=n||(typeof document<"u"?document.getElementById("imageGrid"):null),r=t||(typeof fetch<"u"?fetch:null);if(!e)throw new Error("imageGrid not found");if(!r)throw new Error("fetch is not available");try{const i=await r("/api/v1/images",{credentials:"include"});if(!i.ok){if(i.status===401){typeof s=="function"&&s();return}throw new Error(await f(i)||"Failed to load images")}const o=await i.json();if(!Array.isArray(o)||o.length===0){k(e);return}C(e,o)}catch(i){e.innerHTML=`<div class="empty-state" style="color: var(--error-color);">Load failed: ${a((i==null?void 0:i.message)||String(i))}</div>`}}async function x(t,{fetchFn:n,confirmFn:s,onDeleted:e}={}){const r=n||(typeof fetch<"u"?fetch:null);if(!r)throw new Error("fetch is not available");const i=s||(typeof confirm<"u"?confirm:null);if(i&&!i("确定要删除这条记录吗？"))return;const o=await r(`/api/v1/videos/${encodeURIComponent(t)}`,{method:"DELETE",credentials:"include",headers:{...d()}});if(!o.ok)throw new Error(await f(o)||"删除失败");typeof e=="function"&&e()}async function b(t,{fetchFn:n,confirmFn:s,onDeleted:e}={}){const r=n||(typeof fetch<"u"?fetch:null);if(!r)throw new Error("fetch is not available");const i=s||(typeof confirm<"u"?confirm:null);if(i&&!i("Delete this record?"))return;const o=await r(`/api/v1/images/${encodeURIComponent(t)}`,{method:"DELETE",credentials:"include",headers:{...d()}});if(!o.ok)throw new Error(await f(o)||"Delete failed");typeof e=="function"&&e()}async function E(t){try{await x(t),await g({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})}catch(n){typeof alert=="function"&&alert((n==null?void 0:n.message)||"删除出错")}}async function $(t){try{await b(t),await m({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})}catch(n){typeof alert=="function"&&alert((n==null?void 0:n.message)||"Delete failed")}}function M(){typeof document>"u"||document.addEventListener("DOMContentLoaded",()=>{g({onUnauthorized:()=>{window.location.href="/login?next=/storage"}}),m({onUnauthorized:()=>{window.location.href="/login?next=/storage"}})})}return{getCookie:c,csrfHeaders:d,loadVideos:g,loadImages:m,deleteVideo:x,deleteImage:b,deleteVideoAndReload:E,deleteImageAndReload:$,init:M,_test:{escapeHtml:a,readError:f,renderEmpty:y,renderVideos:w}}});const v=globalThis.StoragePage;v!=null&&v.init&&v.init();S(j).mount("#app")});export default z();
