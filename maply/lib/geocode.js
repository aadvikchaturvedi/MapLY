export async function getDistrict(lat,lng){

const res = await fetch(
`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
);

const data = await res.json();

return {
 state:data.address.state,
 district:
 data.address.county ||
 data.address.city ||
 data.address.town
};
}
