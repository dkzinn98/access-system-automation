import pyautogui # type: ignore
import time
import pandas as pd # type: ignore
import keyboard # type: ignore
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
    pyautogui.click(x=986, y=569)  # Campo do login
    pyautogui.write("deryk.silva")
    pyautogui.press("tab")
    pyautogui.write("!Deryksilva10")
    pyautogui.press("enter")
    time.sleep(2)

def navegar_ate_cadastrar():
    pyautogui.click(x=359, y=268)  # Aba "Pessoas"
    time.sleep(1)
    pyautogui.click(x=355, y=372)  # Cadastro de Pessoa
    time.sleep(1)
    pyautogui.click(x=1536, y=899)  # Botão "Cadastrar"

def cadastrar_pessoa(nome, cpf):
    pyautogui.click(x=555, y=438)  # Campo MATRÍCULA = CPF do usuário
    pyautogui.write(cpf)
    pyautogui.press("tab")
    pyautogui.write(nome, interval=0.01)
    time.sleep(1)

    pyautogui.click(x=692, y=464)  # Situação
    time.sleep(1)
    pyautogui.click(x=556, y=522)  # Ativo
    time.sleep(1)

    pyautogui.click(x=1145, y=503)  # Lupa Estrutura
    time.sleep(1)
    pyautogui.click(x=741, y=512)  # Unidade
    time.sleep(1)
    pyautogui.click(x=1061, y=752)  # OK
    time.sleep(1)
    
    pyautogui.click(x=477, y=390)  # Aba Credenciais
    time.sleep(1)
    pyautogui.click(x=513, y=457)  # Campo Número
    pyautogui.write(cpf)

    pyautogui.click(x=937, y=453)  # Botão Adicionar
    time.sleep(1)
    pyautogui.click(x=1400, y=955)  # Botão Salvar
    time.sleep(2)

    pyautogui.click(x=1536, y=899)  # Botão Cadastrar (loop)
    time.sleep(2)

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
