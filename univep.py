import customtkinter as ctk
from tkinter import filedialog
import threading
from ultralytics import YOLO
import cv2
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from PIL import Image   # <-- FALTAVA ESSE IMPORT


# ========================= CONFIGURAÇÃO GLOBAL =========================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ========================= APP PRINCIPAL ===============================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🦺 Sistema de Detecção de EPI")
        self.geometry("1200x700")

        self.modelo_path = None
        self.video_path = None
        self.resultados = None
        self.video_saida = None

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tela_inicio = self.tabview.add("Início")
        self.tela_execucao = self.tabview.add("Execução")
        self.tela_resultados = self.tabview.add("Resultados")

        self.montar_tela_inicio()
        self.montar_tela_execucao()
        self.montar_tela_resultados()


    # ========================= TELA 1 - INÍCIO =========================

    def montar_tela_inicio(self):
        lbl1 = ctk.CTkLabel(
            self.tela_inicio,
            text="🦺 Sistema de Detecção Automática de EPI",
            font=("Arial", 32)
        )
        lbl1.pack(pady=20)

        texto = (
            "Bem-vindo ao sistema de detecção de capacetes utilizando Visão Computacional.\n\n"
            "Este aplicativo analisa vídeos com o modelo YOLO e identifica automaticamente\n"
            "funcionários com ou sem o Equipamento de Proteção Individual (EPI).\n\n"
            "Use as abas acima para navegar:\n"
            " • Execução — selecione modelo e vídeo e processe o arquivo\n"
            " • Resultados — visualize gráficos e gere o PDF"
        )

        lbl2 = ctk.CTkLabel(
            self.tela_inicio,
            text=texto,
            font=("Arial", 18),
            justify="center"
        )
        lbl2.pack(pady=20)


    # ========================= TELA 2 - EXECUÇÃO =========================

    def montar_tela_execucao(self):

        self.btn_modelo = ctk.CTkButton(
            self.tela_execucao,
            text="Selecionar Modelo YOLO (.pt)",
            command=self.selecionar_modelo
        )
        self.btn_modelo.pack(pady=20)

        self.btn_video = ctk.CTkButton(
            self.tela_execucao,
            text="Selecionar Vídeo",
            command=self.selecionar_video
        )
        self.btn_video.pack(pady=20)

        self.btn_iniciar = ctk.CTkButton(
            self.tela_execucao,
            text="Iniciar Detecção",
            command=self.thread_iniciar
        )
        self.btn_iniciar.pack(pady=30)

        self.progress = ctk.CTkProgressBar(self.tela_execucao, width=600)
        self.progress.set(0)
        self.progress.pack(pady=20)

        self.lbl_status = ctk.CTkLabel(self.tela_execucao, text="", font=("Arial", 18))
        self.lbl_status.pack(pady=20)


    def selecionar_modelo(self):
        self.modelo_path = filedialog.askopenfilename(filetypes=[("YOLO Model", "*.pt")])
        if self.modelo_path:
            self.lbl_status.configure(text=f"Modelo selecionado:\n{self.modelo_path}")


    def selecionar_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov")]
        )
        if self.video_path:
            self.lbl_status.configure(text=f"Vídeo selecionado:\n{self.video_path}")


    def thread_iniciar(self):
        threading.Thread(target=self.iniciar_processamento).start()


    def iniciar_processamento(self):

        # --- CORRIGIDO: identação quebrada ---
        if not self.modelo_path or not self.video_path:
            self.lbl_status.configure(text="Selecione modelo e vídeo!")
            return

        self.lbl_status.configure(text="Carregando modelo YOLO...")
        model = YOLO(self.modelo_path)

        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24

        output_path = "video_anotado.mp4"
        self.video_saida = output_path

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        frame_id = 0
        com_epi = 0
        sem_epi = 0

        self.lbl_status.configure(text="Processando vídeo...")

        preview = ctk.CTkLabel(self.tela_execucao, text="")
        preview.pack(pady=10)

        # ========================= LOOP DO VÍDEO =========================
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)[0]
            capacete_detectado = False

            for box in results.boxes:
                cls = int(box.cls[0])
                label = results.names[cls].lower()

                if not any(k in label for k in ["person", "pessoa", "helmet", "capacete", "hardhat"]):
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                is_capacete = any(w in label for w in ["capacete", "helmet", "hardhat"])

                if is_capacete:
                    capacete_detectado = True
                    color = (0, 255, 0)
                    texto = "COM EPI"
                else:
                    color = (0, 0, 255)
                    texto = "SEM EPI"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, texto, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            if capacete_detectado:
                com_epi += 1
            else:
                sem_epi += 1

            cv2.putText(
                frame,
                f"Frame {frame_id+1}/{total_frames}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            out.write(frame)
            frame_id += 1

            self.progress.set(frame_id / total_frames)

            # --- Mini Preview ---
            preview_frame = cv2.resize(frame, (400, 220))
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)

            img = ctk.CTkImage(
                light_image=Image.fromarray(preview_frame),
                dark_image=Image.fromarray(preview_frame),
                size=(400, 220)
            )
            preview.configure(image=img)
            preview.image = img

        cap.release()
        out.release()
        preview.destroy()

        total = com_epi + sem_epi
        pct_com = com_epi / total * 100 if total else 0
        pct_sem = sem_epi / total * 100 if total else 0

        self.resultados = {
            "com": com_epi,
            "sem": sem_epi,
            "pct_com": pct_com,
            "pct_sem": pct_sem,
        }

        self.lbl_status.configure(text="Processamento concluído!")
        self.tabview.set("Resultados")
        self.atualizar_tela_resultados()


    # ========================= TELA 3 - RESULTADOS =========================

    def montar_tela_resultados(self):

        self.frame_graficos = ctk.CTkFrame(self.tela_resultados)
        self.frame_graficos.pack(pady=20)

        self.lbl_stats = ctk.CTkLabel(self.tela_resultados, text="", font=("Arial", 18))
        self.lbl_stats.pack(pady=20)

        self.btn_pdf = ctk.CTkButton(
            self.tela_resultados,
            text="Gerar PDF do Relatório",
            command=self.gerar_pdf
        )
        self.btn_pdf.pack(pady=10)

        self.btn_video_save = ctk.CTkButton(
            self.tela_resultados,
            text="Salvar Vídeo Anotado",
            command=self.salvar_video
        )
        self.btn_video_save.pack(pady=10)


    def atualizar_tela_resultados(self):

        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        if not self.resultados:
            return

        self.lbl_stats.configure(
            text=(f"Frames com EPI: {self.resultados['com']}\n"
                  f"Frames sem EPI: {self.resultados['sem']}\n"
                  f"Conformidade: {self.resultados['pct_com']:.2f}%")
        )

        fig, ax = plt.subplots(1, 3, figsize=(12, 4))

        ax[0].pie(
            [self.resultados['pct_com'], self.resultados['pct_sem']],
            labels=["Com EPI", "Sem EPI"],
            autopct="%1.1f%%"
        )
        ax[0].set_title("Distribuição")

        ax[1].bar(["Com EPI", "Sem EPI"], [self.resultados['com'], self.resultados['sem']])
        ax[1].set_title("Contagem de Frames")

        ax[2].bar(["Conformidade"], [self.resultados['pct_com']])
        ax[2].set_ylim(0, 100)
        ax[2].set_title("Conformidade (%)")

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack()


    # ========================= PDF =========================

    def gerar_pdf(self):
        nome = f"relatorio_epi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = pdf_canvas.Canvas(nome, pagesize=A4)

        c.setFont("Helvetica", 16)
        c.drawString(50, 800, "Relatório de Detecção de EPI")

        c.setFont("Helvetica", 12)
        c.drawString(50, 770, f"Frames com EPI: {self.resultados['com']}")
        c.drawString(50, 750, f"Frames sem EPI: {self.resultados['sem']}")
        c.drawString(50, 730, f"Conformidade: {self.resultados['pct_com']:.2f}%")

        c.save()

        self.lbl_stats.configure(text="PDF gerado!")


    # ========================= SALVAR VÍDEO =========================

    def salvar_video(self):
        if not self.video_saida:
            return

        destino = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if destino:
            os.rename(self.video_saida, destino)
            self.lbl_stats.configure(text="Vídeo salvo com sucesso!")


# ========================= INICIAR PROGRAMA ===============================

app = App()
app.mainloop()
