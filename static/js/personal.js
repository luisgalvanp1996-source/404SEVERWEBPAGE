// ===============================
// ESTADO GLOBAL
// ===============================
let estadoActual = "SELECTOR"; // SELECTOR | VER | EDITAR
let viajeActivoId = null;
let modoFormulario = null; // "nuevo" | "editar"


// ===============================
// ELEMENTOS DOM
// ===============================
const selectorViajes = document.getElementById("viajes-selector");
const viajeActivo = document.getElementById("viaje-activo");
const formularioViaje = document.getElementById("viaje-formulario");

const listaViajes = document.getElementById("viajes-lista");

const btnNuevoViaje = document.getElementById("btn-viaje-nuevo");
const btnVolver = document.getElementById("btn-volver");
const btnEditar = document.getElementById("btn-editar");
const btnEliminar = document.getElementById("btn-eliminar");
const btnGuardar = document.getElementById("btn-guardar");
const btnCancelar = document.getElementById("btn-cancelar");


// ===============================
// CAMBIO DE ESTADO
// ===============================
function setEstado(nuevoEstado, opciones = {}) {
  estadoActual = nuevoEstado;
  viajeActivoId = opciones.viajeId ?? viajeActivoId;
  modoFormulario = opciones.modo ?? null;

  selectorViajes.classList.add("hidden");
  viajeActivo.classList.add("hidden");
  formularioViaje.classList.add("hidden");

  if (estadoActual === "SELECTOR") {
    selectorViajes.classList.remove("hidden");
  }

  if (estadoActual === "VER") {
    viajeActivo.classList.remove("hidden");
    cargarViaje(viajeActivoId);
  }

  if (estadoActual === "EDITAR") {
    formularioViaje.classList.remove("hidden");
    prepararFormulario(modoFormulario);
  }
}


// ===============================
// EVENTOS
// ===============================
btnNuevoViaje.onclick = () => {
  setEstado("EDITAR", { modo: "nuevo" });
};

btnVolver.onclick = () => {
  setEstado("SELECTOR");
};

btnEditar.onclick = () => {
  setEstado("EDITAR", { modo: "editar" });
};

btnCancelar.onclick = () => {
  if (modoFormulario === "nuevo") {
    setEstado("SELECTOR");
  } else {
    setEstado("VER");
  }
};


// ===============================
// FUNCIONES PLACEHOLDER
// ===============================
function cargarViajes() {
  // aquí irá el fetch al backend
  // por ahora mock
  listaViajes.innerHTML = "";

  const ejemplo = [
    { id: 1, titulo: "Viaje a Oaxaca" },
    { id: 2, titulo: "Valle de Guadalupe" }
  ];

  ejemplo.forEach(v => {
    const li = document.createElement("li");
    li.textContent = v.titulo;
    li.onclick = () => setEstado("VER", { viajeId: v.id });
    listaViajes.appendChild(li);
  });
}

function cargarViaje(id) {
  console.log("Cargando viaje", id);

  fetch(`/personal/api/viajes/${id}`)
    .then(r => r.json())
    .then(viaje => {

      // Header
      document.getElementById("viaje-titulo").textContent = viaje.titulo;
      document.getElementById("viaje-meta").textContent =
        `${viaje.pie.lugar} · ${new Date(viaje.pie.fecha).toLocaleDateString()}`;

      // Contenido
      renderViajeContenido(viaje);
    })
    .catch(err => {
      console.error("Error cargando viaje:", err);
    });
}


function prepararFormulario(modo) {
  document.getElementById("form-titulo").textContent =
    modo === "nuevo" ? "Nuevo viaje" : "Editar viaje";
}


// ===============================
// INIT
// ===============================
setEstado("SELECTOR");
cargarViajes();

function renderViajeContenido(viaje) {
  const contenedor = document.getElementById("viaje-contenido");
  if (!contenedor) return;

  contenedor.innerHTML = "";

  if (!viaje.secciones || !viaje.secciones.length) {
    contenedor.innerHTML = "<p>No hay contenido para este viaje.</p>";
    return;
  }

  viaje.secciones
    .sort((a, b) => a.seccion - b.seccion)
    .forEach(seccion => {

      const sec = document.createElement("section");
      sec.className = `viaje-seccion ${seccion.tipo}`;

      const titulo = document.createElement("h3");
      titulo.textContent = seccion.tipo.toUpperCase();
      sec.appendChild(titulo);

      seccion.parrafos
        .sort((a, b) => a.orden - b.orden)
        .forEach(p => {

          const bloque = document.createElement("div");
          bloque.className = "parrafo";

          const texto = document.createElement("p");
          texto.textContent = p.texto;
          bloque.appendChild(texto);

          if (p.frases && p.frases.length) {
            p.frases.forEach(f => {
              const frase = document.createElement("blockquote");
              frase.textContent = f;
              bloque.appendChild(frase);
            });
          }

          sec.appendChild(bloque);
        });

      contenedor.appendChild(sec);
    });
}
