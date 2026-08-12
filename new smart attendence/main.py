"""
SMART ATTENDANCE SYSTEM WITH RFID (MFRC522)
SDG 4: Quality Education
ESP32 | MicroPython | Wokwi Simulator
4 Students: Aisyah, Balqis, Danish, Farah
"""

from machine import Pin, SoftI2C, PWM
import time

# IMPORT LIBRARIES (nama file mesti TEPAT)
from mfrc522 import MFRC522
from ssd1306 import SSD1306_I2C

# ============================================
# COMPONENT INITIALIZATION
# ============================================

# OLED Display (SSD1306) - I2C Connection
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 64, i2c)

# LEDs
green_led = Pin(13, Pin.OUT)   # Green LED - On Time attendance
red_led = Pin(12, Pin.OUT)     # Red LED - Error / Duplicate
blue_led = Pin(14, Pin.OUT)    # Blue LED - Late entry

# Buzzer (PWM for sound)
buzzer = PWM(Pin(15), freq=1000, duty=0)

# ============================================
# RFID MFRC522 INITIALIZATION (SPI)
# ============================================
# Pin connections:
# SDA  = GPIO5
# SCK  = GPIO18
# MOSI = GPIO23
# MISO = GPIO19
# RST  = GPIO21

sda = Pin(5, Pin.OUT)
sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.IN)
rst = Pin(21, Pin.OUT)

rfid = MFRC522(sck=sck, mosi=mosi, miso=miso, rst=rst, cs=sda)

# ============================================
# STUDENT DATABASE (4 STUDENTS)
# Mapping UID dari RFID card ke nama pelajar
# ============================================

# Di Wokwi, preset cards:
# Blue Card   : UID = 0x01 0x02 0x03 0x04  -> "01020304"
# Green Card  : UID = 0x11 0x22 0x33 0x44  -> "11223344"
# Yellow Card : UID = 0x55 0x66 0x77 0x88  -> "55667788"
# Red Card    : UID = 0xAA 0xBB 0xCC 0xDD  -> "aabbccdd"

students = {
    "01020304": {"name": "Aisyah", "status": None, "scan_time": None},
    "11223344": {"name": "Balqis", "status": None, "scan_time": None},
    "55667788": {"name": "Danish", "status": None, "scan_time": None},
    "aabbccdd": {"name": "Farah", "status": None, "scan_time": None},
}

TOTAL_STUDENTS = 4

# ============================================
# BUZZER FUNCTIONS
# ============================================

def buzzer_beep(duration_ms, frequency=1000):
    """Generate a beep sound"""
    buzzer.freq(frequency)
    buzzer.duty(512)
    time.sleep_ms(duration_ms)
    buzzer.duty(0)

def success_beep():
    """Short beep for on-time attendance"""
    buzzer_beep(150, 1500)

def late_beep():
    """Double beep for late entry"""
    buzzer_beep(100, 1000)
    time.sleep_ms(100)
    buzzer_beep(100, 1000)

def error_beep():
    """Long beep for error/invalid"""
    buzzer_beep(500, 500)

def session_start_beep():
    """Alert sound when session begins"""
    buzzer_beep(200, 2000)
    buzzer_beep(200, 2000)

def session_end_beep():
    """Triple beep when session ends"""
    buzzer_beep(300, 800)
    buzzer_beep(300, 800)
    buzzer_beep(300, 800)

# ============================================
# OLED DISPLAY FUNCTIONS
# ============================================

def clear_oled():
    """Clear the OLED screen"""
    oled.fill(0)
    oled.show()

def show_text_line(line1="", line2="", line3="", line4=""):
    """Display 4 lines of text on OLED"""
    clear_oled()
    if line1:
        oled.text(line1, 0, 0)
    if line2:
        oled.text(line2, 0, 16)
    if line3:
        oled.text(line3, 0, 32)
    if line4:
        oled.text(line4, 0, 48)
    oled.show()

def show_live_status(remaining_time):
    """Display live attendance status on OLED"""
    clear_oled()
    
    # Line 1: Remaining time
    oled.text(f"Time Left: {remaining_time}s", 0, 0)
    oled.text("--- STUDENT STATUS ---", 0, 12)
    
    # Lines 2-5: Student list with status
    y_pos = 24
    for student_id, data in students.items():
        if data["status"] == "On Time":
            status_text = "OT"
        elif data["status"] == "Late":
            status_text = "L"
        else:
            status_text = "-"
        
        # Shorten name to 6 characters max
        name = data['name'][:6]
        oled.text(f"{name}: {status_text}", 0, y_pos)
        y_pos += 10
    
    # Bottom line: instruction
    oled.text("Tap RFID card", 0, 55)
    oled.show()

