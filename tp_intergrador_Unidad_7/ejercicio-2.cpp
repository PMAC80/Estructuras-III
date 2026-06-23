#include <iostream>
#include <string>

// ═══════════════════════════════════════════════════════════════
// 1. DEFINICIÓN DEL NODO (la cajita)
// ═══════════════════════════════════════════════════════════════
struct Nodo 
{
    char dato;
    Nodo* izq;
    Nodo* der;

    // Constructor: crea el nodo con un valor y los hijos vacíos
    Nodo(char val) : dato(val), izq(nullptr), der(nullptr) {}
};


// ═══════════════════════════════════════════════════════════════
// 2. CLASE ABB (el árbol completo)
// ═══════════════════════════════════════════════════════════════
class ABB 
{
private:
    Nodo* raiz;

    // Métodos privados (recursivos, los "obreros")
    void insertarRec(Nodo*& actual, char valor);
    void inordenRec(Nodo* actual);
    void liberarRec(Nodo* actual);
    void borrarRec(Nodo*& actual, char valor);
    Nodo*& encontrarMinimo(Nodo*& nodo);

public:
    ABB();                    // Constructor
    ~ABB();                   // Destructor
    void insertar(char valor);
    void mostrarOrdenado();
    void borrar(char valor);
};


// ═══════════════════════════════════════════════════════════════
// 3. IMPLEMENTACIÓN DE LOS MÉTODOS
// ═══════════════════════════════════════════════════════════════

// Constructor: árbol vacío
ABB::ABB() : raiz(nullptr) {}

// Destructor: libera toda la memoria
ABB::~ABB() {
    liberarRec(raiz);
}

void ABB::liberarRec(Nodo* actual) {
    if (actual == nullptr) return;
    liberarRec(actual->izq);
    liberarRec(actual->der);
    delete actual;
}

// ───────────────────────────────────────────────────────────────
// INSERTAR
// ───────────────────────────────────────────────────────────────
void ABB::insertar(char valor) {
    insertarRec(raiz, valor);
}

void ABB::insertarRec(Nodo*& actual, char valor) {
    if (actual == nullptr) {
        actual = new Nodo(valor);
        return;
    }
    if (valor < actual->dato) {
        insertarRec(actual->izq, valor);
    } 
    else if (valor > actual->dato) {
        insertarRec(actual->der, valor);
    }
    // Si es igual, no hacemos nada (no se permiten duplicados)
}

// ───────────────────────────────────────────────────────────────
// MOSTRAR EN ORDEN (para verificar)
// ───────────────────────────────────────────────────────────────
void ABB::mostrarOrdenado() {
    std::cout << "  Inorden: ";
    inordenRec(raiz);
    std::cout << std::endl;
}

void ABB::inordenRec(Nodo* actual) {
    if (actual == nullptr) return;
    inordenRec(actual->izq);
    std::cout << actual->dato << " ";
    inordenRec(actual->der);
}

// ───────────────────────────────────────────────────────────────
// BORRAR
// ───────────────────────────────────────────────────────────────
void ABB::borrar(char valor) {
    borrarRec(raiz, valor);
}

// Encuentra el nodo mínimo (el más a la izquierda)
Nodo*& ABB::encontrarMinimo(Nodo*& nodo) {
    if (nodo->izq == nullptr) {
        return nodo;
    }
    return encontrarMinimo(nodo->izq);
}

void ABB::borrarRec(Nodo*& actual, char valor) {
    // No se encontró el valor
    if (actual == nullptr) {
        std::cout << "  [!] Valor '" << valor << "' no encontrado." << std::endl;
        return;
    }

    // Buscar el nodo
    if (valor < actual->dato) {
        borrarRec(actual->izq, valor);
    } 
    else if (valor > actual->dato) {
        borrarRec(actual->der, valor);
    }
    else {
        // ═══ ¡Encontramos el nodo a borrar! ═══

        // CASO 1: Nodo hoja (0 hijos)
        if (actual->izq == nullptr && actual->der == nullptr) {
            delete actual;
            actual = nullptr;
            return;
        }

        // CASO 2: Solo hijo derecho
        if (actual->izq == nullptr) {
            Nodo* temp = actual;
            actual = actual->der;
            delete temp;
            return;
        }

        // CASO 2: Solo hijo izquierdo
        if (actual->der == nullptr) {
            Nodo* temp = actual;
            actual = actual->izq;
            delete temp;
            return;
        }

        // CASO 3: Dos hijos
        // Buscamos el sucesor inorden (mínimo del subárbol derecho)
        Nodo*& sucesor = encontrarMinimo(actual->der);
        
        // Copiamos su valor al nodo actual
        actual->dato = sucesor->dato;
        
        // Borramos el sucesor original (que ya no tiene hijo izquierdo)
        borrarRec(actual->der, sucesor->dato);
    }
}


// ═══════════════════════════════════════════════════════════════
// 4. MAIN: Resuelve los ejercicios 1 y 2 del TP
// ═══════════════════════════════════════════════════════════════
int main() {
    ABB arbol;
    std::string letras = "G B Q A C K F P D E R H";

    std::cout << "=== EJERCICIO 1: Construir el ABB ===" << std::endl;
    std::cout << "Insertando letras: " << letras << std::endl;

    for (char c : letras) {
        if (c != ' ') {
            arbol.insertar(c);
        }
    }

    std::cout << "Arbol inicial:" << std::endl;
    arbol.mostrarOrdenado();
    std::cout << std::endl;

    std::cout << "=== EJERCICIO 2: Extracciones iterativas ===" << std::endl;

    // a) Borrar E
    std::cout << "a) Borrar 'E':" << std::endl;
    arbol.borrar('E');
    arbol.mostrarOrdenado();

    // b) Borrar C
    std::cout << "b) Borrar 'C':" << std::endl;
    arbol.borrar('C');
    arbol.mostrarOrdenado();

    // c) Borrar G
    std::cout << "c) Borrar 'G':" << std::endl;
    arbol.borrar('G');
    arbol.mostrarOrdenado();

    return 0;
}