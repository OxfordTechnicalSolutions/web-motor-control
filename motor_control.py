from flask import Flask, send_from_directory
from flask import request
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from flask_socketio import SocketIO

import time
import atexit
import threading
import json
# import random

app = Flask(__name__)
socketio = SocketIO(app)


# constants
STOP_ALL_PERIOD = 1.0          # secs from receiving command to stopping motors
STOP_ALL_PERIOD_CHECK = 0.1    # period for stop all check

# global variables
lastCommandTicks = time.time()

try:
  mh = Adafruit_MotorHAT(addr=0x60)
  # left motor
  myMotorL = mh.getMotor(4)
  myMotorL.setSpeed(150)
  myMotorL.run(Adafruit_MotorHAT.FORWARD)
  myMotorL.run(Adafruit_MotorHAT.RELEASE)
  # right motor
  myMotorR = mh.getMotor(3)
  myMotorR.setSpeed(150)
  myMotorR.run(Adafruit_MotorHAT.FORWARD)
  myMotorR.run(Adafruit_MotorHAT.RELEASE)
except:
  # TODO: notify user of error nicely
  pass
  

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

def dc_worker(motor, direction, speed):
  motor.run(direction)
  motor.setSpeed(abs(int(speed)))

def dc_set_speed(motor, speed):
  direction = Adafruit_MotorHAT.FORWARD
  if int(speed) < 0:
    direction = Adafruit_MotorHAT.BACKWARD
  motor.run(direction)
  motor.setSpeed(abs(int(speed)))

def stop_all_check():
  currentTicks = time.time()
  
  if (currentTicks-lastCommandTicks) > STOP_ALL_PERIOD:
    print "STOP ALL: " + str(currentTicks-lastCommandTicks) + " sec since last command"
    try:
      myMotorL.setSpeed(0)
      myMotorR.setSpeed(0)
    except:
      # TODO: notify user of error nicely
      pass
  else:
    # keep checking
    threading.Timer(STOP_ALL_PERIOD_CHECK, stop_all_check).start()

@app.route("/")
def web_interface():
  html = open("web_interface_sockets.html")
  response = html.read().replace('\n', '')
  html.close()
  try:
    myMotorL.setSpeed(0)
    myMotorR.setSpeed(0)
  except:
    # TODO: notify user of error nicely
    pass
  return response

@socketio.on('set_speed')
def set_speed(data):
  #print('received json: ' + str(data))

  global lastCommandTicks
  lastCommandTicks = time.time()
  stop_all_check()

  left_speed = data['left_speed']
  right_speed = data['right_speed']
  print "Received " + str(left_speed) + " " + str(right_speed)

  try:
    dc_set_speed(myMotorL, left_speed)
    dc_set_speed(myMotorR, right_speed)
  except:
    # TODO: notify user of error nicely
    pass

@app.route('/files/<path:path>')
def send_file(path):
    return send_from_directory('files', path)

def main():
  socketio.run(app, host='0.0.0.0')
  # app.run(host= '0.0.0.0')

main()
