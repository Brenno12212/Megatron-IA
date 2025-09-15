import random
import os
import difflib
import re

BASE_PERGUNTAS = "base_perguntas.txt"

def carregar_base():
    base = {}
    if os.path.exists(BASE_PERGUNTAS):
        with open(BASE_PERGUNTAS, "r", encoding="utf-8") as f:
            for linha in f:
                if "|" in linha:
                    pergunta, resposta = linha.strip().split("|", 1)
                    base[pergunta.lower()] = resposta
    return base

def salvar_pergunta_resposta(pergunta, resposta):
    # Não salva respostas padrão ou vazias
    respostas_padrao = [
        "Ainda não sei responder isso, mas registrei sua pergunta!",
        "Pergunta registrada para futura resposta.",
        "Não sei responder, mas vou aprender! Sua pergunta foi salva."
    ]
    if resposta and resposta.strip() and resposta not in respostas_padrao:
        with open(BASE_PERGUNTAS, "a", encoding="utf-8") as f:
            f.write(f"{pergunta}|{resposta}\n")

def identificar_tipo(frase):
    frase_lc = frase.strip().lower()
    frase_lc = re.sub(r'[!.,;:]+$', '', frase_lc)  # remove pontuação final comum

    # Saudações (prioridade)
    saudacoes = [
        r'\bol[áa]\b', r'\boi\b', r'\bbom dia\b', r'\bboa tarde\b', r'\bboa noite\b', r'\beai\b', r'\be aí\b', r'\bsaudações\b'
    ]
    for saud in saudacoes:
        if re.search(saud, frase_lc):
            return "Saudacao"

    # Perguntas (prioridade após saudação)
    interrogativas = [
        r'\bcomo\b', r'\bo que\b', r'\bpor que\b', r'\bquando\b', r'\bonde\b', r'\bquem\b', r'\bqual\b', r'\bquais\b',
        r'\bquanto\b', r'\bquantos\b', r'\bpara que\b', r'\bde que\b', r'\bem que\b', r'\ba que\b', r'\bexiste\b', r'\bposso\b', r'\bserá que\b'
    ]
    if frase_lc.endswith("?"):
        return "Pergunta"
    for palavra in interrogativas:
        if re.search(palavra, frase_lc):
            return "Pergunta"

    # Frases imperativas (ex: faça, mostre, diga, explique)
    imperativos = [r'\bfaça\b', r'\bmostre\b', r'\bdiga\b', r'\bexplique\b', r'\bconte\b', r'\bme fale\b', r'\bme diga\b']
    for imp in imperativos:
        if re.search(imp, frase_lc):
            return "Pergunta"

    # Default: afirmação
    return "Afirmação"

def responder(pergunta, base):
    tipo = identificar_tipo(pergunta)
    pergunta_lc = pergunta.lower()
    if tipo == "Saudacao":
        return random.choice([
            "Olá! Como posso ajudar?",
            "Oi! Tudo bem?",
            "Olá, estou aqui para conversar!"
        ])
    if tipo == "Afirmação":
        return random.choice([
            "Entendi, obrigado por compartilhar!",
            "Mensagem recebida!",
            "Ok, anotado!",
            "Legal, obrigado pela informação!"
        ])
    # Se for pergunta, segue o fluxo normal
    # Busca exata na base dinâmica
    if pergunta_lc in base:
        resposta = base[pergunta_lc]
        if ";" in resposta:
            opcoes = [r.strip() for r in resposta.split(";") if r.strip()]
            return random.choice(opcoes)
        return resposta
    # Busca aproximada na base
    similares = difflib.get_close_matches(pergunta_lc, base.keys(), n=1, cutoff=0.7)
    if similares:
        resposta = base[similares[0]]
        if ";" in resposta:
            opcoes = [r.strip() for r in resposta.split(";") if r.strip()]
            return random.choice(opcoes)
        return resposta
    # Se não souber, pede para o usuário ensinar
    print("Ainda não sei responder isso. Pode me ensinar a resposta?")
    nova_resposta = input("Digite a resposta para eu aprender: ").strip()
    if nova_resposta:
        salvar_pergunta_resposta(pergunta, nova_resposta)
        print("Obrigado! Aprendi a resposta.")
        return nova_resposta
    else:
        return "Pergunta registrada para futura resposta."

def chatbot():
    print("Olá! Eu sou o Chatbot local. Pergunte o que quiser ou digite 'sair' para encerrar.")
    base = carregar_base()
    while True:
        pergunta = input("Você: ").strip()
        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Chatbot: Até logo!")
            break
        resposta = responder(pergunta, base)
        # Atualiza base em memória se aprendeu algo novo
        base = carregar_base()
        print("Chatbot:", resposta)


