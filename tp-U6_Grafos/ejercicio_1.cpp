//Dado el siguiente itinerario del recorrido de nuestro Agente de ventas que Muestra ciudades y costos asociados a, implementar el camino d emenor coste entre los nodos.
//Usar Dijkstra o Kruscal

#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <climits>
#include <algorithm>

using namespace std;

class Grafo {
private:
    map<char, vector<pair<char, int>>> grafo;
    
public:
    void agregarArista(char u, char v, int peso) {
        grafo[u].push_back({v, peso});
        grafo[v].push_back({u, peso});
    }
    
    map<char, int> dijkstra(char inicio, map<char, char>& predecesores) {
        map<char, int> distancias;
        
        // Inicializar distancias
        for (auto& par : grafo) {
            distancias[par.first] = INT_MAX;
        }
        distancias[inicio] = 0;
        
        // Cola de prioridad: (distancia, nodo)
        priority_queue<pair<int, char>, vector<pair<int, char>>, greater<pair<int, char>>> cola;
        cola.push({0, inicio});
        
        while (!cola.empty()) {
            int distActual = cola.top().first;
            char nodoActual = cola.top().second;
            cola.pop();
            
            if (distActual > distancias[nodoActual]) continue;
            
            for (auto& vecino : grafo[nodoActual]) {
                char v = vecino.first;
                int peso = vecino.second;
                
                if (distancias[nodoActual] + peso < distancias[v]) {
                    distancias[v] = distancias[nodoActual] + peso;
                    predecesores[v] = nodoActual;
                    cola.push({distancias[v], v});
                }
            }
        }
        
        return distancias;
    }
};

int main() {
    Grafo grafo;
    
    // Agregar aristas del grafo
    grafo.agregarArista('A', 'B', 3);
    grafo.agregarArista('A', 'C', 5);
    grafo.agregarArista('A', 'D', 9);
    grafo.agregarArista('A', 'H', 10);
    grafo.agregarArista('B', 'C', 5);
    grafo.agregarArista('B', 'D', 8);
    grafo.agregarArista('B', 'E', 6);
    grafo.agregarArista('B', 'H', 6);
    grafo.agregarArista('C', 'E', 4);
    grafo.agregarArista('C', 'F', 7);
    grafo.agregarArista('C', 'G', 9);
    grafo.agregarArista('D', 'E', 12);
    grafo.agregarArista('D', 'G', 3);
    grafo.agregarArista('D', 'H', 2);
    grafo.agregarArista('E', 'F', 1);
    grafo.agregarArista('E', 'G', 15);
    grafo.agregarArista('F', 'H', 9);
    grafo.agregarArista('G', 'H', 14);
    
    cout << "=== DIJKSTRA - Camino de menor costo ===" << endl;
    
    map<char, char> predecesores;
    map<char, int> distancias = grafo.dijkstra('A', predecesores);
    
    cout << "\nCaminos desde A:" << endl;
    for (auto& par : distancias) {
        cout << "A -> " << par.first << ": " << par.second << endl;
    }
    
    return 0;
}