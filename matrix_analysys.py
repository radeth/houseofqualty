import numpy as np

zmywarkaAplikacjaAI = np.array([[9, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
                                [0, 9, 0, 0, 0, 0, 0, 0, 0, 9, 0, 3, 0, 0],
                                [0, 0, 9, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 9],
                                [0, 0, 0, 9, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0],
                                [3, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0],
                                [0, 0, 0, 1, 0, 0, 1, 9, 0, 0, 0, 0, 0, 0],
                                [0, 0, 3, 0, 0, 9, 0, 0, 0, 0, 0, 0, 9, 0],
                                [0, 0, 0, 0, 9, 3, 0, 0, 9, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 9, 0, 0, 0, 3, 0, 0, 0, 0, 0]])

sklepAI = np.array([[9, 3, 3, 0, 1, 3, 1, 0],
                    [0, 3, 9, 0, 3, 1, 0, 0],
                    [0, 0, 0, 9, 1, 3, 1, 3],
                    [0, 0, 0, 0, 9, 3, 0, 3],
                    [0, 0, 0, 0, 0, 0, 9, 3],
                    [0, 0, 0, 0, 0, 9, 1, 3]])

sklepExample = np.array([[3, 3, 1, 0, 0, 0, 1, 0],
                         [9, 3, 9, 5, 1, 0, 0, 0],
                         [0, 0, 0, 8, 0, 0, 0, 3],
                         [0, 0, 0, 0, 9, 0, 0, 3],
                         [0, 0, 0, 0, 1, 0, 9, 0],
                         [0, 0, 0, 0, 0, 9, 3, 0]])

zmywarkaPrzyklad = np.array([
    # [temperatury zmywania, gabaryty, materiał dna, zużycie energii, zużycie wody, kolorystyka obudowy, typ panelu sterowania, długość kabla zasilającego, poziom hałasu, regulacja półek, autoodkamienianie i czyszczenie, liczba programów zmywania, materiał obudowy, wskaźnik pracy]
    [9, 3, 1, 3, 9, 1, 1, 1, 1, 9, 9, 1, 1, 1],  # dokładne zmywanie
    [3, 9, 9, 9, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1],  # różnorodne gabaryty
    [3, 1, 9, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],  # wysoka niezawodność
    [1, 1, 1, 1, 1, 9, 9, 1, 1, 1, 1, 1, 1, 1],  # łatwa obsługa
    [3, 1, 1, 9, 1, 1, 9, 1, 1, 1, 1, 9, 1, 1],  # wiele programów mycia
    [1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # nastawienie czasowe włączania
    [1, 1, 1, 1, 1, 9, 9, 1, 1, 1, 1, 1, 1, 1],  # nowoczesny i ładny wygląd
    [3, 1, 1, 9, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],  # niskie zużycie energii elektrycznej
    [1, 1, 1, 1, 9, 1, 1, 1, 1, 1, 3, 1, 1, 1],  # niskie zużycie wody
])

are_equal = np.array_equal(sklepExample, sklepAI)
print(are_equal)
# Różnica elementów
difference = sklepExample - sklepAI
print(difference)
# Norma Frobeniusa
frobenius_norm = np.linalg.norm(sklepExample - sklepAI)
print(frobenius_norm)

# Sprawdzenie czy macierze mają takie same wymiary
if sklepExample.shape == sklepAI.shape:
    matching_cells = np.sum(sklepExample == sklepAI)
    total_cells = sklepExample.size
    percentage_match = (matching_cells / total_cells) * 100
    print(percentage_match)
else:
    print("Macierze mają różne wymiary!")

# Sprawdzenie równości
are_equal = np.array_equal(zmywarkaPrzyklad, zmywarkaAplikacjaAI)
print(are_equal)
# Różnica elementów
difference = zmywarkaPrzyklad - zmywarkaAplikacjaAI
print(difference)
# Norma Frobeniusa
frobenius_norm = np.linalg.norm(zmywarkaPrzyklad - zmywarkaAplikacjaAI)
print(frobenius_norm)
