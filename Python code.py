import cv2
import tkinter as tk
from tkinter import filedialog
from threading import Thread

class MotionDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Moving Element Detector")
        self.root.geometry("400x200")
        
        self.video_source = None
        self.cap = None
        self.running = False
        
        # Buttons
        tk.Button(root, text="Open Video File", command=self.open_file, width=20).pack(pady=10)
        tk.Button(root, text="Start Detection", command=self.start_detection, width=20).pack(pady=10)
        tk.Button(root, text="Stop Detection", command=self.stop_detection, width=20).pack(pady=10)
        
    def open_file(self):
        self.video_source = filedialog.askopenfilename(
            title="Select Video",
            filetypes=(("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*"))
        )
    
    def start_detection(self):
        if self.video_source:
            self.running = True
            self.cap = cv2.VideoCapture(self.video_source)
            Thread(target=self.detect_motion).start()
        else:
            print("Please select a video file first!")
    
    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def detect_motion(self):
        fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40, detectShadows=False)
        
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Resize for faster processing
            frame = cv2.resize(frame, (800, 600))
            
            # Apply background subtraction
            fgmask = fgbg.apply(frame)
            
            # Remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                if cv2.contourArea(cnt) > 500:  # Ignore small movements
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.imshow("Moving Element Detector", frame)
            
            if cv2.waitKey(30) & 0xFF == 27:  # ESC to exit
                break
        
        self.stop_detection()


# Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = MotionDetector(root)
    root.mainloop()
