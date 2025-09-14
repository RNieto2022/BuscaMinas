# -*- coding: utf-8 -*-
# app_buscaminas.py — Interfaz gráfica de Buscaminas con Streamlit (todo en español)
import random
import streamlit as st
from buscaminas import Board  # Lógica del juego (buscaminas.py)

# ----------------------------------------------------
st.set_page_config(page_title="Buscaminas", layout="centered")

# ===== Estilos compactos para reducir espacios en el tablero, se vean los botones mas pegados (filas/columnas) =====

st.markdown("""
<style>
/* === Compactar espacios del GRID (filas/columnas) === */
[data-testid="stAppViewContainer"] div[data-testid="stVerticalBlock"]   { gap: 0rem !important; }
[data-testid="stAppViewContainer"] div[data-testid="stHorizontalBlock"] { gap: 0rem !important; }

/* Quitar márgenes alrededor de los botones del tablero */
[data-testid="stAppViewContainer"] .stButton { margin: 0 !important; }

/* === Celdas del TABLERO: grises y compactas === */
[data-testid="stAppViewContainer"] .stButton > button {
  margin: 0 !important;                 /* evita separación extra del botón */
  padding: 0.05rem 0.10rem !important;  /* compacto */
  height: 1.8rem !important;            /* alto de cada celda */
  line-height: 1 !important;
  min-height: 0 !important; min-width: 0 !important;
  width: 100% !important;               /* ocupa toda la columna */
  background-color: #e0e0e0 !important; /* gris base */
  border-color: #bdbdbd !important;
  color: #111 !important;
}
[data-testid="stAppViewContainer"] .stButton > button:hover {
  background-color: #d4d4d4 !important; /* hover un poco más oscuro */
}
[data-testid="stAppViewContainer"] .stButton > button:disabled {
  background-color: #f0f0f0 !important; /* reveladas */
  opacity: 1 !important;                /* evita translucidez por defecto */
}

/* === Sidebar: deja el botón más grande y legible === */
[data-testid="stSidebar"] .stButton > button {
  height: 2.8rem !important;
  padding: 0.30rem 0.70rem !important;
  font-size: 1rem !important;
  line-height: 1.2 !important;
}
</style>
""", unsafe_allow_html=True)



# ----------------------------------------------------
def nuevo_juego(tam: int, minas: int, semilla: int | None = None):
    # Crea un nuevo tablero y reinicia el estado de la sesión.
    if semilla is not None:
        random.seed(semilla)
    st.session_state.tablero = Board(tam, minas)
    st.session_state.tam = tam
    st.session_state.minas = minas
    st.session_state.banderas = set()
    st.session_state.fin = False
    st.session_state.victoria = False

def excavar_celda(fila: int, col: int):
    # Excava una celda; si hay mina termina el juego, si no continúa.
    if st.session_state.fin or st.session_state.victoria:
        return
    if (fila, col) in st.session_state.banderas:
        return
    seguro = st.session_state.tablero.excavar(fila, col)
    if not seguro:
        st.session_state.fin = True
    else:
        tam, minas = st.session_state.tam, st.session_state.minas
        if len(st.session_state.tablero.dug) == tam * tam - minas:
            st.session_state.victoria = True

def alternar_bandera(fila: int, col: int):
    # Coloca o quita una bandera en la celda indicada.
    if st.session_state.fin or st.session_state.victoria:
        return
    if (fila, col) in st.session_state.tablero.dug:
        return
    if (fila, col) in st.session_state.banderas:
        st.session_state.banderas.remove((fila, col))
    else:
        st.session_state.banderas.add((fila, col))

def etiqueta_celda(fila: int, col: int) -> str:
    # Devuelve el símbolo a mostrar para una celda (según estado actual).
    b = st.session_state.tablero
    esta_banderada = (fila, col) in st.session_state.banderas
    revelada = (fila, col) in b.dug
    val = b.board[fila][col]

    if st.session_state.fin and val == '*':
        return "💣"
    if revelada:
        if val == '*':
            return "💣"
        if val == 0:
            return " "
        return str(val)
    else:
        if esta_banderada:
            return "🚩"
        return "□"

