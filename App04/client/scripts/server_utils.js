import { uuidv4 } from "./utils.js";
// Inicializa um ID
const client_id = uuidv4();

// Constroi URL base usando o ID
const baseURL = `http://localhost:5000/${client_id}`;
// RequestInit para GET request
const GETReqInit = {method: 'GET'};
// RequestInit para PUT request
let PUTReqInit = {method: 'PUT', headers: {'Content-Type': 'application/json'}, body:{}};
// RequestInit para DELETE request
let DELETEReqInit = {method: 'DELETE', headers: {'Content-Type': 'application/json'}, body:{}};

// Funcao para tratar resposta do servidor
async function handleServerResponse(res){
  if (res['status'] === 204) {
    // Resposta deu certo, mas nao tem body, retorna json vazio
    return {};
  }
  // Tem body/json
  const json = await res.json();

  // Problema na resposta
  if('error' in json){
    const what = json['error']['what'];
    const reason = json['error']['reason'];
    alert(`Error: ${what}\nReason: ${reason}`);
    return {};
  }
  
  // Sem problema com resposta, retorna payload
  return json['data'];
}

async function fetchServer(url, reqInit) {
  // Realiza fetch para url, com requestInit = reqInit
  // Trata a resposta do servidor e retorna payload da resposta
  try {
    const response = await fetch(url, reqInit);
    const res = handleServerResponse(response);
    return res;
  } catch (error) {
    console.log("Error trying to fetch server");
    console.log(error);
  }
}

export function initClient(){
  console.log(`Initializing client ${client_id}`);
  // Envia um GET para o server em '/', sinalizando a inicializacao do cliente
  const res = fetchServer(baseURL, GETReqInit);
  return res;
}

export  function getTopic(topic) {
  const url = new URL(baseURL + topic);
  const data = fetchServer(url, GETReqInit);
  return data;
}

export  function addToTopic(topic, data){
  const url = new URL(baseURL + topic);
  PUTReqInit.body = JSON.stringify(data);
  const res = fetchServer(url, PUTReqInit);
  return res;
}

export function removeFromTopic(topic, data){
  const url = new URL(baseURL + topic);
  DELETEReqInit.body = JSON.stringify(data);
  const res = fetchServer(url, DELETEReqInit);
  return res;
}

export function subToTopic(topic, onMessage){
  const url = baseURL + '/listen' + topic;
  const eventSource = new EventSource(url);
  eventSource.onmessage = onMessage;
}