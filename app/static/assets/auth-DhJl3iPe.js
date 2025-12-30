async function t(){const e=await fetch("/api/v1/auth/me",{credentials:"include"});return e.ok?await e.json():null}export{t as g};
