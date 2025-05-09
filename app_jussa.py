import streamlit as st
import pandas as pd
from io import BytesIO

# Função para converter DataFrame para Excel em memória
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Planilha')
    processed_data = output.getvalue()
    return processed_data

st.title("Atualização de Catálogo de Livros")

# Upload dos arquivos
catalogo_file = st.file_uploader("Upload do Catálogo Novo (CSV)", type="csv")
base_file = st.file_uploader("Upload da Base Atual (CSV)", type="csv")

if catalogo_file and base_file:
    if catalogo_file.name == base_file.name:
        st.error("Os arquivos enviados são idênticos. Por favor, envie arquivos diferentes para comparação.")
    else:
    # Leitura dos CSVs
        df_catalogo_novo = pd.read_csv(catalogo_file, sep=";")
        df_base = pd.read_csv(base_file, sep=";")
    
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
    
        df_simplificado = df_base_atualizado[["titulo", "precio", "isbn"]]
    
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
    
       # Botões de download para arquivos Excel
        st.download_button(
        "📥 Baixar Base Atualizada (Excel)",
        convert_df_to_excel(df_base_atualizado),
        "base_atualizada.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        st.download_button(
        "📥 Baixar Base Atualizada Simplificada (Excel)",
        convert_df_to_excel(df_simplificado),
        "base_atualizada_simplificada.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        st.download_button(
        "📥 Baixar Diferenças de Preço (Excel)",
        convert_df_to_excel(df_preco_diferente),
        "precos_diferentes.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        st.download_button(
        "📥 Baixar Fora de Estoque (Excel)",
        convert_df_to_excel(df_fora_de_estoque),
        "fora_de_estoque.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        st.download_button(
        "📥 Baixar Novos Lançamentos (Excel)",
        convert_df_to_excel(df_novos_lancamentos),
        "novos_lancamentos.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
