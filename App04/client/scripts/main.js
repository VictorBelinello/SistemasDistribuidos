import { setupMenu } from "./utils.js";
import { initClient, subToTopic } from "./server_utils.js";

async function main() {
  // Inicializa o cliente no lado do server
  const symbols = await initClient(); 
  // Inicializa a area do simbolos com o retorno da funcao 
  const symbolsArea = document.querySelector("textarea#symbols");
  for (const key in symbols) {
    symbolsArea.value += key + '\n';
  }
  const notificationsArea = document.querySelector("textarea#notifications");
  subToTopic('/subscriptions/listen', (event) => {
    notificationsArea.value += event.data;
  });
  setupMenu();
}

main();