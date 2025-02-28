const searchIcon = document.querySelector("#search-icon");

searchIcon.addEventListener("click", () => {
    const nav = document.querySelector(".nav");
    nav.classList.toggle("search");
    nav.classList.toggle("no-search");
    const searchInput = document.querySelector(".search-input");
    searchInput.classList.toggle("search-active");
});