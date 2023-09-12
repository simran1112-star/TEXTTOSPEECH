const urlOption = document.getElementById("urlOption");
const textOption = document.getElementById("textOption");
const urlInputSection = document.getElementById("urlInputSection");
const displayOptionSection = document.getElementById("displayOptionSection");
const textInputSection = document.getElementById("textInputSection");
const webpageContentSelector = document.getElementById("webpage-frame");

urlOption.addEventListener("click", () => {
    urlInputSection.style.display = "block";
    displayOptionSection.style.display = "block"; 
    textInputSection.style.display = "none";
});

textOption.addEventListener("click", () => {
    urlInputSection.style.display = "none";
    displayOptionSection.style.display = "none"; 
    textInputSection.style.display = "block";
    webpageContentSelector.style.display = "none";
});

function loadWebpage() {
    const urlInput = document.getElementById("urlInput").value;

    setIframeSource(urlInput);
    webpageContentSelector.style.display = "block";
}

function setIframeSource(url) {
    var iframe = document.getElementById("webpage-frame");
    iframe.src = url;
}
