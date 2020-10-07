import { getAllSymbols, getStocks, getBuyTransactions, getSellTransactions, baseURL } from './server.js';
import { fillSymbolsArea, fillNotificationsArea } from './handleDOM.js';


// Implementacao obtida do link: https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
const user_id = uuidv4();
// Chama uma vez inicialmente para obter acoes iniciais
getStocks(user_id);

// Abre uma conexao para as notificacoes
const streamURL = baseURL + `listen/${user_id}`;
let eventSource = new EventSource(streamURL);
eventSource.onmessage = function (event) {
  fillNotificationsArea({message:event.data});
}

async function updateSymbolsArea(){
  const data = await getAllSymbols();
  fillSymbolsArea(data);
}
setInterval(updateSymbolsArea, 2000);

export {user_id};

