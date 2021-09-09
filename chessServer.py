#!/usr/bin/env python3

from datetime import date
import configparser
import socket
import chess
import chess.engine
import chess.pgn
import sys  # Admision argumentos.
def juegaServidor():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    board.push(result.move)
    jugadaServidor = bytes(str(result.move), encoding="ascii")
    cliente.send(jugadaServidor)
    return str(result.move)

def juegaCliente():
    jugadaCliente = cliente.recv(10).decode("ascii")
    board.push_san(jugadaCliente)
    return jugadaCliente

def jueganBlancas(i):
    if i%2 == 1:
        return juegaCliente()
    else:
        return juegaServidor()

def jueganNegras(i):
    if i%2 == 0:
        return juegaCliente()
    else:
        return juegaServidor()

def anotaMarcador():
    if board.outcome().winner != None:
        print ("\a \a")  # Señal aviso partida decidida.
        if game.headers['White'] == 'Cliente':
            marcador[0] += int(board.result()[0])
            marcador[1] += int(board.result()[-1])
        else:
            marcador[0] += int(board.result()[-1])
            marcador[1] += int(board.result()[0])
    return 'Cliente ' + str(marcador[0]) + ' - ' + 'Servidor ' + str(marcador[1])

configuración = configparser.ConfigParser()
configuración.read("datos.cfg")
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("", int(configuración["conexión"]["port"])))
servidor.listen(1)
print("Esperando al rival...")
cliente, addr = servidor.accept()
print("Conexión establecida!")

intLMatch=int(sys.argv[1])
if intLMatch < 1:
    sys.argv[1]="0"
    intLMatch=0
print("Se van a jugar %s partidas, Good Luck!"%(intLMatch))
intLMatch=int(intLMatch)
cliente.send(bytes(sys.argv[1], "utf-8"))    # EEnví (1 byte)a el número de partidas a jugar.
engine = chess.engine.SimpleEngine.popen_uci("stockfish")
marcador = [0, 0]

for i in range(1, intLMatch+1):
    print("Jugando partida " + str(i))
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers['Date'] = date.today()
    game.headers['Round'] = i
    if i%2 == 1:
        game.headers['White'] = 'Cliente'
        game.headers['Black'] = 'Servidor'
    else:
        game.headers['White'] = 'Servidor'
        game.headers['Black'] = 'Cliente'
    while not board.is_game_over():
        if board.fen() == chess.STARTING_FEN:
            node = game.add_variation(chess.Move.from_uci(jueganBlancas(i)))
        else:
            node = node.add_variation(chess.Move.from_uci(jueganBlancas(i)))
        if not board.is_game_over():
            node = node.add_variation(chess.Move.from_uci(jueganNegras(i)))
    game.headers['Result'] = board.result()
    print(anotaMarcador())
    print(game, file=open("partidas.pgn", "a"), end="\n\n")

engine.quit()
print("\a Match Finalizado - ")
print("Marcador Final Cliente %s Servidor%s" %(marcador[0], marcador[1]))  # Marcador Final.
cliente.close()
print("FIN")
