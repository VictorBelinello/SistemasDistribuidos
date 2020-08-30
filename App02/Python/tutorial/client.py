import Pyro4

def main():
    name_server = Pyro4.locateNS()
    uri = name_server.lookup("Hello")
    obj = Pyro4.Proxy(uri)
    print(obj.hi())

if __name__ == "__main__":
    main()