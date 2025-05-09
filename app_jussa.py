import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Atualização de Catálogo de Livros")

# Upload dos arquivos
catalogo_file = st.file_uploader("Upload do Catálogo Novo (CSV)", type="csv")
base_file = st.file_uploader("Upload da Base Atual (CSV)", type="csv")

if catalogo_file and base_file:
    # Leitura dos CSVs
    df_catalogo_novo = pd.read_csv(catalogo_file)
    df_base = pd.read_csv(base_file)

    # Padronização de ISBNs
    df_catalogo_novo['isbn'] = df_catalogo_novo['isbn'].astype(str).str.strip().str.replace('-', '')
    df_base['isbn'] = df_base['isbn'].astype(str).str.strip().str.replace('-', '')

    # MERGE para comparação de preços
    df_comparado = pd.merge(
        df_catalogo_novo, df_base,
        on='isbn', how='inner',
        suffixes=('_novo', '_base')
    )

    # Diferenças de preço
    df_preco_diferente = df_comparado[df_comparado['precio_novo'] != df_comparado['precio_base']][['isbn', 'precio_novo']]

    # Fora de estoque
    df_fora_de_estoque = df_base[~df_base['isbn'].isin(df_catalogo_novo['isbn'])]

    # Novos lançamentos
    df_novos_lancamentos = df_catalogo_novo[~df_catalogo_novo['isbn'].isin(df_base['isbn'])]

    # Atualizando a base
    isbn_remover = set(df_fora_de_estoque['isbn']) | set(df_preco_diferente['isbn'])
    df_base_filtrada = df_base[~df_base['isbn'].isin(isbn_remover)]
    df_precos_atualizados = df_catalogo_novo[df_catalogo_novo['isbn'].isin(df_preco_diferente['isbn'])]

    df_base_atualizado = pd.concat([
        df_base_filtrada,
        df_precos_atualizados,
        df_novos_lancamentos
    ], ignore_index=True)

    # Exibição
    st.subheader("Diferenças de Preço")
    st.dataframe(df_preco_diferente)

    st.subheader("Itens Fora de Estoque")
    st.dataframe(df_fora_de_estoque)

    st.subheader("Novos Lançamentos")
    st.dataframe(df_novos_lancamentos)

    st.subheader("Base Atualizada")
    st.dataframe(df_base_atualizado)

    # Download helper
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    st.download_button("Baixar Base Atualizada", convert_df(df_base_atualizado), "base_atualizada.csv", "text/csv")
    st.download_button("Baixar Diferenças de Preço", convert_df(df_preco_diferente), "precos_diferentes.csv", "text/csv")
    st.download_button("Baixar Fora de Estoque", convert_df(df_fora_de_estoque), "fora_de_estoque.csv", "text/csv")
    st.download_button("Baixar Novos Lançamentos", convert_df(df_novos_lancamentos), "novos_lancamentos.csv", "text/csv")
