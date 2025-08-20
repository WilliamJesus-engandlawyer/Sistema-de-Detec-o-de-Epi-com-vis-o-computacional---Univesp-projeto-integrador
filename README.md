
---

# 🦺 Sistema de Detecção de EPI com Visão Computacional

**Projeto Integrador - Univesp**

Este projeto tem como objetivo aplicar **Visão Computacional** e **Aprendizado de Máquina** para a detecção automática do uso de **Equipamentos de Proteção Individual (EPI)**, com foco em **capacetes de segurança**.

A aplicação foi desenvolvida como parte do tema:

> *"Desenvolver análise de dados em escala utilizando algum conjunto de dados existentes e aprendizagem de máquina. Preparar uma interface para visualização dos resultados."*

---

## 📌 Funcionalidades

* ✅ Detecção de uso de **capacetes de segurança (EPI)** em vídeos
* ✅ Processamento automatizado utilizando **YOLO (You Only Look Once)**
* ✅ Geração de vídeo anotado com as detecções
* ✅ Dashboard interativo com:

  * Gráfico de **pizza (distribuição de EPI)**
  * Gráfico **gauge (nível de conformidade)**
  * Gráfico de **barras comparativas**
* ✅ Download direto do vídeo processado

---

## 🚀 Tecnologias Utilizadas

* [Python](https://www.python.org/)
* [Streamlit](https://streamlit.io/) (interface web)
* [OpenCV](https://opencv.org/) (processamento de vídeo)
* [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (modelo de detecção)
* [Plotly](https://plotly.com/python/) (dashboards interativos)

---

## 🖥️ Como Executar o Projeto

1. Clone este repositório:

   ```bash
   git clone https://github.com/SeuUsuario/Sistema-de-Detec-o-de-Epi-com-vis-o-computacional---Univesp-projeto-integrador
   cd Sistema-de-Detec-o-de-Epi-com-vis-o-computacional---Univesp-projeto-integrador
   ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Inicie a aplicação:

   ```bash
   streamlit run main.py
   ```

---

## 📂 Estrutura do Projeto

```
├── main.py               # Página inicial (apresentação do projeto)
├── execucao.py           # Lógica de execução, detecção e dashboards
├── models/
│   └── modelodedetecçãodecapacete.pt  # Modelo YOLO treinado
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação
```

---

## 🎯 Como Usar

1. Na página inicial, clique na aba **Execução** no menu lateral.
2. Faça upload de um **vídeo** (formatos suportados: mp4, avi, mov).
3. Clique em **Iniciar processo** e aguarde a análise.
4. Visualize os resultados nos gráficos.
5. Baixe o vídeo anotado diretamente pela interface.

---

## 📊 Exemplo de Dashboard

* **Pizza:** proporção de frames com/sem capacete
* **Gauge:** nível de conformidade em %
* **Barras:** comparação de frames detectados

---

## 👨‍💻 Autor

**William Jesus da Silva**

**Izabel Da Silva Freitas Gomes**

**Arthur Mello**


* Projeto Integrador - Univesp
* Engenharia da Computação

---

