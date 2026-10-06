import pandas as pd
import streamlit as st

# Configuración visual de la página web
st.set_page_config(
    page_title="Simulador de Puntajes Ponderados UNAB",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 Simulador de Puntajes Ponderados UNAB")
st.markdown(
    "Selecciona tu carrera y calcula tu ponderación oficial considerando de"
    " forma inteligente la **prueba electiva (Historia o Ciencias)**."
)


# Cargar los datos desde el Excel oficial
@st.cache_data
def cargar_datos():
  file_path = "Maestra ID carreras y vías 202710_25AGO.xlsx"
  df = pd.read_excel(file_path, sheet_name="PONDERACIONES")
  df["CARRERA_SEDE"] = (
      df["CARRERA"].str.strip()
      + " - "
      + df["SEDE"].str.strip()
      + " ("
      + df["RÉGIMEN"].str.strip()
      + ")"
  )
  return df


try:
  df_pond = cargar_datos()

  # 1. Menú desplegable de selección
  carrera_seleccionada = st.selectbox(
      "Selecciona tu Carrera, Sede y Régimen:",
      df_pond["CARRERA_SEDE"].unique(),
  )

  fila = df_pond[df_pond["CARRERA_SEDE"] == carrera_seleccionada].iloc[0]

  # Ficha técnica informativa
  st.info(
      f"**Facultad:** {fila['Facultad']} | **Modalidad:**"
      f" {fila['Modalidad']} | **DEMRE:** {fila['DEMRE']}"
  )

  st.subheader("Ingresa tus Puntajes PAES y Notas")
  col1, col2 = st.columns(2)

  with col1:
    nem = st.number_input("Puntaje NEM", 150, 1000, 650)
    rkn = st.number_input("Puntaje Ranking", 150, 1000, 700)
    lem = st.number_input("Comprensión Lectora (LEM)", 150, 1000, 600)
    mat1 = st.number_input("Matemática 1 (MAT1)", 150, 1000, 600)

  with col2:
    mat2 = st.number_input("Matemática 2 (MAT2)", 150, 1000, 550)
    historia = st.number_input("Puntaje Historia", 150, 1000, 600)
    ciencias = st.number_input("Puntaje Ciencias", 150, 1000, 680)

  # 2. Extracción de ponderaciones oficiales
  w_nem = float(fila["NEM"]) if pd.notnull(fila["NEM"]) else 0.0
  w_rkn = float(fila["RKN"]) if pd.notnull(fila["RKN"]) else 0.0
  w_lem = float(fila["LEM "]) if pd.notnull(fila["LEM "]) else 0.0
  w_mat1 = float(fila["MAT1"]) if pd.notnull(fila["MAT1"]) else 0.0
  w_mat2 = (
      float(fila["MAT2"])
      if pd.notnull(fila["MAT2"]) and fila["MAT2"] != "-"
      else 0.0
  )

  w_his = (
      float(fila["HIS"])
      if pd.notnull(fila["HIS"]) and fila["HIS"] != "-"
      else 0.0
  )
  w_cien = (
      float(fila["CIEN"])
      if pd.notnull(fila["CIEN"]) and fila["CIEN"] != "-"
      else 0.0
  )

  # 3. Lógica inteligente de la Electiva (Historia o Ciencias)
  peso_electiva = max(w_his, w_cien)
  if w_his >= w_cien and w_his > 0:
    puntaje_electiva = historia
    nombre_electiva = "Historia"
  elif w_cien > w_his and w_cien > 0:
    puntaje_electiva = ciencias
    nombre_electiva = "Ciencias"
  else:
    puntaje_electiva = 0
    nombre_electiva = "Ninguna"

  # 4. Cálculo de subtotales
  sub_nem = nem * w_nem
  sub_rkn = rkn * w_rkn
  sub_lem = lem * w_lem
  sub_mat1 = mat1 * w_mat1
  sub_mat2 = mat2 * w_mat2
  sub_elec = puntaje_electiva * peso_electiva

  total_ponderado = (
      sub_nem + sub_rkn + sub_lem + sub_mat1 + sub_mat2 + sub_elec
  )

  # 5. Visualización de Resultados en Tarjetas KPI
  st.divider()
  col_res1, col_res2, col_res3 = st.columns(3)
  col_res1.metric("Puntaje Ponderado Final", f"{total_ponderado:.2f}")
  col_res2.metric(
      "Corte Histórico 2026", f"{fila['PSU CORTE 2026'] or 'N/D'}"
  )
  col_res3.metric("Electiva Considerada", nombre_electiva)

  # Tabla de desglose detallado
  st.subheader("Desglose del Cálculo")
  df_desglose = pd.DataFrame({
      "Factor": [
          "NEM",
          "Ranking",
          "Comp. Lectora",
          "Matemática 1",
          "Matemática 2",
          f"Electiva ({nombre_electiva})",
      ],
      "Ponderación": [
          f"{w_nem*100:.0f}%",
          f"{w_rkn*100:.0f}%",
          f"{w_lem*100:.0f}%",
          f"{w_mat1*100:.0f}%",
          f"{w_mat2*100:.0f}%",
          f"{peso_electiva*100:.0f}%",
      ],
      "Puntaje Ingresado": [nem, rkn, lem, mat1, mat2, puntaje_electiva],
      "Subtotal": [
          f"{sub_nem:.2f}",
          f"{sub_rkn:.2f}",
          f"{sub_lem:.2f}",
          f"{sub_mat1:.2f}",
          f"{sub_mat2:.2f}",
          f"{sub_elec:.2f}",
      ],
  })
  st.table(df_desglose)

except Exception as e:
  st.error(f"Error al cargar los datos: {e}")