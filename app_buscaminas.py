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
/* === Área principal (grid): botones compactos === */
[data-testid="stAppViewContainer"] .stButton > button {
    padding: 0.05rem 0.1rem;
    height: 1.8rem;
    line-height: 1;
    min-height: 0; min-width: 0;
    width: 100%;
    border-radius: 4px;
}

/* === Sidebar: botones más grandes y legibles === */
.stButton > button {
  padding: 0.25rem 0.6rem;      /* padding: espacio interno entre borde y texto/icono; agranda el área donde dar clic sin cambiar la fuente. */
  height: 2.6rem;               /* height: altura total del botón; si es menor que el contenido, puede desbordar (salvo que intervenga min-height). */
  line-height: 1;               /* line-height: altura de cada línea; ayuda al centrado vertical del texto (igualarlo a height centra una sola línea). */
  min-height: 0;                /* min-height: altura mínima permitida; impide que el botón se haga más bajo que este valor. */
  min-width: 0;                 /* min-width: ancho mínimo; evita que el botón se estreche por debajo de ese umbral. */
  width: 50%;                  /* width: ancho del botón; 100% ocupa todo el contenedor, a 50% ocupa la mitad (quedará a la izquierda salvo margin:0 auto). */
  border-radius: 4px;           /* border-radius: radio de las esquinas; 4px da un redondeo suave (0 = cuadrado, mayor = más redondo). */
}

/* Gaps compactos en el grid principal */
[data-testid="stAppViewContainer"] div[data-testid="stHorizontalBlock"] { gap: 0.15rem !important; }
[data-testid="stAppViewContainer"] div[data-testid="stVerticalBlock"]   { gap: 0.15rem !important; }
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
