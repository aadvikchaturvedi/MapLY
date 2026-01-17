"use client";
import {MapContainer,TileLayer,Polyline,Circle} from "react-leaflet";

export default function Map({segments=[]}: {segments: Array<{risk: string; path: Array<[number, number]>}>}){

return(
<MapContainer center={[28.61,77.20]} zoom={13}
style={{height:"100vh"}}>

<TileLayer
url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
/>

{segments.map((seg,i)=>{

 let color="green";
 if(seg.risk==="High Risk") color="red";
 if(seg.risk==="Moderate Risk") color="orange";

 return(
 <Polyline
  key={i}
  positions={seg.path}
  pathOptions={{color}}
 />
 )
})}

</MapContainer>
)
}
