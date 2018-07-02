from flask import Flask, send_from_directory
from flask import request
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import time
import atexit
# import threading
# import random

app = Flask(__name__)

# create empty threads (these will hold the stepper 1 and 2 threads)
# tL = threading.Thread()
# tR = threading.Thread()

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

  # t = threading.Thread(target=dc_worker, args=(motor, direction, speed))
  # t.start()

@app.route("/")
def web_interface():
  # html = open("web_interface.html")
  html = open("web_interface.html")
  response = html.read().replace('\n', '')
  html.close()
  try:
    myMotorL.setSpeed(0)
    myMotorR.setSpeed(0)
  except:
  # TODO: notify user of error nicely
    pass
  return response

@app.route("/set_speed")
def set_speed():

  # try:
  left_speed = request.args.get("left_speed")
  right_speed = request.args.get("right_speed")
  print "Received " + str(left_speed) + " " + str(right_speed)

  dc_set_speed(myMotorL, left_speed)
  dc_set_speed(myMotorR, right_speed)
  # except:
  #   return "Error!"

  return "Received " + str(left_speed) + " " + str(right_speed)

@app.route('/files/<path:path>')
def send_file(path):
    return send_from_directory('files', path)

def main():
  app.run(host= '0.0.0.0')

main()
