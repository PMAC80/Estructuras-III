/*
Un Negocio necesita gestionar la atención a sus cliente, 
el mismo recibe los clientes en un Box de Atencia que registra 
los clientes y los carga para su atención según su llegada.
Nos piden desarrollar un sistema de “Turnos” que se muestren en 
una pantalla.
La aplicación deberá registrar los clientes, mostrarlos en 
orden de llegada, llamarlos según ese orden por pantalla con 
una opción “próximo cliente – Box nro”
*/

#include <iostream>
#include <queue>
#include <string>

using namespace std;

// Función que muestra los clientes en la cola (se pasa por valor para no vaciar la cola original)
void mostrarClientes(queue<string> q) {
    if (q.empty()) 
    {
        cout << "No hay clientes en espera.\n";
        return;
    }
    cout << "\n--- Clientes en Espera (Orden de Llegada) ---\n";
    int turno = 1;
    while (!q.empty()) 
    {
        cout << turno++ << ". " << q.front() << "\n";
        q.pop();
    }
    cout << "---------------------------------------------\n";
}

int main() {
    queue<string> colaClientes;
    int opcion;
    string nombreCliente;
    int numeroBox = 1;

    do {
        cout << "\n========== SISTEMA DE TURNOS ==========\n";
        cout << "1. Registrar cliente\n";
        cout << "2. Mostrar clientes en orden de llegada\n";
        cout << "3. Llamar proximo cliente (Pantalla)\n";
        cout << "4. Salir\n";
        cout << "=======================================\n";
        cout << "Ingrese una opcion: ";
        cin >> opcion;

        switch (opcion) {
            case 1:
                cout << "Ingrese el nombre del cliente: ";
                cin.ignore();
                getline(cin, nombreCliente);
                colaClientes.push(nombreCliente);
                cout << "-> Cliente '" << nombreCliente << "' registrado exitosamente.\n";
                break;

            case 2:
                mostrarClientes(colaClientes);
                break;

            case 3:
                if (!colaClientes.empty()) {
                    cout << "\n**************** PANTALLA ****************\n";
                    cout << "   Proximo cliente: " << colaClientes.front() << " - Box nro: " << numeroBox << "\n";
                    cout << "******************************************\n";
                    
                    colaClientes.pop();
                    
                    // Simulamos que hay 3 boxes rotativos (ej. Box 1, Box 2, Box 3)
                    numeroBox = (numeroBox % 3) + 1;
                } else {
                    cout << "\n-> No hay clientes esperando para ser atendidos.\n";
                }
                break;

            case 4:
                cout << "\nSaliendo del sistema de turnos...\n";
                break;

            default:
                cout << "\n-> Opcion invalida. Por favor, intente de nuevo.\n";
        }
    } while (opcion != 4);

    return 0;
}

