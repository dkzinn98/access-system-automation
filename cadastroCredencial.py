import io
import sys
import pyautogui # type: ignore
import time
import pandas as pd # type: ignore
import keyboard # type: ignore
import threading

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
            print("⏸️ Pausa ativada. Aguardando término do cadastro atual...")
            time.sleep(1)
        elif keyboard.is_pressed("c"):
            if pause_flag:
                pause_flag = False
                print("▶️ Retomando a automação...")
                time.sleep(1)
        elif keyboard.is_pressed("s"):
            stop_flag = True
            print("🛑 Encerramento solicitado. Finalizando após o cadastro atual...")
            break

# === THREAD DO MONITORAMENTO ===
threading.Thread(target=monitorar_teclas, daemon=True).start()

# === SETUP INICIAL ===
pyautogui.PAUSE = 0.5

def abrir_sistema():
    pyautogui.press("win")
    pyautogui.write("chrome")
    pyautogui.press("enter")
    time.sleep(3)
    pyautogui.write("http://10.100.10.52:81/logon.aspx")
    pyautogui.press("enter")
    time.sleep(3)

def login():
    pyautogui.click(x=986, y=569)  # Campo do login
    pyautogui.write("deryk.silva")
    pyautogui.press("tab")
    pyautogui.write("!Deryksilva10")
    pyautogui.press("enter")
    time.sleep(2)

def navegar_ate_cadastrar():
    pyautogui.click(x=1260, y=261)  # AMBIENTE FÍSICO
    time.sleep(1)
    pyautogui.click(1261, y=688)  # CREDENCIAL
    time.sleep(1)
    pyautogui.click(x=1529, y=889)  # CADASTRAR
    time.sleep(2) 

def cadastrar_credencial(cpf):
    pyautogui.click(x=1134, y=411) # ==> SELECIONA CAMPO NÚMERO
    pyautogui.write(cpf) # ==> DIGITA O CPF
    pyautogui.click(x=1476, y=545) # ==> SELECIONA CREDENCIAL PUBLICA
    time.sleep(1)
    pyautogui.click(x=678, y=548) # ==> SELECIONA TECNOLOGIA
    time.sleep(1)
    pyautogui.click(x=569, y=654) # ==> SELECIONA PROXIMIDADE
    time.sleep(1)
    pyautogui.click(x=1410, y=959) # ==> SALVAR
    time.sleep(1)
    pyautogui.click(x=1529, y=889)  # ==> CADASTRAR NOVAMENTE

def registrar_log(cpf):
    datahora = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("credenciaisCadastradas.txt", "a", encoding="utf-8") as log:
        log.write(f"{datahora} | {cpf} | SUCESSO\n")
    print(f"✅ Cadastrado: ({cpf}) às {datahora}")

# === INICIAR AUTOMAÇÃO ===

abrir_sistema()
login()
navegar_ate_cadastrar()

try:
    tabela = pd.read_csv("medicos_para_cadastro.csv", sep=";", encoding="latin1")
    tabela.columns = [col.strip().upper() for col in tabela.columns]  # ← NINJUTSU APLICADO
    print("✅ CSV lido com sucesso.")
except FileNotFoundError:
    print("❌ Arquivo 'medicos_para_cadastro.csv' não encontrado.")
    exit()
except Exception as e:
    print(f"❌ Erro ao ler o CSV: {e}")
    exit()
except login:
    login()

for linha in tabela.index:
    cpf = str(tabela.loc[linha, "CPF"])  # ← agora CPF está garantido, sem frescura

    cadastrar_credencial(cpf)
    registrar_log(cpf)

    # Verifica pausa
    while pause_flag and not stop_flag:
        print("⏸️ Pausado. Pressione 'c' para continuar...")
        time.sleep(1)

    # Verifica parada total
    if stop_flag:
        print("🛑 Automação finalizada manualmente.")
        break
