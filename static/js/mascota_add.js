const botonesGenero = document.querySelectorAll(".btn-genero");
const inputGenero = document.getElementById("genero");

botonesGenero.forEach(btn => {
    btn.addEventListener("click", () => {
        botonesGenero.forEach(b => b.classList.remove("activo"));
        btn.classList.add("activo");
        inputGenero.value = btn.dataset.genero;
    });
});

const slider = document.getElementById("peso");
const valor = document.getElementById("pesoValor");

slider.addEventListener("input", () => {
    valor.textContent = parseFloat(slider.value).toFixed(1);
});