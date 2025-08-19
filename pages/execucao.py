import cv2
import os
import tempfile
import streamlit as st
from ultralytics import YOLO
import matplotlib.pyplot as plt

st.set_page_config(page_title="Execução - Detecção EPI", page_icon="⚙️", layout="wide")
st.title("⚙️ Execução do Sistema de Detecção de EPI")

# Upload dos arquivos
modelo_file = st.file_uploader("📂 Envie o modelo YOLO (.pt)", type=["pt"])
video_file = st.file_uploader("📂 Envie o vídeo", type=["mp4", "avi", "mov"])

# Só roda se os arquivos existirem e o botão for pressionado
if modelo_file and video_file:
    if st.button("▶️ Iniciar processo"):
        temp_dir = tempfile.mkdtemp()
        model_path = os.path.join(temp_dir, modelo_file.name)
        video_path = os.path.join(temp_dir, video_file.name)

        with open(model_path, "wb") as f:
            f.write(modelo_file.read())
        with open(video_path, "wb") as f:
            f.write(video_file.read())

        # Carregar modelo YOLO
        model = YOLO(model_path)

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
        with col1:
            st.metric("✅ Frames com EPI", f"{pct_com:.1f}%")
        with col2:
            st.metric("❌ Frames sem EPI", f"{pct_sem:.1f}%")

        # Gráfico de pizza
        fig, ax = plt.subplots()
        ax.pie([pct_com, pct_sem],
               labels=["Com EPI", "Sem EPI"],
               autopct='%1.1f%%',
               colors=["#4CAF50", "#F44336"])
        ax.set_title("Distribuição do Uso de EPI nos Frames")
        st.pyplot(fig)

        # Mostrar vídeo anotado
        st.success("✅ Processamento concluído!")
        st.video(output_path)
