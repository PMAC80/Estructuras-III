// Importación de librerías necesarias para entrada/salida y manejo de cadenas
#include <iostream>
#include <string>

// Uso del espacio de nombres estándar para evitar escribir std:: constantemente
using namespace std;

// Estructura que representa a un cliente en el sistema
struct Cliente {
    string nombre;       // Nombre del cliente
    int tiempo_espera;   // Tiempo de espera estimado en minutos
};

// Constante que define el máximo número de clientes. Funciona como límite del arreglo estático.
const int MAX_CLIENTES = 100; 

// Clase que maneja el sistema de turnos utilizando un arreglo estático circular
class TurnosArregloSimple {
private:
    // Arreglo estático de tipo Cliente que funciona como la cola de espera
    Cliente cola[MAX_CLIENTES]; 
    int frente;     // Índice que marca el primer elemento de la cola (el próximo a ser atendido)
    int final;      // Índice que indica en qué posición ingresará el nuevo elemento
    int cantidad;   // Lleva el control de la cantidad actual de elementos en la cola

    // Función recursiva privada para recorrer y mostrar la información de la cola
    void recursividad_espera(int indice, int elementos_restantes) {
        // Caso Base: Si no quedan elementos por imprimir, se detiene la recursividad
        if (elementos_restantes == 0) {
            return;
        }

        // Procesamiento: Imprimo el nombre y el tiempo de espera del cliente en el índice actual
        cout << "- " << cola[indice].nombre << " | Espera: " << cola[indice].tiempo_espera << " min\n";

        // Llamada Recursiva: Movemos el índice a la siguiente posición. 
        // Se usa (indice + 1) % MAX_CLIENTES para simular una Cola Circular (al llegar a 100, vuelve al índice 0)
        recursividad_espera((indice + 1) % MAX_CLIENTES, elementos_restantes - 1);
    }

public:
    // Constructor de la clase: inicializa los índices y la cantidad en 0
    TurnosArregloSimple() {
        frente = 0;
        final = 0;
        cantidad = 0;
    }

    // Método para registrar/encolar a un nuevo cliente
    void registrar_cliente(string nombre, int tiempo) {
        // Si la cola está llena, no se puede registrar (Validación)
        if (cantidad >= MAX_CLIENTES) {
            cout << "Error: La sala de espera esta a su maxima capacidad!\n";
            return;
        }

        // Se asigna la información en la posición que marca 'final'
        cola[final].nombre = nombre;
        cola[final].tiempo_espera = tiempo;
        
        // Se incrementa 'final' de forma circular y se aumenta la cantidad
        final = (final + 1) % MAX_CLIENTES;
        cantidad++;
        
        cout << "Registrado: " << nombre << endl;
    }

    // Método para llamar/desencolar al próximo cliente de la cola
    void llamar_proximo(int box) {
        // Validación: No se puede llamar a nadie si la cola está vacía
        if (cantidad == 0) {
            cout << "\n[Box " << box << "] No hay clientes en espera.\n";
            return;
        }

        // Se obtiene el cliente guardado en la posición 'frente'
        Cliente llamado = cola[frente];
        
        // Se avanza el 'frente' de manera circular y se decrementa la cantidad
        frente = (frente + 1) % MAX_CLIENTES; 
        cantidad--;

        // Se muestra la información del cliente llamado
        cout << "\n>>> PROXIMO CLIENTE: " << llamado.nombre << " - Box Nro: " << box << " <<<\n";
    }

    // Método público que invoca a la función recursiva privada para mostrar todos
    void mostrar_tiempos_espera() {
        cout << "\n--- Tiempo de Espera (Recursivo - Arreglo Estatico) ---\n";
        // Si no hay elementos, se indica que la lista está vacía
        if (cantidad == 0) {
            cout << "Lista vacia.\n";
            return;
        }

        // Se inicia la recursión pasando el índice de inicio ('frente') y la cantidad de elementos
        recursividad_espera(frente, cantidad);
    }
};

// Función principal del programa
int main() {
    // Creación de una instancia del sistema de turnos
    TurnosArregloSimple sistema;
    
    // Registro de 3 clientes de prueba
    sistema.registrar_cliente("Ana Perez", 15);
    sistema.registrar_cliente("Carlos Gomez", 10);
    sistema.registrar_cliente("Maria Lopez", 25);

    // Muestra cómo quedó la lista de espera
    sistema.mostrar_tiempos_espera();
    
    // Atiende (desencola) al primer cliente y lo envía al Box 1
    sistema.llamar_proximo(1);
    
    // Muestra la lista de espera actualizada
    sistema.mostrar_tiempos_espera();

    return 0;
}
