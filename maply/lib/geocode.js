const NOMINATIM_HEADERS = {
  "User-Agent": "MapLY-Safety-Application/1.0",
};

export async function getDistrict(lat, lng) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
      { headers: NOMINATIM_HEADERS }
    );

    if (!res.ok) return { state: "", district: "" };

    const data = await res.json();

    if (!data || !data.address) return { state: "", district: "" };

    return {
      state: data.address.state ?? "",
      district:
        data.address.county ||
        data.address.city ||
        data.address.town ||
        data.address.state_district ||
        "",
    };
  } catch {
    return { state: "", district: "" };
  }
}
