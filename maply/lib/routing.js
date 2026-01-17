export async function getRoute(start, end) {

  const url =
  `https://router.project-osrm.org/route/v1/driving/`+
  `${start.lng},${start.lat};${end.lng},${end.lat}`+
  `?overview=full&geometries=geojson`;

  const res = await fetch(url);
  const data = await res.json();

  return data.routes[0].geometry.coordinates;
}

export function simplifyRoute(coords){
  return coords
  .filter((_,i)=>i%10===0)
  .map(p=>[p[1],p[0]]);
}
