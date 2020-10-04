import { handleMenuOption } from "./handleMenu.js";

const symbolsArea = document.querySelector("textarea#symbols");
const responseArea = document.querySelector("textarea#response");
const menuSelect = document.querySelector("select#menu");

function fillSymbolsArea(data) {
  fillTextArea(symbolsArea, data);
}
function fillResponseArea(data){
  fillTextArea(responseArea, data);
}

function fillTextArea(area, data) {
  area.value = "";
  for(const key in data){
    area.value += key + " " + data[key] + "\n";
  }
}


menuSelect.addEventListener("change", () => {
  handleMenuOption(menuSelect.value)
});


export {fillSymbolsArea, fillResponseArea};