# %%

# Ambiente e dependências: Instalação de dependências

import bs4
import urllib.request as urllib_request
import pandas as pd
import requests
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# from urllib.request import urlopen, Request
# from urllib.error import URLError, HTTPError

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

    def alterarinfos (self):
        self.data['preco'] = self.data['preco'].str.extract(r'(\d+\.\d+|\d+)')
        self.data['metros'] = self.data['metros'].str.extract(r'(\d+)')
        self.data['qtdquartos'] = self.data['qtdquartos'].str.extract(r'(\d+)')
        self.data['qtdbanheiros'] = self.data['qtdbanheiros'].str.extract(r'(\d+)')
        return self.data

    def incluir (self):
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
print(df.keys())


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

# Gráfico de contagem de imóveis por estado

plt.figure(figsize = (15, 8))
ax = sns.countplot(x='estado', data=data, palette="hls")
ax.bar_label(ax.containers[0]);

#%%



#%%
# Machine Learning

# Definindo as features e a variável target
X = data[['qtdquartos', 'qtdbanheiros', 'estado']]
y = data['preco'] # Target

# Definindo os pré-processadores
numeric_imputer = SimpleImputer(strategy='constant', fill_value=0)
categorical_imputer = SimpleImputer(strategy='most_frequent')

# Definindo o pipeline de pré-processamento
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_imputer, ['qtdquartos', 'qtdbanheiros']),
        ('cat', categorical_imputer, ['estado'])
    ]
)

# Criando o pipeline completo
pipeline = Pipeline(
    steps=[
    ('preprocessor', preprocessor),
    ('encoder', OneHotEncoder()),
    ('model', XGBRegressor())
    ]
)

#%%
# Dividindo os dados em conjuntos de treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinando o pipeline completo
pipeline.fit(X_train, y_train)

# Fazendo previsões com o conjunto de teste
y_pred = pipeline.predict(X_test)

# Avaliando o modelo
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse}")
print(f"R^2: {r2}")


# %%

# Exportando os dados
data.to_csv('F:/Projects/Python/webscraping-vivareal/raw/rawvivareal.csv', sep=',', index=False, encoding='utf-8-sig')