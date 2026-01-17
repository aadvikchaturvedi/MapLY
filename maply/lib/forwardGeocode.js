export async function getLatLng(place){

const res = await fetch(
`https://nominatim.openstreetmap.org/search?format=json&q=${place}`
);

const data = await res.json();

return {
 lat: parseFloat(data[0].lat),
 lng: parseFloat(data[0].lon)
};
}
