// static/js/biblia.js
document.addEventListener("DOMContentLoaded", () => {

  // ---------- helpers ----------
  const $ = id => document.getElementById(id);
  const qs = sel => document.querySelector(sel);

  // elementos principales
  const toggleRegBtn = $("toggle-btn-reg");
  const toggleDatBtn = $("toggle-btn-dat");
  const registroCont = $("registro-contenedor");
  const detalleCont = $("detalle-contenedor");

  // selects y cajas
  const libroSel = $("libro");
  const capSel = $("capitulo");
  const iniSel = $("versiculoinicio");
  const finSel = $("versiculofin");

  const aprendizSel = $("opciones");
  const textoCaja = $("texto-detalle");
  const btnAdjuntos = $("btnAdjuntos");

  // modal / lightbox
  const modal = $("lightboxModal");
  const modalBody = $("lightbox-body");
  const closeModalBtn = $("closeLightbox");
  const prevBtn = $("prevSlide");
  const nextBtn = $("nextSlide");
  const metaText = $("meta-text");
  const openOriginal = $("open-original");

  // datos del carrusel (array de objetos {tipo, ubicacion, nombre})
  let currentGallery = [];
  let currentIndex = 0;

  // ---------- UI: mostrar/ocultar secciones ----------
  toggleRegBtn.addEventListener("click", () => {
    registroCont.style.display = registroCont.style.display === "none" ? "block" : "none";
    toggleRegBtn.textContent = registroCont.style.display === "none" ? "Mostrar Registro de Aprendizajes" : "Ocultar Registro de Aprendizajes";
  });

  toggleDatBtn.addEventListener("click", () => {
    detalleCont.style.display = detalleCont.style.display === "none" ? "block" : "none";
    toggleDatBtn.textContent = detalleCont.style.display === "none" ? "Mostrar Sección de Aprendizajes" : "Ocultar Sección de Aprendizajes";
  });

  // ---------- Selects dinámicos para libro -> capitulos -> versiculos ----------
  libroSel && libroSel.addEventListener("change", async () => {
    const libro = libroSel.value;
    capSel.innerHTML = `<option disabled selected>-- Cargando... --</option>`;
    iniSel.innerHTML = `<option disabled selected>-- Selecciona inicio --</option>`;
    finSel.innerHTML = `<option disabled selected>-- Selecciona fin --</option>`;
    try {
      const resp = await fetch(`/biblia/api/capitulos?libro=${encodeURIComponent(libro)}`);
      const capitulos = await resp.json();
      capSel.innerHTML = `<option value="" disabled selected>-- Selecciona --</option>`;
      capitulos.forEach(c => {
        const o = document.createElement("option"); o.value = c; o.textContent = c;
        capSel.appendChild(o);
      });
    } catch(e) {
      capSel.innerHTML = `<option value="" disabled selected>-- Error --</option>`;
      console.error(e);
    }
  });

  capSel && capSel.addEventListener("change", async () => {
    const libro = libroSel.value;
    const cap = capSel.value;
    iniSel.innerHTML = `<option disabled selected>-- Cargando... --</option>`;
    finSel.innerHTML = `<option disabled selected>-- Cargando... --</option>`;
    try {
      const resp = await fetch(`/biblia/api/versiculos?libro=${encodeURIComponent(libro)}&capitulo=${encodeURIComponent(cap)}`);
      const vers = await resp.json();
      iniSel.innerHTML = `<option value="" disabled selected>-- Selecciona inicio --</option>`;
      finSel.innerHTML = `<option value="" disabled selected>-- Selecciona fin --</option>`;
      vers.forEach(v => {
        const o1 = document.createElement("option"); o1.value = v; o1.textContent = v;
        const o2 = document.createElement("option"); o2.value = v; o2.textContent = v;
        iniSel.appendChild(o1);
        finSel.appendChild(o2);
      });
    } catch(e) {
      console.error(e);
    }
  });

  // ---------- cargar aprendizajes en el select de detalle ----------
  (async function loadAprendizajes(){
    try {
      const resp = await fetch("/biblia/api/aprendizajes");
      const datos = await resp.json();
      // formato: "Abrev — Cap X — Vers a-b"
      datos.forEach(a => {
        const opt = document.createElement("option");
        opt.value = a.id;
        opt.textContent = `(${a.abreviatura}) — ${a.nombre} ${a.capitulo}:${a.ini}-${a.fin}`;
        opt.dataset.nombre = a.nombre;
        opt.dataset.cap = a.capitulo;
        opt.dataset.ini = a.ini;
        opt.dataset.fin = a.fin;
        opt.dataset.texto = a.texto;
        aprendizSel.appendChild(opt);
      });

      // cuando se selecciona uno mostramos el texto con salto de línea
      aprendizSel.addEventListener("change", () => {
        const op = aprendizSel.options[aprendizSel.selectedIndex];
        if (!op) return;
        const referencia = `${op.dataset.nombre} ${op.dataset.cap}:${op.dataset.ini}-${op.dataset.fin}`;
        const contenido = op.dataset.texto || "";
        textoCaja.textContent = `${referencia}\n\n${contenido}`;
      });

    } catch(e) {
      console.error("Error cargando aprendizajes:", e);
    }
  })();

  // ---------- BOTÓN mostrar adjuntos: trae archivos desde API y abre modal ----------
  btnAdjuntos.addEventListener("click", async () => {
    const aprId = aprendizSel.value;
    if (!aprId) { alert("Selecciona primero un aprendizaje."); return; }

    // carga archivos
    modalBody.innerHTML = "<p>Cargando adjuntos...</p>";
    try {
      const resp = await fetch(`/biblia/api/archivos?id=${encodeURIComponent(aprId)}`);
      const archivos = await resp.json();

      if (!Array.isArray(archivos) || archivos.length === 0) {
        modalBody.innerHTML = "<p>No hay archivos adjuntos.</p>";
        metaText.textContent = "";
        openOriginal.href = "#";
        modal.style.display = "block";
        return;
      }

      // construimos currentGallery
      currentGallery = archivos.map(a => {
        return {
          tipo: a.tipo,                // 1 img, 2 doc, 3 video, 4 audio
          ubicacion: a.ubicacion,      // "Data/..."
          nombre: (a.nombre || a.ubicacion.split("/").pop())
        };
      });

      // abrir el modal en el primero
      currentIndex = 0;
      renderCurrent();
      modal.style.display = "block";
      modal.setAttribute("aria-hidden","false");

    } catch(e) {
      modalBody.innerHTML = "<p>Error cargando adjuntos.</p>";
      console.error(e);
      modal.style.display = "block";
    }
  });

  // ---------- render según tipo (imagen/video/audio/pdf/otros) ----------
  function renderCurrent() {
    if (!currentGallery.length) return;
    const item = currentGallery[currentIndex];
    const path = item.ubicacion.startsWith("/") ? item.ubicacion : `/${item.ubicacion}`;

    // meta
    metaText.textContent = `${item.nombre} (${typeName(item.tipo)}) — ${currentIndex+1}/${currentGallery.length}`;
    openOriginal.href = path;

    // limpia
    modalBody.innerHTML = "";

    // depend on type
    if (item.tipo === 1) { // imagen -> lightbox + carrusel
      const img = document.createElement("img");
      img.src = path;
      img.style.maxWidth = "100%";
      img.style.maxHeight = "70vh";
      img.alt = item.nombre || "Imagen";
      modalBody.appendChild(img);
    }
    else if (item.tipo === 3) { // video
      const vid = document.createElement("video");
      vid.controls = true;
      vid.autoplay = true;
      vid.style.maxWidth = "100%";
      vid.style.maxHeight = "70vh";
      vid.src = path;
      modalBody.appendChild(vid);
    }
    else if (item.tipo === 4) { // audio
      const aud = document.createElement("audio");
      aud.controls = true;
      aud.autoplay = true;
      aud.src = path;
      aud.style.width = "100%";
      modalBody.appendChild(aud);
    }
    else if (item.tipo === 2) { // documento
      // si es PDF, embed; si no, mostrar icon + abrir
      if (path.toLowerCase().endsWith(".pdf")) {
        const iframe = document.createElement("iframe");
        iframe.src = path;
        iframe.style.width = "100%";
        iframe.style.height = "70vh";
        modalBody.appendChild(iframe);
      } else {
        const icon = document.createElement("img");
        icon.src = "/static/icons/doc.png";
        icon.className = "icono-tipo";
        icon.style.width = "96px";
        modalBody.appendChild(icon);
        const a = document.createElement("a");
        a.href = path; a.target = "_blank"; a.textContent = "Abrir documento en nueva pestaña";
        a.style.display = "block"; a.style.marginTop = "12px";
        modalBody.appendChild(a);
      }
    } else {
      modalBody.innerHTML = `<p>Tipo de archivo no reconocido. <a href="${path}" target="_blank">Abrir</a></p>`;
    }
  }

  // ---------- navegación prev / next ----------
  prevBtn.addEventListener("click", () => {
    if (!currentGallery.length) return;
    currentIndex = (currentIndex - 1 + currentGallery.length) % currentGallery.length;
    renderCurrent();
  });
  nextBtn.addEventListener("click", () => {
    if (!currentGallery.length) return;
    currentIndex = (currentIndex + 1) % currentGallery.length;
    renderCurrent();
  });

  // ---------- cerrar modal ----------
  closeModalBtn.addEventListener("click", closeModal);
  window.addEventListener("keydown", (e) => {
    if (modal.style.display === "block") {
      if (e.key === "Escape") closeModal();
      if (e.key === "ArrowLeft") prevBtn.click();
      if (e.key === "ArrowRight") nextBtn.click();
    }
  });

  // cerrar clic fuera
  window.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  function closeModal() {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden","true");
    modalBody.innerHTML = "";
    currentGallery = [];
    currentIndex = 0;
    metaText.textContent = "";
  }

  function typeName(t) {
    switch(t) {
      case 1: return "Imagen";
      case 2: return "Documento";
      case 3: return "Video";
      case 4: return "Audio";
      default: return "Archivo";
    }
  }

});// ----------------------------------------------
//  BOTÓN PARA VER VERSÍCULOS
// ----------------------------------------------
document.getElementById("btnVerVersiculo").addEventListener("click", function () {
    const id = document.getElementById("opciones").value;

    if (!id) {
        alert("Selecciona un aprendizaje primero.");
        return;
    }

    fetch(`/biblia/obtener_versiculos/${id}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert("No se encontraron versículos.");
                return;
            }

            // Título como "Hechos 12:1-25"
            document.getElementById("tituloVersiculo").textContent = data.cabecera;

            // Texto completo ya formateado desde el servidor
            document.getElementById("textoVersiculo").textContent = data.texto;

            // Mostrar modal
            document.getElementById("modalVersiculo").style.display = "block";
        })
        .catch(() => alert("Error consultando los versículos."));
});

// Cerrar modal
document.getElementById("cerrarVersiculo").addEventListener("click", function () {
    document.getElementById("modalVersiculo").style.display = "none";
});


let rutaActual = "";

function cargarResources(path = "") {
    rutaActual = path;

    fetch(`/biblia/api/resources?path=${encodeURIComponent(path)}`)
        .then(res => res.json())
        .then(data => {
            const lista = document.getElementById("lista-resources");
            const ruta = document.getElementById("ruta-actual");

            lista.innerHTML = "";
            ruta.textContent = "resources" + (path ? " / " + path : "");

            // ⬅️ volver
            if (path) {
                const padre = path.split("/").slice(0, -1).join("/");
                const liBack = document.createElement("li");
                liBack.textContent = "⬅️ ..";
                liBack.onclick = () => cargarResources(padre);
                lista.appendChild(liBack);
            }

            data.items.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item.name;

                if (item.type === "folder") {
                    li.classList.add("resource-folder");
                    li.onclick = () => cargarResources(item.path);
                } else {
                    li.classList.add("resource-file");

                    const ext = item.name.split(".").pop().toLowerCase();
                    li.classList.add(`file-${ext}`);
                    li.onclick = () => {
                        window.location.href = `/biblia/descargar/${item.path}`;
                    };
                }

                lista.appendChild(li);
            });
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("btnActualizar");
    if (btn) btn.addEventListener("click", () => cargarResources(rutaActual));

    cargarResources();
});


document.getElementById("btnActualizar").addEventListener("click", () => {
    cargarResources(rutaActual);
});

document.addEventListener("DOMContentLoaded", () => {
    cargarResources();
});
