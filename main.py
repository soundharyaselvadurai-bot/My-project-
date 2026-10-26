from machine import Pin, PWM, I2C
import time
import ssd1306

# -------------------------
# PIN CONNECTIONS
# -------------------------
SOS_BUTTON = 18
LED_PIN = 2
BUZZER_PIN = 4

# OLED
SDA_PIN = 21
SCL_PIN = 22

# -------------------------
# COMPONENT SETUP
# -------------------------
button = Pin(SOS_BUTTON, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT)

# Passive buzzer using PWM
buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty_u16(0)

# OLED
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# -------------------------
# SIMULATED GPS
# -------------------------
LATITUDE = "13.0827"
LONGITUDE = "80.2707"

# -------------------------
# SYSTEM READY
# -------------------------
def ready_screen():
    oled.fill(0)
    oled.text("BRIDGEBOX", 20, 8)
    oled.text("SYSTEM READY", 8, 28)
    oled.text("Press SOS", 22, 48)
    oled.show()

# -------------------------
# SOS ALERT
# -------------------------
def sos_alert():

    # OLED
    oled.fill(0)
    oled.text("SOS ALERT!", 15, 0)
    oled.text("RISK: HIGH", 20, 14)
    oled.text("RED ZONE", 25, 26)
    oled.text("LAT:" + LATITUDE, 2, 42)
    oled.text("LON:" + LONGITUDE, 2, 54)
    oled.show()

    # LED ON
    led.value(1)

    # BUZZER ON
    buzzer.freq(1000)
    buzzer.duty_u16(32768)

    # Sound for 3 seconds
    time.sleep(3)

    # BUZZER OFF
    buzzer.duty_u16(0)

# -------------------------
# START
# -------------------------
led.value(0)
buzzer.duty_u16(0)

ready_screen()

# -------------------------
# MAIN LOOP
# -------------------------
while True:

    if button.value() == 0:
        sos_alert()

        # Wait until button is released
        while button.value() == 0:
            time.sleep(0.05)

        time.sleep(1)
        ready_screen()

    time.sleep(0.1)