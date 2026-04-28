#include <iostream>
#include <vector>
#include <string>

using namespace std;

struct Cliente {
    string nombre;
    int tiempo_espera; // en minutos
};

class TurnosVector {
private:
    vector<Cliente> cola;

    // Función recursiva privada (oculta al usuario)
    void recursividad_espera(int indice) {
        // Caso base: si el índice llega al tamaño del vector, terminamos
        if (indice >= cola.size()) {
            return; 
        }
        
        // Procesamiento: imprimimos el valor en la posición 'indice'
        cout << "- " << cola[indice].nombre << " | Espera: " << cola[indice].tiempo_espera << " min\n";
        
        // Llamada Recursiva: Avanzamos al siguiente índice
        recursividad_espera(indice + 1);
    }

public:
    void registrar_cliente(string nombre, int tiempo) {
        Cliente nuevoC = {nombre, tiempo};
        cola.push_back(nuevoC); // push_back lo coloca al final
        cout << "Registrado: " << nombre << endl;
    }

    void llamar_proximo(int box) {
        if (cola.empty()) {
            cout << "\n[Box " << box << "] No hay clientes en espera.\n";
            return;
        }
        
        // Obtenemos el primero y luego lo borramos
        Cliente llamado = cola.front(); 
        cola.erase(cola.begin()); 
        
        cout << "\n>>> PROXIMO CLIENTE: " << llamado.nombre << " - Box Nro: " << box << " <<<\n";
    }

    void mostrar_tiempos_espera() {
        cout << "\n--- Tiempo de Espera (Recursivo - Vector) ---\n";
        if (cola.empty()) {
            cout << "Lista vacia.\n";
            return;
        }
        recursividad_espera(0); // Iniciamos la recursión en el índice 0
    }
};

int main() {
    TurnosVector sistema;
    sistema.registrar_cliente("Ana Perez", 15);
    sistema.registrar_cliente("Carlos Gomez", 10);
    sistema.registrar_cliente("Maria Lopez", 25);

    sistema.mostrar_tiempos_espera();
    
    sistema.llamar_proximo(1);
    
    // Verificamos que Ana ya no este en la cola
    sistema.mostrar_tiempos_espera();

    return 0;
}
