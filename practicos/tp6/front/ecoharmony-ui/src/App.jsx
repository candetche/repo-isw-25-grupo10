// src/App.jsx
import React, { useMemo, useState } from "react";

async function apiInscribirse(data) {
  const res = await fetch("http://127.0.0.1:8000/api/inscribirse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    let detail = "No se pudo procesar la inscripción.";
    try {
      const err = await res.json();
      detail = err.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

async function apiGetActividades() {
  const res = await fetch("http://127.0.0.1:8000/api/actividades");
  if (!res.ok) throw new Error("No se pudieron obtener las actividades");
  return res.json();
}

async function apiGetTurnos(fechaISO) {
  const url = `http://127.0.0.1:8000/api/turnos?fecha=${fechaISO}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("No se pudieron obtener los turnos");
  return res.json();
}



// Helper simple de email
const isValidEmail = (s) => /^[^\s@]+@gmail\.com$/i.test(String(s));
  
// Mayus la primera letra; respeta el resto del string.
function capFirst(s) {
  if (!s) return s;
  return s.charAt(0).toLocaleUpperCase() + s.slice(1);
}

// 💡 CAMBIO AÑADIDO: Función para pasar fecha a formato DD/MM/AAAA
function toDDMMYYYY(isoDate) {
  if (!isoDate) return "";
  // El split original produce [Y, M, D]
  const [y, m, d] = isoDate.split("-");
  // Formato: DD/MM/AAAA
  return `${d}/${m}/${y}`;
}

function pad(n){ return String(n).padStart(2, "0"); }
function toISODate(d){ return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; }
function addDays(d, days){ const x = new Date(d); x.setDate(x.getDate()+days); return x; }
function parseISODate(iso){ const [y,m,day] = iso.split("-").map(Number); return new Date(y, m-1, day); }

// Lunes
function isMondayISO(iso){
  const d = parseISODate(iso);
  return d.getDay() === 1; // 0=Dom,1=Lun,...
}

// Festivos (independiente del año)
const HOLIDAYS_MM_DD = new Set(["01-01","12-25"]);
function isHolidayISO(iso){
  const [, mm, dd] = iso.split("-");
  return HOLIDAYS_MM_DD.has(`${mm}-${dd}`);
}

// Ventana de inscripción: hoy..hoy+2 (inclusive)
function getTodayISO(){ return toISODate(new Date()); }
function getMaxISO(){ return toISODate(addDays(new Date(), 2)); }

// comparación HH:MM
function hhmmToMinutes(hhmm){
  const [h,m] = hhmm.split(":").map(Number);
  return h*60 + m;
}
function nowHHMM(){
  const now = new Date();
  return `${pad(now.getHours())}:${pad(now.getMinutes())}`;
}




// slots 09:00..17:30 cada 30'
function buildSlots() {
  const out = [];
  for (let h = 9; h <= 17; h++) {
    for (let m of [0, 30]) {
      out.push(`${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`);
    }
  }
  return out;
}
const SLOTS = buildSlots();

// “BD” in-memory solo para demo (ocupaciones pre-cargadas)
const PRESEED = [
  // {actividad, fechaISO, hora, dni}
  { actividad: "Safari", fechaISO: "2025-07-21", hora: "10:00", dni: "111" },
  { actividad: "Safari", fechaISO: "2025-07-21", hora: "10:00", dni: "222" },
  { actividad: "Palestra", fechaISO: "2025-07-21", hora: "09:30", dni: "333" },
  { actividad: "Tirolesa", fechaISO: "2025-07-21", hora: "12:00", dni: "444" },
];

function countOcupados(regs, actividad, fechaISO, hora) {
  return regs.filter(
    (r) =>
      r.actividad === actividad && r.fechaISO === fechaISO && r.hora === hora
  ).length;
}
function existeSolapado(regs, dni, fechaISO, hora) {
  return regs.some(
    (r) => r.dni === dni && r.fechaISO === fechaISO && r.hora === hora
  );
}

/** ====== App ====== */
export default function App() {

  const [fechaErr, setFechaErr] = useState("");
  const TODAY_ISO = getTodayISO();
  const MAX_INSCRIPCION_ISO = getMaxISO();

  const [step2Errors, setStep2Errors] = useState([]);

  const [step, setStep] = useState(1);
  const [regs, setRegs] = useState(PRESEED);

  const [actividades, setActividades] = useState([]);
  const [turnos, setTurnos] = useState([]);
  const [loading, setLoading] = useState(true);

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Step 1
  const [actividad, setActividad] = useState("");
  const [fechaISO, setFechaISO] = useState("");
  const [hora, setHora] = useState("");
  const [cantidad, setCantidad] = useState(1);

  // Step 2
  const [participantes, setParticipantes] = useState([]);

  // Step 3
  const [showTC, setShowTC] = useState(false);
  const [aceptaTC, setAceptaTC] = useState(false);
  const [email, setEmail] = useState("");

  // Éxito
  const [okMsg, setOkMsg] = useState("");

  // Modal de mensajes (reemplaza alert)
  const [modal, setModal] = useState({ open: false, title: "", content: "" });
  const openModal = (title, content) => setModal({ open: true, title, content });
  const [resetOnModalClose, setResetOnModalClose] = useState(false);
  const closeModal = () => {
    setModal(m => ({ ...m, open: false }));
    if (resetOnModalClose) {
      setResetOnModalClose(false);
      reset();
    }
  };

  // Conflictos de DNI detectados en Step 2 (evita avanzar)
  const [dniConflicts, setDniConflicts] = useState(false);

  async function handleSubmit() {
    if (isSubmitting) return; // evita doble envío
    setIsSubmitting(true);

    try {
      const result = await apiInscribirse(payload);
      openModal("Inscripción", result.mensaje || "Inscripción procesada.");
    } catch (e) {
      openModal("Error", e.message || "Error al inscribirse.");
    } finally {
      setIsSubmitting(false);
    }
  }


  React.useEffect(() => {
    async function fetchData() {
      try {
        const acts = await apiGetActividades();
        setActividades(acts);

        const hoy = getTodayISO();
        const t = await apiGetTurnos(hoy);
        setTurnos(t);

        console.log("Actividades cargadas:", acts);
        console.log("Turnos cargados:", t);
      } catch (e) {
        console.error("Error cargando datos iniciales:", e);
        openModal("Error", "No se pudieron obtener los datos del servidor.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Actualizar turnos cuando cambia la fecha seleccionada
  React.useEffect(() => {
    async function fetchTurnosFecha() {
      try {
        if (!fechaISO) return;
        const t = await apiGetTurnos(fechaISO);
        setTurnos(t);
        console.log("Turnos cargados para fecha", fechaISO, t);
      } catch (e) {
        console.error("Error obteniendo turnos para fecha", fechaISO, e);
      }
    }
    fetchTurnosFecha();
  }, [fechaISO]);


  // Derivados
  const actividadSeleccionada = actividades.find(a => a.nombre === actividad);
  const cuposTotales = actividadSeleccionada ? actividadSeleccionada.cupos : 0;
  const ocupados = useMemo(
    () => countOcupados(regs, actividad, fechaISO, hora),
    [regs, actividad, fechaISO, hora]
  );
  // Preferimos el dato del backend por turno específico; si no existe, caemos al cálculo local
  const turnoSeleccionado = useMemo(() => {
    if (!actividad || !fechaISO || !hora) return null;
    const actSel = actividades.find(a => a.nombre === actividad);
    if (!actSel) return null;
    const fechaSel = String(fechaISO).trim();
    return turnos.find(t =>
      Number(t.actividad_id) === Number(actSel.id) &&
      String(t.fecha).split("T")[0].trim() === fechaSel &&
      String(t.hora).trim() === String(hora).trim()
    ) || null;
  }, [actividad, fechaISO, hora, actividades, turnos]);

  const cuposRestantes = useMemo(() => {
    if (turnoSeleccionado) {
      const fromBackend = Number(
        (turnoSeleccionado.cupos_disponibles ?? turnoSeleccionado.cupo_disponible ?? 0)
      );
      return Math.max(0, fromBackend);
    }
    if (actividad && fechaISO && hora) {
      return Math.max(0, cuposTotales - ocupados);
    }
    return 0;
  }, [turnoSeleccionado, actividad, fechaISO, hora, cuposTotales, ocupados]);

  const puedeAvanzarStep1 =
    actividad && fechaISO && hora && !fechaErr && cantidad > 0 && cantidad <= cuposRestantes;

  async function goNext() {
    if (step === 1 && !puedeAvanzarStep1) return;

    if (step === 1) {

      // Re-chequeo: si la fecha es HOY, el horario debe ser FUTURO,
      // por si dejaron pasar el tiempo entre elegir y “Siguiente”
      if (fechaISO === TODAY_ISO && hhmmToMinutes(hora) <= hhmmToMinutes(nowHHMM())) {
        setFechaErr("El horario seleccionado ya no es válido para hoy. Elegí otro horario futuro.");
        return; // bloquea el avance; el botón “Siguiente” ya queda deshabilitado por fechaErr
      }

      // generar filas para participantes
      const actSel = actividades.find(a => a.nombre === actividad);
      const requiereTalle = actSel ? actSel.requiere_talle : false;

      const arr = Array.from({ length: Number(cantidad) }, () => ({
        nombre: "",
        dni: "",
        edad: "",
        talle: requiereTalle ? "" : undefined,
      }));
      setParticipantes(arr);
      setStep(2);
      return;
    }

    if (step === 2) {
      if (dniConflicts) {
        openModal("Conflictos de DNI", "Hay participantes con DNI ya inscriptos en ese horario. Revisá los avisos en la tabla.");
        return;
      }
      const errs = [];

  // Anti-duplicados dentro de la misma inscripción
      const dniIndex = new Map(); // dniNormalizado -> primeraFila (idx)
            const normalizeDNI = (v) => String(v ?? "").replace(/\D/g, ""); // solo dígitos

    participantes.forEach((p, idx) => {
      const nombreOk = !!p.nombre?.trim();
      const dniNorm = normalizeDNI(p.dni);
      const edadNum = Number(p.edad); // <-- nombre distinto para evitar redeclaración

      const actividadSel = actividades.find(a => a.nombre === actividad);
      const edadMinima = actividadSel ? Number(actividadSel.edad_min ?? 0) : 0;
      const requiereTalle = actividadSel ? actividadSel.requiere_talle : false;

      // Reglas existentes
      if (!nombreOk) errs.push(`Fila ${idx + 1}: nombre es requerido`);
      if (p.nombre) {
        const nombreStr = String(p.nombre);
        const soloLetrasYEspacios = /^[\p{L}\s]+$/u.test(nombreStr);
        if (!soloLetrasYEspacios)
          errs.push(`Fila ${idx + 1}: el nombre solo puede contener letras y espacios`);
      }
      if (!/^\d{6,10}$/.test(dniNorm))
        errs.push(`Fila ${idx + 1}: DNI debe tener 6 a 10 dígitos`);
      if (!Number.isFinite(edadNum) || edadNum <= 0 || edadNum > 150)
        errs.push(`Fila ${idx + 1}: edad inválida`);
      if (edadNum > 0 && Number.isFinite(edadMinima) && edadMinima > 0 && edadNum < edadMinima)
        errs.push(`Fila ${idx + 1}: edad mínima para ${actividad} es ${edadMinima}`);
      if (requiereTalle && !p.talle)
        errs.push(`Fila ${idx + 1}: talle es obligatorio en ${actividad}`);
      // NUEVO: DNI duplicado en esta inscripción
      if (dniNorm) {
        if (dniIndex.has(dniNorm)) {
          const first = dniIndex.get(dniNorm);
          errs.push(`Fila ${idx + 1}: DNI ${dniNorm} está repetido en esta inscripción (también en fila ${first + 1})`);
        } else {
          dniIndex.set(dniNorm, idx);
        }
      }

      // Regla ya existente: no solapado con inscripciones previas guardadas
      if (existeSolapado(regs, dniNorm, fechaISO, hora))
        errs.push(`Fila ${idx + 1}: DNI ${dniNorm} ya está inscripto en otro turno a la misma hora`);
    });

    if (errs.length) {
      setStep2Errors(errs);
      openModal("Revisá los datos", "- " + errs.join("\n- "));
      return;
    }
    setStep2Errors([]);

    setStep(3);
    if (loading) {
      return <div className="container"><p>Cargando datos del parque...</p></div>;
    }

    return;
  }


    if (step === 3) {
        if (!isValidEmail(email)) {
            openModal("Email inválido", "Ingresá un email válido de Gmail.");
            return;
        }
        if (!aceptaTC) {
            openModal("Términos y Condiciones", "Debes aceptar Términos y Condiciones.");
            return;
        }

        const payload = {
            actividad,
            fecha: fechaISO,
            hora,
            email,
            acepta_terminos: aceptaTC,
            participantes: participantes.map((p) => ({
                nombre: p.nombre,
                dni: Number(p.dni),
                edad: Number(p.edad),
                talle: p.talle || null,
            })),
        };
        console.log("Payload enviado al backend:", payload);

        try {
          const result = await apiInscribirse(payload);
          if (result) {
            const id = result.id_inscripcion;
            const idTxt = id ? `\nN° de inscripción: ${id}` : "";
            setResetOnModalClose(true);
            openModal(
              "Inscripción",
              `¡Inscripción confirmada! ${participantes.length} lugar(es) reservado(s) para ${actividad} el ${toDDMMYYYY(fechaISO)} a las ${hora}.${idTxt}`
            );
          }
        } catch (e) {
          openModal("Error", e.message || "No se pudo procesar la inscripción.");
        }
    }

  }

  function goBack() {
    if (step === 2) setStep(1);
    if (step === 3) setStep(2);
  }

  function reset() {
    setStep(1);
    setActividad("");
    setFechaISO("");
    setHora("");
    setCantidad(1);
    setParticipantes([]);
    setAceptaTC(false);
    setShowTC(false);
    setEmail("");
    setOkMsg("");
  }

  return (
    <div className="container">
      <div className="header">
        <img src="/logo.PNG" alt="EcoHarmony Park" />
        <div>
          <h1 className="h1">Inscripción a Actividad</h1>
          <p className="sub">EcoHarmony Park</p>
        </div>
        
      </div>

      <div className="card">
        <div className="stepper">
          <span className={`step ${step === 1 ? "active" : ""}`}>
            1. Selección
          </span>
          <span className={`step ${step === 2 ? "active" : ""}`}>
            2. Participantes
          </span>
          <span className={`step ${step === 3 ? "active" : ""}`}>
            3. Confirmación
          </span>
        </div>

        {step === 1 && (
          <Step1
            actividad={actividad}
            setActividad={setActividad}
            fechaISO={fechaISO}
            setFechaISO={setFechaISO}
            hora={hora}
            setHora={setHora}
            cantidad={cantidad}
            setCantidad={setCantidad}
            cuposRestantes={cuposRestantes}
            todayISO={TODAY_ISO}
            maxISO={MAX_INSCRIPCION_ISO}
            fechaErr={fechaErr}
            setFechaErr={setFechaErr}
            regs={regs}
            actividades={actividades}
            turnos={turnos}

          />
        )}

        {step === 2 && (
          <Step2
            actividad={actividad}
            fechaISO={fechaISO}
            hora={hora}
            participantes={participantes}
            setParticipantes={setParticipantes}
            errors={step2Errors}
            actividades={actividades}
            setDniConflicts={setDniConflicts}

          />
        )}

        {step === 3 && (
          <Step3
            actividad={actividad}
            fechaISO={fechaISO}
            hora={hora}
            participantes={participantes}
            aceptaTC={aceptaTC}
            setAceptaTC={setAceptaTC}
            showTC={showTC}
            setShowTC={setShowTC}
            email={email}
            setEmail={setEmail}
          />
        )}

        <div className="btnbar">
          {step > 1 && (
            <button className="btn secondary" onClick={goBack}>
              Atrás
            </button>
          )}
          {step < 3 && (
            <button
              className="btn"
              disabled={(step === 1 && !puedeAvanzarStep1) || (step === 2 && dniConflicts)}
              onClick={goNext}
            >
              Siguiente
            </button>
          )}
          {step === 3 && (
            <button
              className="btn"
              onClick={async () => {
                if (isSubmitting) return; // Evita doble envío
                setIsSubmitting(true);

                try {
                  await goNext(); // Ejecuta el flujo normal (valida y llama al backend)
                } finally {
                  setIsSubmitting(false);
                }
              }}
              disabled={!aceptaTC || !isValidEmail(email) || isSubmitting}
            >
              {isSubmitting ? "Enviando..." : "Confirmar inscripción"}
            </button>

          )}
        </div>
      </div>

      

      {modal.open && (
        <Modal onClose={closeModal} title={modal.title}>
          <div style={{ whiteSpace: 'pre-wrap' }}>{modal.content}</div>
        </Modal>
      )}
    </div>
  );
}

/** ====== Modal genérico para mensajes ====== */
function Modal({ title, children, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <header>
          <b>{title || "Mensaje"}</b>
        </header>
        <main>
          {children}
        </main>
        <footer>
          <button className="btn secondary" onClick={onClose}>Cerrar</button>
        </footer>
      </div>
    </div>
  );
}

/** ====== Step 1: Selección & cupos previos ====== */
function Step1({
  actividad,
  setActividad,
  fechaISO,
  setFechaISO,
  hora,
  setHora,
  cantidad,
  setCantidad,
  cuposRestantes,
  todayISO,
  maxISO,
  fechaErr,
  setFechaErr,
  regs,
  actividades,
  turnos,
}) {
  const [err, setErr] = useState("");

  function onActividadChange(e) {
    setActividad(e.target.value);
    setHora("");
    setErr("");
  }
  function onFechaChange(e){
    const val = e.target.value;
    setFechaISO(val);
    setHora("");
    setErr("");

    if (!val) { setFechaErr(""); return; }

    // 1) No pasado
    if (val < todayISO) { setFechaErr(`No podés inscribirte en una fecha pasada.`); return; }

    // 2) Ventana: hasta 2 días de anticipación (inclusive)
    if (val > maxISO) { setFechaErr(`Solo podés inscribirte hasta ${maxISO} (máx. 2 días de anticipación).`); return; }

    // 3) No lunes
    if (isMondayISO(val)) { setFechaErr(`El parque esta cerrado los lunes.`); return; }

    // 4) No festivos
    if (isHolidayISO(val)) { setFechaErr(`No se permite inscribirse en días festivos (01/01 y 25/12).`); return; }

    setFechaErr("");
  }

  function onHoraChange(e) {
    setHora(e.target.value);
    setErr("");
  }
  function onCantidadChange(e) {
    const v = Number(e.target.value);
    setCantidad(v);
    if (v > cuposRestantes)
      setErr(`Solo quedan ${cuposRestantes} cupos para ese horario`);
    else setErr("");
  }

  // Horarios a mostrar:
  // - Si la fecha es hoy, filtrar a horarios "posteriores al ahora".
  // - Si hay error de fecha, deshabilitar el select.

  // 1) Base: todos los slots del día
  let baseSlots = SLOTS;

  // 2) Si la fecha es hoy, solo futuros
  if (fechaISO && fechaISO === todayISO) {
    baseSlots = baseSlots.filter(s => hhmmToMinutes(s) > hhmmToMinutes(nowHHMM()));
  }

  // 3) Ocultar slots sin cupo (solo si ya hay actividad + fecha válidas)
  let availableSlots = [];

  if (actividad && fechaISO && !fechaErr) {
    const actSel = actividades.find(a => a.nombre === actividad);
    if (actSel && fechaISO) {
      console.log("🎯 DEBUG - Fecha seleccionada:", fechaISO);
      console.log("🎯 DEBUG - Actividad seleccionada (id):", actSel.id);
      console.log("🎯 DEBUG - Turnos totales recibidos:", turnos.length);


      const fechaSel = fechaISO.trim().slice(0, 10); // asegurar formato AAAA-MM-DD

      availableSlots = turnos
        .filter((t) => {
    // Normalizamos ambos valores para evitar diferencias de formato o espacios
          const fechaTurno = String(t.fecha).split("T")[0].trim();
          const fechaSel = String(fechaISO).trim();

          return (
            Number(t.actividad_id) === Number(actSel.id) && // aseguramos mismo tipo
            fechaTurno === fechaSel &&
            (t.cupos_disponibles > 0 || t.cupo_disponible > 0)
          );
        })
        .map((t) => t.hora);

      console.log("Slots resultantes:", availableSlots);
    }

  }


  // 🔧 Si la fecha es hoy, mostrar solo horarios futuros
  if (fechaISO === todayISO) {
    availableSlots = availableSlots.filter(
      (s) => hhmmToMinutes(s) > hhmmToMinutes(nowHHMM())
    );
  }

  // 💡 CAMBIO AÑADIDO: Conversión a formato DD/MM/AAAA para la visualización del helper
  const displayTodayDDMMYYYY = toDDMMYYYY(todayISO);
  const displayMaxDDMMYYYY = toDDMMYYYY(maxISO);


  return (
    <>
      <div className="row">
        <div className="field">
          <label>Actividad *</label>
          <select value={actividad} onChange={onActividadChange}>
            <option value="">Selecciona una actividad</option>
            {actividades.map(a => (
              <option key={a.nombre} value={a.nombre}>
                {a.nombre}
              </option>
            ))}
          </select>
          <p className="helper">Cupos: Safari 8 · Palestra 12 · Jardinería 12 · Tirolesa 10</p>
        </div>

        <div className="field">
          <label>Fecha *</label>
          <input
            type="date"
            value={fechaISO}
            onChange={onFechaChange}
            min={todayISO}  // no pasado
            max={maxISO}    // hasta hoy+2
          />
          {!!fechaErr && <div className="err">{fechaErr}</div>}
          {!fechaErr && (
            <p className="helper">
              {/* 💡 CAMBIO: Usar las variables formateadas DD/MM/AAAA */}
              Podés inscribirte desde <b>{displayTodayDDMMYYYY}</b> hasta <b>{displayMaxDDMMYYYY}</b>. No se permiten Lunes ni festivos (01/01, 25/12).
            </p>
          )}
        </div>
      </div>

      <div className="row">
        <div className="field">
          <label>Horario *</label>
          <select
            value={hora}
            onChange={onHoraChange}
            disabled={!actividad || !fechaISO || !!fechaErr}
          >
            <option value="">
              {!actividad || !fechaISO ? "Selecciona actividad y fecha" : "Selecciona horario"}
            </option>
            {availableSlots.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          {actividad && fechaISO && hora && !fechaErr && (
            <p className="helper">Quedan <b>{Math.max(0, cuposRestantes)}</b> cupos para este horario.</p>
          )}
          {fechaISO === todayISO && availableSlots.length === 0 && !fechaErr && (
            <div className="err">No quedan horarios futuros disponibles para hoy. Elegí mañana o pasado.</div>
          )}
          {actividad && fechaISO && !fechaErr && availableSlots.length === 0 && (
            <div className="err">No quedan horarios con cupos disponibles para esta fecha. Probá otra fecha.</div>
          )}
        </div>

        <div className="field">
          <label>Cantidad de personas *</label>
          <input type="number" min="1" value={cantidad} onChange={onCantidadChange} />
          {!!err && <div className="err">{err}</div>}
        </div>
      </div>

      <div className="hr"></div>
      <p className="helper">
        Validamos <b>fecha</b> y <b>cupos</b> antes de pedir datos personales. Si no hay disponibilidad o la fecha no es válida, probá otra combinación.
      </p>
    </>
  );
}

/** ====== Step 2: Participantes ====== */
function Step2({ actividad, fechaISO, hora, participantes, setParticipantes, actividades, setDniConflicts }) {
  // Buscar si la actividad seleccionada requiere talle
  const actSel = actividades.find(a => a.nombre === actividad);
  const requiereTalle = actSel ? actSel.requiere_talle : false;

  function update(i, field, value) {
    const copy = [...participantes];
    let nextVal = value;
    if (field === "dni") {
      nextVal = String(value || "").replace(/\D/g, "");
    }
    if (field === "edad") {
      nextVal = String(value || "").replace(/\D/g, "");
    }
    copy[i] = { ...copy[i], [field]: nextVal };
    setParticipantes(copy);
    if (field === "dni") {
      const dniNum = String(nextVal || "");
      const formatMsg = dniNum && !/^\d{6,10}$/.test(dniNum)
        ? "El DNI debe tener entre 6 y 10 dígitos."
        : (!dniNum ? "El DNI es obligatorio." : "");

      setDniFormatWarns(prev => {
        const nextFmt = { ...prev, [i]: formatMsg };
        setDniWarns(prevWarn => {
          const nextWarn = { ...prevWarn, [i]: prevWarn[i] && formatMsg ? "" : prevWarn[i] };
          const hasConflict = Object.values(nextWarn).some(Boolean);
          const hasFormat = Object.values(nextFmt).some(Boolean);
          setTimeout(() => setDniConflicts(hasConflict || hasFormat), 0);
          return nextWarn;
        });
        return nextFmt;
      });
    }
    if (field === "nombre") {
      const v = String(value || "");
      const soloLetrasYEspacios = /^[\p{L}\s]+$/u.test(v);
      setNameWarns(prev => ({ ...prev, [i]: v && !soloLetrasYEspacios ? "El nombre solo puede contener letras y espacios." : "" }));
    }
    if (field === "edad") {
      const n = Number(nextVal);
      let msg = "";
      if (!Number.isFinite(n) || n <= 0) msg = "La edad debe ser mayor a 0.";
      else if (n > 150) msg = "La edad no puede ser mayor a 150.";
      setAgeWarns(prev => ({ ...prev, [i]: msg }));
    }
  }

  const [dniWarns, setDniWarns] = React.useState({}); // {index: message} conflictos (DNI ya inscripto)
  const [dniFormatWarns, setDniFormatWarns] = React.useState({}); // {index: message} formato inválido
  const [nameWarns, setNameWarns] = React.useState({}); // {index: message}
  const [ageWarns, setAgeWarns] = React.useState({});

  async function validarDNIHorario(i, dniValor) {
    try {
      const dniNum = String(dniValor || "").replace(/\D/g, "");
      if (!dniNum || !/^\d{6,10}$/.test(dniNum) || !fechaISO || !hora) return;
      const url = `http://127.0.0.1:8000/api/validar-dni?dni=${dniNum}&fecha=${encodeURIComponent(fechaISO)}&hora=${encodeURIComponent(hora)}`;
      const res = await fetch(url);
      if (!res.ok) return;
      const json = await res.json();
      setDniWarns(prev => {
        const nextWarn = { ...prev, [i]: json.existe ? "Este DNI ya está inscripto en ese horario." : "" };
        const hasConflict = Object.values(nextWarn).some(Boolean);
        const hasFormat = Object.values(dniFormatWarns).some(Boolean);
        setTimeout(() => setDniConflicts(hasConflict || hasFormat), 0);
        return nextWarn;
      });
    } catch {
    }
  }

  const TALLES = ["XS", "S", "M", "L", "XL", "XXL"];

  return (
    <>
      <div className="field">
        <label>Actividad y Horario</label>
        <div className="card" style={{ padding: "12px", borderRadius: "12px" }}>
          <b>{capFirst(actividad)}</b> — {toDDMMYYYY(fechaISO)} a las {hora}
          <br />
          {participantes.length} participante(s) a inscribir.
        </div>
      </div>

      <div className="field">
        <label>Participantes</label>
        <div className="helper">
          {requiereTalle
            ? "Esta actividad requiere talle de vestimenta (arnés/casco)."
            : "Esta actividad no requiere talle de vestimenta."}
        </div>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Nombre *</th>
            <th>DNI *</th>
            <th>Edad *</th>
            {requiereTalle && <th>Talle *</th>}
          </tr>
        </thead>
        <tbody>
          {participantes.map((p, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>
                <input
                  value={p.nombre}
                  onChange={(e) => update(i, "nombre", e.target.value)}
                  placeholder="Nombre y apellido"
                />
                {!!nameWarns[i] && (
                  <div className="err" style={{ marginTop: 4 }}>{nameWarns[i]}</div>
                )}
              </td>
              <td>
                <input
                  value={p.dni}
                  onChange={(e) => update(i, "dni", e.target.value)}
                  onBlur={(e) => validarDNIHorario(i, e.target.value)}
                  placeholder="Solo números"
                  inputMode="numeric"
                  pattern="[0-9]*"
                />
                {!!dniFormatWarns[i] && (
                  <div className="err" style={{ marginTop: 4 }}>{dniFormatWarns[i]}</div>
                )}
                {!!dniWarns[i] && (
                  <div className="err" style={{ marginTop: 4 }}>{dniWarns[i]}</div>
                )}
              </td>
              <td>
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  value={p.edad}
                  onChange={(e) => update(i, "edad", e.target.value)}
                  placeholder="Edad"
                />
                {!!ageWarns[i] && (
                  <div className="err" style={{ marginTop: 4 }}>{ageWarns[i]}</div>
                )}
              </td>
              {requiereTalle && (
                <td>
                  <select
                    value={p.talle || ""}
                    onChange={(e) => update(i, "talle", e.target.value)}
                  >
                    <option value="">Talle</option>
                    {TALLES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="hr"></div>
      <ul className="helper" style={{ margin: "0 0 0 18px" }}>
        <li>Safari/Jardinería: sin límite de edad.</li>
        <li>Palestra: mínimo 12 años. Tirolesa: mínimo 8 años.</li>
        <li>Mismo DNI no puede estar inscripto en otra actividad a la misma hora.</li>
      </ul>
    </>
  );
}


/** ====== Step 3: Confirmación + T&C + Email ====== */
function Step3({
  actividad,
  fechaISO,
  hora,
  participantes,
  aceptaTC,
  setAceptaTC,
  showTC,
  setShowTC,
  email,
  setEmail,
}) {
  return (
    <>
      <div className="field">
        <label>Resumen</label>
        <div className="card" style={{ padding: "12px", borderRadius: "12px" }}>
          <b>{capFirst(actividad)}</b> — {toDDMMYYYY(fechaISO)} a las {hora}
          <br />
          {participantes.length} participante(s).
        </div>
      </div>

      <div className="field">
        <label>Participantes</label>
        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Nombre</th>
              <th>DNI</th>
              <th>Edad</th>
              <th>Talle</th>
            </tr>
          </thead>
          <tbody>
            {participantes.map((p, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{p.nombre}</td>
                <td>{p.dni}</td>
                <td>{p.edad}</td>
                <td>{p.talle || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="field">
        <label>Términos y Condiciones</label>
        <div className="row">
          <button
            type="button"
            className="btn secondary"
            onClick={() => setShowTC(true)}
          >
            Ver Términos
          </button>
          <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="checkbox"
              checked={aceptaTC}
              onChange={(e) => setAceptaTC(e.target.checked)}
            />
            Acepto los Términos y Condiciones
          </label>
        </div>
      </div>

      <div className="field">
        <label>Email para la confirmación *</label>
        <input
          type="email"
          placeholder="tu@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        {!!email && !isValidEmail(email) && (
          <div className="err" style={{ marginTop: 4 }}>El email debe ser una cuenta de Gmail terminada en @gmail.com</div>
        )}
        <p className="helper">
          Usaremos este correo para enviarte el comprobante y la confirmación de
          la inscripción.
        </p>
      </div>

      {showTC && <ModalTC onClose={() => setShowTC(false)} />}
    </>
  );
}

/** ====== Modal de T&C ====== */
function ModalTC({ onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <header>
          <b>Términos y Condiciones de Participación – EcoHarmony Park</b>
        </header>
        <main>
          <ol>
            <li>
              <b>Aceptación de riesgo:</b> Las actividades se desarrollan en
              entornos naturales y pueden implicar cierto nivel de riesgo
              físico. El/la participante asume voluntariamente dichos riesgos y
              se compromete a seguir todas las indicaciones del personal del
              parque.
            </li>
            <li>
              <b>Condiciones de participación:</b> No se permitirá la
              participación bajo efectos de alcohol, medicamentos o sustancias
              que alteren el estado físico o mental. Los menores de edad deben
              contar con autorización y supervisión de un adulto responsable. El
              parque podrá suspender o reprogramar actividades por razones
              climáticas o de seguridad.
            </li>
            <li>
              <b>Seguridad y equipamiento:</b> El uso del equipamiento de
              seguridad provisto por el parque es obligatorio en todas las
              actividades que así lo requieran. El/la participante se compromete
              a utilizarlo correctamente y devolverlo en las condiciones
              recibidas.
            </li>
            <li>
              <b>Responsabilidad:</b> El parque no se hace responsable por
              pérdidas o daños de objetos personales ni por lesiones derivadas
              del incumplimiento de las normas de seguridad. La participación
              implica la aceptación plena de estas condiciones y la renuncia a
              cualquier reclamo por daños derivados de la práctica de las
              actividades.
            </li>
            <li>
              <b>Protección de datos personales:</b> Los datos brindados serán
              utilizados únicamente para la gestión de la inscripción y
              comunicaciones relacionadas, conforme a la legislación vigente.
            </li>
            <li>
              <b>Específicos por actividad:</b> <br />
              <ul>
                <li>
                  <b>Palestra:</b> requiere arnés y casco provistos; edad mínima
                  12.
                </li>
                <li>
                  <b>Tirolesa:</b> requiere arnés y casco provistos; edad mínima
                  8.
                </li>
                <li>
                  <b>Safari/Jardinería:</b> sin límite de edad; seguir
                  instrucciones del guía.
                </li>
              </ul>
            </li>
            <li>
              <b>Confirmación:</b> Al confirmar la inscripción, el/la
              participante declara haber leído y aceptado estos términos y
              condiciones en su totalidad.
            </li>
          </ol>
        </main>
        <footer>
          <button className="btn secondary" onClick={onClose}>
            Cerrar
          </button>
        </footer>
      </div>
    </div>
  );
}
