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
        self.server_port = 7777  # Defina a porta do servidor aqui
        self.username = None

        self.enter_server_frame()

    def run(self):
        self.mainloop()
        
    def config_root(self):
        self.configure(fg_color="#635985") 
        self.title("Port777 Main")
    def _centralize_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.window_width = screen_width // 2 + 100
        self.window_height = screen_height // 2 + 100

        x = (screen_width // 2) - (self.window_width // 2)
        y = (screen_height // 2) - (self.window_height // 2)

        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def enter_server_frame(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#393053")
        self.main_frame.pack(pady=self.window_width//4)

        self.main_frame_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter your server", border_color="black", fg_color="white", width=290, font=("Terminal",16))
        self.main_frame_entry.grid(row=0, column=0, pady=15, padx=(15,10))

        self.main_frame_button = ctk.CTkButton(self.main_frame, text="Enter", command=self.send_server_ip, font=("Terminal",16))
        self.main_frame_button.grid(row=0, column=1, pady=(15,0), padx=(10,15))

        self.main_frame_username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter your username", border_color="black", fg_color="white", width=290, font=("Terminal",16))
        self.main_frame_username_entry.grid(row=1, column=0, pady=(0,15), padx=(15,10))

    def send_server_ip(self):
        self.server_ip = self.main_frame_entry.get()
        self.username = self.main_frame_username_entry.get()
        if not self.server_ip or "." not in self.server_ip or not self.username or ["admin","adm","administrador","administrator"] in self.username:
            self.main_frame_entry.configure(placeholder_text="Error, try again")
            self.main_frame_entry.delete(0, ctk.END)
            self.main_frame_button.configure(fg_color="#CD1818")
        else:
            print(f"Server IP entered: {self.server_ip}")
            self.main_frame.pack_forget()  
            self.open_chat_frame()  
            self.connect_to_server()  

    def open_chat_frame(self):
        self.withdraw()
        self.chat_frame = ctk.CTkFrame(self, fg_color="#393053")
        self.chat_frame.pack(pady=self.window_height//7)

        self.chat_label = ctk.CTkLabel(self.chat_frame, width=self.window_width//2, height=self.window_height//2, font=("Terminal", 16), text="", anchor="nw", justify="left",text_color="white")
        self.chat_label.grid(row=0, column=0, pady=15, padx=20)

        self.chat_entry = ctk.CTkEntry(self.chat_frame, placeholder_text="Type your message", border_color="black", fg_color="white", width=290, font=("Terminal", 16))
        self.chat_entry.grid(row=1, column=0, pady=(5, 15), padx=20)

        self.send_button = ctk.CTkButton(self.chat_frame, text="Send", command=self.send_message, font=("Terminal", 16))
        self.send_button.grid(row=2, column=0, pady=(5, 15), padx=20)
        self.after(1)
        self.deiconify()

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.title(f"Port7777 {self.server_ip} Chat")
            self.client.connect((self.server_ip, self.server_port))
            print("Conectado ao servidor!")

            # Envia o nome de usuário ao servidor
            self.client.send(self.username.encode('utf-8'))

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True  
            thread.start()
            
        except Exception as e:  
            print(f"Erro ao conectar: {e}")
            self.send_server_ip()
            
    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(2048).decode('utf-8')
                if msg:
                    if msg == "!clear":
                        self.chat_label.configure(text="")  
                    elif msg.startswith("!kick"):
                        if msg.split(" ")[1] == self.username:
                            self.client.close()
                            self.destroy()
                            sys.exit() 
                    else:
                        self.chat_label.configure(text=self.chat_label.cget("text") + f"{msg}\n")
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
                self.chat_label.configure(text=self.chat_label.cget("text") + f"{full_message}\n")
                self.chat_entry.delete(0, ctk.END)  
                try:
                    self.client.send(full_message.encode('utf-8'))
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")

    def handle_command(self, command):
        if command == "!cls":
            if self.is_admin():
                self.client.send("!cls".encode('utf-8'))
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        elif command.startswith("!kick"):
            if self.is_admin():
                username = command.split(" ")[1]
                self.client.send(f"!kick {username}".encode('utf-8'))
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        elif command.startswith("!ban"):
            if self.is_admin():
                ip = command.split(" ")[1]
                self.client.send(f"!ban {ip}".encode('utf-8'))
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        elif command.startswith("!unbanip"):
            if self.is_admin():
                ip = command.split(" ")[1]
                self.client.send(f"!unbanip {ip}".encode('utf-8'))
            else:
                self.chat_label.configure(text=self.chat_label.cget("text") + "Você não tem permissão para usar este comando.\n")
        else:
            self.chat_label.configure(text=self.chat_label.cget("text") + "Comando desconhecido.\n")

    def is_admin(self):
        user_ip = self.get_local_ip()
        if self.server_ip == user_ip:
            self.username = f"{self.username} [ADMIN]"
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
    app = App() 
    app.run()
    print("running as principal")
else:
    app = App()
    app.run()