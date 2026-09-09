from pathlib import Path
import pandas as pd


def load_raw_data(filepath: str | Path) -> pd.DataFrame:
  """Carga el dataset crudo de encuestas de lectura."""
  return pd.read_csv(filepath)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
  """Renombra columnas hacia un formato estándar técnico en snake_case."""
  column_mapping = {
      'Age': 'age',
      'Sex': 'sex',
      'Race': 'race',
      'Marital status?': 'marital_status',
      'Education': 'education',
      'Employement': 'employment',
      'Incomes': 'income',
      'How many books did you read during last 12months?': 'books_read_count',
      'Read any printed books during last 12months?': 'read_print_raw',
      'Read any audiobooks during last 12months?': 'read_audio_raw',
      'Read any e-books during last 12months?': 'read_ebook_raw',
      'Last book you read, you…': 'last_book_source',
      'Do you happen to read any daily news or newspapers?': 'read_news',
      'Do you happen to read any magazines or journals?': 'read_magazines',
  }
  return df.rename(columns=column_mapping)


def handle_missing_and_binarize(df: pd.DataFrame) -> pd.DataFrame:
  """Convierte respuestas de formato a variables binarias 0/1,

  tratando NaN (no lectores) y 'Don’t know' como 0.
  """
  df = df.copy()
  format_cols = {
      'read_print_raw': 'read_print',
      'read_audio_raw': 'read_audio',
      'read_ebook_raw': 'read_ebook',
  }

  for raw_col, new_col in format_cols.items():
    df[new_col] = (df[raw_col] == 'Yes').astype(int)

  # Imputar categoría a la fuente del último libro para no lectores
  df['last_book_source'] = df['last_book_source'].fillna('Did not read/None')
  df['education'] = df['education'].fillna('Not specified')

  return df


def create_reader_segments(df: pd.DataFrame) -> pd.DataFrame:
  """Segmenta a los encuestados según su modalidad y volumen de lectura."""
  df = df.copy()

  def assign_segment(row):
    if row['books_read_count'] == 0:
      return 'Non-reader'
    reads_print = row['read_print'] == 1
    reads_digital = (row['read_ebook'] == 1) or (row['read_audio'] == 1)

    if reads_print and reads_digital:
      return 'Hybrid'
    elif reads_print and not reads_digital:
      return 'Print-only'
    elif not reads_print and reads_digital:
      return 'Digital/Audio-only'
    else:
      return 'Non-reader'

  df['reader_segment'] = df.apply(assign_segment, axis=1)

  # Indicador binario de adopción de cualquier medio digital
  df['is_digital_adopter'] = (
      (df['read_ebook'] == 1) | (df['read_audio'] == 1)
  ).astype(int)

  return df


def clean_reading_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
  """Pipeline completo: carga, limpia, transforma y exporta a processed/."""
  df = load_raw_data(input_path)
  df = standardize_columns(df)
  df = handle_missing_and_binarize(df)
  df = create_reader_segments(df)

  # Guardar salida
  Path(output_path).parent.mkdir(parents=True, exist_ok=True)
  df.to_csv(output_path, index=False)
  return df