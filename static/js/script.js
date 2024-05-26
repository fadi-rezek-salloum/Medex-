const menu = document.querySelector(".sidebar-mini");
const targetElement = document.getElementById("jazzy-logo");
const logo = document.querySelector("#jazzy-logo img");

const newElem = document.createElement("span");
newElem.textContent = "×";
newElem.classList.add("closeBtn");

targetElement.removeChild(logo);

targetElement.style.display = "flex";
targetElement.style.justifyContent = "space-between";
targetElement.appendChild(newElem);

newElem.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();

    // menu.classList.add("sidebar-closed");
    // menu.classList.add("sidebar-collapse");
});
