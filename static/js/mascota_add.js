const botonesGenero = document.querySelectorAll(".btn-genero");
const inputGenero = document.getElementById("id_sexo");

if (inputGenero) {
    botonesGenero.forEach(btn => {
        btn.addEventListener("click", () => {
            botonesGenero.forEach(b => b.classList.remove("activo"));
            btn.classList.add("activo");
            inputGenero.value = btn.dataset.genero;
        });
    });
}

const slider = document.getElementById("id_peso");
const pesoManual = document.getElementById("pesoManual");

if (slider && pesoManual) {
    const syncPesoManual = valor => {
        pesoManual.value = parseFloat(valor).toFixed(1);
    };

    syncPesoManual(slider.value);

    slider.addEventListener("input", () => {
        syncPesoManual(slider.value);
    });

    pesoManual.addEventListener("input", () => {
        slider.value = pesoManual.value;
    });

    pesoManual.addEventListener("change", () => {
        let valorNormalizado = parseFloat(pesoManual.value);

        if (Number.isNaN(valorNormalizado)) {
            valorNormalizado = parseFloat(slider.min || "1");
        }

        const min = parseFloat(slider.min || "1");
        const max = parseFloat(slider.max || "50");
        valorNormalizado = Math.min(Math.max(valorNormalizado, min), max);

        slider.value = valorNormalizado.toFixed(1);
        syncPesoManual(slider.value);
    });
}