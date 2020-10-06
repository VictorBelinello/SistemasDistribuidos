const baseURL = "http://localhost:5000/";

function handleServerResponse(res){
  if (res['status'] != '200') {
    alert("Problem with server response");
    alert(res['data']);
  } else {
    console.log("Server response OK.");
  }
}

async function getJSONFromServer(url) {
  // Obtem json do servidor baseado na url
  try {
    const response = await fetch(url);
    const res = await response.json();
    handleServerResponse(res);
    return res['data'];
  } catch (error) {
    console.log("Error trying to get data from server");
  }
}

async function postJSONToServer(url, data){
  try {
    const response = await fetch(url, {method: 'POST',
    headers: {"Content-Type": "application/json"},
    body: data});
    const res = await response.json();
    handleServerResponse(res)
  } catch (error) {
    console.log("Error trying to send data to server");
  }
}

async function removeDataFromServer(url, data){
  try {
    const response = await fetch(url, {method: 'DELETE',
    headers: {"Content-Type": "application/json"},
    body: data});
    const res = await response.json();
    handleServerResponse(res)
  } catch (error) {
    console.log("Error trying to remove data from server");
  }
}

function addInterest(id, symbol){
  const url = new URL(baseURL + `interests/${id}`);
  const data = {symbol: symbol};
  const json = JSON.stringify(data);

  postJSONToServer(url, json);
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
  
  postJSONToServer(url, json);
}

async function getSubscriptions(id){
  const url = new URL(baseURL + `subscriptions/${id}`);
  const subs = await getJSONFromServer(url);
  return subs;
}

async function getStocks(id){
  const url = new URL(baseURL + `transactions/${id}`);
  const stocks = await getJSONFromServer(url);
  return stocks;
}

function buyStock(id, data) {
  const url = new URL(baseURL + `transactions/${id}/buy`);
  const json = JSON.stringify(data);
  postJSONToServer(url, json);
}

function sellStock(id, data) {
  const url = new URL(baseURL + `transactions/${id}/sell`);
  const json = JSON.stringify(data);

  postJSONToServer(url, json);
}

async function getAllSymbols() {
  // Pega todos os simbolos disponiveis, em formato json
  const url = new URL(baseURL);
  return getJSONFromServer(url);
}


export {getAllSymbols, baseURL,
        addInterest, getInterests, removeInterest,
        addSubscription, getSubscriptions,
        getStocks, buyStock, sellStock};