def celda_deshabilitada(fila: int, col: int) -> bool:
    # Indica si una celda no debe aceptar clics (fin, victoria o ya revelada).
    b = st.session_state.tablero
    return (fila, col) in b.dug or st.session_state.fin or st.session_state.victoria

def inicializar_estado_si_falta(tam: int, minas: int, semilla: int | None):
    # Asegura que el estado inicial esté creado antes de pintar la UI.
    if "tablero" not in st.session_state:
        nuevo_juego(tam, minas, semilla)

# ----------------------------------------------------
# Barra lateral (controles)
st.sidebar.title("⚙️ Configuración")

# Tamaño (entero siempre)
tam = st.sidebar.number_input("Tamaño (N × N)", min_value=5, max_value=20, value=10, step=1, format="%d")
tam = int(tam)  # fuerza entero

# Máximo de minas dinámico según tam
max_minas = int(max(1, tam * tam - 1))

# Valor por defecto de minas respetando el máximo
prev_minas = st.session_state.get("minas", 10)
default_minas = int(min(prev_minas if isinstance(prev_minas, int) else 10, max_minas))

# Minas (sin mezclar tipos; todos int)
minas = st.sidebar.number_input("Minas", min_value=1, max_value=max_minas,
                                value=default_minas, step=1, format="%d")
minas = int(minas)  # fuerza entero

# Semilla (opcional)
semilla_txt = st.sidebar.text_input("Semilla (opcional)", value="")
semilla = None if semilla_txt.strip() == "" else int(abs(hash(semilla_txt)) % (2**32))

colA, colB = st.sidebar.columns(2)
with colA:
    if st.button("🆕 Nuevo juego"):
        nuevo_juego(tam, minas, semilla)
with colB:
    modo_bandera = st.toggle("🚩 Modo bandera", value=False)

# ----------------------------------------------------
# Inicialización de estado
inicializar_estado_si_falta(tam, minas, semilla)

# Si cambiaron controles, sugerir reinicio
if (st.session_state.tam != tam) or (st.session_state.minas != minas):
    st.info("Has cambiado la configuración. Pulsa **🆕 Nuevo juego** para aplicarla.")

# ----------------------------------------------------
# Encabezado principal
st.title("💣 Buscaminas")
st.caption("Clic = excavar | Activa **🚩 Modo bandera** para poner/quitar banderas.")

# ----------------------------------------------------
# Pintado de la cuadrícula (compacto)
b = st.session_state.tablero
for f in range(st.session_state.tam):
    cols = st.columns(st.session_state.tam, gap="small")
    for c in range(st.session_state.tam):
        etiqueta = etiqueta_celda(f, c)
        deshabilitar = celda_deshabilitada(f, c)

        def _al_hacer_clic(ff=f, cc=c):
            # Maneja el clic en una celda: excava o alterna bandera.
            if modo_bandera:
                alternar_bandera(ff, cc)
            else:
                excavar_celda(ff, cc)

        cols[c].button(
            etiqueta,
            key=f"celda-{f}-{c}",
            on_click=_al_hacer_clic,
            disabled=deshabilitar,
            use_container_width=True  # ocupa toda la columna
        )

# ----------------------------------------------------
# Estado del juego y panel inferior
st.divider()
if st.session_state.victoria:
    st.success("🎉 ¡Felicidades! ¡Ganaste!")
elif st.session_state.fin:
    st.error("💥 ¡Boom! Fin del juego.")
else:
    descubiertas = len(b.dug)
    seguras_totales = st.session_state.tam * st.session_state.tam - st.session_state.minas
    minas_restantes = max(0, st.session_state.minas - len(st.session_state.banderas))
    st.write(f"🔎 Celdas seguras descubiertas: **{descubiertas}/{seguras_totales}**")
    st.write(f"🚩 Minas marcadas / restantes estimadas: **{len(st.session_state.banderas)} / {minas_restantes}**")
