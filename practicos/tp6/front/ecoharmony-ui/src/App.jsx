// src/App.jsx
import React, { useMemo, useState } from "react";

/** ====== Datos base / reglas ====== */
const ACTIVIDADES = ["Safari", "Palestra", "Jardinería", "Tirolesa"];
const CUPOS = { Safari: 8, Palestra: 12, "Jardinería": 12, Tirolesa: 10 };
const REQUIERE_TALLE = new Set(["Palestra", "Tirolesa"]);
const TALLES = ["XS", "S", "M", "L", "XL", "XXL"];
const EDAD_MIN = { Safari: 0, "Jardinería": 0, Palestra: 12, Tirolesa: 8 };


// Helper simple de email
const isValidEmail = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(s));

// Mayus la primera letra; respeta el resto del string.
function capFirst(s) {
  if (!s) return s;
  return s.charAt(0).toLocaleUpperCase() + s.slice(1);
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


  const [step, setStep] = useState(1);
  const [regs, setRegs] = useState(PRESEED);

  

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

  // Derivados
  const cuposTotales = actividad ? CUPOS[actividad] : 0;
  const ocupados = useMemo(
    () => countOcupados(regs, actividad, fechaISO, hora),
    [regs, actividad, fechaISO, hora]
  );
  const cuposRestantes =
    actividad && fechaISO && hora
      ? Math.max(0, cuposTotales - ocupados)
      : 0;

  const puedeAvanzarStep1 =
    actividad && fechaISO && hora && !fechaErr && cantidad > 0 && cantidad <= cuposRestantes;

  function goNext() {
    if (step === 1 && !puedeAvanzarStep1) return;

    if (step === 1) {

      // Re-chequeo: si la fecha es HOY, el horario debe ser FUTURO, 
      // por si dejaron pasar el tiempo entre elegir y “Siguiente”
      if (fechaISO === TODAY_ISO && hhmmToMinutes(hora) <= hhmmToMinutes(nowHHMM())) {
        setFechaErr("El horario seleccionado ya no es válido para hoy. Elegí otro horario futuro.");
        return; // bloquea el avance; el botón “Siguiente” ya queda deshabilitado por fechaErr
      }

      // generar filas para participantes
      const requiereTalle = REQUIERE_TALLE.has(actividad);
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
      const errs = [];

  // Anti-duplicados dentro de la misma inscripción
      const dniIndex = new Map(); // dniNormalizado -> primeraFila (idx)
            const normalizeDNI = (v) => String(v ?? "").replace(/\D/g, ""); // solo dígitos

    participantes.forEach((p, idx) => {
      const nombreOk = !!p.nombre?.trim();
      const dniNorm = normalizeDNI(p.dni);
      const edadNum = Number(p.edad); // <-- nombre distinto para evitar redeclaración

      // Reglas existentes
      if (!nombreOk) errs.push(`Fila ${idx + 1}: nombre es requerido`);
      if (!/^\d{6,10}$/.test(dniNorm))
        errs.push(`Fila ${idx + 1}: DNI debe tener 6 a 10 dígitos`);
      if (!Number.isFinite(edadNum) || edadNum < 0)
        errs.push(`Fila ${idx + 1}: edad inválida`);
      if (edadNum < (EDAD_MIN[actividad] ?? 0))
        errs.push(`Fila ${idx + 1}: edad mínima para ${actividad} es ${EDAD_MIN[actividad]}`);
      if (REQUIERE_TALLE.has(actividad) && !p.talle)
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
      alert("Corrige:\n- " + errs.join("\n- "));
      return;
    }
    setStep(3);
    return;
  }


    if (step === 3) {
      if (!isValidEmail(email)) {
        alert("Ingresá un email válido para la confirmación.");
        return;
      }
      if (!aceptaTC) {
        alert("Debes aceptar Términos y Condiciones.");
        return;
      }
      // Re-chequeo de cupos por carrera
      const ocupadosAhora = countOcupados(regs, actividad, fechaISO, hora);
      const resta = CUPOS[actividad] - ocupadosAhora;
      if (resta < participantes.length) {
        alert(`Hubo cambios en la disponibilidad. Quedan ${resta} cupos.`);
        setStep(1);
        return;
      }
      // “persistir” en memoria
      const nuevas = participantes.map((p) => ({
        actividad,
        fechaISO,
        hora,
        dni: String(p.dni),
      }));
      setRegs((prev) => [...prev, ...nuevas]);
      setOkMsg(
        `¡Inscripción confirmada! ${participantes.length} lugar(es) reservado(s) para ${actividad} el ${fechaISO} a las ${hora}. Enviaremos la confirmación a ${email}.`
      );
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
          <p className="sub">EcoHarmony Park — prototipo front-only</p>
        </div>
        <span className="badge">Alpha • Solo vista previa</span>
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

          />
        )}

        {step === 2 && (
          <Step2
            actividad={actividad}
            participantes={participantes}
            setParticipantes={setParticipantes}
            errors={step2Errors}
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
              disabled={
              step === 1 && !puedeAvanzarStep1 ||
              (step === 2 && step2Errors.length > 0)  
            }
              onClick={goNext}
            >
              Siguiente
            </button>
          )}
          {step === 3 && (
            <button
              className="btn"
              onClick={goNext}
              disabled={!aceptaTC || !isValidEmail(email)}
            >
              Confirmar inscripción
            </button>
          )}
        </div>
      </div>

      {okMsg && (
        <div style={{ marginTop: 16 }} className="success">
          {okMsg}{" "}
          <button
            className="btn secondary"
            style={{ marginLeft: 10 }}
            onClick={reset}
          >
            Nueva inscripción
          </button>
        </div>
      )}
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
    if (cuposRestantes && v > cuposRestantes)
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
  let availableSlots = baseSlots;
  if (actividad && fechaISO && !fechaErr) {
    availableSlots = baseSlots.filter(s => {
      const ocup = countOcupados(regs, actividad, fechaISO, s);
      const total = CUPOS[actividad] ?? 0;
      return (total - ocup) > 0; // mostrar solo si quedan cupos
    });
  }

  // 4) Si el slot seleccionado quedó inválido (p.ej. cambiaste fecha/actividad)
  //    o se quedó sin cupo, lo limpiamos para que el usuario elija otro
  if (hora && !availableSlots.includes(hora)) {
    setHora("");
  }
  
  return (
    <>
      <div className="row">
        <div className="field">
          <label>Actividad *</label>
          <select value={actividad} onChange={onActividadChange}>
            <option value="">Selecciona una actividad</option>
            {ACTIVIDADES.map(a => <option key={a} value={a}>{a}</option>)}
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
              Podés inscribirte desde <b>{todayISO}</b> hasta <b>{maxISO}</b>. No se permiten Lunes ni festivos (01/01, 25/12).
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
function Step2({ actividad, participantes, setParticipantes }) {
  const requiereTalle = REQUIERE_TALLE.has(actividad);

  function update(i, field, value) {
    const copy = [...participantes];
    copy[i] = { ...copy[i], [field]: value };
    setParticipantes(copy);
  }

  return (
    <>
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
              </td>
              <td>
                <input
                  value={p.dni}
                  onChange={(e) => update(i, "dni", e.target.value)}
                  placeholder="Solo números"
                />
              </td>
              <td>
                <input
                  type="number"
                  min="0"
                  value={p.edad}
                  onChange={(e) => update(i, "edad", e.target.value)}
                  placeholder="Edad"
                />
              </td>
              {requiereTalle && (
                <td>
                  <select
                    value={p.talle}
                    onChange={(e) => update(i, "talle", e.target.value)}
                  >
                    <option value="">Selecciona talle</option>
                    {TALLES.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
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
        <li>
          Mismo DNI no puede estar inscripto en otra actividad a la misma hora.
        </li>
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
          <b>{capFirst(actividad)}</b> — {fechaISO} a las {hora}
          <br />
          {participantes.length} participante(s).
        </div>
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
