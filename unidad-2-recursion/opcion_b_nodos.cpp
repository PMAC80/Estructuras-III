#include <iostream>
#include <string>

using namespace std;

struct Cliente {
    string nombre;
    int tiempo_espera;
};

// El nodo es la caja que envuelve al Cliente y el puntero al próximo
struct Nodo {
    Cliente dato;
    Nodo* siguiente;
};

class TurnosNodos {
private:
    Nodo* frente;
    Nodo* final;

    // Función recursiva privada
    void recursividad_espera(Nodo* actual) {
        // Caso Base: si llegamos a un puntero que apunta a la nada (nullptr), terminamos.
        if (actual == nullptr) {
            return;
        }

        // Procesamiento: imprimimos el dato del nodo actual
        cout << "- " << actual->dato.nombre << " | Espera: " << actual->dato.tiempo_espera << " min\n";

        // Llamada Recursiva: Pasamos en memoria al SIGUIENTE nodo
        recursividad_espera(actual->siguiente);
    }

public:
    TurnosNodos() {
        frente = nullptr;
        final = nullptr;
    }

    void registrar_cliente(string nombre, int tiempo) {
        Nodo* nuevoNodo = new Nodo();
        nuevoNodo->dato = {nombre, tiempo};
        nuevoNodo->siguiente = nullptr;

        if (frente == nullptr) {
            frente = nuevoNodo;
            final = nuevoNodo;
        } else {
            final->siguiente = nuevoNodo;
            final = nuevoNodo;
        }
        cout << "Registrado: " << nombre << endl;
    }

    void llamar_proximo(int box) {
        if (frente == nullptr) {
            cout << "\n[Box " << box << "] No hay clientes en espera.\n";
            return;
        }

        Nodo* aux = frente;
        Cliente llamado = aux->dato;
        
        frente = frente->siguiente; // Movemos el frente al siguiente
        
        if (frente == nullptr) {
            final = nullptr; // Si se vacío la cola, el final también queda nulo
        }

        delete aux; // Liberamos la memoria del nodo que desencolamos (C++)
        
        cout << "\n>>> PROXIMO CLIENTE: " << llamado.nombre << " - Box Nro: " << box << " <<<\n";
    }

    void mostrar_tiempos_espera() {
        cout << "\n--- Tiempo de Espera (Recursivo - Nodos) ---\n";
        if (frente == nullptr) {
            cout << "Lista vacia.\n";
            return;
        }
        recursividad_espera(frente); // Empezamos en el puntero del frente
    }
};

int main() {
    TurnosNodos sistema;
    sistema.registrar_cliente("Ana Perez", 15);
    sistema.registrar_cliente("Carlos Gomez", 10);
    sistema.registrar_cliente("Maria Lopez", 25);

    sistema.mostrar_tiempos_espera();
    
    sistema.llamar_proximo(1);
    
    sistema.mostrar_tiempos_espera();

    return 0;
}
