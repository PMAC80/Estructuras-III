#include <iostream>
#include <string>

using namespace std;

// Estructura para almacenar los datos del paciente (La informacion o "Carga Útil" del nodo)
struct Paciente {
    int identificacion;  // Documento de identidad del paciente
    string nombre;       // Nombre completo 
    int edad;            // Edad del paciente
    string diagnostico;  // Motivo de consulta o diagnóstico
};

// Estructura del Nodo para la lista simplemente enlazada
struct Nodo {
    Paciente paciente;   // Datos integrados del paciente
    Nodo* siguiente;     // Puntero que enlazará a este nodo con el consecutivo en memoria
};

// Función para registrar (Se realizará una inserción al final de la lista)
// Pasamos el puntero 'lista' por referencia (*&) para poder modificar la cabeza de la lista globalmente
void registrarPaciente(Nodo*& lista) {
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

    // 1. Creación del nuevo nodo dinámicamente en memoria
    Nodo* nuevoNodo = new Nodo();
    nuevoNodo->paciente = p;           // Guardamos los datos recibidos
    nuevoNodo->siguiente = nullptr;    // Como irá al final, no apunta a nada todavía

    // 2. Comprobar si la lista está vacía
    if (lista == nullptr) {
        lista = nuevoNodo; // El nuevo nodo se convierte en el primer y único elemento (cabeza)
    } else {
        // 3. Si ya existen elementos, debemos recorrer la lista hasta el último nodo
        Nodo* temporal = lista; // Puntero auxiliar para no perder el inicio de la lista
        while (temporal->siguiente != nullptr) {
            temporal = temporal->siguiente; // Avanzamos al siguiente eslabón
        }
        // Cuando temporal->siguiente sea nullptr, significa que llegamos al final
        temporal->siguiente = nuevoNodo; // Enlazamos el antiguo último nodo con el nuevo
    }
    cout << "Paciente registrado con exito!" << endl;
}

// Función para mostrar por pantalla todos los registros
// Aquí solo pasamos 'lista' por valor, ya que no vamos a modificar los enlaces primarios, solo a iterar
void listarPacientes(Nodo* lista) {
    // Si la cabeza (el inicio de la lista) es nulo, la lista está vacía
    if (lista == nullptr) {
        cout << "\nNo hay pacientes registrados en el sistema." << endl;
        return;
    }

    cout << "\n--- Lista de Pacientes ---" << endl;
    
    // Utilizamos un iterador temporal y lo ubicamos al inicio
    Nodo* temporal = lista;
    
    // Iteramos nodo por nodo mientras no nos salgamos del último eslabón
    while (temporal != nullptr) {
        // Imprimimos la data
        cout << "ID: " << temporal->paciente.identificacion 
             << " | Nombre: " << temporal->paciente.nombre 
             << " | Edad: " << temporal->paciente.edad 
             << " | Diagnostico: " << temporal->paciente.diagnostico << endl;
             
        // Movemos el iterador "temporal" al nodo que sigue ("paso adelante")
        temporal = temporal->siguiente;
    }
}

// Función para modificar los datos de un paciente basado en su ID.
// La modificamos _in situ_, es decir, sin crear un nuevo nodo.
void modificarPaciente(Nodo* lista) {
    // Protección inicial: si la lista no existe, no busques nada.
    if (lista == nullptr) {
        cout << "\nNo hay pacientes registrados." << endl;
        return;
    }

    int id;
    cout << "\nIngrese el ID del paciente a modificar: ";
    cin >> id;

    // Nuestro puntero para recorrer pacientemente
    Nodo* temporal = lista;
    bool encontrado = false; // Bandera o flag para verificar si tuvimos éxito

    // Ciclo principal de búsqueda
    while (temporal != nullptr) {
        // ¿Encontramos el ID que nos pasaste?
        if (temporal->paciente.identificacion == id) {
            // ¡Eureka! Solicitamos los nuevos valores.
            // Sobreescribimos directamente a través del puntero temporal.
            cout << "Paciente encontrado. Ingrese los nuevos datos:" << endl;
            cin.ignore();
            cout << "Nuevo Nombre (actual: " << temporal->paciente.nombre << "): ";
            getline(cin, temporal->paciente.nombre);
            
            cout << "Nueva Edad (actual: " << temporal->paciente.edad << "): ";
            cin >> temporal->paciente.edad;
            cin.ignore(); // Limpiador de buffer previo a un getline()
            
            cout << "Nuevo Diagnostico (actual: " << temporal->paciente.diagnostico << "): ";
            getline(cin, temporal->paciente.diagnostico);
            
            cout << "Paciente modificado exitosamente." << endl;
            encontrado = true; // Levantamos la bandera de éxito
            break; // Rompemos el bucle pues ya hicimos lo que vinimos a hacer (optimización)
        }
        // Saltamos de nodo por si no hubo match en el 'if'
        temporal = temporal->siguiente;
    }

    // Mostramos mensaje de error si nunca encontramos el ID (bandera sigue baja)
    if (!encontrado) {
        cout << "Error: No se encontro ningun paciente con el ID proporcionado." << endl;
    }
}

