const baseURL = "http://localhost:5000";

async function getDataFromServer(url) {
  // Obtem json do servidor baseado na url
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.log(url);   
    console.log(error);
  }
}

function sendDataToServer(url, data){
  console.log(data);
  fetch(url,
     {method: 'POST',
      body: data})
  .then(res => res.json())
  .then(res => console.log(res));
}

function addInterest(id, symbol){
  const url = new URL(baseURL + `/clients/${id}` + '/interests');
  const data = {'symbol': symbol}
  sendDataToServer(url, data);
}

async function getAllSymbols() {
  // Pega todos os simbolos disponiveis, em formato json
  const url = new URL(baseURL);
  return getDataFromServer(url);
}

export {getAllSymbols, addInterest};