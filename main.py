import pandas as pd
from fastapi import FastAPI
import operator
import random

app = FastAPI()

#Cantidad de películas producidas por un determinado país en determinado año. 
#La función debe llamarse get_country(year, country) 
#y debe devolver sólo número de películas producidas por dicho país en dicho año. 'United States of America'
df = pd.read_csv('peliculas')
@app.get("/")
def read_root():
    return "Bienvenido a PI01"

@app.get("/get_country/{year}/{country}")
def get_country(year, country):
    paises = {}
    for i,x in enumerate(df['name_production_countries']):
        df['release_year'][i]
        if type(x) == list:
            for l in x:
                if l not in paises and l == country and df['release_year'][i] == int(year) :
                    paises[l] = 1
                elif l == country and df['release_year'][i] == int(year):
                    paises[l] += 1
        else:
            if x not in paises and x == country and df['release_year'][i] == int(year):
                paises[x] = 1
            elif x == country and df['release_year'][i] == int(year):
                paises[x] += 1
    return paises
#print(get_country('1990','Russia'))

#Recaudacion por productora y por año. La función debe llamarse get_company_revenue(company, year) 
#y debe devolver un int, con el total de dólares recaudados ese año por esa productora.
@app.get("/get_company_revenue/{year}/{company}")
def get_company_revenue(year,company):
    compa = {}
    for i,x in enumerate(df['name_production_companies']):
        if type(x) == list:
            for l in x:
                if l not in compa and l == company and df['release_year'][i] == int(year):
                    compa[l] = df.revenue[i]
                elif l == company and df['release_year'][i] == int(year):
                    compa[l] += df.revenue[i]
        else:
            if x not in compa  and x == company and df['release_year'][i] == int(year):
                compa[x] = df.revenue[i]
            elif x == company and df['release_year'][i] == int(year):
                compa[x] += df.revenue[i]
    return compa

#Cantidad de películas que salieron en determinado año. La función debe llamarse get_count_movies(year) 
#y debe devolver un int, con el número total de películas que salieron ese año.
@app.get("/get_count_movies/{year}")
def get_count_movies(year:int):
    titulo = {}
    for i,x in enumerate(df['release_year']):
        if type(x) == list:
            for l in x:
                if l not in titulo and df['release_year'][i] == year:
                    titulo[l] = 1
                elif df['release_year'][i] == year:
                    titulo[l] += 1
        else:
            if x not in titulo and df['release_year'][i] == year:
                titulo[x] = 1
            elif df['release_year'][i] == year:
                titulo[x] += 1
    return titulo
#Película con mayor retorno en determinado año. La función debe llamarse get_return(title, year)
#y debe devolver sólo el string con el nombre de la película con mayor retorno de inversión en ese año.
@app.get("/get_return/{year}")
def get_return(year:int):
    v = {}
    for i,x in enumerate(df.title):
        if x not in v and df['release_year'][i] == year:
            v[x] = df['return'][i]
        elif df['release_year'][i] == year:
            v[x] += df['return'][i]
    return max(v,key=v.get)

#Película con el menor presupuesto en determinado año. La función debe llamarse get_min_budget(year) 
#deberia devolver el string con el nombre de la película, el año de estreno y el presupuesto, 
#en un diccionario con las llaves llamadas 'title', 'year', 'budget' y cada una con su valor correspondiente.
@app.get("/get_min_budget/{year}")
def get_min_budget(year:int):
    presupuesto = df[['budget','title','release_year']]
    pre = {}
    for i,x in enumerate(presupuesto.title):
        if x not in pre and presupuesto['release_year'][i] == year:
            pre[x] = presupuesto['budget'][i]
        elif presupuesto['release_year'][i] == year:
            pre[x] += presupuesto['budget'][i]
    return min(pre,key=pre.get)

#Lista con las 5 franquicias, colleciones o series de películas que más recaudaron históricamente. 
#La función se llamará get_collection_revenue() y debería devolver una lista de longitud 5 que contenga el 
#nombre en string de las 5 franquicias que más recaudaron históricamente.
@app.get("/get_collection_revenue")
def get_collection_revenue():
    lista = df[['name_production_companies','revenue','release_year']]
    company = {}
    for i,x in enumerate(lista.name_production_companies):
        if type(x) == list:
            for l in x:
                if l not in company:
                    company[l] = lista['revenue'][i]
                else:
                    company[l] += lista['revenue'][i]
        else:
            if x not in company:
                company[x] = lista['revenue'][i]
            else:
                company[x] += lista['revenue'][i]
            
    franquicias = sorted(company.items(), key=operator.itemgetter(1), reverse=True)
    return franquicias[0:5]
##SISTEMA DE RECOMENDACION
@app.get("/get_recommendation/{titulo}")
def get_recommendation(titulo: str):
    # Function to compute the IMDB weighted rating for each movie
    m = df['vote_count'].quantile(0.80)
    q_movies = df[(df['runtime'] >= 45) & (df['runtime'] <= 300)]
    q_movies = q_movies[q_movies['vote_count'] >= m]
    C = df['vote_average'].mean()
    def weighted_rating(x, m=m, C=C):
        v = x['vote_count']
        R = x['vote_average']
        # Compute the weighted score
        return (v/(v+m) * R) + (m/(m+v) * C)
    # Compute the score using the weighted_rating function defined above
    q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
    generos = []
    peliculas = []
    for x in list(q_movies[q_movies.title.str.contains(titulo.capitalize())].name_genres):
        for gen in x:
            generos.append(gen)
    for index,serie in q_movies.iterrows():
        if len(set(generos).intersection(set(serie[17]))) > 3:
            peliculas.append(q_movies.title[index])
    random.shuffle(peliculas)
    return peliculas[0:5]