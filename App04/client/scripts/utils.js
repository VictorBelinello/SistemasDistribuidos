import { getTopic, addToTopic, removeFromTopic } from "./server_utils.js";


// Implementacao obtida do link: https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid
export function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export async function handleMenuOption(option) {
  let symbol = "";
  let stocks = "";
  switch (option) {
    case 1:
      const interests = await getTopic('/quotes');
      //TODO: Mudar para textarea depois
      console.log(interests);
      break;
    case 2:
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      addToTopic('/quotes', {symbol: symbol});
      break;
    case 3:
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      removeFromTopic('/quotes', {symbol: symbol});
      break;
    case 4:
      symbol = prompt("Informe o nome do símbolo").toUpperCase();
      const lower = prompt("Limite de perda. Use '.' para separar casas decimais.");
      const upper = prompt("Limite de ganho. Use '.' para separar casas decimais.");
      
      addToTopic('/subscriptions', {symbol:symbol, lower:lower, upper:upper});
      break;
    case 5:
      const stocks = await getTopic('/stocks');
      console.log(stocks);
      break;
    case 6:
      break;
    case 7:
      break;
    default:
      break;
  }
}


export function setupMenu(){
  const menuSelect = document.querySelector("select#menu");

  menuSelect.addEventListener('change', () => {
    // Pega o valor selecionado no menu, convertendo para int
    const option = parseInt(menuSelect.value);
    // Reseta selecao para primeiro opcao do menu
    menuSelect.selectedIndex = 0; 
    // Trata a opcao de acordo
    handleMenuOption(option);
  });
}