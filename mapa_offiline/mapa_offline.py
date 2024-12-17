from offline_folium import offline  # Importa o modo offline
import folium

# Cria um mapa centrado em uma localização específica
m = folium.Map(location=[-22.8816822, -47.071096], zoom_start=12)

# Salva o mapa em um arquivo HTML
m.save("C:/Users/leo00/OneDrive/Desktop/DPADesktop/mapa_offiline/mapa_offline.html")