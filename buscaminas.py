# -*- coding: utf-8 -*-
import random
import re

class Board:
    def __init__(self, dim_size, num_bombs):
        # Inicializa el tablero con dimensiones y número de minas.
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.board = self.crear_nuevo_tablero()  # matriz con minas colocadas
        self.asignar_valores_al_tablero()        # números de minas vecinas
        self.dug = set()                         # celdas excavadas (tuplas (r,c))

    def crear_nuevo_tablero(self):
        # Crea y devuelve una matriz inicial del tablero con minas ubicadas aleatoriamente.
        tablero = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        plantar_bombas = 0
        while plantar_bombas < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size
            if tablero[row][col] == '*':
                continue
            tablero[row][col] = '*'
            plantar_bombas += 1
        return tablero

    def asignar_valores_al_tablero(self):
        # Calcula y asigna la cantidad de minas vecinas a cada celda.
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    continue
                self.board[r][c] = self.numero_minas_cerca(r, c)

    def numero_minas_cerca(self, row, col):
        # Devuelve el número de minas vecinas a la celda (row, col).
        total_minas = 0
        for r in range(max(0, row - 1), min(self.dim_size, row + 2)):
            for c in range(max(0, col - 1), min(self.dim_size, col + 2)):
                if r == row and c == col:
                    continue
                if self.board[r][c] == '*':
                    total_minas += 1
        return total_minas

    def excavar(self, row, col):
        # Excava una celda; True si es segura, False si explota una mina.
        self.dug.add((row, col))
        if self.board[row][col] == '*':
            return False
        elif self.board[row][col] > 0:
            return True
        # Si es 0, excavar vecinos recursivamente
        for r in range(max(0, row - 1), min(self.dim_size, row + 2)):
            for c in range(max(0, col - 1), min(self.dim_size, col + 2)):
                if (r, c) in self.dug:
                    continue
                self.excavar(r, c)
        return True

    def __str__(self):
        # Devuelve una representación en texto del tablero para la consola.
        visible_board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if (r, c) in self.dug:
                    if self.board[r][c] == 0:
                        visible_board[r][c] = ' '
                    else:
                        visible_board[r][c] = str(self.board[r][c])
                else:
                    visible_board[r][c] = '□'
        # Ensamblar filas con encabezados de columna
        string_rep = '   ' + ' '.join([f'{i:2d}' for i in range(self.dim_size)]) + '\n'
        string_rep += '   ' + '--' * self.dim_size + '-\n'
        for i in range(self.dim_size):
            row = visible_board[i]
            string_rep += f'{i:2d}| ' + ' '.join(f'{ch:2s}' for ch in row) + '\n'
        return string_rep

def jugar(dim_size=10, num_bombs=10):
    # Bucle principal para jugar Buscaminas en consola.
    board = Board(dim_size, num_bombs)
    safe = True
    while len(board.dug) < board.dim_size ** 2 - num_bombs:
        print(board)
        user_input = re.split(r',(\s)*', input("¿Dónde excavar? Formato fila,col: "))
        try:
            row, col = int(user_input[0]), int(user_input[-1])
        except Exception:
            print("Entrada inválida. Usa el formato fila,col (ej: 0,3)")
            continue
        if row < 0 or row >= board.dim_size or col < 0 or col >= dim_size:
            print("Ubicación fuera del tablero. Intenta de nuevo.")
            continue
        safe = board.excavar(row, col)
        if not safe:
            break
    if safe:
        print("🎉 ¡Felicidades! ¡Ganaste!")
    else:
        print("💥 ¡Boom! Fin del juego.")
        # Revelar todo el tablero
        board.dug = {(r, c) for r in range(board.dim_size) for c in range(board.dim_size)}
        print(board)

if __name__ == '__main__':
    jugar()
