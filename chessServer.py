#!/usr/bin/env python3

from datetime import date
import configparser
import socket
import chess
import chess.engine
import chess.pgn
import sys  # Admision argumentos.
def juegaServidor():
    result = engine.play(board, chess.engine.Limit(TiempoDeReflexion))
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
def NotifMarCli():
  # Notifica al cliente el resultado final del match.
  MarcaFinal="Marcador Final: Cliente " + str(marcador[0]) + " Servidor " + str(marcador[1])
  cliente.send(bytes(MarcaFinal, "utf-8") )
def ShakingHands(intLMatch):
  # Comprueba algunas   condiciones de juego.  
  try:
    if intLMatch > 999:
      intLMatch=999
    if (int(sys.argv[2]) > 20) or (int(sys.argv[2]) < 1):
      intLMatch=-1
      
  except:
    intLMatch=-1
  finally:    
    return(intLMatch)

def AjustarNivel(intNivel):
  # Devuelve el tiempo de reflexión
  # ajustado al nivel elegido.
  intNivel=int(intNivel)
  intFactor = (intNivel - 1) * float(0.5)
  return(intNivel *int(0.1) + intFactor)


  
# Main()
configuración = configparser.ConfigParser()
configuración.read("datos.cfg")
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("", int(configuración["conexión"]["port"])))
servidor.listen(1)
print("Esperando al rival...")
cliente, addr = servidor.accept()
print("Conexión establecida!")

intLMatch=int(sys.argv[1])
intLMatch=ShakingHands(intLMatch) 
if intLMatch < 1:
    sys.argv[1]="0"
    intLMatch=0
intLMatch=int(intLMatch)
TiempoDeReflexion=AjustarNivel(sys.argv[2])
print("Se van a jugar %s partidas a nivel %s, Good Luck!"%(intLMatch, sys.argv[2]))
print("Tiempo medio de reflexión: %s sec. por jugada. Nivel ajustable entre [1-20]"%(TiempoDeReflexion))
cliente.send(bytes(sys.argv[1], "utf-8"))  # Envía    el número de partidas a jugar.
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
print("Marcador Final Cliente %s Servidor %s" %(marcador[0], marcador[1]))  # Marcador Final.
NotifMarCli()
cliente.close()
print("FIN")
