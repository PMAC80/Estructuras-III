from src.gui.consola import ConsolaReal
from tests.e2e.ayudas_gui import ConsolaFake


def test_consolaFakeDevuelveEntradasProgramadasYCapturaSalida():
    consola = ConsolaFake(["Ana", "ana@example.com"])

    assert consola.leer("Nombre: ") == "Ana"
    assert consola.leer("Email: ") == "ana@example.com"
    consola.escribir("Registro exitoso.")

    assert "Nombre: " in consola.texto
    assert "Email: " in consola.texto
    assert "Registro exitoso." in consola.texto


def test_consolaRealDelegaEnInputYPrint(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda mensaje="": "respuesta")
    consola = ConsolaReal()

    assert consola.leer("Pregunta: ") == "respuesta"
    consola.escribir("Mensaje de salida")

    assert "Mensaje de salida" in capsys.readouterr().out
