import streamlit as st

st.set_page_config(page_title="Detecção de EPI", page_icon="🦺", layout="centered")

st.title("🦺 Sistema de Detecção de Capacetes (EPI)")
st.subheader("Segurança do Trabalho com Visão Computacional")

st.write("""
Bem-vindo ao sistema de **detecção automática de uso de capacetes**!  
Este programa utiliza **Inteligência Artificial (YOLO)** para analisar vídeos
e verificar se os funcionários estão utilizando **Equipamentos de Proteção Individual (EPI)**.

### 📌 Por que isso é importante?
- Aumenta a **segurança no ambiente de trabalho**  
- Reduz riscos de **acidentes e multas trabalhistas**  
- Auxilia no **monitoramento em tempo real** do uso correto de EPIs  

### 🚀 Como usar?
1. Vá até a aba **Execução** no menu lateral.  
2. Envie o **modelo YOLO (.pt)** e um **vídeo**.  
3. Aguarde o processamento.  
4. Baixe o vídeo anotado e o relatório CSV com os registros de funcionários sem EPI.  
""")

st.success("Pronto para começar? Clique na aba 'Execução' no menu lateral!")
