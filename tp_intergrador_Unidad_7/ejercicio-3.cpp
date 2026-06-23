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
    void preordenRec(Nodo* actual);
    void postordenRec(Nodo* actual);
    void liberarRec(Nodo* actual);
    void borrarRec(Nodo*& actual, char valor);
    Nodo*& encontrarMinimo(Nodo*& nodo);

public:
    ABB();                    // Constructor
    ~ABB();                   // Destructor
    void insertar(char valor);
    void borrar(char valor);
    
    // Recorridos
    void preorden();
    void inorden();
    void postorden();
};


// ═══════════════════════════════════════════════════════════════
// 3. IMPLEMENTACIÓN DE LOS MÉTODOS
// ═══════════════════════════════════════════════════════════════

// Constructor: árbol vacío
ABB::ABB() : raiz(nullptr) {}

// Destructor: libera toda la memoria (postorden)
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
// RECORRIDOS
// ───────────────────────────────────────────────────────────────

// PREORDEN: Raíz → Izq → Der
void ABB::preorden() {
    std::cout << "  Preorden:  ";
    preordenRec(raiz);
    std::cout << std::endl;
}

void ABB::preordenRec(Nodo* actual) {
    if (actual == nullptr) return;
    std::cout << actual->dato << " ";   // 1. Imprimo la raíz
    preordenRec(actual->izq);           // 2. Bajo a la izquierda
    preordenRec(actual->der);           // 3. Bajo a la derecha
}

// INORDEN: Izq → Raíz → Der (imprime ordenado)
void ABB::inorden() {
    std::cout << "  Inorden:   ";
    inordenRec(raiz);
    std::cout << std::endl;
}

void ABB::inordenRec(Nodo* actual) {
    if (actual == nullptr) return;
    inordenRec(actual->izq);            // 1. Bajo a la izquierda
    std::cout << actual->dato << " ";   // 2. Imprimo la raíz
    inordenRec(actual->der);            // 3. Bajo a la derecha
}

// POSTORDEN: Izq → Der → Raíz
void ABB::postorden() {
    std::cout << "  Postorden: ";
    postordenRec(raiz);
    std::cout << std::endl;
}

void ABB::postordenRec(Nodo* actual) {
    if (actual == nullptr) return;
    postordenRec(actual->izq);          // 1. Bajo a la izquierda
    postordenRec(actual->der);          // 2. Bajo a la derecha
    std::cout << actual->dato << " ";   // 3. Imprimo la raíz
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
// 4. MAIN: Resuelve los ejercicios 1, 2 y 3 del TP
// ═══════════════════════════════════════════════════════════════
int main() {
    ABB arbol;
    std::string letras = "G B Q A C K F P D E R H";

    // ─────────────────────────────────────────────────────────
    // EJERCICIO 1: Construir el ABB
    // ─────────────────────────────────────────────────────────
    std::cout << "==============================================" << std::endl;
    std::cout << " EJERCICIO 1: Construir el ABB" << std::endl;
    std::cout << "==============================================" << std::endl;
    std::cout << "Insertando letras: " << letras << std::endl;

    for (char c : letras) {
        if (c != ' ') {
            arbol.insertar(c);
        }
    }

    std::cout << "Arbol construido. Verificacion con inorden:" << std::endl;
    arbol.inorden();
    std::cout << std::endl;

    // ─────────────────────────────────────────────────────────
    // EJERCICIO 3: Recorridos del árbol original
    // (Lo pongo antes del ejercicio 2 para mostrar el árbol "limpio")
    // ─────────────────────────────────────────────────────────
    std::cout << "==============================================" << std::endl;
    std::cout << " EJERCICIO 3: Recorridos del arbol original" << std::endl;
    std::cout << "==============================================" << std::endl;
    arbol.preorden();
    arbol.inorden();
    arbol.postorden();
    std::cout << std::endl;

    // ─────────────────────────────────────────────────────────
    // EJERCICIO 2: Extracciones iterativas
    // ─────────────────────────────────────────────────────────
    std::cout << "==============================================" << std::endl;
    std::cout << " EJERCICIO 2: Extracciones iterativas" << std::endl;
    std::cout << "==============================================" << std::endl;

    // a) Borrar E (nodo hoja)
    std::cout << "a) Borrar 'E':" << std::endl;
    arbol.borrar('E');
    arbol.inorden();

    // b) Borrar C (nodo con 2 hijos)
    std::cout << "b) Borrar 'C':" << std::endl;
    arbol.borrar('C');
    arbol.inorden();

    // c) Borrar G (raíz, con 2 hijos)
    std::cout << "c) Borrar 'G':" << std::endl;
    arbol.borrar('G');
    arbol.inorden();

    std::cout << std::endl;
    std::cout << "Arbol final despues de todas las extracciones:" << std::endl;
    std::cout << "  Preorden:  "; arbol.preorden();
    std::cout << "  Inorden:   "; arbol.inorden();
    std::cout << "  Postorden: "; arbol.postorden();

    return 0;
}