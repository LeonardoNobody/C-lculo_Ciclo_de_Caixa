import tkinter as tk
import threading
import time
import pyautogui
import pytesseract
import keyboard
import pygame
import sys
import string

from PIL import Image, ImageEnhance, ImageFilter
from pynput.keyboard import Controller, Key
from winsound import Beep

# === Configurações Gerais ===
pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\tibia\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"
pynput_keyboard = Controller()
pygame.mixer.init()
alerta_som = pygame.mixer.Sound("alerta.wav")

# === Flags de Controle ===
ataque_em_andamento = False
runador_ativo = False
food_ativo = False
ring_ativo = False
autosd_ativo = False
autoattack_ativo = False
verificar_gm_ativo = False

# === Tempos ===
intervalo_runa = 70
intervalo_food = 240
intervalo_ring = 1200
intervalo_sd = 1
intervalo_attack = 0.1

# === Cores ===
slot_x, slot_y = 1755, 598
cor_slot_vazio = (27, 27, 27)

# === Funções auxiliares ===
def preprocess_image(img):
    img = img.convert("L")
    img = img.resize((img.width * 2, img.height * 2))
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2)
    return img

def cor_igual(c1, c2, tolerancia=5):
    return all(abs(a - b) <= tolerancia for a, b in zip(c1, c2))

def eh_nome_valido(linha):
    linha = linha.lower().strip()
    if len(linha) < 3:
        return False
    if any(p in linha for p in ["lista", "batalha", "a - x", "|", "»", "v"]):
        return False
    if not any(c.isalpha() for c in linha):
        return False
    return True

# === OCR Battle List (Completa) ===
tempo_ultimo_target = 0
TOLERANCIA_TEMPO = 2

def tem_target_na_bl():
    global tempo_ultimo_target
    screenshot = pyautogui.screenshot(region=(1529, 336, 190, 288))
    imagem = preprocess_image(screenshot)
    texto = pytesseract.image_to_string(imagem, config='--psm 6')
    linhas = texto.splitlines()
    for linha in linhas:
        if eh_nome_valido(linha.strip()):
            tempo_ultimo_target = time.time()
            return True
    return time.time() - tempo_ultimo_target < TOLERANCIA_TEMPO

# === Auto SD ===
def auto_sd():
    global ataque_em_andamento
    while autosd_ativo:
        try:
            if ataque_em_andamento:
                keyboard.send('f10')
                print("[AUTO SD] SD usada")
            else:
                print("[AUTO SD] Aguardando alvo...")
        except Exception as e:
            print(f"[ERRO] Auto SD falhou: {e}")
        time.sleep(intervalo_sd)




# === Auto Attack ===
# === Auto Attack com trava de alvo ===
def auto_attack():
    global ataque_em_andamento
    alvo_atual = None
    tempo_sem_alvo = 0

    while autoattack_ativo:
        try:
            screenshot = pyautogui.screenshot(region=(1529, 336, 190, 288))
            imagem = preprocess_image(screenshot)
            texto = pytesseract.image_to_string(imagem, config='--psm 6')
            linhas = [linha.strip() for linha in texto.splitlines() if eh_nome_valido(linha.strip())]

            if not linhas:
                tempo_sem_alvo += intervalo_attack
                print(f"[AUTO ATTACK] Sem alvo... ({tempo_sem_alvo:.1f}s)")

                if tempo_sem_alvo >= TOLERANCIA_TEMPO:
                    print("[AUTO ATTACK] Alvo sumiu — encerrando ataque")
                    alvo_atual = None
                    ataque_em_andamento = False

            else:
                if alvo_atual is None:
                    alvo_atual = linhas[0]  # Primeiro nome detectado
                    keyboard.send("f3")
                    print(f"[AUTO ATTACK] Alvo detectado — atacando: {alvo_atual}")
                    ataque_em_andamento = True
                    tempo_sem_alvo = 0

                elif alvo_atual in linhas:
                    print("[AUTO ATTACK] Mantendo ataque no mesmo alvo")
                    ataque_em_andamento = True
                    tempo_sem_alvo = 0

                else:
                    tempo_sem_alvo += intervalo_attack
                    print(f"[AUTO ATTACK] {alvo_atual} não encontrado ({tempo_sem_alvo:.1f}s)")
                    
                    if tempo_sem_alvo >= TOLERANCIA_TEMPO:
                        print(f"[AUTO ATTACK] Perdido {alvo_atual}, liberando para novo alvo")
                        alvo_atual = None
                        ataque_em_andamento = False

        except Exception as e:
            print(f"[ERRO] Auto Attack falhou: {e}")

        time.sleep(intervalo_attack)




# === Outras Features (Runador, Food, Ring) ===
def runador():
    while runador_ativo:
        pynput_keyboard.press(Key.f12)
        pynput_keyboard.release(Key.f12)
        print(f"[RUNADOR] F12 - aguardando {intervalo_runa}s")
        time.sleep(intervalo_runa)

def auto_food():
    while food_ativo:
        pynput_keyboard.press(Key.f11)
        pynput_keyboard.release(Key.f11)
        print(f"[FOOD] F11 - aguardando {intervalo_food}s")
        time.sleep(intervalo_food)

