// static/js/finanzas.js
document.addEventListener("DOMContentLoaded", () => {
  // toggles
  const btnDetalle = document.getElementById("toggle-btn-Detalle-Finanzas");
  const detalleSec = document.getElementById("movimientos-detalle");
  btnDetalle.addEventListener("click", () => {
    if (detalleSec.style.display === "none" || detalleSec.style.display === "") {
      detalleSec.style.display = "block";
      btnDetalle.textContent = "Ocultar detalle de movimientos";
    } else {
      detalleSec.style.display = "none";
      btnDetalle.textContent = "Mostrar detalle de movimientos";
    }
  });

  const btnRegistro = document.getElementById("toggle-btn-Registro-Finanzas");
  const registroSec = document.getElementById("registro-seccion");
  btnRegistro.addEventListener("click", () => {
    if (registroSec.style.display === "none" || registroSec.style.display === "") {
      registroSec.style.display = "block";
      btnRegistro.textContent = "Ocultar registro";
    } else {
      registroSec.style.display = "none";
      btnRegistro.textContent = "Realizar Registros";
    }
  });

  // Modal de adjuntos
  const modal = document.getElementById("modalAdjuntos");
  const cerrar = document.getElementById("cerrarModal");
  const galeria = document.getElementById("galeria-archivos");

  // abrir modal cuando se hace click en "Mostrar adjuntos"
  document.querySelectorAll(".btn-ver-adjuntos").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const movId = btn.dataset.id;
      if (!movId) return alert("Movimiento no identificado");

      galeria.innerHTML = "<p>Cargando...</p>";
      modal.style.display = "block";

      try {
        const resp = await fetch(`/finanzas/api/archivos?id=${encodeURIComponent(movId)}`);
        const archivos = await resp.json();

        if (!Array.isArray(archivos) || archivos.length === 0) {
          galeria.innerHTML = "<p>No hay archivos adjuntos.</p>";
          return;
        }

        galeria.innerHTML = "";
        archivos.forEach(a => {
          const item = document.createElement("div");
          item.className = "galeria-item";

          // Tipo: 1 imagen, 2 doc, 3 video, 4 audio
          if (a.tipo === 1) {
            item.innerHTML = `
              <img src="/${a.ubicacion}" alt="img" style="max-width:120px;">
              <a href="/${a.ubicacion}" target="_blank">Ver imagen</a>
            `;
          } else if (a.tipo === 3) {
            item.innerHTML = `
              <img src="/static/icons/video.png" class="icono-tipo" alt="video">
              <a href="/${a.ubicacion}" target="_blank">Reproducir video</a>
              <video controls style="max-width:120px; display:block; margin-top:6px;">
                <source src="/${a.ubicacion}" type="video/mp4">
                Tu navegador no soporta video.
              </video>
            `;
          } else if (a.tipo === 4) {
            item.innerHTML = `
              <img src="/static/icons/audio.png" class="icono-tipo" alt="audio">
              <a href="/${a.ubicacion}" target="_blank">Escuchar audio</a>
              <audio controls style="width:120px; display:block; margin-top:6px;">
                <source src="/${a.ubicacion}">
                Tu navegador no soporta audio.
              </audio>
            `;
          } else { // docs y otros
            item.innerHTML = `
              <img src="/static/icons/doc.png" class="icono-tipo" alt="doc">
              <a href="/${a.ubicacion}" target="_blank">Abrir documento</a>
            `;
          }

          galeria.appendChild(item);
        });

      } catch (err) {
        galeria.innerHTML = `<p>Error cargando archivos: ${err}</p>`;
      }
    });
  });

  // cerrar modal
  cerrar.addEventListener("click", () => modal.style.display = "none");
  window.addEventListener("click", (e) => { if (e.target === modal) modal.style.display = "none"; });
});
