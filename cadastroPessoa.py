import pyautogui
import time
import pandas as pd
import keyboard
import threading
import io
import sys

# === FORÇA UTF-8 NO TERMINAL ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === FLAGS DE CONTROLE ===
pause_flag = False
stop_flag = False

# === MONITORADOR DE TECLAS (RODA EM PARALELO) ===
def monitorar_teclas():
    global pause_flag, stop_flag
    while True:
        if keyboard.is_pressed("p"):
            pause_flag = True
            print("⏸️ Pausa ativada. Aguardando fim do cadastro atual...")
            time.sleep(1)
        elif keyboard.is_pressed("c"):
            if pause_flag:
                pause_flag = False
                print("▶️ Retomando...")
                time.sleep(1)
        elif keyboard.is_pressed("s"):
            stop_flag = True
            print("🛑 Encerramento solicitado. Finalizando após o cadastro atual...")
            break

# === INICIA A THREAD DO MONITORAMENTO ===
threading.Thread(target=monitorar_teclas, daemon=True).start()

# === CONFIGURAÇÃO DO DELAY ENTRE AÇÕES DO PYAUTOGUI ===
pyautogui.PAUSE = 0.5

# === FUNÇÕES DE NAVEGAÇÃO E CADASTRO ===
def abrir_sistema():
    pyautogui.press("win")
    pyautogui.write("chrome")
    pyautogui.press("enter")
    time.sleep(1)
    pyautogui.write("http://10.100.10.52:81/logon.aspx")
    pyautogui.press("enter")
    time.sleep(1)

def login():
    pyautogui.click(x=805, y=453)  # Campo do login
    pyautogui.write("deryk.silva")
    pyautogui.press("tab")
    pyautogui.write("!Deryksilva10")
    pyautogui.press("enter")
    time.sleep(2)

def navegar_ate_cadastrar():
    pyautogui.click(x=304, y=212)  # Aba "Pessoas"
    time.sleep(1)
    pyautogui.click(x=364, y=289)  # Cadastro de Pessoa
    time.sleep(1)
    pyautogui.click(x=1246, y=720)  # Botão "Cadastrar"

def cadastrar_pessoa(nome, cpf):
    pyautogui.click(x=467, y=351)  # Campo MATRÍCULA = CPF do usuário
    pyautogui.write(cpf)
    pyautogui.press("tab")
    pyautogui.write(nome, interval=0.01)
    time.sleep(1)

    pyautogui.click(x=499, y=379)  # Situação
    time.sleep(1)
    pyautogui.click(x=453, y=416)  # Ativo
    time.sleep(1)

    pyautogui.click(x=945, y=400)  # Lupa Estrutura
    time.sleep(1)
    pyautogui.click(x=623, y=424)  # Unidade
    time.sleep(1)
    pyautogui.click(x=884, y=624)  # OK
    time.sleep(1)
    
    pyautogui.click(x=425, y=310)  # Aba Credenciais
    time.sleep(1)
    pyautogui.click(x=437, y=365)  # Campo Número
    pyautogui.write(cpf)

    pyautogui.click(x=755, y=363)  # Botão Adicionar
    time.sleep(1)
    pyautogui.click(x=1164, y=765)  # Botão Salvar
    time.sleep(2)

    pyautogui.click(x=1246, y=720)  # Botão Cadastrar (loop)
    time.sleep(1)

def registrar_log(nome, cpf):
    datahora = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("usuariosCadastrados.txt", "a", encoding="utf-8") as log:
        log.write(f"{datahora} | {cpf} | {nome}\n")
    print(f"✅ Cadastrado: {nome} ({cpf}) às {datahora}")

# === EXECUÇÃO PRINCIPAL ===
abrir_sistema()
login()
navegar_ate_cadastrar()

try:
    tabela = pd.read_csv("medicos_para_cadastro.csv", sep=";", encoding="latin1")
    tabela.columns = [col.strip().upper() for col in tabela.columns]
    print("✅ CSV lido com sucesso.")
    print("🧩 Colunas disponíveis:", tabela.columns.tolist())

    for linha in tabela.index:
        nome = str(tabela.loc[linha, "NOME_COMPLETO"]).strip()
        cpf = str(tabela.loc[linha, "CPF"]).strip()

        if not nome or not cpf:
            print(f"⚠️ Linha {linha+1} ignorada (dados incompletos).")
            continue

        cadastrar_pessoa(nome, cpf)
        registrar_log(nome, cpf)

        while pause_flag and not stop_flag:
            print("⏸️ Pausado. Pressione 'c' para continuar...")
            time.sleep(1)

        if stop_flag:
            print("🛑 Automação encerrada por comando manual.")
            break

except FileNotFoundError:
    print("❌ Arquivo 'medicos_para_cadastro.csv' não encontrado.")
    exit()
except Exception as e:
    print(f"❌ Erro ao processar o CSV: {e}")
    exit()
