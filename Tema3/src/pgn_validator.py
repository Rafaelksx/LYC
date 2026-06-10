import sys

class PGNValidator:
    def __init__(self):
        # Estados:
        # 0: Inicio
        # 1: Pieza leída (K, Q, R, B, N)
        # 2: Captura leída (x)
        # 3: Columna leída (a-h)
        # 4: Fila leída (1-8) -> ACEPTACIÓN (Movimiento completo)
        # 5: Jaque/Mate leído (+, #) -> ACEPTACIÓN
        # 99: Estado de error / muerto
        self.accepting_states = {4, 5}

    def transition(self, state, char):
        if state == 99:
            return 99

        # Transiciones desde el estado 0 (Inicio)
        if state == 0:
            if char in {'K', 'Q', 'R', 'B', 'N'}:
                return 1
            elif char == 'x':
                return 2
            elif 'a' <= char <= 'h':
                return 3
            else:
                return 99

        # Transiciones desde el estado 1 (Pieza leída)
        elif state == 1:
            if char == 'x':
                return 2
            elif 'a' <= char <= 'h':
                return 3
            else:
                return 99

        # Transiciones desde el estado 2 (Captura leída)
        elif state == 2:
            if 'a' <= char <= 'h':
                return 3
            else:
                return 99

        # Transiciones desde el estado 3 (Columna leída)
        elif state == 3:
            if '1' <= char <= '8':
                return 4
            else:
                return 99

        # Transiciones desde el estado 4 (Fila leída - Aceptación)
        elif state == 4:
            if char in {'+', '#'}:
                return 5
            else:
                return 99

        # Transiciones desde el estado 5 (Jaque/Mate leído - Aceptación)
        elif state == 5:
            # Una vez en 5, cualquier carácter adicional es inválido en un solo movimiento
            return 99

        return 99

    def validate_move(self, move):
        """
        Valida si un único movimiento PGN es sintácticamente correcto.
        Retorna (True/False, último_estado)
        """
        current_state = 0
        for char in move:
            current_state = self.transition(current_state, char)
            if current_state == 99:
                return False, current_state
        
        return current_state in self.accepting_states, current_state

    def validate_game(self, game_string):
        """
        Valida una secuencia de movimientos separados por espacios.
        Ejemplo: "e4 Nf3 Qxe5+ Bxf7#"
        """
        moves = game_string.strip().split()
        results = []
        all_valid = True
        
        for move in moves:
            # Eliminar numeración de jugadas clásica de PGN si existe (ej. "1.e4" -> "e4")
            # Esto simplifica la validación del juego completo
            cleaned_move = move
            if "." in move:
                cleaned_move = move.split(".")[-1]
            
            if not cleaned_move:
                continue

            valid, final_state = self.validate_move(cleaned_move)
            results.append((move, cleaned_move, valid, final_state))
            if not valid:
                all_valid = False
                
        return all_valid, results

if __name__ == "__main__":
    validator = PGNValidator()
    
    # Casos de prueba individuales
    test_moves = [
        "e4", "Nf3", "Qxe5+", "Bxf7#",  # Válidos
        "xe4", "Kxf8", "d8",            # Válidos (d8 es peón a d8, x es captura de peón)
        "e9", "Nx", "KQRBNe4", "a1+#",  # Inválidos
        "Nxe4", "c3"                    # Válidos
    ]
    
    print("Validación de movimientos individuales:")
    for move in test_moves:
        valid, state = validator.validate_move(move)
        status = "VÁLIDO" if valid else "INVÁLIDO"
        print(f"- '{move}': {status} (Estado final: {state})")

    # Prueba de secuencia de juego
    game = "1.e4 e5 2.Nf3 Nc6 3.Bc4 Nf6 4.Ng5 d5 5.exd5 Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 Ne7 9.d4 c6 10.Bg5"
    print("\nValidación de secuencia de juego:")
    all_valid, results = validator.validate_game(game)
    print(f"Juego completo: {'VÁLIDO' if all_valid else 'CONTIENE ERRORES'}")
    for orig, clean, val, state in results[:10]:
        status = "VÁLIDO" if val else "INVÁLIDO"
        print(f"  - Jugada '{orig}' (evaluada como '{clean}'): {status}")
