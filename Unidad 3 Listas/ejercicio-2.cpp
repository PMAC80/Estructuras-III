#include <iostream>
#include <string>
#include <list>

using namespace std;

// Estructura para almacenar los datos del paciente (sin punteros extra para STL)
struct Paciente {
    int identificacion;
    string nombre;
    int edad;
    string diagnostico;
};

// Función para registrar usando list de STL
void registrarPaciente(list<Paciente>& lista) {
    Paciente p;
    cout << "\n--- Registrar Paciente ---" << endl;
    cout << "ID / DNI: ";
    cin >> p.identificacion;
    cin.ignore();
    cout << "Nombre completo: ";
    getline(cin, p.nombre);
    cout << "Edad: ";
    cin >> p.edad;
    cin.ignore();
    cout << "Diagnostico/Motivo: ";
    getline(cin, p.diagnostico);

    // Al usar push_back, STL reserva la memoria dinámica, guarda la data y enlaza todo mágicamente.
    lista.push_back(p); 
    cout << "Paciente registrado con exito!" << endl;
}

// Función para listar pacientes
void listarPacientes(const list<Paciente>& lista) {
    if (lista.empty()) { // El método .empty() nos dice si no hay nodos
        cout << "\nNo hay pacientes registrados en el sistema." << endl;
        return;
    }

    cout << "\n--- Lista de Pacientes ---" << endl;
    
    // For-each de C++ moderno: Itera sobre cada elemento p en la lista. 
    // Usamos 'const' para no editar y '&' para no copiar memoria a la fuerza.
    for (const Paciente& p : lista) {
        cout << "ID: " << p.identificacion 
             << " | Nombre: " << p.nombre 
             << " | Edad: " << p.edad 
             << " | Diagnostico: " << p.diagnostico << endl;
    }
}

// Función para modificar un paciente
void modificarPaciente(list<Paciente>& lista) {
    if (lista.empty()) {
        cout << "\nNo hay pacientes registrados." << endl;
        return;
    }

    int id;
    cout << "\nIngrese el ID del paciente a modificar: ";
    cin >> id;

    bool encontrado = false;

    // Recorremos la lista por referencia (&) sin iteradores manuales para actualizarlo in-situ
    for (Paciente& p : lista) {
        if (p.identificacion == id) {
            cout << "Paciente encontrado. Ingrese los nuevos datos:" << endl;
            cin.ignore();
            cout << "Nuevo Nombre (actual: " << p.nombre << "): ";
            getline(cin, p.nombre);
            cout << "Nueva Edad (actual: " << p.edad << "): ";
            cin >> p.edad;
            cin.ignore();
            cout << "Nuevo Diagnostico (actual: " << p.diagnostico << "): ";
            getline(cin, p.diagnostico);
            
            cout << "Paciente modificado exitosamente." << endl;
            encontrado = true;
            break; // Rompemos una vez que se modificó
        }
    }

    if (!encontrado) {
        cout << "Error: No se encontro ningun paciente con el ID proporcionado." << endl;
    }
}

// Función para eliminar un paciente
void eliminarPaciente(list<Paciente>& lista) {
    if (lista.empty()) {
        cout << "\nNo hay pacientes registrados." << endl;
        return;
    }

    int id;
    cout << "\nIngrese el ID del paciente a eliminar: ";
    cin >> id;

    bool encontrado = false;
    
    // Para usar la función erase() ocupamos "Iteradores" de STL.
    auto iterador = lista.begin(); 
    while (iterador != lista.end()) {
        if (iterador->identificacion == id) {
            // El método erase se encarga de re-enlazar los nodos adyacentes y hacer delete.
            lista.erase(iterador); 
            cout << "Paciente eliminado del sistema." << endl;
            encontrado = true;
            break;
        }
        iterador++; // Avanzamos al siguiente paciente
    }

    if (!encontrado) {
        cout << "Error: No se encontro ningun paciente con el ID proporcionado." << endl;
    }
}

int main() {
    // Declaración de una lista de doble enlace perteneciente a STL
    list<Paciente> listaPacientes; 
    int opcion;

    do {
        cout << "\n===================================" << endl;
        cout << "      SISTEMA CLINICO LOCAL (STL)" << endl;
        cout << "===================================" << endl;
        cout << "1. Registrar paciente" << endl;
        cout << "2. Modificar paciente" << endl;
        cout << "3. Eliminar paciente" << endl;
        cout << "4. Listar pacientes" << endl;
        cout << "5. Salir" << endl;
        cout << "Ingrese una opcion: ";
        cin >> opcion;

        switch (opcion) {
            case 1: registrarPaciente(listaPacientes); break;
            case 2: modificarPaciente(listaPacientes); break;
            case 3: eliminarPaciente(listaPacientes); break;
            case 4: listarPacientes(listaPacientes); break;
            case 5: cout << "Saliendo del sistema..." << endl; break;
            default: cout << "Opcion invalida. Intente de nuevo." << endl;
        }
    } while (opcion != 5);

    // No es necesario hacer nada manualmente para eliminar los nodos en memoria (evitar memory leaks).
    // STL (como "list") cuenta con destructores internos que se ejecutan solos al final del ámbito (scope) o return, 
    // y limpian toda la memoria alojada.

    return 0;
}