def show_final_report():
    """Display final attendance report on OLED"""
    # Count statistics
    on_time_count = 0
    late_count = 0
    absent_count = 0
    
    for student_id, data in students.items():
        if data["status"] == "On Time":
            on_time_count += 1
        elif data["status"] == "Late":
            late_count += 1
        elif data["status"] is None:
            absent_count += 1
    
    present_count = on_time_count + late_count
    attendance_percentage = (present_count / TOTAL_STUDENTS) * 100
    
    # Report Page 1: Summary
    show_text_line(
        "=== FINAL REPORT ===",
        f"On Time: {on_time_count}",
        f"Late   : {late_count}",
        f"Absent : {absent_count}"
    )
    time.sleep(3)
    
    # Report Page 2: Percentage
    show_text_line(
        "ATTENDANCE SUMMARY",
        f"Present: {present_count}/{TOTAL_STUDENTS}",
        f"Percentage: {int(attendance_percentage)}%",
        "Session Ended"
    )
    time.sleep(3)

# ============================================
# RFID FUNCTIONS
# ============================================

def uid_to_string(uid):
    """Convert UID list to string"""
    uid_str = ""
    for byte in uid:
        uid_str += format(byte, '02x')
    return uid_str

def read_rfid():
    """Read RFID card and return UID as string"""
    try:
        # Check if card is present
        (status, tag_type) = rfid.request(rfid.REQIDL)
        if status == rfid.OK:
            # Get UID
            (status, uid) = rfid.anticoll()
            if status == rfid.OK:
                # Select card
                rfid.select_tag(uid)
                uid_string = uid_to_string(uid)
                return uid_string
    except Exception as e:
        pass
    return None

# ============================================
# ATTENDANCE PROCESSING FUNCTION
# ============================================

def process_attendance(student_uid, current_time):
    """Process a student's attendance scan"""
    
    # Check if UID exists in database
    if student_uid not in students:
        show_text_line("INVALID CARD!", "Card not registered", "Please use assigned card", "")
        red_led.value(1)
        error_beep()
        time.sleep(1.5)
        red_led.value(0)
        return False
    
    student = students[student_uid]
    
    # Check if student already scanned
    if student["status"] is not None:
        show_text_line("ALREADY SCANNED!", f"{student['name']} already marked", f"Status: {student['status']}", "")
        red_led.value(1)
        error_beep()
        time.sleep(1.5)
        red_led.value(0)
        return False
    
    # Determine status based on time
    if current_time <= 20:
        status = "On Time"
        green_led.value(1)
        success_beep()
        time.sleep(0.5)
        green_led.value(0)
    else:
        status = "Late"
        blue_led.value(1)
        late_beep()
        time.sleep(0.5)
        blue_led.value(0)
    
    # Save student data
    student["status"] = status
    student["scan_time"] = current_time
    
    # Display feedback
    if status == "On Time":
        msg = "On Time!"
    else:
        msg = "Late Entry!"
    
    show_text_line(
        f"WELCOME {student['name']}!",
        f"{msg}",
        f"Time: {current_time}s",
        ""
    )
    time.sleep(2)
    
    return True

# ============================================
# MAIN PROGRAM
# ============================================

def main():
    session_duration = 60   # 60 seconds attendance session
    start_time = time.time()
    session_active = True
    
    # Opening screen
    show_text_line(
        "SMART ATTENDANCE",
        "SYSTEM WITH RFID",
        "SDG 4: Quality Education",
        "4 Students Registered"
    )
    time.sleep(2)
    
    # Instructions screen
    show_text_line(
        "Session: 60 seconds",
        "On Time: 0-20s",
        "Late: 21-60s",
        "Tap RFID card"
    )
    time.sleep(2)
    
    session_start_beep()
    
    # Main attendance loop
    while session_active:
        current_elapsed = int(time.time() - start_time)
        remaining = session_duration - current_elapsed
        
        # End session if time runs out
        if remaining <= 0:
            session_active = False
            break
        
        # Display live status on OLED
        show_live_status(remaining)
        
        # Check for RFID card
        uid = read_rfid()
        if uid:
            process_attendance(uid, current_elapsed)
            time.sleep(0.5)  # Prevent multiple reads
        
        # Check if all 4 students have scanned
        all_scanned = all(data["status"] is not None for data in students.values())
        if all_scanned:
            show_text_line("ALL STUDENTS PRESENT!", "Ending session early...", "", "")
            time.sleep(2)
            session_active = False
            break
        
        time.sleep(0.1)
    
    # Session ended
    session_end_beep()
    
    # Display final report
    show_final_report()
    
    # Keep final display on screen forever
    while True:
        on_time = sum(1 for d in students.values() if d["status"] == "On Time")
        late = sum(1 for d in students.values() if d["status"] == "Late")
        absent = sum(1 for d in students.values() if d["status"] is None)
        
        clear_oled()
        oled.text("=== FINAL REPORT ===", 0, 0)
        oled.text(f"On Time: {on_time}", 0, 16)
        oled.text(f"Late   : {late}", 0, 28)
        oled.text(f"Absent : {absent}", 0, 40)
        oled.text("Session Ended", 0, 52)
        oled.show()
        
        time.sleep(1)

# ============================================
# RUN THE PROGRAM
# ============================================

if __name__ == "__main__":
    main()