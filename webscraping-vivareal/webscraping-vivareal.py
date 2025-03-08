# %%

# Ambiente e dependências: Instalação de dependências

import bs4
import urllib.request as urllib_request
import pandas as pd
import requests
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt


# from urllib.request import urlopen, Request
# from urllib.error import URLError, HTTPError

# Printando versões das dependências
print("BeautifulSoup: ", bs4.__version__)
print("urllib: ", urllib_request.__version__)
print("Pandas:  ", pd.__version__)

# %%

# Scraping...
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

cards = []
page = 1
base_url = 'https://www.vivareal.com.br'

while True:
    url = f'{base_url}/venda/?pagina={page}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    anuncios = soup.find("div", class_="results-list js-results-list")

    # Se não houver mais anúncios, interrompe o loop
    if anuncios is None:
        break

    anuncios = anuncios.find_all(class_="property-card__container")

    for anuncio in anuncios:
        card = {}

        card['preco'] = anuncio.find("div", class_="property-card__price js-property-card-prices js-property-card__price-small").get_text(strip=True)
        card['imovel'] = anuncio.find("span", class_="property-card__title js-cardLink js-card-title").string.split("," or "-")[0].lstrip()
        endereco = anuncio.find("span", class_="property-card__address").get_text(strip=True)
        card['endereco'] = endereco

        infos = anuncio.find("ul", class_="property-card__details").findAll('span')

        for i in range(0, len(infos), 2):
            valor = infos[i].get_text(strip=True)
            texto = infos[i+1].get_text(strip=True)

            if "m²" in texto:
                card["metros"] = f"{valor} {texto}"
            elif "Quartos" in texto:
                card["qtdquartos"] = f"{valor} {texto}"
            elif "Banheiros" in texto:
                card["qtdbanheiros"] = f"{valor} {texto}"
            elif "Garagem" in texto:
                card["garagem"] = f"{valor} {texto}"

        # Adiciona a URL do anúncio ao card
        anuncio_link = anuncio.find('a', class_="property-card__content-link js-card-title")
        if anuncio_link is not None and 'href' in anuncio_link.attrs:
            card['url'] = base_url + anuncio_link['href']

        cards.append(card)

    # Verifica se existe uma próxima página
    prox_button = soup.find('button', {'class': 'js-change-page', 'title': 'Próxima página'})
    if prox_button is None:
        break

    page = int(prox_button['data-page'])

# %%

# Salvando em um dataframe
data = pd.DataFrame(cards)

# Verificando a dimensão do dataframe
print(data.shape)

# %%

# Tratamento de Features

class tratamento:
    
    def __init__(self, data) -> None:
        self.data = data

    def alterarinfos(self):
        self.data['preco'] = self.data['preco'].str.extract(r'(\d+\.\d+|\d+)')
        self.data['metros'] = self.data['metros'].str.extract(r'(\d+)')
        self.data['qtdquartos'] = self.data['qtdquartos'].str.extract(r'(\d+)')
        self.data['qtdbanheiros'] = self.data['qtdbanheiros'].str.extract(r'(\d+)')
        return self.data

    def incluir(self):
        self.data = self.data.assign(tipo_imovel="")
        
        # Alocar tipo de imóvel
        imoveistipo = ["Casa", "Apartamento", "Lote", "Chácara", "Imóvel comercial", "Ponto comercial", "Sala", "Sobrado"]

        for imovel in imoveistipo:
            self.data.loc[self.data['imovel'].str.contains(imovel, case=False), 'tipo_imovel'] = imovel
        
        # Alocar sigla estado em uma nova feature
        self.data['estado'] = self.data['endereco'].str[-2:]
        # self.data['municipio'] = self.data['municipio'].str.replace(r' - \w+$', '', regex=True)

        return self.data

tratar = tratamento(data)
data = tratar.alterarinfos()
data = tratar.incluir()

data.head()

#%%

# col = list()
# for key in data.keys():
#     for rep in ['(',')','$','-','1100']:
#         key = (key.replace(rep,''))
#     key = key.strip().replace(' ','_')
#     col.append(key)
    
# data.columns = col
# data.head()


# %%

# EDA

print('\n-----------------------------------------------')
print(data.info())
print('\n-----------------------------------------------')
print(data.isnull().sum())
print('\n-----------------------------------------------')
print(data.describe(include='all'))
print('\n-----------------------------------------------')
print(data.keys())


#%%

#Preenchendo os valores dos lotes com 0 para quartos e banheiros

data['qtdquartos'] = data['qtdquartos'].fillna(0)
data['qtdbanheiros'] = data['qtdbanheiros'].fillna(0)

data.head()
# %%

# Convertendo dtype

data['preco'] = data['preco'].astype(float)
data['metros'] = data['metros'].astype(int)
data['qtdquartos'] = data['qtdquartos'].astype(int)
data['qtdbanheiros'] = data['qtdbanheiros'].astype(int)
data['tipo_imovel'] = data['tipo_imovel'].astype(str)
data['estado'] = data['estado'].astype(str)

#%%

print(data.info())

#%%

# Gráfico de contagem de imóveis por estado

plt.figure(figsize = (15, 8))
ax = sns.countplot(x='estado', data=data, palette="hls")
ax.bar_label(ax.containers[0]);
plt.title('Contagem de imóveis por estado', fontsize=20)

# %%

# Exportando os dados
data.to_csv('F:/Projects/Python/webscraping-vivareal/raw/rawvivareal.csv', sep=',', index=False, encoding='utf-8-sig')