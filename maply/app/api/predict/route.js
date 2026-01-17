export async function POST(req) {

  const body = await req.json();

  const mlRes = await fetch(
    `http://127.0.0.1:8000/api/v1/risk/location?state=${body.state}&district=${body.district}`
  );

  const result = await mlRes.json();

  return Response.json(result);
}
