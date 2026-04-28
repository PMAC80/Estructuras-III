#include <iostream>
#include <string>

using namespace std;

struct Cliente {
    string nombre;
    int tiempo_espera;
};

// Máximo número de clientes. Al ser un arreglo estático, necesitamos un límite.
const int MAX_CLIENTES = 100; 

class TurnosArregloSimple {
private:
    Cliente cola[MAX_CLIENTES]; 
    int frente;     // Índice del primer elemento
    int final;      // Índice donde ingresará el nuevo elemento
    int cantidad;   // Cantidad actual de elementos

    // Función recursiva privada
    void recursividad_espera(int indice, int elementos_restantes) {
        // Caso Base: Si no quedan elementos por imprimir, nos detenemos.
        if (elementos_restantes == 0) {
            return;
        }

        // Procesamiento: Imprimo lo que hay en el índice actual
        cout << "- " << cola[indice].nombre << " | Espera: " << cola[indice].tiempo_espera << " min\n";

        // Llamada Recursiva: Movemos el índice una posición. 
        // Usamos (indice+1)%MAX para que si llega a 100 vuelva al inicio (Cola Circular Simple)
        recursividad_espera((indice + 1) % MAX_CLIENTES, elementos_restantes - 1);
    }

public:
    TurnosArregloSimple() {
        frente = 0;
        final = 0;
        cantidad = 0;
    }

    void registrar_cliente(string nombre, int tiempo) {
        if (cantidad >= MAX_CLIENTES) {
            cout << "Error: La sala de espera esta a su maxima capacidad!\n";
            return;
        }

        cola[final].nombre = nombre;
        cola[final].tiempo_espera = tiempo;
        
        final = (final + 1) % MAX_CLIENTES; // Avanza o da la vuelta al inicio del arreglo
        cantidad++;
        
        cout << "Registrado: " << nombre << endl;
    }

    void llamar_proximo(int box) {
        if (cantidad == 0) {
            cout << "\n[Box " << box << "] No hay clientes en espera.\n";
            return;
        }

        Cliente llamado = cola[frente];
        frente = (frente + 1) % MAX_CLIENTES; // El frente avanza
        cantidad--;

        cout << "\n>>> PROXIMO CLIENTE: " << llamado.nombre << " - Box Nro: " << box << " <<<\n";
    }

    void mostrar_tiempos_espera() {
        cout << "\n--- Tiempo de Espera (Recursivo - Arreglo Estatico) ---\n";
        if (cantidad == 0) {
            cout << "Lista vacia.\n";
            return;
        }

        // Le pasamos el índice inicial y cuántos debe recorrer
        recursividad_espera(frente, cantidad);
    }
};

int main() {
    TurnosArregloSimple sistema;
    sistema.registrar_cliente("Ana Perez", 15);
    sistema.registrar_cliente("Carlos Gomez", 10);
    sistema.registrar_cliente("Maria Lopez", 25);

    sistema.mostrar_tiempos_espera();
    
    sistema.llamar_proximo(1);
    
    sistema.mostrar_tiempos_espera();

    return 0;
}
