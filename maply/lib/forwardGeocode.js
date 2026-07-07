const NOMINATIM_HEADERS = {
  "User-Agent": "MapLY-Safety-Application/1.0",
};

export async function getLatLng(place) {
  const res = await fetch(
    `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}`,
    { headers: NOMINATIM_HEADERS }
  );

  if (!res.ok) return null;

  const data = await res.json();

  if (!data || data.length === 0) return null;

  return {
    lat: parseFloat(data[0].lat),
    lng: parseFloat(data[0].lon),
  };
}
