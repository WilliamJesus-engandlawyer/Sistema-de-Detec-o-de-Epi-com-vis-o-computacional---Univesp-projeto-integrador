import os
import cv2
import io
import tempfile
import plotly.graph_objects as go
import streamlit as st
from ultralytics import YOLO
from datetime import datetime

# ===== PDF (ReportLab) =====
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ====== CONFIG BÁSICA ======
st.set_page_config(page_title="Execução - Detecção EPI", page_icon="⚙️", layout="wide")
st.title("⚙️ Execução do Sistema de Detecção de EPI")

# --- Flags de estado (reset após download) ---
if st.session_state.get("reset_after_download", False):
    # Limpa tudo e reinicia a app
    st.session_state.clear()
    st.rerun()

# ====== UPLOAD ======
video_file = st.file_uploader("📂 Envie o vídeo", type=["mp4", "avi", "mov", "mpeg4"])

# Caminho do modelo padrão
MODEL_PATH = os.path.join("models", "modelodedetecçãodecapacete.pt")

def criar_figuras(res):
    # Donut
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Com EPI", "Sem EPI"],
        values=[res["pct_com"], res["pct_sem"]],
        hole=0.5,
        marker=dict(colors=["#4CAF50", "#F44336"])
    )])
    fig_donut.update_layout(title_text="Distribuição do Uso de EPI", title_x=0.5, showlegend=True)

    # Gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=res["pct_com"],
        title={'text': "Conformidade EPI (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4CAF50"},
            'steps': [
                {'range': [0, 50], 'color': "#F44336"},
                {'range': [50, 80], 'color': "#FFEB3B"},
                {'range': [80, 100], 'color': "#4CAF50"}
            ]
        }
    ))

    # Barras
    fig_bar = go.Figure(data=[
        go.Bar(name='Com EPI', x=['Frames'], y=[res["total_com_epi"]], marker_color="#4CAF50"),
        go.Bar(name='Sem EPI', x=['Frames'], y=[res["total_sem_epi"]], marker_color="#F44336")
    ])
    fig_bar.update_layout(barmode='group', title="Frames Detectados", title_x=0.5)
    return fig_donut, fig_gauge, fig_bar

def gerar_pdf(res, figs):
    """
    Gera PDF do dashboard + dados.
    Tenta exportar figuras Plotly como PNG (exige kaleido). Se não houver, salva somente os dados.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    margem = 36

    # Cabeçalho
    c.setTitle("Relatório de Detecção de EPI")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem, H - margem, "Relatório de Detecção de EPI")
    c.setFont("Helvetica", 10)
    c.drawString(margem, H - margem - 16, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Dados principais
    c.setFont("Helvetica", 12)
    y = H - 90
    c.drawString(margem, y, f"Frames com EPI: {res['total_com_epi']}")
    y -= 16
    c.drawString(margem, y, f"Frames sem EPI: {res['total_sem_epi']}")
    y -= 16
    c.drawString(margem, y, f"Conformidade: {res['pct_com']:.2f}%")
    y -= 16
    c.drawString(margem, y, f"Não conformidade: {res['pct_sem']:.2f}%")
    y -= 24

    # Tenta inserir gráficos
    inserted_any_image = False
    try:
        # to_image precisa do pacote 'kaleido'
        for fig in figs:
            png_bytes = fig.to_image(format="png", scale=2)
            img = ImageReader(io.BytesIO(png_bytes))

            # Proporção para caber na página
            iw, ih = img.getSize()
            disp_w = W - 2 * margem
            disp_h = disp_w * (ih / iw)
            if y - disp_h < margem:
                c.showPage()
                y = H - margem

            c.drawImage(img, margem, y - disp_h, width=disp_w, height=disp_h, preserveAspectRatio=True, mask='auto')
            y -= (disp_h + 16)
            inserted_any_image = True
    except Exception:
        # Kaleido ausente ou erro — segue sem gráficos
        pass

    if not inserted_any_image:
        c.setFillColorRGB(0.8, 0.2, 0.2)
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(margem, y, "Atenção: gráficos não incluídos. Para exportá-los, instale o pacote 'kaleido'.")
        c.setFillColorRGB(0, 0, 0)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ========================= PROCESSAMENTO =========================
if st.button("▶️ Iniciar processo") and video_file:
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, video_file.name)

    # Salvar vídeo temporário
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    # Carregar modelo YOLO (fixo no projeto)
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 24  # fallback

    output_path = os.path.join(temp_dir, "video_anotado.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    frame_id = 0
    total_com_epi = 0
    total_sem_epi = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    progress = st.progress(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        capacete_detectado = False

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_idx = int(box.cls[0])
                objeto_nome = result.names[class_idx]

                if "capacete" in objeto_nome.lower() or "helmet" in objeto_nome.lower():
                    capacete_detectado = True

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, objeto_nome, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        if capacete_detectado:
            total_com_epi += 1
        else:
            total_sem_epi += 1

        out.write(frame)
        frame_id += 1
        progress.progress(min(frame_id / total_frames, 1.0))

    cap.release()
    out.release()

    # ---- Guardar resultados no estado ----
    total = total_com_epi + total_sem_epi
    pct_com = (total_com_epi / total * 100) if total > 0 else 0.0
    pct_sem = (total_sem_epi / total * 100) if total > 0 else 0.0

    st.session_state["resultados"] = {
        "total_com_epi": total_com_epi,
        "total_sem_epi": total_sem_epi,
        "pct_com": pct_com,
        "pct_sem": pct_sem,
        "output_path": output_path
    }

# ========================= DASHBOARD / AÇÕES =========================
if "resultados" in st.session_state:
    res = st.session_state["resultados"]
    fig_donut, fig_gauge, fig_bar = criar_figuras(res)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_donut, use_container_width=True)
    with col2:
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader("Comparativo de Frames")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.success("✅ Processamento concluído!")

    # ===== Aviso + opção de salvar PDF =====
    st.warning("⚠️ Ao clicar em **Baixar vídeo anotado**, o processo será reiniciado. "
               "Se desejar, **salve o dashboard e os dados em PDF** antes de baixar.")

    if st.button("📄 Salvar dashboard + dados em PDF", key="btn_pdf", use_container_width=False):
        pdf_buffer = gerar_pdf(res, (fig_donut, fig_gauge, fig_bar))
        st.download_button(
            label="⬇️ Baixar PDF do relatório",
            data=pdf_buffer,
            file_name=f"relatorio_epi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            key="download_pdf_btn"
        )

    # ===== Download do vídeo (reinicia após download) =====
    with open(res["output_path"], "rb") as f:
        clicked = st.download_button(
            label="🎬 Baixar vídeo anotado",
            data=f,
            file_name="video_anotado.mp4",
            mime="video/mp4",
            key="download_video_btn"
        )
        if clicked:
            # Marca para resetar no próximo rerun (que o próprio download provoca)
            st.session_state["reset_after_download"] = True
