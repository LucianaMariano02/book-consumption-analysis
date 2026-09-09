from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Estilo general limpio y profesional
sns.set_theme(style='whitegrid', font_scale=1.05)
PALETTE = {
    'Print-only': '#2b5c8f',
    'Hybrid': '#e26d5c',
    'Non-reader': '#8d99ae',
    'Digital/Audio-only': '#38b000',
}


def save_figure(fig, filename: str, output_dir: Path):
  """Exporta gráficos en alta resolución para el README de GitHub."""
  output_dir.mkdir(parents=True, exist_ok=True)
  filepath = output_dir / filename
  fig.savefig(filepath, dpi=300, bbox_inches='tight')
  print(f'Gráfico guardado en: {filepath}')


def plot_segments_distribution(df, output_dir: Path):
  """Gráfico de barras horizontales con el porcentaje por segmento."""
  counts = df['reader_segment'].value_counts(normalize=True).mul(100).round(1)

  fig, ax = plt.subplots(figsize=(8, 4))
  bars = ax.barh(counts.index, counts.values, color=[PALETTE.get(x, '#333') for x in counts.index])
  ax.set_title('Distribución de Segmentos de Lectores (% Población)', fontsize=13, weight='bold', pad=12)
  ax.set_xlabel('Porcentaje (%)')

  for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f'{w:.1f}%', va='center', weight='bold')

  ax.set_xlim(0, max(counts.values) + 10)
  sns.despine(top=True, right=True)
  save_figure(fig, 'reader_segments_distribution.png', output_dir)
  return fig


def plot_books_read_by_segment(df, output_dir: Path):
  """Boxplot comparativo de volumen de libros leídos anuales."""
  readers_only = df[df['reader_segment'] != 'Non-reader'].copy()

  fig, ax = plt.subplots(figsize=(9, 5))
  sns.boxplot(
      data=readers_only,
      x='reader_segment',
      y='books_read_count',
      palette=PALETTE,
      showfliers=False,  # Oculta outliers extremos para ver bien la mediana
      ax=ax,
  )
  ax.set_title('Volumen Anual de Lectura según Formato (Sin Atípicos)', fontsize=13, weight='bold', pad=12)
  ax.set_ylabel('Libros leídos (últimos 12 meses)')
  ax.set_xlabel('Segmento')
  sns.despine(top=True, right=True)
  save_figure(fig, 'books_read_by_segment.png', output_dir)
  return fig

def plot_age_vs_adoption(df, output_dir: Path):
  """KDE plot comparando la distribución de edad según adopción digital."""
  fig, ax = plt.subplots(figsize=(8, 4.5))
  sns.kdeplot(
      data=df[df['reader_segment'] != 'Non-reader'],
      x='age',
      hue='is_digital_adopter',
      common_norm=False,
      fill=True,
      palette={0: '#2b5c8f', 1: '#38b000'},
      alpha=0.3,
      ax=ax,
  )
  ax.set_title(
      'Distribución de Edad: Lectores Tradicionales vs. Adopción Digital',
      fontsize=13,
      weight='bold',
      pad=12,
  )
  ax.set_xlabel('Edad')
  ax.set_ylabel('Densidad')
  ax.legend(
      labels=['Digital / Híbrido', 'Solo Papel'],
      title='Tipo',
      frameon=True,
  )
  sns.despine(top=True, right=True)
  save_figure(fig, 'age_vs_digital_adoption.png', output_dir)
  return fig