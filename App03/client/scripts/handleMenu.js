import { addInterest, getInterests, removeInterest, addSubscription } from './server.js';
import { fillResponseArea } from './handleDOM.js';
import { user_id } from "./main.js";

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
      break;
    case '6':
      break;
    case '7':
      break;
    default:
      break;
  }
}

export {handleMenuOption};