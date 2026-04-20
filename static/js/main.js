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
        if (!switchElement) return;
        
        if (switchElement.checked) {
            infoConductor?.classList.remove('d-none');
            seccionSolicitudes?.classList.remove('d-none');
        } else {
            infoConductor?.classList.add('d-none');
            seccionSolicitudes?.classList.add('d-none');
        }
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

                if (!response.ok) throw new Error("Fallo en servidor");
                console.log('Estado guardado');
            } catch (error) {
                console.error('Error:', error);
                this.checked = !this.checked; 
                actualizarInterfaz();
            }
        });
    }

    actualizarInterfaz(); 
}); // <--- ESTA LLAVE CIERRA EL DOMContentLoaded. ¡NO LA BORRES!