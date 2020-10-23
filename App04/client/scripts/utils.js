import { getTopic, addToTopic, removeFromTopic, client_id } from "./server_utils.js";

const resultArea = document.querySelector("textarea#response");

// Implementacao obtida do link: https://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid
export function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function getStock(){
  const symbol = prompt("Informe o nome do símbolo").toUpperCase();
  const operation = prompt("Informe a operação (buy ou sell)");
  const amount = prompt("Quantidade de ações");
  const price =  prompt("Preço alvo. Use '.' para separar casas decimais.");
  const timeout =  prompt("Quanto tempo deseja manter a ação em estado condicional?");
  const data = {owner:client_id, symbol:symbol, operation:operation, amount:amount, price:price, timeout:timeout};
  return data;
}

export async function handleMenuOption(option) {
  let symbol = "";
  let stocks = "";

  switch (option) {
    case 1:
      const interests = await getTopic('/quotes');
      resultArea.value = "";
      for (const key in interests) {
        resultArea.value += `${key} ${interests[key]} \n`;
      }
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
      resultArea.value = "";
      for (const key in stocks) {
        resultArea.value +=`${key} ${stocks[key]} \n`;
      }
      break;
    case 6:
      const stock = getStock();
      addToTopic('/order', stock);
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