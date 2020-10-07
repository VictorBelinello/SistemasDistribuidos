import { addInterest, getInterests, removeInterest, addSubscription, getStocks, buyStock, sellStock, getBuyTransactions, getSellTransactions } from './server.js';
import { fillResponseArea } from './handleDOM.js';
import { user_id } from "./main.js";

function getStock() {
  const symbol = prompt("Informe o nome do símbolo").toUpperCase();
  const amount = prompt("Quantidade de ações");
  const price =  prompt("Preço alvo. Use '.' para separar casas decimais.");
  const timeout =  prompt("Quanto tempo deseja manter a ação em estado condicional?");
  const data = {owner:user_id, symbol:symbol, amount:amount, price:price, timeout:timeout};
  return data;
}

async function handleMenuOption(option) {
  let symbol = "";

  switch (option) {
    case '0':
      alert("Flws");
      break;
    case '1':
      const interests = await getInterests(user_id);
      fillResponseArea(interests);
      break;
    case '2':
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      addInterest(user_id, symbol);
      break;
    case '3':
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      removeInterest(user_id, symbol);
      break;
    case '4':
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      const lower = prompt("Limite de perda. Use '.' para separar casas decimais.");
      const upper = prompt("Limite de ganho. Use '.' para separar casas decimais.");
      
      addSubscription(user_id, symbol, lower, upper);
      break;
    case '5':
      const stocks = await getStocks(user_id);
      fillResponseArea(stocks);
      break;
    case '6':
      buyStock(user_id, getStock());
      getBuyTransactions(user_id);
      break;
    case '7':
      sellStock(user_id, getStock());
      getSellTransactions(user_id);
      break;
    default:
      break;
  }
}

export {handleMenuOption};