# Interface gráfica com Tkinter
import tkinter as tk
from tkinter import scrolledtext, simpledialog


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Megatron Chatbot")
        self.base = carregar_base()
        self.root.configure(bg="#111")
        self.root.geometry("380x600")
        self.root.resizable(False, False)
        self.primeira_mensagem = True

        # Mensagem animada centralizada
        self.label_animada = tk.Label(root, text="", font=("Arial", 18, "bold"), fg="#00ffcc", bg="#111")
        self.label_animada.pack(pady=(30, 5))
        self.animar_texto("Como posso te ajudar?")



        # Área de chat com balões (Canvas + Frame + Scrollbar)
        self.canvas = tk.Canvas(root, bg="#222", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.chat_frame = tk.Frame(self.canvas, bg="#222")
        self.chat_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="top", fill="both", expand=True, padx=(10,0), pady=(5,10))
        self.scrollbar.pack(side="right", fill="y", pady=(5,10))

        # Caixa de digitação centralizada e destacada, fixada na parte inferior
        self.frame_input = tk.Frame(root, bg="#111")
        self.frame_input.pack(side="bottom", fill=tk.X, pady=(0, 10))

        self.entry_bg = tk.Frame(self.frame_input, bg="#222", highlightbackground="#00ffcc", highlightcolor="#00ffcc", highlightthickness=2, bd=0)
        self.entry_bg.pack(padx=30, fill=tk.X)

        self.entry = tk.Entry(self.entry_bg, width=28, font=("Arial", 13), bg="#222", fg="#fff", insertbackground="#fff", borderwidth=0, relief=tk.FLAT)
        self.entry.pack(ipady=8, fill=tk.X)
        self.entry.bind("<Return>", self.enviar)

        self.mostrar_mensagem("Olá! Eu sou o Megatron. Pergunte o que quiser ou digite 'sair' para encerrar.", remetente='bot')

    def animar_texto(self, texto, i=0):
        if i <= len(texto):
            self.label_animada.config(text=texto[:i])
            self.root.after(50, lambda: self.animar_texto(texto, i+1))

    def mostrar_mensagem(self, mensagem, animado=False, remetente='bot'):
        # Cria um balão de mensagem (Label) alinhado à esquerda (bot) ou à direita (user)
        if remetente == 'user':
            msg = tk.Label(self.chat_frame, text=mensagem, bg="#333", fg="#00ffcc", font=("Arial", 12, "bold"), wraplength=220, justify='right', anchor='e', padx=10, pady=6, bd=0, relief='flat')
            msg.pack(anchor='e', pady=4, padx=(60,10))
        elif animado:
            self._animar_resposta(mensagem)
            return
        else:
            msg = tk.Label(self.chat_frame, text=mensagem, bg="#222", fg="#fff", font=("Arial", 12), wraplength=220, justify='left', anchor='w', padx=10, pady=6, bd=0, relief='flat')
            msg.pack(anchor='w', pady=4, padx=(10,60))
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _animar_resposta(self, mensagem, i=0, label=None):
        # Anima o texto do bot em um balão (Label)
        if label is None:
            label = tk.Label(self.chat_frame, text="", bg="#222", fg="#fff", font=("Arial", 12), wraplength=220, justify='left', anchor='w', padx=10, pady=6, bd=0, relief='flat')
            label.pack(anchor='w', pady=4, padx=(10,60))
        if i <= len(mensagem):
            label.config(text=mensagem[:i])
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)
            self.root.after(18, lambda: self._animar_resposta(mensagem, i+1, label))

    def enviar(self, event=None):
        pergunta = self.entry.get().strip()
        if not pergunta:
            return
        if self.primeira_mensagem:
            # Limpa os balões do chat (remove todos widgets do chat_frame)
            for widget in self.chat_frame.winfo_children():
                widget.destroy()
            self.primeira_mensagem = False
        self.mostrar_mensagem(pergunta, remetente='user')
        if pergunta.lower() in ["sair", "exit", "quit"]:
            self.mostrar_mensagem("Até logo!", animado=True, remetente='bot')
            self.root.after(1500, self.root.destroy)
            return
        resposta = self.responder_gui(pergunta)
        self.mostrar_mensagem(resposta, animado=True, remetente='bot')
        self.entry.delete(0, tk.END)

    def responder_gui(self, pergunta):
        tipo = identificar_tipo(pergunta)
        pergunta_lc = pergunta.lower()
        if tipo == "Saudacao":
            return random.choice([
                "Olá! Como posso ajudar?",
                "Oi! Tudo bem?",
                "Olá, estou aqui para conversar!"
            ])
        if tipo == "Afirmação":
            return random.choice([
                "Entendi, obrigado por compartilhar!",
                "Mensagem recebida!",
                "Ok, anotado!",
                "Legal, obrigado pela informação!"
            ])
        # Se for pergunta, segue o fluxo normal
        # Busca exata
        if pergunta_lc in self.base:
            resposta = self.base[pergunta_lc]
            if ";" in resposta:
                opcoes = [r.strip() for r in resposta.split(";") if r.strip()]
                return random.choice(opcoes)
            return resposta
        # Busca aproximada
        similares = difflib.get_close_matches(pergunta_lc, self.base.keys(), n=1, cutoff=0.7)
        if similares:
            resposta = self.base[similares[0]]
            if ";" in resposta:
                opcoes = [r.strip() for r in resposta.split(";") if r.strip()]
                return random.choice(opcoes)
            return resposta
        # Se não souber, pede para o usuário ensinar via popup
        from tkinter import simpledialog, messagebox
        resposta_usuario = simpledialog.askstring("Aprender resposta", f"Ainda não sei responder:\n'{pergunta}'\n\nDigite a resposta para eu aprender:", parent=self.root)
        if resposta_usuario and resposta_usuario.strip():
            salvar_pergunta_resposta(pergunta, resposta_usuario.strip())
            self.base = carregar_base()
            messagebox.showinfo("Aprendido!", "Obrigado! Aprendi a resposta.")
            return resposta_usuario.strip()
        else:
            return "Pergunta registrada para futura resposta."

if __name__ == "__main__":
    try:
        import tkinter as tk
        root = tk.Tk()
        app = ChatbotGUI(root)
        root.mainloop()
    except Exception as e:
        print("Erro ao iniciar a interface gráfica:", e)
        print("Iniciando modo terminal...")
        chatbot()

