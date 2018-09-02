import serial
import enum
import json

# Input values are documented in the protocol documentation at http://www.viewsonicglobal.com/public/products_download/97/Commercial_Displays_RS232.pdf?pass
class Input(enum.Enum):
  HDMI1 = "004"
  HDMI2 = "014"
  HDMI3 = "024"
  VGA = "006"
  TV = "000"
  AV = "001"
  SVIDEO = "002"
  Unknown = None

# Send a command that sets a setting. The response should be either 401+ or 401-
def send(command, value):
  ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=3)
  # byte 1 is how many bytes in command - always 8, excluding newline
  # bytes 2-3 are the TV ID
  # byte 4 is the command type - always s for set
  # byte 5 is the command
  # byte 6-8 , which is a code and 3 value bytes
  # byte 9 is CR
  
  ser.write("801s" + command + value + "\x0D")
  r = ser.read(4)
  ser.close()

  if(r == "401+"):
    return "Success"
  elif(r == "401-"):
    return "Invalid"
  else:
    return "Failed"

# Get the current value for a setting. The response is in a similar format to what you would send to set that setting
def get(command):
  ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=3)
  
  ser.write("801g" + command + "\x30\x30\x30\x0D")
  r = ser.read(8)
  if(len(r) < 4):
    return None
  if(r[3] != "r"):
    return None

  value = r[5]+r[6]+r[7]
  ser.close()
  return value


# Set commands
def setPower(value):
  if(value == 1 or value == "on" or value == "On"):
    return send("!", "001")
  elif(value == 0 or value == "off" or value == "Off"):
    return send("!", "000")
  elif(value == "toggle" or value=="Toggle"):
    current = getPower();
    if(current == "On"):
      return send("!", "000")
    else:
      return send("!", "001")
  else:
    return "Specify On, Off or Toggle"

def setInput(name):
  return send('\x22', Input[name.upper()].value)

def setContrast(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x23', str(level).zfill(3))
  else:
    return "Valid levels are 0-100"

def setBrightness(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x24', str(level).zfill(3))
  else:
    return "Valid levels are 0-100"

def setSharpness(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x25', str(level).zfill(3))
  else:
    return "Valid levels are 0-100"

def setColor(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x26', str(level).zfill(3))
  else:
    return "Valid levels are 0-100"

def setTint(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x27', str(level).zfill(3))
  else:
    return  "Valid levels are 0-100"

def setVolume(level):
  level = int(level)
  if 0 <= level <= 100:
    return send('\x35', str(level).zfill(3))
  else:
    return  "Valid levels are 0-100"

def setMute(value):
  if(value == 1 or value == "on" or value == "On"):
    return send("\x36", "001")
  elif(value == 0 or value == "off" or value == "Off"):
    return send("\x36", "000")
  else:
    return "Specify On or Off"

# Get commands

def getInput():
  value = get("j")
  return Input(value).name

def getContrast():
  return get("a")

def getBrightness():
  return get("b")

def getSharpness():
  return get("c")

def getColor():
  return get("d")

def getTint():
  return get("e")

def getVolume():
  return get("f")

def getMute():
  value = get("g")
  if value == '001':
    return "On"
  else:
    return "Off"


def getPower():
  value = get("l")
  if value == '001':
    return "On"
  else:
    return "Off"

def getSettings():
  data = {}
  data['Power'] = getPower()

  # If the TV is off, none of the other settings can be retrieved, so exit early
  if(data['Power'] == "Off"):
    return json.dumps(data)

  data['Input'] = getInput()
  data['Contrast'] = getContrast()
  data['Brightness'] = getBrightness()
  data['Sharpness'] = getSharpness()
  data['Color'] = getColor()
  data['Tint'] = getTint()
  data['Volume'] = getVolume()
  data['Mute'] = getMute();

  return json.dumps(data)


