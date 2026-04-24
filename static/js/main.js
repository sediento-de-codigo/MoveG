console.log("¡HOLA! main.js se está ejecutando correctamente");
document.addEventListener('DOMContentLoaded', () => {
    // 1. Registro Service Worker (en la raíz)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register("/sw.js")
            .then(reg => console.log('PWA Registrada correctamente'))
            .catch(err => console.log('Fallo al registrar PWA', err));
    }

    // 2. Lógica del Switch
    const switchElement = document.getElementById('status-switch');
    const infoConductor = document.getElementById('info-conductor');
    const seccionSolicitudes = document.getElementById('seccion-solicitudes');

    function actualizarInterfaz() {
        
        
        if (switchElement.checked) {
            infoConductor?.classList.remove('d-none');
            seccionSolicitudes?.classList.remove('d-none');
        } else {
            infoConductor?.classList.add('d-none');
            seccionSolicitudes?.classList.add('d-none');
        }
       // FUERZA LA VISIBILIDAD SIEMPRE
    //seccionSolicitudes?.classList.remove('d-none');
    }

    if (switchElement) {
        switchElement.addEventListener('change', async function () {
            actualizarInterfaz();
            
            const nuevoEstado = this.checked ? 'ON' : 'OFF';
            
            try {
                const response = await fetch('/actualizar_estado', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: nuevoEstado })
                });
                // AGREGA ESTO DEBAJO PARA VER LA RESPUESTA:
                  const data = await response.json(); // Intentamos leer la respuesta como JSON
                  console.log("Respuesta del servidor:", data);

                if (data.success) {    
                console.log('Estado guardado');
                actualizarInterfaz();
            } else{
                throw new Error("El servidor no pudo actualizar");}
            } catch (error) {
                console.error('Error:', error);
                this.checked = !this.checked; 
                actualizarInterfaz();
            }
        });
    }

    actualizarInterfaz(); 
}); // <--- ESTA LLAVE CIERRA EL DOMContentLoaded. ¡NO LA BORRES!
document.addEventListener("DOMContentLoaded", function() {
    const switchElement = document.getElementById('btnSwitch');
    const seccion = document.getElementById('seccion-solicitudes');

    if (switchElement && seccion) {
        switchElement.addEventListener('change', function() {
            if (this.checked) {
                seccion.classList.remove('d-none');
                console.log("Activado: Mostrando solicitudes");
            } else {
                seccion.classList.add('d-none');
                console.log("Desactivado: Ocultando solicitudes");
            }
        });
    } else {
        console.error("Error: No se encontró el ID del botón o de la sección");
    }
});

function ver_solicitudes() {
    console.log("Sistema: Mostrando solicitudes activas...");
    // Si en el futuro necesitas refrescar datos vía AJAX, aquí iría el fetch
}