import os
import shutil
from ultralytics import YOLO
import sys

# Caminho do modelo e instanciando o YOLO
model_path = os.path.join(os.path.dirname(__file__), "modelo", "best.pt")
model = YOLO(model_path)
caminho_projeto = sys.argv[2]

# Verifica se a imagem foi passada como argumento
if len(sys.argv) > 1:
    imagem = sys.argv[1]  # Caminho da imagem passada via argumento
    nome_imagem = os.path.basename(imagem)  # Nome da imagem selecionada
    print(f"Nome da imagem selecionada: {nome_imagem}")
else:
    imagem = "0"  # Usa a câmera se nenhum caminho for fornecido

# Caminho para a pasta onde os resultados serão salvos
folder_name = os.path.join(caminho_projeto, "img", "foto")

# Verifica se a pasta 'foto' já existe e a remove, garantindo um diretório limpo
if os.path.exists(folder_name):
    print(f"A pasta '{folder_name}' já existe. Excluindo o conteúdo...")
    shutil.rmtree(folder_name)

# Realiza a predição e salva os resultados diretamente na pasta 'foto'
results = model.predict(
    source=imagem,
    show=True,
    save=True,
    conf=0.77,
    project=os.path.join(caminho_projeto, "img"),  # Define o diretório pai
    name="foto"  # Define a pasta dentro de 'img' onde os resultados serão salvos
)

# Mostra informações sobre o resultado
for result in results:
    print(result)

# Renomeia o primeiro arquivo na pasta de saída para 'imagem.png'
output_files = os.listdir(folder_name)

if output_files:  # Verifica se a lista não está vazia
    file_path = os.path.join(folder_name, output_files[0])
    new_file_path = os.path.join(folder_name, 'imagem.png')
    os.rename(file_path, new_file_path)
    print(f"Imagem processada e renomeada para: {new_file_path}")
else:
    print("Erro: Nenhum arquivo encontrado para renomear.")
