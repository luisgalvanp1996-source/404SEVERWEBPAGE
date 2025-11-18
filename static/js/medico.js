document.addEventListener("DOMContentLoaded", () => {

  //-------------------------------------------
  // 0) TOGGLES DE SECCIONES
  //-------------------------------------------
  const secDetalle = document.getElementById("seccion-detalle-consultas");
  const secRegistro = document.getElementById("seccion-registro");

  const btnToggleDetalle = document.getElementById("toggle-detalle-todas");
  const btnToggleRegistro = document.getElementById("toggle-registro");

  if (btnToggleDetalle) {
    btnToggleDetalle.addEventListener("click", () => {
      secDetalle.style.display =
        secDetalle.style.display === "none" ? "block" : "none";
    });
  }

  if (btnToggleRegistro) {
    btnToggleRegistro.addEventListener("click", () => {
      secRegistro.style.display =
        secRegistro.style.display === "none" ? "block" : "none";
    });
  }


  //-------------------------------------------
  // 1) MODAL ADJUNTOS
  //-------------------------------------------
  const modalAdj = document.getElementById("modalAdjuntos");
  const galeria = document.getElementById("galeria-archivos");
  const cerrarAdj = document.getElementById("cerrarModal");

  if (cerrarAdj) cerrarAdj.onclick = () => modalAdj.style.display = "none";

  async function cargarAdjuntos(consultaId) {
    modalAdj.style.display = "block";
    galeria.innerHTML = "Cargando...";

    try {
      const resp = await fetch(`/medico/api/archivos?id=${consultaId}`);
      const archivos = await resp.json();

      galeria.innerHTML = "";

      archivos.forEach(a => {
        let html = "";
        if (a.tipo === 1) {
          html = `<img src="/${a.ubicacion}" style="max-width:95%;border-radius:10px;">`;
        }
        else if (a.tipo === 2) {
          html = `<embed src="/${a.ubicacion}" type="application/pdf" style="width:100%;height:300px;">`;
        }
        else if (a.tipo === 3) {
          html = `<video controls style="max-width:100%"><source src="/${a.ubicacion}"></video>`;
        }
        else if (a.tipo === 4) {
          html = `<audio controls style="width:100%"><source src="/${a.ubicacion}"></audio>`;
        }

        galeria.innerHTML += `<div>${html}</div>`;
      });

    } catch (err) {
      galeria.innerHTML = "Error cargando archivos";
    }
  }


  //-------------------------------------------
  // 2) MODAL DETALLE CONSULTA
  //-------------------------------------------
  const modalDet = document.getElementById("modalDetalle");
  const cerrarDet = document.getElementById("cerrarDetalle");

  if (cerrarDet) cerrarDet.onclick = () => modalDet.style.display = "none";

  let consultaActual = null;

  async function cargarDetalle(consultaId) {
    consultaActual = consultaId;

    const resp = await fetch(`/medico/api/detalle/${consultaId}`);
    const data = await resp.json();

    document.getElementById("detalle-fecha").innerText = data.fecha;
    document.getElementById("detalle-evento").innerText = data.evento;
    document.getElementById("detalle-importancia").innerText = data.importancia;
    document.getElementById("detalle-clinica").innerText = data.clinica;
    document.getElementById("detalle-medico").innerText = data.medico;
    document.getElementById("detalle-obs").innerText = data.observaciones;

    modalDet.style.display = "block";
  }


  //-------------------------------------------
  // 3) MODAL MEDICAMENTOS
  //-------------------------------------------
  const modalMed = document.getElementById("modalMedicamentos");
  const cerrarMed = document.getElementById("cerrarMedicamentos");
  const listaMed = document.getElementById("listaMedicamentos");

  if (cerrarMed) cerrarMed.onclick = () => modalMed.style.display = "none";

  const btnVerMed = document.getElementById("btn-ver-medicamentos");

  if (btnVerMed) {
    btnVerMed.onclick = async () => {
      if (!consultaActual) return;

      const resp = await fetch(`/medico/api/medicamentos/${consultaActual}`);
      const datos = await resp.json();

      listaMed.innerHTML = "";

      if (datos.medicamentos.length === 0) {
        listaMed.innerHTML = "<li>No hay medicamentos registrados</li>";
      } else {
        datos.medicamentos.forEach(m =>
          listaMed.innerHTML += `<li>• ${m.medicamento}</li>`
        );
      }

      modalMed.style.display = "block";
    };
  }


  //-------------------------------------------
  // 4) ASIGNAR EVENTOS A BOTONES
  //-------------------------------------------
  document.querySelectorAll(".btn-adjuntos").forEach(btn =>
    btn.addEventListener("click", () => cargarAdjuntos(btn.dataset.id))
  );

  document.querySelectorAll(".btn-detalle").forEach(btn =>
    btn.addEventListener("click", () => cargarDetalle(btn.dataset.id))
  );

  // Botón de adjuntos dentro del modal de detalle
  const btnAdjDetalle = document.getElementById("btnAdjuntosDetalle");
  if (btnAdjDetalle)
    btnAdjDetalle.onclick = () => cargarAdjuntos(consultaActual);

});
