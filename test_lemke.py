from app.models.game import BimatrixGame
from app.services.solver_service import SolverService

# Игра "дилемма заключённого"
A = [[3, 0], [5, 1]]
B = [[3, 5], [0, 1]]
game = BimatrixGame(A, B)

service = SolverService()
print("=== Lemke-Howson (одна метка) ===")
print(service.solve(game, 'lemke_howson', initial_label=0))

print("\n=== Lemke-Howson (все метки) ===")
print(service.solve(game, 'lemke_howson_all'))

print("\n=== Перебор опор ===")
print(service.solve(game, 'support_enumeration'))