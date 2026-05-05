document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("inputFoto");
    const preview = document.getElementById("preview");

    if (!input || !preview) {
        console.log("No se encontró input o preview");
        return;
    }

    input.addEventListener("change", function (e) {
        const file = e.target.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (event) {
            preview.src = event.target.result;

            // guardar en navegador
            localStorage.setItem("fotoPerfil", event.target.result);
        };

        reader.readAsDataURL(file);
    });

});