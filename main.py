import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página do painel
st.set_page_config(page_title="Painel Control PIX", page_icon="💰", layout="wide")

# Inicializa o histórico na memória
if "historico_pix" not in st.session_state:
    st.session_state.historico_pix = []

st.title("💰 Monitor de PIX em Tempo Real")
st.subheader("Itaú & Sicredi Integrados")
st.write("---")

# --- LEITURA DOS DADOS DO CELULAR ---
query_params = st.query_params

# O celular vai enviar o texto bruto da notificação para cá
if "texto_notificacao" in query_params and "banco" in query_params:
    banco = query_params.get("banco") # 'itau' ou 'sicredi'
    texto = query_params.get("texto_notificacao")
    
    valor = "0,00"
    nome = "Desconhecido"
    
    # Tratamento do texto do Itaú (Ex: "Pix recebido: R$ 50,00 de Joao")
    if banco.lower() == "itau" and "recebido:" in texto:
        try:
            partes = texto.split("R$ ")[1]
            valor = partes.split(" de ")[0]
            nome = partes.split(" de ")[1]
        except:
            nome = texto
            
    # Tratamento do texto do Sicredi (Ex: "Voce recebeu um Pix de R$ 50,00 de Joao")
    elif banco.lower() == "sicredi" and "R$" in texto:
        try:
            partes = texto.split("R$ ")[1]
            valor = partes.split(" de ")[0]
            nome = partes.split(" de ")[1]
        except:
            nome = texto
    
    # Registro estruturado
    novo_pix = {
        "Horário": datetime.now().strftime("%H:%M:%S"),
        "Banco": banco.upper(),
        "Cliente": nome.strip(),
        "Valor": f"R$ {valor.strip()}",
        "Status": "🔴 Aguardando Liberação"
    }
    
    # Evita duplicados ao atualizar a página
    if not st.session_state.historico_pix or st.session_state.historico_pix[0]["Cliente"] != nome.strip():
        st.session_state.historico_pix.insert(0, novo_pix)
        st.toast(f"🎉 PIX de {nome} recebido no {banco.upper()}!", icon="✅")

# --- INTERFACE DOS VENDEDORES ---
if st.session_state.historico_pix:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="ÚLTIMO PIX", value=st.session_state.historico_pix[0]["Valor"], delta=st.session_state.historico_pix[0]["Cliente"])
    with col2:
        st.metric(label="TOTAL RECEBIDO HOJE", value=len(st.session_state.historico_pix))
else:
    st.info("Aguardando vendas...")

st.write("### 📋 Painel de Liberação Comercial")

if st.session_state.historico_pix:
    for idx, row in enumerate(st.session_state.historico_pix):
        col_hora, col_banco, col_nome, col_val, col_status, col_acao = st.columns([1, 1, 3, 1.5, 2, 2])
        
        col_hora.write(f"⏱️ {row['Horário']}")
        if row['Banco'] == 'ITAU':
            col_banco.markdown("🟠 **ITAU**")
        else:
            col_banco.markdown("🟢 **SICREDI**")
            
        col_nome.write(f"👤 {row['Cliente']}")
        col_val.write(f"💵 {row['Valor']}")
        col_status.write(row['Status'])
        
        if "Aguardando" in row['Status']:
            if col_acao.button("Liberar", key=f"btn_{idx}"):
                st.session_state.historico_pix[idx]["Status"] = "🟢 LIBERADO"
                st.rerun()
else:
    st.write("Nenhum PIX na lista.")
