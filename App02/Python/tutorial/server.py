import Pyro4
import subprocess
from threading import Thread


@Pyro4.expose
class Hello(object):
    def hi(self):
        return "Hi"

def startNameServer():
    subprocess.run(["pyro4-ns"])

def main():
    Thread(target=startNameServer, daemon=True).start()
    daemon = Pyro4.Daemon()
    uri = daemon.register(Hello)

    name_server = Pyro4.locateNS()
    name_server.register("Hello", uri)

    daemon.requestLoop()

if __name__ == "__main__":
    main()