import { getAllSymbols, addInterest } from './server.js';
import { fillResponseArea } from './handleDOM.js';
import { user_id } from "./main.js";

async function handleMenuOption(option) {
  let data = "";
  let symbol = "";
  switch (option) {
    case '0':
      alert("Flws");
      break;
    case '1':
      data = await getAllSymbols();
      fillResponseArea(data);
      break;
    case '2':
      symbol = prompt("Coe").toUpperCase();
      addInterest(user_id, symbol);
      break;
    case '3':
      break;
    case '4':
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