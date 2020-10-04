const baseURL = "http://localhost:5000";

async function getDataFromServer(url) {
  // Obtem json do servidor baseado na url
  try {
    const response = await fetch(url);
    const res = await response.json();
    return res;
  } catch (error) {
    console.log(url);   
    console.log(error);
  }
}

async function sendDataToServer(url, data){
  try {
    const response = await fetch(url, {method: 'POST',
    body: data});
    const res = await response.json();
    console.log(res);
  } catch (error) {
    console.log(url);   
    console.log(error);
  }
}

async function removeDataFromServer(url, data){
  try {
    const response = await fetch(url, {method: 'DELETE',
    body: data});
    const res = await response.json();
    console.log(res);
  } catch (error) {
    console.log(url);   
    console.log(error);
  }
}

function addInterest(id, symbol){
  const url = new URL(baseURL + `/clients/${id}/interests`);
  const data = new FormData();
  data.append("symbol", symbol);

  sendDataToServer(url, data);
}

async function getInterests(id){
  const url = new URL(baseURL + `/clients/${id}/interests`);
  const interests = await getDataFromServer(url);
  return interests;
}

function removeInterest(id, symbol){
  const url = new URL(baseURL + `/clients/${id}/interests`);
  const data = new FormData();
  data.append("symbol", symbol);
  
  removeDataFromServer(url, data);
}

function addSubscription(id, symbol, lower, upper){
  const url = new URL(baseURL + `/clients/${id}/subscriptions`);
  const data = new FormData();
  data.append("symbol", symbol);
  data.append("lower", lower);
  data.append("upper", upper);

  sendDataToServer(url, data);
}
async function getSubscriptions(id){
  const url = new URL(baseURL + `/clients/${id}/subscriptions`);
  const subs = await getDataFromServer(url);
  return subs;
}
async function getAllSymbols() {
  // Pega todos os simbolos disponiveis, em formato json
  const url = new URL(baseURL);
  return getDataFromServer(url);
}


export {getAllSymbols, addInterest, getInterests, removeInterest, addSubscription, getSubscriptions, baseURL};