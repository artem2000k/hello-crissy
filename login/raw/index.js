const openMenuButtonElement = document.querySelector("[data-open-menu]");
const closeMenuButtonElement = document.querySelector("[data-close-menu]");

const menuElem = document.querySelector(".navmenu");
const menuBlur = document.querySelector("[data-menu-blur]")
openMenuButtonElement.addEventListener("click", ()=>{
    menuElem.style.transform = "translate(0, 0) scale(1, 1)";
    menuBlur.style.backdropFilter = "blur(3px)"
    menuBlur.style.visibility = "visible"
})

const close = ()=>{
    menuElem.style.transform = "translate(-50%, -50%) scale(0, 0)";
    menuBlur.style.backdropFilter = "blur(0)"
    menuBlur.style.visibility = "hidden"
}

closeMenuButtonElement.addEventListener("click", close)
menuBlur.addEventListener("click", close)