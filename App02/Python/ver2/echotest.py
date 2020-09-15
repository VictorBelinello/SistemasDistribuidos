from Pyro5.api import Proxy
import Pyro5.errors

if __name__ == "__main__":
    print("Obtendo referencia para objeto remoto...")
   
    uri = "PYRONAME:test.echoserver"
    echo = Proxy(uri)
    print("Referência obtida ")

    try:
        echo.error()
    except Exception:
        print("".join(Pyro5.errors.get_pyro_traceback()))
    echo.shutdown()