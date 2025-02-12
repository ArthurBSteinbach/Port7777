import threading
import socket

clients = []
banned_ips = set()  # Conjunto para armazenar IPs banidos

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
    username = client.recv(2048).decode('utf-8')
    while True:
        try:
            msg = client.recv(2048)
            if not msg:
                break  
            msg = msg.decode('utf-8')
            if msg.startswith("!"):
                handle_command(msg, client, addr)
            else:
                broadcast(f"{username}: {msg}".encode('utf-8'), client)
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break
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
        print(f"Cliente desconectado. Total de clientes: {len(clients)}")

def handle_command(command, client, addr):
    global banned_ips
    if command == "!cls":
        for c in clients:
            c.send("!clear".encode('utf-8'))  # Envia o comando para limpar o chat
    elif command.startswith("!kick"):
        username = command.split(" ")[1]
        for c in clients:
            c.send(f"!kick {username}".encode('utf-8'))  # Envia o comando para expulsar o usuário
    elif command.startswith("!ban"):
        ip = command.split(" ")[1]
        banned_ips.add(ip)
        broadcast(f"IP {ip} foi banido.".encode('utf-8'), client)
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
            clients.append(client)
            print(f'Cliente conectado com sucesso. IP: {addr}')

            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")

main()