// Función súper importante para borrar de la lista dinámica un nodo sin perder enlaces de memoria.
// Debe usar parámetro por referencia, por si tenemos que borrar "la cabeza" de la lista.
void eliminarPaciente(Nodo*& lista) {
    if (lista == nullptr) {
        cout << "\nNo hay pacientes registrados." << endl;
        return;
    }

    int id;
    cout << "\nIngrese el ID del paciente a eliminar: ";
    cin >> id;

    Nodo* temporal = lista;     // Apunta al nodo actual a chequear
    Nodo* anterior = nullptr;   // Mantendrá rastros del nodo 'justo antes de' temporal
    bool encontrado = false;

    // Recorrido clásico
    while (temporal != nullptr) {
        // Si hay una coincidencia con el ID de la solicitud
        if (temporal->paciente.identificacion == id) {
            // Caso 1: ¡El nodo a borrar es el primero en la lista!
            if (anterior == nullptr) {
                lista = temporal->siguiente; // La lista ahora arranca un lugar adelante "dejando suelto" al nodo actual
            } else { 
                // Caso 2: El nodo a borrar está en "el vientre" o "la cola" de la lista.
                // Le decimos al de atrás que ya no salte al temporal (que va a morir), sino al de adelante del temporal.
                // Es como puentearlo ("ByPass")
                anterior->siguiente = temporal->siguiente;
            }
            
            // Destruimos explícitamente el objeto guardado en la memoria en el Heap
            delete temporal;
            cout << "Paciente eliminado del sistema." << endl;
            encontrado = true;
            break; // No seguimos iterando sobre un puntero borrado (dangling pointer).
        }
        
        // El 'anterior' actualiza su posición al nodo que recién revisamos
        anterior = temporal;
        // Avanzamos 'temporal' para que se vuelva el próximo nodo en evaluar
        temporal = temporal->siguiente;
    }

    if (!encontrado) {
        cout << "Error: No se encontro ningun paciente con el ID proporcionado." << endl;
    }
}

int main() {
    Nodo* listaPacientes = nullptr;
    int opcion;

    do {
        cout << "\n===================================" << endl;
        cout << "      SISTEMA CLINICO LOCAL" << endl;
        cout << "===================================" << endl;
        cout << "1. Registrar paciente" << endl;
        cout << "2. Modificar paciente" << endl;
        cout << "3. Eliminar paciente" << endl;
        cout << "4. Listar pacientes" << endl;
        cout << "5. Salir" << endl;
        cout << "Ingrese una opcion: ";
        cin >> opcion;

        switch (opcion) {
            case 1:
                registrarPaciente(listaPacientes);
                break;
            case 2:
                modificarPaciente(listaPacientes);
                break;
            case 3:
                eliminarPaciente(listaPacientes);
                break;
            case 4:
                listarPacientes(listaPacientes);
                break;
            case 5:
                cout << "Saliendo del sistema..." << endl;
                break;
            default:
                cout << "Opcion invalida. Intente de nuevo." << endl;
        }
    } while (opcion != 5);

    // Bucle para prevenir filtraciones de memoria (Memory Leaks).
    // Antes de apagar el programa (que el sistema borre nuestro espacio del stack)
    // eliminamos manualmente los pedazos de memoria pedidos interactivamente al Heap.
    while (listaPacientes != nullptr) {
        Nodo* temporal = listaPacientes;             // Cogemos la cabeza de lista
        listaPacientes = listaPacientes->siguiente;  // Movemos la cabeza de referencia una posicion atras
        delete temporal;                             // Exterminamos a la que ahora es huerfana (que guardamos la posicion en temporal)
    }

    return 0;
}
