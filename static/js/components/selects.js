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