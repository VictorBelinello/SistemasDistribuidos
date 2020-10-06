import { getAllSymbols, getStocks, baseURL } from './server.js';
import { fillSymbolsArea, fillNotificationsArea } from './handleDOM.js';


// Implementacao obtida do link: https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
const user_id = uuidv4();
const notifyStreamURL = baseURL + `subscriptions/${user_id}/stream`;
const transactionStreamURL = baseURL + `transactions/${user_id}/stream`;
let notificationsSource = new EventSource(notifyStreamURL);
let transactionsSource = new EventSource(transactionStreamURL);

async function updateSymbolsArea(){
  const data = await getAllSymbols();
  fillSymbolsArea(data);
}

//setInterval(updateSymbolsArea, 2000);

notificationsSource.onmessage = function (event) {
  fillNotificationsArea({message:event.data});
}

transactionsSource.onmessage = function (event) {
  console.log(event);
  fillNotificationsArea({message:event.data});
}

// Chama uma vez inicialmente para obter acoes iniciais
getStocks(user_id);

export {user_id};