def auto_ring():
    while ring_ativo:
        if cor_igual(pyautogui.pixel(slot_x, slot_y), cor_slot_vazio):
            keyboard.send('f9')
            print("[RING] Slot vazio - F9 enviado")
        else:
            print("[RING] Slot ainda com anel")
        time.sleep(intervalo_ring)

# === Monitoramento GM ===
def monitorar_battle_list():
    global verificar_gm_ativo
    while verificar_gm_ativo:
        screenshot = pyautogui.screenshot(region=(1529, 336, 190, 288))
        imagem = preprocess_image(screenshot)
        texto = pytesseract.image_to_string(imagem, config='--psm 6')
        linhas = texto.splitlines()
        for linha in linhas:
            if eh_nome_valido(linha.strip()):
                print("[⚠️ ALERTA] Player detectado na BL!")
                alerta_som.play()
                time.sleep(1.5)
                janela.destroy()
                sys.exit(0)
        time.sleep(2)

# === Interface TK ===
janela = tk.Tk()
janela.title("Medivia HUD Bot")
janela.geometry("125x750+1650+125")
janela.configure(bg="#f2f2f2")
janela.attributes("-topmost", True)
janela.overrideredirect(True)

def iniciar_movimento(e): janela.x = e.x; janela.y = e.y

def movimentar(e): janela.geometry(f"+{janela.winfo_pointerx() - janela.x}+{janela.winfo_pointery() - janela.y}")

barra = tk.Frame(janela, bg="#ccc", height=20)
barra.pack(fill="x")
barra.bind("<Button-1>", iniciar_movimento)
barra.bind("<B1-Motion>", movimentar)

btn_fechar = tk.Button(barra, text="X", command=janela.destroy, bg="red", fg="white", bd=0)
btn_fechar.pack(side="right")

# === Controles ===
def iniciar_thread(flag_name, func, label):
    globals()[flag_name] = True
    threading.Thread(target=func, daemon=True).start()
    label.config(text=f"{flag_name.replace('_', ' ').title()}: Ativo", fg="green")

def parar_thread(flag_name, label):
    globals()[flag_name] = False
    label.config(text=f"{flag_name.replace('_', ' ').title()}: Parado", fg="red")

# === Layout ===
fonte_padrao = ("Segoe UI", 8)

def criar_slider_botao(nome, from_, to, var, start, iniciar, parar):
    tk.Label(janela, text=nome, font=fonte_padrao, bg="#f2f2f2").pack()
    slider = tk.Scale(janela, from_=from_, to=to, orient="horizontal", command=lambda v: globals().__setitem__(var, type(start)(v)), bg="#e6e6e6")
    slider.set(start)
    slider.pack()
    tk.Button(janela, text=f"Iniciar {nome}", command=iniciar, bg="#4CAF50", fg="white").pack()
    tk.Button(janela, text=f"Parar {nome}", command=parar, bg="#f44336", fg="white").pack()
    return tk.Label(janela, text=f"{nome}: Parado", fg="red", bg="#f2f2f2")

status_runador = criar_slider_botao("Runador (s)", 10, 1800, "intervalo_runa", intervalo_runa, lambda: iniciar_thread("runador_ativo", runador, status_runador), lambda: parar_thread("runador_ativo", status_runador)); status_runador.pack()
status_food = criar_slider_botao("Food (s)", 10, 1800, "intervalo_food", intervalo_food, lambda: iniciar_thread("food_ativo", auto_food, status_food), lambda: parar_thread("food_ativo", status_food)); status_food.pack()
status_ring = criar_slider_botao("Ring (s)", 10, 1800, "intervalo_ring", intervalo_ring, lambda: iniciar_thread("ring_ativo", auto_ring, status_ring), lambda: parar_thread("ring_ativo", status_ring)); status_ring.pack()
status_autosd = criar_slider_botao("Auto SD (s)", 1, 10, "intervalo_sd", intervalo_sd, lambda: iniciar_thread("autosd_ativo", auto_sd, status_autosd), lambda: parar_thread("autosd_ativo", status_autosd)); status_autosd.pack()
status_autoattack = criar_slider_botao("Auto Attack (s)", 0.1, 5.0, "intervalo_attack", intervalo_attack, lambda: iniciar_thread("autoattack_ativo", auto_attack, status_autoattack), lambda: parar_thread("autoattack_ativo", status_autoattack)); status_autoattack.pack()

def alternar_gm():
    global verificar_gm_ativo
    verificar_gm_ativo = not verificar_gm_ativo
    if verificar_gm_ativo:
        threading.Thread(target=monitorar_battle_list, daemon=True).start()
    status_gm.config(text="✔️ GM: Ativo" if verificar_gm_ativo else "❌ GM: Desligado", fg="green" if verificar_gm_ativo else "red")

tk.Button(janela, text="Detectar Players (OCR)", command=alternar_gm, bg="#2196F3", fg="white").pack()
status_gm = tk.Label(janela, text="❌ GM: Desligado", fg="red", bg="#f2f2f2"); status_gm.pack()

janela.mainloop()