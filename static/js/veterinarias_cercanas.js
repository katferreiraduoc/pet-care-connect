const map = L.map('map').setView([0, 0], 2);
const markersLayer = L.layerGroup().addTo(map);
const list = document.getElementById('vets-list');

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
subdomains: 'abcd',
maxZoom: 20,
attribution: '© OpenStreetMap contributors © CARTO'
}).addTo(map);

let userMarker = null;
let firstFix = true;

function obtenerUbicacion() {


if (!navigator.geolocation) {
    list.innerHTML = '<p class="vets-list-empty">Tu navegador no soporta geolocalización.</p>';
    return;
};

list.innerHTML = '<p class="vets-list-empty">Detectando tu ubicación...</p>';

navigator.geolocation.watchPosition(

    function (position) {

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const accuracy = position.coords.accuracy;

        if (firstFix) {
            map.setView([lat, lon], 17);
            firstFix = false;
        } else {
            map.panTo([lat, lon]);
        };

        setTimeout(function () {
            map.invalidateSize();
        }, 200);

        if (userMarker) {
            userMarker.setLatLng([lat, lon]);
        } else {
            userMarker = L.marker([lat, lon])
                .addTo(markersLayer)
                .bindPopup('<b>Tú estás aquí</b><br>Precisión: ' + Math.round(accuracy) + ' m')
                .openPopup();
        };

        if (markersLayer.getLayers().length === 1) {
            cargarVetsReales();
        };

    },

    function (error) {
        console.error(error);

        let mensaje = 'Error al obtener ubicación';

        if (error.code === 1) mensaje = 'Permiso denegado';
        if (error.code === 2) mensaje = 'Ubicación no disponible';
        if (error.code === 3) mensaje = 'Tiempo agotado';

        list.innerHTML = '<p class="vets-list-empty">' + mensaje + '</p>';
    },

    {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 0
    }
);


};

function cargarVetsReales() {


fetch('/api/veterinarias/')
    .then(function (response) {
        if (!response.ok) {
            throw new Error("Error API");
        };
        return response.json();
    })
    .then(function (data) {

        list.innerHTML = '';

        if (data.length === 0) {
            list.innerHTML = '<p class="vets-list-empty">No hay veterinarias.</p>';
            return;
        };

        data.forEach(function (vet) {

            const marker = L.marker([vet.lat, vet.lng])
                .addTo(markersLayer)
                .bindPopup('<b>' + vet.nombre + '</b><br>' + vet.direccion);

            const item = document.createElement('article');
            item.className = 'vet-item';

            item.innerHTML =
                '<h3>' + vet.nombre + '</h3>' +
                '<p>' + vet.direccion + '</p>' +
                '<small>Ver en mapa</small>';

            item.onclick = function () {
                map.setView([vet.lat, vet.lng], 17);
                marker.openPopup();
            };

            list.appendChild(item);
        });
    })
    .catch(function () {
        list.innerHTML = '<p class="vets-list-empty">Error cargando veterinarias.</p>';
    });

};

window.onload = function () {
setTimeout(function () {
map.invalidateSize();
obtenerUbicacion();
}, 300);
};

