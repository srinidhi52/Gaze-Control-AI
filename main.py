import cv2
import mediapipe as mp
import pyautogui
import keyboard
import speech_recognition as sr  # NEW: Voice AI!

pyautogui.PAUSE = 0 
pyautogui.FAILSAFE = True 

# Initialize the Voice Recognizer
recognizer = sr.Recognizer()

print("🚀 Firing up GazeControl AI V3.0...")
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cam.isOpened():
    print("🚨 ERROR: Cannot access the webcam.")
    exit()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
prev_x, prev_y = screen_w / 2, screen_h / 2 

print("\n" + "="*35)
print("🌟 GAZE-CONTROL PRO ACTIVATED 🌟")
print("🖱️  NOSE: Move head to move mouse")
print("👈  LEFT WINK: Click")
print("👉  RIGHT WINK: Voice Typing!")
print("😲  JAW-DROP: Scroll Down")
print("😁  SMILE: Scroll Up")
print("🛑  ESC KEY: Emergency Stop")
print("="*35 + "\n")

while True:
    if keyboard.is_pressed('esc'):
        print("🛑 ESC PRESSED! Quitting...")
        break

    success, frame = cam.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    window_h, window_w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    
    if output.multi_face_landmarks:
        face_landmarks = output.multi_face_landmarks[0]
        
        # --- 1. MOUSE MOVEMENT ---
        nose = face_landmarks.landmark[1]
        mult_x, mult_y = (nose.x - 0.2) / 0.6, (nose.y - 0.2) / 0.6
        target_x, target_y = mult_x * screen_w, mult_y * screen_h
        smooth_x = prev_x + (target_x - prev_x) * 0.25
        smooth_y = prev_y + (target_y - prev_y) * 0.25
        pyautogui.moveTo(smooth_x, smooth_y)
        prev_x, prev_y = smooth_x, smooth_y
        cv2.circle(frame, (int(nose.x * window_w), int(nose.y * window_h)), 5, (0, 255, 0), -1)
        
        # --- 2. LEFT WINK TO CLICK ---
        left_top, left_bottom = face_landmarks.landmark[159], face_landmarks.landmark[145]
        right_top, right_bottom = face_landmarks.landmark[386], face_landmarks.landmark[374]
        
        left_dist = left_bottom.y - left_top.y
        right_dist = right_bottom.y - right_top.y
        
        if left_dist < 0.015 and right_dist > 0.02: 
            print("🖱️ Left Wink: CLICK!")
            pyautogui.click()
            pyautogui.sleep(1)
            
        # --- 3. RIGHT WINK FOR VOICE TYPING ---
        if right_dist < 0.015 and left_dist > 0.02:
            print("\n🎙️ Right Wink detected! LISTENING... (Speak now!)")
            try:
                # Turn on the microphone
                with sr.Microphone() as source:
                    # Listen for up to 4 seconds
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)
                    print("🧠 Processing voice...")
                    # Translate voice to text
                    text = recognizer.recognize_google(audio)
                    print(f"✅ You said: '{text}'")
                    # Make the computer type it out!
                    pyautogui.write(text + " ") 
            except Exception as e:
                print("❌ Didn't catch that. Try again.")
            pyautogui.sleep(1) # Pause before starting again
            
        # --- 4. SCROLLING (Jaw-Drop & Smile) ---
        lip_top, lip_bottom = face_landmarks.landmark[13], face_landmarks.landmark[14]
        mouth_dist = lip_bottom.y - lip_top.y
        
        mouth_left, mouth_right = face_landmarks.landmark[61], face_landmarks.landmark[291]
        smile_dist = mouth_right.x - mouth_left.x
        
        # Open mouth (Jaw Drop) = Scroll Down
        if mouth_dist > 0.05: 
            print("📜 Jaw Drop: Scrolling Down!")
            pyautogui.scroll(-30) 
            
        # Wide smile = Scroll Up
        elif smile_dist > 0.12: # You might need to change 0.12 if it scrolls too easily!
            print("📜 Smile: Scrolling Up!")
            pyautogui.scroll(30) 

    cv2.imshow("GazeControl - AI Camera", frame)
    cv2.waitKey(1)

cam.release()
cv2.destroyAllWindows()