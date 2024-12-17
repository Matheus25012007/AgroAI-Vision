import folium

# Função para carregar as coordenadas e nome das doenças de um arquivo txt
def carregar_dados(arquivo_txt):
    dados = []
    with open(arquivo_txt, 'r', encoding='utf-8') as f:  # Especificando a codificação
        for linha in f:
            nome_doenca, lon, lat = linha.strip().split(',')
            dados.append((nome_doenca, float(lon), float(lat)))
    return dados

# Caminho para o arquivo de coordenadas (apenas o nome do arquivo)
arquivo_txt = "C:\\Users\\leo00\\OneDrive\\Desktop\\DPADesktop\\scripts\\Conexao\\coordenadas.txt"  # Sem o caminho completo

# Carregar os dados do arquivo
dados = carregar_dados(arquivo_txt)

# Defina o local inicial do mapa com base no primeiro ponto
if dados:  # Verifique se há dados
    start_coords = [dados[0][2], dados[0][1]]  # Usar latitude e longitude do primeiro ponto
else:
    start_coords = [-23.5505, -46.6333]  # Coordenadas padrão se não houver dados

# Criar o mapa
mapa = folium.Map(location=start_coords, zoom_start=18)

# Adicione uma camada de tiles usando o caminho local
tile_path = "PNG_MAPA/"
folium.TileLayer(
    tiles=tile_path + '{z}/{x}/{y}.png',
    name='Mapa Offline',
    attr='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
).add_to(mapa)

# Mapeamento de cores para as doenças
cor_por_doenca = {
    'Doenca1': 'red',
    'Doenca2': 'blue',
    'Doenca3': 'green',
    'Doenca4': 'orange',
    # Adicione mais doenças e suas respectivas cores conforme necessário
}

# Adicionar marcadores no mapa para cada coordenada e nome de doença
for nome_doenca, lon, lat in dados:
    cor = cor_por_doenca.get(nome_doenca, 'gray')  # Usar cor padrão se não houver mapeamento
    folium.Marker(
        location=[lat, lon],
        popup=nome_doenca,  # Exibir apenas o nome da doença
        icon=folium.Icon(color=cor)  # Usar a cor correspondente
    ).add_to(mapa)

# Adicione a camada de controle para alternar entre camadas
folium.LayerControl().add_to(mapa)

# Salve o mapa em um arquivo HTML
mapa.save("C:\\Users\\leo00\\OneDrive\\Desktop\\DPADesktop\\scripts\\mapas\\mapa.html")
print("Mapa salvo como mapa_offline.html")
