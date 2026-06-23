//Ejercicio 1. Construye un árbol binario de búsqueda a partir de la siguiente lista: G B Q A C K F P D E R H 

#include <iostream>
#include <string>

// 1. Definimos el nodo
struct Nodo 
{
    char dato;
    Nodo* izq;
    Nodo* der;

    Nodo(char val) : dato(val), izq(nullptr), der(nullptr) {}
};

class ABB {
private:
    Nodo* raiz;

    // Función recursiva para insertar
    // OJO: Nodo*& es "referencia a puntero", así modificamos el árbol original
    void insertarRec(Nodo*& actual, char valor) {
        // CASO BASE: encontramos un hueco, creamos el nodo
        if (actual == nullptr) {
            actual = new Nodo(valor);
            return;
        }

        // PASO RECURSIVO: decidimos a qué lado bajar
        if (valor < actual->dato) {
            insertarRec(actual->izq, valor);   // Baja por la izquierda
        } else if (valor > actual->dato) {
            insertarRec(actual->der, valor);   // Baja por la derecha
        }
        // Si es igual, no hacemos nada (los ABB típicos no aceptan duplicados)
    }

    // Recorrido Inorden: Izq - Raíz - Der (imprime ordenado)
    void inordenRec(Nodo* actual) {
        if (actual == nullptr) return;
        inordenRec(actual->izq);
        std::cout << actual->dato << " ";
        inordenRec(actual->der);
    }

    // Destructor recursivo (¡no te olvides de liberar memoria!)
    void liberarRec(Nodo* actual) {
        if (actual == nullptr) return;
        liberarRec(actual->izq);
        liberarRec(actual->der);
        delete actual;
    }

public:
    ABB() : raiz(nullptr) {}

    ~ABB() { liberarRec(raiz); }

    void insertar(char valor) {
        insertarRec(raiz, valor);
    }

    void mostrarOrdenado() {
        std::cout << "Inorden: ";
        inordenRec(raiz);
        std::cout << std::endl;
    }
};

int main() {
    ABB arbol;
    std::string letras = "G B Q A C K F P D E R H";

    // Insertamos letra por letra (saltándonos los espacios)
    for (char c : letras) 
    {
        if (c != ' ') 
        {
            arbol.insertar(c);
        }
    }

    arbol.mostrarOrdenado();  // Debería imprimir: A B C D E F G H K P Q R

    return 0;
}
