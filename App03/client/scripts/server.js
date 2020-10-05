const baseURL = "http://localhost:5000/";

async function getJSONFromServer(url) {
  // Obtem json do servidor baseado na url
  try {
    const response = await fetch(url);
    const res = await response.json();
    console.log("Server response: ", res['status']);
    return res['data'];
  } catch (error) {
    console.log("Error trying to get data from server");
  }
}

async function sendJSONToServer(url, data){
  try {
    const response = await fetch(url, {method: 'POST',
    body: data});
    const res = await response.json();
    console.log("Server response: ", res['status']);
  } catch (error) {
    console.log("Error trying to send data to server");
  }
}

async function removeDataFromServer(url, data){
  try {
    const response = await fetch(url, {method: 'DELETE',
    body: data});
    const res = await response.json();
    console.log("Server response: ", res['status']);
  } catch (error) {
    console.log("Error trying to remove data from server");
  }
}

function addInterest(id, symbol){
  const url = new URL(baseURL + `interests/${id}`);
  const data = {symbol: symbol};
  const json = JSON.stringify(data);

  sendJSONToServer(url, json);
}

async function getInterests(id){
  const url = new URL(baseURL + `interests/${id}`);
  const interests = await getJSONFromServer(url);

  return interests;
}

function removeInterest(id, symbol){
  const url = new URL(baseURL + `interests/${id}`);
  const data = {symbol: symbol};
  const json = JSON.stringify(data);

  removeDataFromServer(url, json);
}

function addSubscription(id, symbol, lower, upper){
  const url = new URL(baseURL + `subscriptions/${id}`);
  const data = {symbol: symbol, lower: lower, upper: upper};
  const json = JSON.stringify(data);
  
  sendJSONToServer(url, json);
}
async function getSubscriptions(id){
  const url = new URL(baseURL + `subscriptions/${id}`);
  const subs = await getJSONFromServer(url);
  return subs;
}
async function getAllSymbols() {
  // Pega todos os simbolos disponiveis, em formato json
  const url = new URL(baseURL);
  return getJSONFromServer(url);
}


export {getAllSymbols, addInterest, getInterests, removeInterest, addSubscription, getSubscriptions, baseURL};