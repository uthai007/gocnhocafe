// Project Singapore + nearby Johor / Riau coastlines (Natural Earth 10m via world-atlas) to an SVG viewBox 0 0 1000 H.
const topo=require('./wa/countries-10m.json'); const tc=require('./tc/dist/topojson-client.js');
const fc=tc.feature(topo, topo.objects.countries);
const [x0,y0,x1,y1]=[103.56,1.13,104.14,1.56];
const k=Math.cos(1.35*Math.PI/180), W=1000, sx=W/((x1-x0)*k), H=Math.round((y1-y0)*sx);
const P=([x,y])=>[((x-x0)*k*sx).toFixed(1),((y1-y)*sx).toFixed(1)];
const out={viewBox:`0 0 ${W} ${H}`, paths:{}};
for (const f of fc.features){ const n=f.properties.name; if(!['Singapore','Malaysia','Indonesia'].includes(n)) continue;
  const polys=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
  const d=polys.filter(p=>p[0].some(([x,y])=>x>x0-0.3&&x<x1+0.3&&y>y0-0.3&&y<y1+0.3))
    .map(p=>'M'+p[0].map(P).map(a=>a.join(' ')).join('L')+'Z').join('');
  out.paths[n]=d; }
out.project=(lon,lat)=>P([lon,lat]);
const pts={North:[103.82,1.43],West:[103.70,1.35],Central:[103.82,1.355],East:[103.94,1.355],South:[103.82,1.285]};
out.regions=Object.fromEntries(Object.entries(pts).map(([r,p])=>[r,P(p).map(Number)]));
delete out.project;
require('fs').writeFileSync(process.argv[2], JSON.stringify(out));
console.log(out.viewBox, Object.keys(out.paths).map(k=>k+':'+out.paths[k].length), JSON.stringify(out.regions));
