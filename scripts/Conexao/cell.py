import adbutils

# Conectar ao dispositivo
device = adbutils.adb.device()

# Comando para obter o nome do modelo do dispositivo
nome_dispositivo = device.shell('getprop ro.product.model').strip()

# Exibir o nome do dispositivo
print(f"Nome do dispositivo conectado: {nome_dispositivo}")
