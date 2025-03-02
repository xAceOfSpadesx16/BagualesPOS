const menuToggle = document.querySelector(".menu-toggle");

menuToggle.addEventListener("click", () => {
    const nav = document.querySelector(".nav");
    nav.classList.toggle("mobile-nav");
    menuToggle.classList.toggle("is-active");
});

const logoutButton = document.querySelector("#logout-text");

logoutButton.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelector("#logout-form").submit();
});
