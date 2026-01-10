document.addEventListener("DOMContentLoaded", function () {
  const bandas = document.querySelectorAll(".banda");

  bandas.forEach(banda => {
    const header = banda.querySelector(".banda-header");
    const icon = banda.querySelector(".icon");

    header.addEventListener("click", () => {
      const abierta = banda.classList.toggle("active");

      icon.textContent = abierta ? "−" : "+";
    });
  });
});
