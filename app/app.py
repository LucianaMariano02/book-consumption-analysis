from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title='Dashboard Hábitos de Lectura',
    page_icon='📚',
    layout='wide',
)

# Carga de datos procesados
DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / 'data'
    / 'processed'
    / 'reading_habits_cleaned.csv'
)


@st.cache_data
def load_data():
  return pd.read_csv(DATA_PATH)


df = load_data()

# Encabezado
st.title('📚 Análisis de Consumo de Libros: Papel vs. Digital')
st.markdown(
    'Explora los hábitos de lectura y la adopción de formatos digitales '
    'según variables demográficas.'
)

# Sidebar: Filtros interactivos
st.sidebar.header('Filtros')

edad_min = int(df['age'].min())
edad_max = int(df['age'].max())
rango_edad = st.sidebar.slider(
    'Rango de edad:',
    min_value=edad_min,
    max_value=edad_max,
    value=(edad_min, edad_max),
)

educacion_opciones = ['Todos'] + sorted(df['education'].dropna().unique().tolist())
educacion_seleccionada = st.sidebar.selectbox(
    'Nivel educativo:', educacion_opciones
)

# Aplicar filtros
df_filtrado = df[
    (df['age'] >= rango_edad[0]) & (df['age'] <= rango_edad[1])
]

if educacion_seleccionada != 'Todos':
  df_filtrado = df_filtrado[df_filtrado['education'] == educacion_seleccionada]

# Métricas principales (KPIs)
col1, col2, col3, col4 = st.columns(4)
total_resp = len(df_filtrado)
pct_digital = (
    (df_filtrado['is_digital_adopter'].mean() * 100) if total_resp > 0 else 0
)
mediana_libros = (
    df_filtrado[df_filtrado['reader_segment'] != 'Non-reader'][
        'books_read_count'
    ].median()
    if total_resp > 0
    else 0
)
pct_papel_puro = (
    (
        (df_filtrado['reader_segment'] == 'Print-only').sum()
        / total_resp
        * 100
    )
    if total_resp > 0
    else 0
)

col1.metric('Muestra filtrada', f'{total_resp:,}')
col2.metric('Adopción digital', f'{pct_digital:.1f}%')
col3.metric('Solo papel', f'{pct_papel_puro:.1f}%')
col4.metric('Mediana libros/año (lectores)', f'{mediana_libros:.0f}')

st.divider()

# Gráficos interactivos
fila1_col1, fila1_col2 = st.columns(2)

with fila1_col1:
  st.subheader('Distribución por Segmento de Lector')
  conteo_segmentos = (
      df_filtrado['reader_segment']
      .value_counts(normalize=True)
      .mul(100)
      .reset_index()
  )
  conteo_segmentos.columns = ['Segmento', 'Porcentaje']

  fig_segmentos = px.bar(
      conteo_segmentos,
      x='Porcentaje',
      y='Segmento',
      orientation='h',
      color='Segmento',
      text=conteo_segmentos['Porcentaje'].apply(lambda x: f'{x:.1f}%'),
      color_discrete_map={
          'Print-only': '#2b5c8f',
          'Hybrid': '#e26d5c',
          'Non-reader': '#8d99ae',
          'Digital/Audio-only': '#38b000',
      },
  )
  fig_segmentos.update_layout(showlegend=False, xaxis_title='Porcentaje (%)')
  st.plotly_chart(fig_segmentos, use_container_width=True)

with fila1_col2:
  st.subheader('Volumen de Libros por Segmento')
  df_lectores = df_filtrado[
      (df_filtrado['reader_segment'] != 'Non-reader')
      & (df_filtrado['books_read_count'] <= 50)  # Filtro visual de outliers
  ]

  fig_box = px.box(
      df_lectores,
      x='reader_segment',
      y='books_read_count',
      color='reader_segment',
      labels={
          'reader_segment': 'Segmento',
          'books_read_count': 'Libros leídos (año)',
      },
      color_discrete_map={
          'Print-only': '#2b5c8f',
          'Hybrid': '#e26d5c',
          'Digital/Audio-only': '#38b000',
      },
  )
  fig_box.update_layout(showlegend=False)
  st.plotly_chart(fig_box, use_container_width=True)

# Tabla exploratoria rápida
with st.expander('Ver datos en crudo (primeras 50 filas)'):
  st.dataframe(
      df_filtrado[
          [
              'age',
              'sex',
              'education',
              'income',
              'books_read_count',
              'reader_segment',
          ]
      ].head(50)
  )