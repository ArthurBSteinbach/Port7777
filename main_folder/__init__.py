import customtkinter as ctk
import socket
import threading
import sys

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_root() 
        self._centralize_window()

        self.client = None
        self.server_ip = None
        self.server_port = 7777
        self.username = None
        self.rank = None
        self.user_list = []  # Lista de usuários online

        self.enter_server_frame()

    def run(self):
        self.mainloop()
        
    def config_root(self):
        self.configure(fg_color="#635985") 
        self.title("Port777:Main")

    def _centralize_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.window_width = screen_width // 2 
        self.window_height = screen_height // 2

        x = (screen_width // 2) - (self.window_width // 1)
        y = (screen_height // 2) - (self.window_height // 1)

        self.geometry(f"{screen_width}x{screen_height}+{x}+{y}")

    def enter_server_frame(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#393053")
        self.main_frame.pack(pady=self.window_width//4)

        self.main_frame_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter your server", border_color="black", fg_color="white", width=290, font=("Terminal",16))
        self.main_frame_entry.grid(row=0, column=0, pady=15, padx=(15,10))

        self.main_frame_button = ctk.CTkButton(self.main_frame, text="Enter", command=self.send_server_ip, font=("Terminal",16))
        self.main_frame_button.grid(row=0, column=1, rowspan=2, padx=(10,15))

        self.main_frame_username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter your username", border_color="black", fg_color="white", width=290, font=("Terminal",16))
        self.main_frame_username_entry.grid(row=1, column=0, pady=(0,15), padx=(15,10))

    def send_server_ip(self):
        self.server_ip = self.main_frame_entry.get()
        self.username = self.main_frame_username_entry.get()

        if not self.server_ip or "." not in self.server_ip:
            self.main_frame_entry.configure(placeholder_text="Invalid IP, try again")
            self.main_frame_entry.delete(0, ctk.END)
            self.main_frame_button.configure(fg_color="#CD1818")
            return

        if not self.username:
            self.main_frame_username_entry.configure(placeholder_text="Username is required")
            self.main_frame_username_entry.delete(0, ctk.END)
            self.main_frame_button.configure(fg_color="#CD1818")
            return

        if any(name in self.username.lower() for name in ["admin", "adm", "administrador", "administrator"]):
            self.main_frame_username_entry.configure(placeholder_text="Invalid username")
            self.main_frame_username_entry.delete(0, ctk.END)
            self.main_frame_button.configure(fg_color="#CD1818")
            return

        print(f"Server IP entered: {self.server_ip}")
        self.iconify()
        self.connect_to_server()  

    def open_content_frame(self):
        self.main_frame.pack_forget()

        self.frame_content = ctk.CTkFrame(self, fg_color="#B6EADA" )
        self.frame_content.pack(padx=self.window_width//4, pady=self.window_height//4, fill="both", expand=True)
        
        self.open_chat_frame()
        self.open_chat_users()
        self.open_user_info()

    def open_user_info(self):
        self.frame_users = ctk.CTkFrame(self.frame_content, fg_color="#393053")
        self.frame_users.grid(row=0,column=1)

    def open_chat_frame(self):
        self.chat_frame = ctk.CTkFrame(self.frame_content, fg_color="#393053")
        self.chat_frame.grid(row=0, column=0, pady=self.window_height // 7, padx=(20,0), sticky="nsew")

        self.chat_frame.grid_columnconfigure(0, weight=4)
        self.chat_frame.grid_columnconfigure(1, weight=1)

        # Label para exibir o nome do usuário
        self.user_label = ctk.CTkLabel(
            self.chat_frame,
            text=f"{self.username} {self.rank}",
            font=("Terminal", 16),
            text_color="white"
        )
        self.user_label.grid(row=0, column=0, pady=10, padx=10, sticky="nw")

        self.chat_scrollable_frame = ctk.CTkScrollableFrame(self.chat_frame, fg_color="#393053", height=self.window_height, width=self.window_width)
        self.chat_scrollable_frame.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

        self.chat_label = ctk.CTkLabel(
            self.chat_scrollable_frame,
            width=self.window_width // 2,
            font=("Terminal", 16),
            text="",
            anchor="nw",
            justify="left",
            text_color="white",
            wraplength=self.window_width // 2 - 30
        )
        self.chat_label.pack(expand=True, fill="both", padx=10, pady=10)

        self.chat_entry = ctk.CTkEntry(
            self.chat_frame,
            placeholder_text="Type your message",
            border_color="black",
            fg_color="white",
            font=("Terminal", 16)
        )
        self.chat_entry.grid(row=2, column=0, pady=(5, 15), padx=(15, 5), sticky="nsew")

        self.chat_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(
            self.chat_frame,
            text="Send",
            command=self.send_message,
            font=("Terminal", 16),
            fg_color="#18122B"
        )
        self.send_button.grid(row=2, column=1, pady=(5, 15), padx=(5, 15), sticky="nsew")

        self.deiconify()

    def open_chat_users(self):
        self.users_frame = ctk.CTkFrame(self.frame_content, fg_color="#393053")
        self.users_frame.grid(row=1, column=1, pady=self.window_height // 7, padx=(10, 0), sticky="nsew")

        self.users_label = ctk.CTkLabel(
            self.users_frame,
            text="Users Online",
            font=("Terminal", 16),
            text_color="white"
        )
        self.users_label.pack(pady=10)

        # Cria o users_scrollable_frame
        self.users_scrollable_frame = ctk.CTkScrollableFrame(self.users_frame, fg_color="#393053")
        self.users_scrollable_frame.pack(padx=10, pady=10)

        # Inicializa a lista de usuários
        self.update_user_list(self.user_list)

    def update_user_list(self, users):
        if not hasattr(self, 'users_scrollable_frame'):
            print("users_scrollable_frame não foi criado ainda.")
            return

        # Limpa o frame atual
        for widget in self.users_scrollable_frame.winfo_children():
            widget.destroy()

        # Adiciona os usuários à lista
        for user in users:
            user_label = ctk.CTkLabel(
                self.users_scrollable_frame,
                text=user,
                font=("Terminal", 15),
                text_color="white"
            )
            user_label.pack(pady=5)

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.title(f"Port7777:[{self.server_ip}]:Chat")
            self.client.connect((self.server_ip, self.server_port))
            print("Conectado ao servidor!")

            self.is_admin()
            full_username = f"{self.username} {self.rank}"
            
            # Envia o nome do usuário para o servidor
            self.client.send(full_username.encode('utf-8'))

            # Solicita a lista de usuários ao conectar
            self.client.send("!users".encode('utf-8'))

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True  
            thread.start()

            # Abre o frame de conteúdo
            self.open_content_frame()

            # Atualiza a lista de usuários após o frame ser criado
            self.update_user_list(self.user_list)
            
        except Exception as e:  
            print(f"Erro ao conectar: {e}")
            self.deiconify()
            self.main_frame.pack()
            self.main_frame_entry.configure(placeholder_text="Connection failed, try again")
            self.main_frame_entry.delete(0, ctk.END)
            self.main_frame_button.configure(fg_color="#CD1818")
            
    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(2048).decode('utf-8')
                if msg:
                    # Verifica se o chat_label já foi criado
                    if not hasattr(self, 'chat_label'):
                        continue  # Aguarda até que o chat_label seja criado

                    if msg == "!clear":
                        self.chat_label.configure(text="")  
                    elif msg.startswith("!kick"):
                        if msg.split(" ")[1] == self.username:
                            self.client.close()
                            self.destroy()
                            sys.exit() 
                    elif msg.startswith("!ban"):
                        if msg.split(" ")[1] == self.username:
                            self.client.close()
                            self.destroy()
                            sys.exit() 
                    elif msg == "!banned":
                        self.chat_label.configure(text="Seu IP foi banido. Você não pode se conectar novamente.")
                        self.client.close()
                        self.destroy()
                        sys.exit()
                    elif msg.startswith("!users"):
                        # Atualiza a lista de usuários
                        users = msg.split(":")[1].split(",")
                        self.user_list = users
                        self.update_user_list(self.user_list)
                    elif msg.startswith("!join:"):
                        # Novo usuário entrou no chat
                        new_user = msg.split(":")[1]
                        self.chat_label.configure(text=self.chat_label.cget("text") + f"\n**{new_user} entrou no chat**\n", text_color="white")
                        # Atualiza a lista de usuários
                        if new_user not in self.user_list:
                            self.user_list.append(new_user)
                            self.update_user_list(self.user_list)
                    elif msg.startswith("!leave:"):
                        # Usuário saiu do chat
                        left_user = msg.split(":")[1]
                        self.chat_label.configure(text=self.chat_label.cget("text") + f"\n**{left_user} saiu do chat**\n", text_color="white")
                        if left_user in self.user_list:
                            self.user_list.remove(left_user)
                            self.update_user_list(self.user_list)
                    elif " [ADMIN]" in msg:
                        if ":" in msg:
                            username_part, message_part = msg.split(":", 1)
                            if " [ADMIN]" in username_part:
                                username, rank = username_part.split(" [ADMIN]")
                                formatted_message = f"{username} [ADMIN]:{message_part}"
                                self.chat_label.configure(text=self.chat_label.cget("text") + f"\n{formatted_message}\n", text_color="red")
                        else:
                            self.chat_label.configure(text=self.chat_label.cget("text") + f"\n{msg}\n", text_color="white")
                    else:
                        self.chat_label.configure(text=self.chat_label.cget("text") + f"\n{msg}\n", text_color="white")
                else:
                    break  
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break
        self.client.close()

    def send_message(self):
        message = self.chat_entry.get()
        if message:
            if message.startswith("!"):
                self.handle_command(message)
            else:
                full_message = f"{message}"
                self.chat_label.configure(text=self.chat_label.cget("text") + f"\n{full_message}\n")
                self.chat_entry.delete(0, ctk.END)  
                try:
                    self.client.send(full_message.encode('utf-8'))
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")

    def get_user_list(self):
            try:
                self.client.send("!users".encode('utf-8'))
                
                user_list = self.client.recv(2048).decode('utf-8')
                
                return user_list
            except Exception as e:
                print(f"Erro ao obter lista de usuários: {e}")
                return "Erro ao obter lista de usuários."

    def handle_command(self, command):
        if command.startswith("!help"):
            if self.is_admin():
                self.chat_label.configure(text=self.chat_label.cget("text") + "\nComandos:\n\n[ADMIN]:\n\n!kick <username>\n!ban <IP>\n!unbanip <IP>\n!cls\n\n[USERS]\n\n!help\n")
        elif command.startswith("!fenix"):
            self.configure(fg_color="#09122C")
            self.chat_frame.configure(fg_color="#BE3144")
            self.chat_scrollable_frame.configure(fg_color="#872341")
            self.frame_content.configure(fg_color="#E17564")
            self.frame_users.configure(fg_color="#BE3144")
            self.users_frame.configure(fg_color="#BE3144")
            self.chat_label.configure(text=self.chat_label.cget("text") + f"{self.username} - das cinzas, renasço.\n")
        elif command == "!cls":
            if self.is_admin():
                self.client.send("!cls".encode('utf-8'))
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        
        elif command.startswith("!kick"):
            if self.is_admin():
                parts = command.split(" ")
                if len(parts) > 1:
                    username = parts[1]
                    self.client.send(f"!kick {username}".encode('utf-8'))
                else:
                    self.chat_label.configure(text=self.chat_label.cget("text") + "Uso: !kick <username>\n")
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")

        elif command.startswith("!ban"):
            if self.is_admin():
                parts = command.split(" ")
                if len(parts) > 1:
                    ip = parts[1]
                    self.client.send(f"!ban {ip}".encode('utf-8'))
                else:
                    self.chat_label.configure(text=self.chat_label.cget("text") + "Uso: !ban <IP>\n")
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        elif command.startswith("!unbanip"):
            if self.is_admin():
                parts = command.split(" ")
                if len(parts) > 1:
                    ip = parts[1]
                    self.client.send(f"!unbanip {ip}".encode('utf-8'))
                else:
                    self.chat_label.configure(text=self.chat_label.cget("text") + "Uso: !unbanip <IP>\n")
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        else:
            self.chat_label.configure(text=self.chat_label.cget("text") + "Comando desconhecido.\n")

    def is_admin(self):
        user_ip = self.get_local_ip()
        if self.server_ip == user_ip:
            self.rank = "[ADMIN]"
        else:
            self.rank = "[BETA]"
        return self.server_ip == user_ip
            
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  
            ip = s.getsockname()[0]  
            s.close()
            return ip
        except Exception as e:
            print(f"Erro ao obter o IP: {e}")
            return None


if __name__ == "__main__":
    print("running as principal")
app = App() 
app.run()