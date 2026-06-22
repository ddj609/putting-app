import streamlit as st
import os
import json
import numpy as np
import cv2

DB_FILE = "user_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Putting Dynamics | Bio-Mechanical Analysis", layout="wide")

db = load_db()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if not st.session_state["authenticated"]:
    st.title("⛳ Putting Dynamics | Bio-Mechanical Analysis")
    st.subheader("🔒 Access Portal: Please Log In or Register")
    
    tab1, tab2 = st.tabs(["Existing Client Login", "New Client Registration"])
    
    with tab1:
        login_email = st.text_input("Email Address", key="login_email_input")
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        if st.button("Log In", key="login_btn"):
            if login_email in db and db[login_email]["password"] == login_pass:
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = login_email
                st.rerun()
            else:
                st.error("Incorrect email address or password.")
                
    with tab2:
        reg_email = st.text_input("Email Address", key="reg_email_input")
        reg_pass = st.text_input("Password", type="password", key="reg_pass_input")
        if st.button("Create Account", key="reg_btn"):
            if reg_email in db:
                st.error("An account with this email already exists.")
            elif not reg_email or not reg_pass:
                st.error("Please fill in all fields.")
            else:
                db[reg_email] = {"password": reg_pass, "credits": 0}
                save_db(db)
                st.success("Account created! Please log in on the left tab.")
else:
    current_user = st.session_state["current_user"]
    
    # LOGOUT BUTTON
    if st.sidebar.button("🚪 Log Out"):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.rerun()
        
    # ROUTE TO ADMIN OR CUSTOMER
    if current_user == "admin@sportsanalytics.com":
        st.title("🛠️ Master Owner Administration Control Panel")
        st.subheader("Manage User Accounts and Analysis Credits")
        
        st.write("### Active Client Database")
        for user, data in list(db.items()):
            if user == "admin@sportsanalytics.com":
                continue
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(f"**User:** {user}")
            col2.write(f"**Credits:** {data['credits']}")
            
            if col3.button("➕ Add 5 Credits", key=f"add_{user}"):
                db[user]["credits"] += 5
                save_db(db)
                st.success(f"Added 5 credits to {user}")
                st.rerun()
                
            if col4.button("➖ Deduct 1 Credit", key=f"ded_{user}"):
                if db[user]["credits"] > 0:
                    db[user]["credits"] -= 1
                    save_db(db)
                    st.success(f"Deducted 1 credit from {user}")
                    st.rerun()
    else:
        st.sidebar.write(f"**Logged in as:** {current_user}")
        st.sidebar.write(f"**Available Analysis Credits:** {db[current_user]['credits']}")
        
        st.title("⛳ Putting Dynamics | Bio-Mechanical Analysis")
        st.write("Upload 4 camera angles simultaneously to generate a synchronized real-time vision tracking grid.")
        
        st.sidebar.header("📁 Step 1: Upload Video Files")
        file1 = st.sidebar.file_uploader("Upload Video 1", type=["mp4", "mov", "avi"])
        file2 = st.sidebar.file_uploader("Upload Video 2", type=["mp4", "mov", "avi"])
        file3 = st.sidebar.file_uploader("Upload Video 3", type=["mp4", "mov", "avi"])
        file4 = st.sidebar.file_uploader("Upload Video 4", type=["mp4", "mov", "avi"])
        
        if file1 and file2 and file3 and file4:
            if db[current_user]["credits"] <= 0:
                st.error("Insufficient credits. Please contact the administrator to purchase additional analysis runs.")
            else:
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
