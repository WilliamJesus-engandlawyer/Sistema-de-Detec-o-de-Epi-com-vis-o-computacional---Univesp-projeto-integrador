import cv2
import os
import tempfile
import streamlit as st
from ultralytics import YOLO
import plotly.graph_objects as go

st.set_page_config(page_title="Execução - Detecção EPI", page_icon="⚙️", layout="wide")
st.title("⚙️ Execução do Sistema de Detecção de EPI")

# Upload apenas do vídeo
video_file = st.file_uploader("📂 Envie o vídeo", type=["mp4", "avi", "mov"])

# Caminho do modelo padrão
MODEL_PATH = os.path.join("models", "modelodedetecçãodecapacete.pt")

if st.button("▶️ Iniciar processo") and video_file:
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, video_file.name)

    # Salvar vídeo temporário
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    # Carregar modelo YOLO (fixo, já incluso no projeto)
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    output_path = os.path.join(temp_dir, "video_anotado.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    frame_id = 0
    total_com_epi = 0
    total_sem_epi = 0

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

        # Atualizar barra de progresso
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        progress.progress(min(frame_id / total_frames, 1.0))

    cap.release()
    out.release()

    # ==========================
    # 📊 Dashboard de resultados
    # ==========================
    total = total_com_epi + total_sem_epi
    pct_com = (total_com_epi / total * 100) if total > 0 else 0
    pct_sem = (total_sem_epi / total * 100) if total > 0 else 0

    col1, col2 = st.columns(2)

    # ====== 🍩 Donut ======
    with col1:
        fig_donut = go.Figure(data=[go.Pie(
            labels=["Com EPI", "Sem EPI"],
            values=[pct_com, pct_sem],
            hole=0.5,
            marker=dict(colors=["#4CAF50", "#F44336"])
        )])
        fig_donut.update_layout(
            title_text="Distribuição do Uso de EPI",
            title_x=0.5,
            showlegend=True
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ====== 🎯 Gauge ======
    with col2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct_com,
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
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ====== 📊 Barras ======
    st.subheader("Comparativo de Frames")
    fig_bar = go.Figure(data=[
        go.Bar(name='Com EPI', x=['Frames'], y=[total_com_epi], marker_color="#4CAF50"),
        go.Bar(name='Sem EPI', x=['Frames'], y=[total_sem_epi], marker_color="#F44336")
    ])
    fig_bar.update_layout(barmode='group', title="Frames Detectados", title_x=0.5)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Mostrar vídeo anotado
    st.success("✅ Processamento concluído!")
    st.video(output_path)
