#include <iostream>

using namespace std;

// Declaración anticipada (Forward declaration)
// Necesaria en C++ cuando dos funciones se llaman mutuamente, 
// para que el compilador sepa que "impar" existe antes de leer su código.
bool impar(int n);

// Función que determina si un número es par
bool par(int n) {
    // Caso base explícito del problema (y por sanidad agregamos el 0)
    if (n == 0) return true;  // El 0 es par
    if (n == 1) return false; // El problema dice "1 es impar", por ende no es par
    
    // Paso recursivo inverso: Si busco saber si "n" es par, 
    // le pregunto a la otra función si el antecesor (n - 1) es impar.
    return impar(n - 1);
}

// Función que determina si un número es impar
bool impar(int n) {
    // Casos base
    if (n == 0) return false; // El 0 no es impar
    if (n == 1) return true;  // El problema dice: "1 es impar"
    
    // Paso recursivo inverso: Si busco saber si "n" es impar,
    // le pregunto a la otra función si el antecesor (n - 1) es par.
    return par(n - 1);
}

int main() {
    cout << "--- Determinador de Paridad (Recursividad Mutua) ---\n";
    
    int numero;
    cout << "Ingrese un numero natural (mayor o igual a 0): ";
    cin >> numero;

    // Validación sencilla
    if (numero < 0) {
        cout << "Por favor ingrese un numero natural positivo." << endl;
        return 1;
    }

    if (par(numero)) {
        cout << "\nResultado: El numero " << numero << " es PAR." << endl;
    } else { // Si no es par, por lógica y gracias a la recursión, es impar.
        cout << "\nResultado: El numero " << numero << " es IMPAR." << endl;
    }

    // Pruebas directas
    cout << "\n--- Pruebas de escritorio internas ---" << endl;
    cout << "¿1 es impar? " << (impar(1) ? "Si" : "No") << endl;
    cout << "¿4 es par? " << (par(4) ? "Si" : "No") << endl;
    cout << "¿7 es par? " << (par(7) ? "Si" : "No") << endl;

    return 0;
}
