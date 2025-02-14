import threading
import socket

clients = []
banned_ips = set()  # Conjunto para armazenar IPs banidos
usernames = {}  # Dicionário para armazenar os nomes de usuário associados aos clientes

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        ip = s.getsockname()[0]  
        s.close()
        return ip
    except Exception as e:
        print(f"Erro ao obter o IP: {e}")
        return None

ip_user = get_local_ip()
if not ip_user:
    print("Não foi possível obter o IP. Encerrando o servidor.")
    exit()

print(f"Seu IP é: {ip_user}")

def handle_client(client, addr):
    try:
        full_username = client.recv(2048).decode('utf-8')
        usernames[client] = full_username 
        broadcast(f"!join:{full_username}".encode('utf-8'), client)  
        update_user_list()  

        # Envia uma mensagem de boas-vindas ao usuário
        client.send(f"Bem-vindo, {full_username}!".encode('utf-8'))

        while True:
            msg = client.recv(2048)
            if not msg:
                break  
            msg = msg.decode('utf-8')
            if msg.startswith("!"):
                handle_command(msg, client, addr)
            else:
                broadcast(f"{full_username}: {msg}".encode('utf-8'), client)  
    except Exception as e:
        print(f"Erro ao receber mensagem: {e}")
    finally:
        remove_client(client)

def broadcast(msg, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(msg)
            except Exception as e:
                print(f"Erro ao enviar mensagem para um cliente: {e}")
                remove_client(client)

def remove_client(client):
    if client in clients:
        clients.remove(client)
        if client in usernames:
            username = usernames[client]
            del usernames[client]
            broadcast(f"!leave:{username}".encode('utf-8'), client) 
            update_user_list()  
        client.close()  
        print(f"Cliente desconectado. Total de clientes: {len(clients)}")

def update_user_list():
    user_list = ",".join(usernames.values())
    for client in clients:
        try:
            client.send(f"!users:{user_list}".encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar lista de usuários: {e}")

def handle_command(command, client, addr):
    global banned_ips
    if command == "!cls":
        for c in clients:
            c.send("!clear".encode('utf-8')) 

    elif command.startswith("!kick"):
        username = command.split(" ")[1]
        broadcast(f"IP {username} kickado.".encode('utf-8'), client)
        for c in clients:
            c.send(f"!kick {username}".encode('utf-8'))  

    elif command.startswith("!ban"):
        parts = command.split(" ")
        if len(parts) > 1:
            username = parts[1]
            for c in clients:
                c.send(f"!ban {username}".encode('utf-8'))  
            banned_ips.add(addr[0])
            print(f"IP {addr[0]} foi banido.")

    elif command.startswith("!unbanip"):
        ip = command.split(" ")[1]
        banned_ips.discard(ip)
        broadcast(f"IP {ip} foi desbanido.".encode('utf-8'), client)

    else:
        client.send("Comando desconhecido.".encode('utf-8'))

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Iniciou o servidor de bate-papo")

    try:
        server.bind((ip_user, 7777))
        server.listen()
        print("Aguardando conexões...")
    except Exception as e:
        print(f'\nNão foi possível iniciar o servidor: {e}\n')
        return

    while True:
        try:
            client, addr = server.accept()
            if addr[0] in banned_ips:  
                client.send("!banned".encode('utf-8'))  
                client.close()
                print(f"Conexão rejeitada: IP {addr[0]} está banido.")
            else:
                clients.append(client)
                print(f'Cliente conectado com sucesso. IP: {addr}')

                thread = threading.Thread(target=handle_client, args=(client, addr))
                thread.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    main()