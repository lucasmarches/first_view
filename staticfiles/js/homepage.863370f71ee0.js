let yesButton = document.getElementById("yes_btn");

yesButton.addEventListener('click', function () {
  //Create the loading message
  let loadingDiv = document.getElementById("loading_div");
  let loadingMessage = document.createElement("p");
  loadingMessage.appendChild(document.createTextNode("Ok. It will take a few minutes. Why don't you have a coffee while I am working on it?"));
  loadingDiv.appendChild(loadingMessage);

  //Hides the button
  btn_div = document.getElementById('button_div')
  btn_div.innerHTML = '';

  //Add the loading gif
  var DOM_img = document.createElement("img");
  DOM_img.src = "static/img/loading.gif";
  btn_div.appendChild(DOM_img);
  DOM_img.className = "loading"

})
