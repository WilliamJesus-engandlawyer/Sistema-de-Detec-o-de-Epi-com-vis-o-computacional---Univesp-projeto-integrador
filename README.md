

---

# 🦺 Sistema de Detecção de EPI com Visão Computacional

### **Projeto Integrador – UNIVESP | Engenharia da Computação**

Este projeto utiliza **Visão Computacional** e **Machine Learning** para detectar automaticamente o uso de **Equipamentos de Proteção Individual (EPI)** — com foco em **capacetes de segurança** — em vídeos.
A aplicação teve sua primeira versão de teste no streamlit, um frame work simples que nos ofereceu um suporte bacana para tester a ideia, depois...
A aplicação foi reconstruída em **Python + CustomTkinter**, oferecendo uma interface desktop completa, processamento local com **YOLO**, geração de gráficos e criação automática de relatório **PDF**.

---

## 📌 Funcionalidades

✔️ Detecção automática de **capacete de segurança (EPI)** em vídeos
✔️ Processamento usando **YOLO (Ultralytics)**
✔️ Geração de **vídeo anotado** com caixas e classificações
✔️ Dashboard integrado com:

* Gráfico **pizza** (com/sem EPI)
* Gráfico de **barras comparativas**
* Gráfico de **conformidade (%)**

✔️ **Geração de relatório PDF**
✔️ **Salvar vídeo anotado** no final
✔️ Barra de progresso + preview em tempo real
✔️ Interface moderna construída com **CustomTkinter**

---

## 🚀 Tecnologias Utilizadas

* **Python**
* **CustomTkinter** (Interface gráfica)
* **OpenCV** (processamento de vídeo)
* **Ultralytics YOLO**
* **Matplotlib** (gráficos)
* **ReportLab** (geração de PDF)

---

## 🖥️ Como Executar o Projeto

1. **Clone o repositório:**

```bash
git clone https://github.com/SeuUsuario/Sistema-de-Deteccao-EPI-Visao-Computacional
cd Sistema-de-Deteccao-EPI-Visao-Computacional
```

2. **Crie e ative o ambiente virtual (opcional, recomendado):**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute a aplicação:**

```bash
python app.py
```

---

## 📂 Estrutura do Projeto

```
├── app.py                         # Interface completa com CustomTkinter
├── README.md                      # Documentação
├── requirements.txt               # Dependências
└── models/
    └── modelo_yolo.pt             # Modelo YOLO treinado (adicione aqui)
```

---

## 🎯 Como Usar

1. Abra o programa (`python app.py`)
2. Vá até a aba **Execução**
3. Selecione:

   * um **modelo YOLO (.pt)**
   * um **vídeo** para análise
4. Clique em **Iniciar Detecção**
5. Aguarde o processamento:

   * Preview ao vivo
   * Barra de progresso
6. Veja os resultados na aba **Resultados**
7. Gere um **PDF** do relatório
8. Salve o **vídeo anotado**

---

## 📊 Gráficos Gerados

* **Pizza:** distribuição entre frames com EPI e sem EPI
* **Barras:** comparação total de detecções
* **Conformidade (%):** indica aderência ao uso de capacete

---

## 📝 Relatório PDF

O PDF inclui:

* Total de frames com EPI
* Total de frames sem EPI
* Conformidade percentual
* Data e identificação do processamento

---

## 👨‍💻 Autores

**William Jesus da Silva**
**Izabel da Silva Freitas Gomes**
**Arthur Mello**

Projeto Integrador — UNIVESP
Engenharia da Computação

---


