/*  
Un Negocio necesita gestionar la atención a sus cliente, el mismo recibe los clientes en un Box de Atencia que registra los clientes y los carga para su atención según su llegada.
Nos piden desarrollar un sistema de “Turnos” que se muestren en una pantalla.
La aplicación deberá registrar los clientes, mostrarlos en orden de llegada, llamarlos según ese orden por pantalla con una opción “próximo cliente – Box nro”
Implementando Listas en STL
*/

#include <iostream>
#include <list>
#include <string>

using namespace std;

// Con una lista podemos pasarla por referencia constante para no copiarla
// y recorrerla con un bucle, ya que la lista sí permite iterar sobre sus elementos.
void mostrarClientes(const list<string>& lista) {
    if (lista.empty()) {
        cout << "No hay clientes en espera.\n";
        return;
    }
    cout << "\n--- Clientes en Espera (Orden de Llegada) ---\n";
    int turno = 1;
    for (const string& cliente : lista) {
        cout << turno++ << ". " << cliente << "\n";
    }
    cout << "---------------------------------------------\n";
}

int main() {
    list<string> listaClientes;
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
                
                // Con push_back lo insertamos al final de la lista
                listaClientes.push_back(nombreCliente); 
                cout << "-> Cliente '" << nombreCliente << "' registrado exitosamente.\n";
                break;

            case 2:
                mostrarClientes(listaClientes);
                break;

            case 3:
                if (!listaClientes.empty()) {
                    cout << "\n**************** PANTALLA ****************\n";
                    // front() nos da el primer elemento al igual que en la cola
                    cout << "   Proximo cliente: " << listaClientes.front() << " - Box nro: " << numeroBox << "\n";
                    cout << "******************************************\n";
                    
                    // pop_front() elimina el primer elemento de la lista
                    listaClientes.pop_front(); 
                    
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

