import sys, socket, threading, time, re

class Port:
    number = ""
    state = ""
    banner = ""
    def __init__(self, number, state) -> None:
        self.number = number
        self.state = state
        pass

class Host:
    ip_addr = ""
    ports = []
    def __init__(self, ip_addr: str) -> None:
        self.ip_addr = ip_addr
        pass

    def add_port(self, port_number, state) -> None:
        self.ports.append(Port(port_number, state))

    def get_open_ports(self) -> []:
        open_port_list = [p for p in self.ports if p.state == "Open"]

        return open_port_list    
    def banner_grab(self, port: Port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((self.ip_addr, int(port.number)))
            s.send(b'GET / HTTP/1.1\r\nHost: google.com\r\n\r\n')
            banner = s.recv(1024).decode()
            banner = banner.split('\n')[0]
            port.banner = banner.strip()
            

        s.close()



def scan_port(host: Host, port):

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host.ip_addr, port))

        if result == 0:
            port = Port(port, "Open")
            host.ports.append(port)
            host.banner_grab(port)

        else:
            host.add_port(port, "Closed")
            #print(f"{port} closed")

            pass
        
        sock.close()
        return 0
    except Exception as E:
        print(E)
        return 1

def ip_validator(host) -> bool:
    ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    if re.match(ip_pattern, host):
        return True
    return False
    

def scan_host(host: Host, ports):
    print(f"Escaneando host {host.ip_addr}...")

    ports = range(1, 2000)
    threads = []

    for port in ports:
        t = threading.Thread(target=scan_port, args=(host,port))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scanner_portas.py <host> <portas separadas por vírgula>")
        sys.exit(1)

    if not ip_validator(sys.argv[1]):
        print(f"O ip {sys.argv[1]} é invalido.")
        sys.exit(1)
        

    host = Host(sys.argv[1])
    ports = [int(p) for p in sys.argv[2].split(',')]

    scan_host(host, ports)
    print(host.get_open_ports())
    for i in host.get_open_ports():
        servicep = ""
        if i.banner == "":
            servicep = "Could not Fetch"
        else:
            servicep = i.banner

        print(f"""Port {i.number:<7}  {servicep}""")


    