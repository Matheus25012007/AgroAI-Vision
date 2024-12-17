import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowcapture import WindowCapture
from ultralytics import YOLO
import subprocess
import json
import adbutils
import psutil

arquivo = 'coordenadas.txt'
with open(arquivo, 'w') as f:
    pass 

# ------------------------------------------------ FUNÇÃO DE MONITORAMENTO DO SCRCPY ------------------------------------------------------

# Função para verificar se o scrcpy está rodando
def is_scrcpy_running():
    for proc in psutil.process_iter(['name']):
        if "scrcpy" in proc.info['name'].lower():
            return True
    return False

# ATIVANDO O SCRCPY
# Caminho do executável
scrcpy = "scrcpy\scrcpy.exe"

# Executa o scrcpy via subprocess
subprocess.Popen([scrcpy])

# Aguarda um momento para garantir que a janela comece a abrir
sleep(2)

# Aguarda até que o scrcpy esteja rodando
print("Aguardando a janela do scrcpy abrir...")
while not is_scrcpy_running():
    sleep(1)

print("A janela do scrcpy foi aberta. Continuando a execução...")

# ---------------------------------------------------- FUNÇÃO DE EXTRAÇÃO DE COORDENADAS ----------------------------------------------------

# Conectar ao dispositivo
device = adbutils.adb.device()

# Caminho para o arquivo no Android
caminho_arquivo = '/storage/emulated/0/Android/data/com.rxmap.rxdrone/files/Documents/FlightLog.txt'

# Caminho para o arquivo onde as coordenadas serão armazenadas
caminho_arquivo_saida = 'coordenadas.txt'

def processar_ultimo_json(caminho_arquivo, caminho_arquivo_saida, tipo_doenca):
    try:
        # Usar adbutils para ler o conteúdo do arquivo remoto no Android
        conteudo = device.shell(f'cat {caminho_arquivo}').strip()

        # Separar os objetos JSON pelo delimitador
        objetos_json = conteudo.split('----------------------------------------')

        # Remover espaços extras e verificar se há objetos JSON
        objetos_json = [obj.strip() for obj in objetos_json if obj.strip()]

        if objetos_json:
            # Pegar o último objeto JSON
            ultimo_objeto = objetos_json[-1]

            # Processar o último objeto JSON
            try:
                dados = json.loads(ultimo_objeto)

                # Extrair longitude e latitude
                longitude = dados.get("飞机经度", "Não disponível")  # Variável que armazena a longitude
                latitude = dados.get("飞机纬度", "Não disponível")  # Variável que armazena a latitude

                print(f"Longitude: {longitude}")
                print(f"Latitude: {latitude}")

                # Armazenar as coordenadas e o tipo de doença em um arquivo .txt
                with open(caminho_arquivo_saida, 'a', encoding='utf-8') as arquivo_saida:
                    arquivo_saida.write(f"{tipo_doenca}, {longitude}, {latitude}\n")

            except json.JSONDecodeError as e:
                print(f'Erro ao decodificar JSON: {e}')
        else:
            print("Nenhum objeto JSON encontrado no arquivo.")
    except FileNotFoundError:
        print(f'O arquivo {caminho_arquivo} não foi encontrado.')
    except Exception as e:
        print(f'Ocorreu um erro: {e}')

# ------------------------------------------------------------------------------------------------------------------------------

# Mudar o diretório de trabalho para a pasta onde este script está.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Conectar ao dispositivo
device = adbutils.adb.device()

# Comando para obter o nome do modelo do dispositivo
nome_dispositivo = device.shell('getprop ro.product.model').strip()

# inicializar a classe WindowCapture
wincap = WindowCapture(nome_dispositivo)

# Carregar o modelo YOLOv8
model = YOLO("last.pt")

nomes_classes = ['Cercospora coffeicola', 'Bicho Mineiro', 'Ferrugem Cafeeira', 'Acaro Vermelho']

# Definir o limiar de confiança
limiar_confianca = 0.77

loop_time = time()
while True:

    # obter uma imagem atualizada do jogo
    screenshot = wincap.get_screenshot()

    # Fazer a detecção de objetos no frame capturado
    results = model(screenshot)

    # Inicializando uma lista para armazenar os nomes dos objetos detectados
    objetos_detectados = []

    # Iterar sobre as detecções e desenhar as caixas manualmente
    for result in results:
        boxes = result.boxes.xyxy  # Coordenadas das boxes
        confs = result.boxes.conf  # Confiança das detecções
        classes = result.boxes.cls  # Classes detectadas

        for i in range(len(boxes)):
            x1, y1, x2, y2 = map(int, boxes[i])
            confidence = confs[i]
            cls = int(classes[i])

            # Verificar se a confiança é maior que o limiar
            if confidence >= limiar_confianca:
                # Obter o nome do objeto detectado
                nome_objeto = nomes_classes[cls]
                
                # Armazenar o nome do objeto detectado na lista
                objetos_detectados.append(nome_objeto)

                # Desenhar a caixa
                cv.rectangle(screenshot, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Escrever a classe e a confiança
                label = f'{model.names[cls]}: {confidence:.2f}'
                cv.putText(screenshot, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Mostrar os resultados com as detecções
    annotated_frame = results[0].plot()  # Desenha as detecções no frame

    cv.imshow('Visão Computacional', screenshot)

    # Verificar se algum objeto específico foi detectado e ativar a função correspondente
    for nome_doenca in nomes_classes:
        if nome_doenca in objetos_detectados:
            print(f"{nome_doenca} detectada! Chamando Função")
            processar_ultimo_json(caminho_arquivo, caminho_arquivo_saida, nome_doenca)

    # depurar a taxa de loop (FPS)
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # pressione 'q' com a janela de saída focada para sair.
    # espera 1 ms a cada loop para processar pressionamentos de tecla
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Feito.')
