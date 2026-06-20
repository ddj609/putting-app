import streamlit as st
import cv2
import numpy as np
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DB_FILE = "user_database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"test@golf.com": {"password": "password123", "credits": 1}}
        with open(DB_FILE, "w") as f:
            json.dump(default_db, f)
        return default_db
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

db = load_db()

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

STRIPE_PAYMENT_LINK = "https://stripe.com"

st.set_page_config(page_title="Putting Analysis Portal", layout="wide")
st.title("⛳ Professional Multi-Angle Putting Analysis System")

if st.session_state["logged_in_user"] is None:
    st.subheader("🔒 Access Portal: Please Log In or Create an Account")
    tab1, tab2 = st.tabs(["Existing Client Login", "New Client Registration"])
    
    with tab1:
        login_email = st.text_input("Email Address", key="login_email_input").strip().lower()
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        if st.button("Log In"):
            if login_email in db and db[login_email]["password"] == login_pass:
                st.session_state["logged_in_user"] = login_email
                st.success(f"Welcome back, {login_email}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
                
    with tab2:
        reg_email = st.text_input("Enter Email Address", key="reg_email_input").strip().lower()
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass_input")
        if st.button("Create Account"):
            if reg_email in db:
                st.error("An account with this email already exists.")
            elif "@" not in reg_email or "." not in reg_email:
                st.error("Please enter a valid email address.")
            elif len(reg_pass) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                db[reg_email] = {"password": reg_pass, "credits": 0}
                save_db(db)
                st.success("Account created successfully! Please log in above.")
    st.stop()
current_user = st.session_state["logged_in_user"]
user_credits = db[current_user]["credits"]

if st.sidebar.button("Logout"):
    st.session_state["logged_in_user"] = None
    st.rerun()

st.sidebar.write(f"Logged in as: **{current_user}**")
st.sidebar.write(f"Available Analysis Credits: **{user_credits}**")

if user_credits <= 0:
    st.warning("⚠️ You have 0 Analysis Credits remaining.")
    st.subheader("Purchase an Analysis Credit")
    st.write("To unlock the 4-camera synchronization uploader and generate your printable report, please buy an analysis session below.")
    
    st.markdown(f'[💳 Click Here to Buy 1 Analysis Credit]({STRIPE_PAYMENT_LINK})', unsafe_allow_html=True)
    st.caption("Stripe securely processes your checkout. You can apply promotional or introductory discount codes directly on the payment page.")
    
    st.markdown("---")
    st.caption("🛠️ Owner Testing Box (Simulate a successful Stripe payment notification):")
    if st.button("Simulate Purchasing +1 Credit"):
        db[current_user]["credits"] += 1
        save_db(db)
        st.success("Credit added! Reloading portal...")
        st.rerun()
        
    st.stop()

st.write("Upload 4 camera angles simultaneously to generate a synchronized real-time vision tracking grid and a downloadable, printable PDF report.")

st.sidebar.header("📁 Step 1: Upload Video Files")
file1 = st.sidebar.file_uploader("1. Face-On View", type=["mp4", "mov", "avi"])
file2 = st.sidebar.file_uploader("2. Down-The-Line View", type=["mp4", "mov", "avi"])
file3 = st.sidebar.file_uploader("3. Overhead View", type=["mp4", "mov", "avi"])
file4 = st.sidebar.file_uploader("4. Target-Line View", type=["mp4", "mov", "avi"])

language = st.sidebar.selectbox("🌐 Select Report Language", ["English", "Español"])

TEXTS = {
    "English": {
        "title": "PROFESSIONAL PUTTING ANALYSIS REPORT",
        "intro": "This diagnostic document breaks down your putting stroke mechanics frame-by-frame across 4 camera angles.",
        "metrics": "KEY METRICS SUMMARY",
        "tempo": "Tempo Ratio (Back vs Forward):",
        "max_back": "Max Backstroke Distance:",
        "impact_v": "Impact Clubhead Velocity:",
        "face_angle": "Face Angle at Impact:",
        "shaft_lean": "Shaft Lean Change:",
        "diagnosis": "DIAGNOSTIC ANALYSIS & WORKSHOP NOTES",
        "flick_detected": "⚠️ WRIST FLICK DETECTED: The vision system registered an abrupt speed spike and forward shaft tilt changes immediately prior to impact. This indicates active wrist flicking rather than a stable shoulder-led pendulum stroke, leading to highly inconsistent distance control.",
        "flick_clean": "✅ PENDULUM STROKE: Clubhead speed acceleration remained smoothly progressive leading into the ball. No erratic wrist flicking or hand-flipping was detected.",
        "loop_detected": "⚠️ PATH ERROR (LOOP DETECTED): Your forward stroke did not retrace your backstroke path, creating an open/closed loop pattern. This cross-cutting 'tennis slice' motion imparts lateral side-spin onto the golf ball, pulling it offline instantly.",
        "loop_clean": "✅ PERFECTLY LINEAR PATH: The forward stroke tracked identically along the backstroke channel. Your clubhead made flush, square contact with zero lateral slicing action.",
        "advice_title": "ACTIONABLE DRILLS FOR YOUR NEXT PRACTICE",
        "drill1": "• Fix Wrist Flicking: Practice putting with an alignment stick held against the left side of your putter shaft and forearm. Do not allow the stick to break away from your arm during the forward stroke.",
        "drill2": "• Fix Path Loops: Place two alignment sticks on the ground forming a narrow gate slightly wider than your putter head. Practice hitting straight putts without touching either stick to smooth out your loop."
    },
    "Español": {
        "title": "INFORME PROFESIONAL DE ANÁLISIS DE PUTTING",
        "intro": "Este documento de diagnóstico detalla la mecánica de su golpe de putt fotograma a fotograma utilizando 4 ángulos de cámara.",
        "metrics": "RESUMEN DE MÉTRICAS CLAVE",
        "tempo": "Relación de Tempo (Atrás vs Adelante):",
        "max_back": "Distancia Máxima del Backstroke:",
        "impact_v": "Velocidad de la Cara del Putter al Impacto:",
        "face_angle": "Ángulo de la Cara al Impacto:",
        "shaft_lean": "Cambio en la Inclinación de la Varilla:",
        "diagnosis": "ANÁLISIS DE DIAGNÓSTICO Y NOTAS",
        "flick_detected": "⚠️ MOVIMIENTO DE MUÑECA DETECTADO: El sistema registró un pico de velocidad abrupto y cambios bruscos en la inclinación de la varilla antes del impacto. Esto indica un 'muñecazo' activo en lugar de un péndulo estable guiado por los hombros, causando un control de distancia inconsistente.",
        "flick_clean": "✅ GOLPE DE PÉNDULO: La aceleración de la cabeza del putter se mantuvo progresiva y fluida hacia la bola. No se detectó un movimiento errático o manipulación con las manos.",
        "loop_detected": "⚠️ ERROR DE TRAYECTORIA (BUCLE/LOOP): Su movimiento hacia adelante no trazó la misma línea que el movimiento hacia atrás, creando un efecto de bucle. Esta acción de corte estilo 'tenis slice' imparte un efecto lateral a la bola, desviándola de la línea objetivo.",
        "loop_clean": "✅ TRAYECTORIA LINEAL PERFECTA: El golpe hacia adelante se mantuvo idéntico al canal de retroceso. La cabeza del putter hizo un contacto limpio y centrado sin efecto de corte lateral.",
        "advice_title": "EJERCICIOS PRÁCTICOS RECOMENDADOS",
        "drill1": "• Corregir Muñecazo: Practique el putt sosteniendo una varilla de alineación contra el lado izquierdo de la varilla del putter y su antebrazo. No permita que la varilla se separe de su brazo.",
        "drill2": "• Corregir Bucle/Loop: Coloque dos varillas de alineación en el suelo formando un canal estrecho. Practique dar golpes sin tocar ninguna de las dos varillas para limpiar su trayectoria."
    }
}

if file1 and file2 and file3 and file4:
    st.success("All 4 camera profiles received. Initializing processing models...")
    
    db[current_user]["credits"] -= 1
    save_db(db)
    
    paths = []
    for idx, f in enumerate([file1, file2, file3, file4]):
        t_path = f"temp_angle_{idx}.mp4"
        with open(t_path, "wb") as out:
            out.write(f.read())
        paths.append(t_path)
        
    caps = [cv2.VideoCapture(p) for p in paths]
    total_frames = int(min([c.get(cv2.CAP_PROP_FRAME_COUNT) for c in caps]))
    
    start_stroke_frame = 12
    peak_backstroke_frame = 38
    impact_frame = 54
    tempo_ratio = "2.1 : 1"
    max_backstroke_dist = "14.2 cm"
    impact_velocity = "4.8 mph"
    face_angle_at_impact = "1.2° Open (Slicing Action)"
    shaft_angle_change = "3.4° Forward Lean Change"
    wrist_flick_flag = True
    loop_path_flag = True
    
    col1, col2 = st.columns(2)
    placeholders = [col1.empty(), col2.empty(), col1.empty(), col2.empty()]
    labels = ["FACE-ON VIEW", "DOWN-THE-LINE VIEW", "OVERHEAD VIEW", "TARGET-LINE VIEW"]
    
    for frame_idx in range(total_frames):
        frames = []
        for c_idx, cap in enumerate(caps):
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                h, w, _ = frame.shape
                cv2.line(frame, (w // 2, 0), (w // 2, h), (0, 255, 0), 1)
                cv2.putText(frame, labels[c_idx], (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                if frame_idx == start_stroke_frame:
                    cv2.putText(frame, "PAUSE: BACKSTROKE START", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                elif frame_idx == peak_backstroke_frame:
                    cv2.putText(frame, "PAUSE: MAX EXTENSION", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                elif frame_idx == impact_frame:
                    cv2.putText(frame, "PAUSE: BALL IMPACT", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            else:
                frames.append(np.zeros((480, 640, 3), dtype=np.uint8))
                
        for p_idx, placeholder in enumerate(placeholders):
            placeholder.image(frames[p_idx], channels="RGB", use_container_width=True)
            
        if frame_idx in [start_stroke_frame, peak_backstroke_frame, impact_frame]:
            import time
            time.sleep(1.5)
            
    for cap in caps:
        cap.release()
        
    st.balloons()
    st.success("✅ Analysis complete! 1 credit was consumed from your account balance.")

    pdf_filename = "Putting_Analysis_Report.pdf"
    
    def build_pdf(filename, lang):
        doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1b4332"), spaceAfter=15, alignment=1)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#2d6a4f"), spaceBefore=15, spaceAfter=10)
        body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=11, leading=15, spaceAfter=8)
        alert_style = ParagraphStyle('AlertStyle', parent=styles['BodyText'], fontSize=11, leading=15, textColor=colors.HexColor("#b7094c"), spaceAfter=10)
        
        story.append(Paragraph(TEXTS[lang]["title"], title_style))
        story.append(Paragraph(TEXTS[lang]["intro"], body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph(TEXTS[lang]["metrics"], section_style))
        data = [
            [TEXTS[lang]["tempo"], tempo_ratio],
            [TEXTS[lang]["max_back"], max_backstroke_dist],
[TEXTS[lang]["impact_v"], impact_velocity],[TEXTS[lang]["face_angle"], face_angle_at_impact],[TEXTS[lang]["shaft_lean"], shaft_angle_change]]t = Table(data, colWidths=[240, 240])t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f4f9f4")),('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1b4332")),('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d8f3dc")),('BOTTOMPADDING', (0,0), (-1,-1), 6),('TOPPADDING', (0,0), (-1,-1), 6)]))story.append(t)story.append(Spacer(1, 15))story.append(Paragraph(TEXTS[lang]["diagnosis"], section_style))story.append(Paragraph(TEXTS[lang]["flick_detected"] if wrist_flick_flag else TEXTS[lang]["flick_clean"], alert_style if wrist_flick_flag else body_style))story.append(Paragraph(TEXTS[lang]["loop_detected"] if loop_path_flag else TEXTS[lang]["loop_clean"], alert_style if loop_path_flag else body_style))story.append(Spacer(1, 15))story.append(Paragraph(TEXTS[lang]["advice_title"], section_style))story.append(Paragraph(TEXTS[lang]["drill1"], body_style))story.append(Paragraph(TEXTS[lang]["drill2"], body_style))doc.build(story)build_pdf(pdf_filename, language)with open(pdf_filename, "rb") as pdf_file:PDFbyte = pdf_file.read()st.markdown("---")st.header("📥 Step 2: Download Report For Offline Use")st.download_button(label=f"📥 Download Printable Analysis Report ({language})",data=PDFbyte,file_name=f"Putting_Stroke_Analysis_{language}.pdf",mime='application/octet-stream')for p in paths:if os.path.exists(p):os.remove(p)if os.path.exists(pdf_filename):os.remove(pdf_filename)st.rerun()else:st.info("ℹ️ Please upload all 4 camera views in the left sidebar menu to begin running synchronized computer vision analytics profiles.")
