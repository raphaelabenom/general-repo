from gtts import gTTS
import os

# Ler o conteúdo do arquivo de texto
with open('frase.txt', 'r') as file:
    text = file.read()

# Criar um objeto gTTS com a voz masculina
tts = gTTS(text, lang='pt-br', slow=False)  # slow=False reproduz a fala em velocidade normal

# Salvar a fala como um arquivo MP3
tts.save('output.mp3')

# Reproduzir o arquivo de áudio
os.system('start output.mp3')  # Isso funciona no Windows com o player de áudio padrão

# Se você estiver usando um sistema diferente, pode usar outras bibliotecas
# como 'pygame', 'pydub', 'playsound', etc., para reproduzir o arquivo MP3.
