export async function getRisk(state,district){

const res = await fetch("/api/predict",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({state,district})
});
  console.log("Fetching risk for:", state, district)
return await res.json();
}
