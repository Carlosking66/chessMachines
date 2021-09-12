#!/usr/bin/env python3
import configparser
import socket
import chess
import chess.engine

def juegaCliente():
    result = engine.play(board, chess.engine.Limit(float(TiempoRef)))
    board.push(result.move)
    jugadaCliente = bytes(str(result.move), encoding="ascii")
    obj.send(jugadaCliente)

def juegaServidor():
    recibido = obj.recv(10).decode("ascii")
    board.push_san(recibido)

def juega():
    if (i%2 == 1 and board.turn == chess.WHITE) or (i%2 == 0 and board.turn == chess.BLACK):
        juegaCliente()
    else:
        juegaServidor()

configuración = configparser.ConfigParser()
configuración.read("datos.cfg")
engine = chess.engine.SimpleEngine.popen_uci("stockfish")
host = configuración["conexión"]["host"]
port = int(configuración["conexión"]["port"])
obj = socket.socket()
obj.connect((host, port))
print("Conectado al servidor")

# ...

intLMatch=obj.recv(3) # Recibe (3 bytes) el  nº de partidas a jugar.
# ...
strLMatch=intLMatch.decode("utf-8")

obj.send(bytes("X", "utf-8"))  # Envia una espera al servidor.
TiempoRef=obj.recv(4) # Recibe (4 bytes) el tiempo de reflexión.
TiempoRef=TiempoRef.decode("utf-8")


print("Se van a jugar %s partidas, a un tiempo medio de %s sec por jugada.  Good Luck!" %(strLMatch, TiempoRef))


for i in range(1, int(strLMatch)+1):
    board = chess.Board()
    while not board.is_game_over():
        juega()
        if not board.is_game_over():
            juega()

print("Match Finalizado!")
print(obj.recv(48).decode("utf-8"))
engine.quit()
obj.close()
print("FIN")
