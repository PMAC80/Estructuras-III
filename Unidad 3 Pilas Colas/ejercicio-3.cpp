/*  
Una empresa necesita implementar un Historial de llamadas a sus cliente, 
la aplicación deberá ir cargando los números telefónicos en un historial
 y el usuario podrá ir recorriendo el histórico de llamadas 
 (similar al botón Back del navegador).
Implementar una app que realice esta función.
*/

#include <iostream>
#include <stack>
#include <string>

using namespace std;

// Pasamos la pila por valor para recorrerla sin perder los datos originales
void mostrarHistorial(stack<string> s) {
    if (s.empty()) {
        cout << "El historial de llamadas esta vacio.\n";
        return;
    }
    
    cout << "\n--- Historial Completo (Mas reciente primero) ---\n";
    while (!s.empty()) {
        cout << " Numero: " << s.top() << "\n";
        s.pop();
    }
    cout << "-------------------------------------------------\n";
}

int main() {
    stack<string> historial;
    int opcion;
    string numeroTelefono;

    do {
        cout << "\n========== HISTORIAL DE LLAMADAS ==========\n";
        cout << "1. Registrar nueva llamada\n";
        cout << "2. Recorrer/Volver a la llamada anterior (Back)\n";
        cout << "3. Mostrar todo el historial\n";
        cout << "4. Salir\n";
        cout << "===========================================\n";
        cout << "Ingrese una opcion: ";
        cin >> opcion; 

        switch (opcion) {
            case 1:
                cout << "Ingrese el numero de telefono (ej. 341-5555): ";
                cin >> numeroTelefono;
                historial.push(numeroTelefono);
                cout << "-> Llamada registrada.\n";
                break;

            case 2:
                // El comportamiento tipo 'Back' se logra viendo el tope (top) 
                // y luego sacándolo de la pila (pop)
                if (!historial.empty()) {
                    cout << "\n-> Volviendo atras... Llamada anterior fue a: " << historial.top() << "\n";
                    historial.pop();
                } else {
                    cout << "\n-> No hay mas llamadas en el historial (Llego al principio).\n";
                }
                break;

            case 3:
                mostrarHistorial(historial);
                break;

            case 4:
                cout << "\nSaliendo del historial...\n";
                break;

            default:
                cout << "\n-> Opcion invalida. Intente de nuevo.\n";
        }
    } while (opcion != 4);

    return 0;
}


