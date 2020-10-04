const baseURL = "http://localhost:5000/";

const getSymbolsButton = document.querySelector("button#get_symbols");
getSymbolsButton.addEventListener("click", getAllSymbols);

const symbolsArea = document.querySelector("textarea#symbols");

function getAllSymbols() {
  const url = new URL(baseURL+"symbols")
  fetch(url)
  .then((response) => {
    return response.json();
  })
  .then( data => {
    symbolsArea.value = "";
    for(const key in data){
      symbolsArea.value += key + " " + data[key] + "\n";
    }
  })
  .catch((err) => {
    console.log("Error");
  });
}