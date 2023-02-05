import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import altair as alt
from scipy.stats import ranksums


## PARTE 00 - WEB SCRAPPING ###############################################################################################################
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import numpy as np

# URL PrincipaL do Projeto

# Define a dictionary of label and URL pairs
options = {"Campeonato Brasileiro 2022": "https://fbref.com/en/comps/24/schedule/Serie-A-Scores-and-Fixtures",
           "Premier League 2021-2022": "https://fbref.com/en/comps/9/2021-2022/schedule/2021-2022-Premier-League-Scores-and-Fixtures",
           "La Liga 2021-2022": "https://fbref.com/en/comps/12/2021-2022/schedule/2021-2022-La-Liga-Scores-and-Fixtures",
          "Serie A 2021-2022": "https://fbref.com/en/comps/11/2021-2022/schedule/2021-2022-Serie-A-Scores-and-Fixtures"}





selected_option = st.sidebar.selectbox("Choose an option", list(options.keys()))

selected_url = options[selected_option]

# COLETANDO O HTML
html = urlopen(selected_url)
        
# CRIANDO O BEAUTIFUL SOUP APARTIR DO HTML
soup = BeautifulSoup(html, features="lxml")

## PARTE 00 - CRIANDO O DATAFRAME #######################################################################################################
# CRIANDO O CABEÇALHO - HEADERS2
headers = [th.getText() for th in soup.findAll('th')]
headers2 = headers[1:14]

# CRIANDO AS LINHAS - ROWDATA
rows = soup.findAll('tr')[1:]
rows_data = [[td.getText() for td in rows[i].findAll('td')]
                    for i in range(len(rows))]

# CRIANDO UM DATAFRAME
mydata = pd.DataFrame(rows_data, columns = headers2)

# ACRESCENTANDO O VALOR - NUMERO RODADA
val_rodada = [th.getText() for th in soup.findAll('th')][14:]

# CRIANDO O CABEÇALHO - VARIAVEL ADICIONAL
titulo = ['Rodada']
mydata2 = pd.DataFrame(val_rodada, columns = titulo)

# CONCATENANDO OS DATAFRAMES
mydata3 = pd.concat([mydata, mydata2], axis = 1)

# DROPANDO COLUNAS
mydata3.drop(columns=['Match Report','Notes'], inplace = True)

## DF1 = BASE PRINCIPAL DO PROJETO!!!! FONTE - WEB SCRAPPING URL ##########################################################################
filtro  = mydata['Day'] != ''
mydata4 = mydata3[filtro]
df1 = mydata4


## DF1A = BASE P/RESULT FINAL!!!! FONTE - DF1 #########################################################################

Placar_Home = mydata4['Score'].astype(str).str.slice(0,1)
Placar_Away = mydata4['Score'].astype(str).str.slice(2,3)

mydata4['Placar_Home'] = Placar_Home
mydata4['Placar_Away'] = Placar_Away


## Marcando a Pontuação para Cada Time e Rodada

conditions = [
    (mydata4['Placar_Home'] > mydata4['Placar_Away']),
    (mydata4['Placar_Home'] < mydata4['Placar_Away']),
    (mydata4['Placar_Home'] == mydata4['Placar_Away'])
]

choices = [3,0,1]

mydata4['Result1'] = np.select(conditions, choices, default=0)


conditions2 = [
    (mydata4['Placar_Away'] > mydata4['Placar_Home']),
    (mydata4['Placar_Away'] < mydata4['Placar_Home']),
    (mydata4['Placar_Away'] == mydata4['Placar_Home'])
]

choices2 = [3,0,1]

mydata4['Result2'] = np.select(conditions2, choices2, default=0)

## Marcando o resultado final para Cada Time e Rodada

conditions3 = [
    (mydata4['Placar_Home'] > mydata4['Placar_Away']),
    (mydata4['Placar_Home'] < mydata4['Placar_Away']),
    (mydata4['Placar_Home'] == mydata4['Placar_Away'])
]

choices3 = ['VITORIA_MANDANTE','VITORIA_VISITANTE','EMPATE']

mydata4['RESULT_FINAL'] = np.select(conditions3, choices3, default=0)

df1A = mydata4

## DF3 = BASE PONTUAÇÃO ACUMULADA #########################################################################################################
dfC = pd.DataFrame(df1A[['Rodada', 'Home', 'Result1']])
dfD = pd.DataFrame(df1A[['Rodada', 'Away', 'Result2']])

dfC = dfC.rename(columns={'Rodada': 'Rodada', 'Home': 'Time', 'Result1': 'Pontos'})
dfD = dfD.rename(columns={'Rodada': 'Rodada', 'Away': 'Time', 'Result2': 'Pontos'})

df3 = pd.concat([dfC, dfD], axis=0)

df3['Rodada'] = df3['Rodada'].astype(int)
df3.sort_values(by=['Time', 'Rodada'], inplace=True)

df3['Pontos_Acum'] = df3.groupby('Time')['Pontos'].cumsum()


## DF55 = MELHOR ATAQUE ##################################################################################################################

df11 = pd.DataFrame(df1A[['Rodada', 'Home', 'Placar_Home']])
df22 = pd.DataFrame(df1A[['Rodada', 'Away', 'Placar_Away']])

df11 = df11.rename(columns={'Rodada': 'Rodada', 'Home': 'Time', 'Placar_Home': 'Gols_Feitos'})
df22 = df22.rename(columns={'Rodada': 'Rodada', 'Away': 'Time', 'Placar_Away': 'Gols_Feitos'})

df33 = pd.concat([df11, df22], axis=0)

df33['Gols_Feitos'] = df33['Gols_Feitos'].astype(int)
df44 = df33.groupby(['Time'])['Gols_Feitos'].sum()
df55 = pd.DataFrame(df44)

df55_sorted = df55.sort_values('Gols_Feitos')

df55_sorted.reset_index(inplace=True)


## DFEE = MELHOR DEFESA ##################################################################################################################
dfaa = pd.DataFrame(df1A[['Rodada', 'Home', 'Placar_Away']])
dfbb = pd.DataFrame(df1A[['Rodada', 'Away', 'Placar_Home']])

dfaa = dfaa.rename(columns={'Rodada': 'Rodada', 'Home': 'Time', 'Placar_Away': 'Gols_Sofridos'})
dfbb = dfbb.rename(columns={'Rodada': 'Rodada', 'Away': 'Time', 'Placar_Home': 'Gols_Sofridos'})

dfcc = pd.concat([dfaa, dfbb], axis=0)

dfcc['Gols_Sofridos'] = dfcc['Gols_Sofridos'].astype(int)
dfdd = dfcc.groupby(['Time'])['Gols_Sofridos'].sum()
dfee = pd.DataFrame(dfdd)

dfee_sorted = dfee.sort_values('Gols_Sofridos')

dfee_sorted.reset_index(inplace=True)

## DFRR1 = REFEREE #######################################################################################################################

df1B = df1A

## Marcando a Pontuação para Cada Time e Rodada

conditions3 = [
    (df1B['Placar_Home'] > df1B['Placar_Away']),
    (df1B['Placar_Home'] < df1B['Placar_Away']),
    (df1B['Placar_Home'] == df1B['Placar_Away'])
]

choices3 = ['VITORIA_MANDANTE','VITORIA_VISITANTE','EMPATE']

df1B['RESULT_FINAL'] = np.select(conditions3, choices3, default=0)

dfrr1 = pd.DataFrame(df1B[['Rodada', 'Referee', 'RESULT_FINAL']])

## IMPORT DE BASES OBTIDAS NO WEB SCRAPPING ###############################################################################################
# df1 = pd.read_csv('mydata4.csv')
# df3 = pd.read_csv('df3.csv')
# df55_sorted = pd.read_csv('df55_sorted.csv')
# dfee_sorted = pd.read_csv('dfee_sorted.csv')
# dfrr1 = pd.read_csv('dfrr1.csv')
 
###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################
###########################################################################################################################################

st.image("https://images.cdn4.stockunlimited.net/preview1300/soccer-banner-with-france-flag_1818626.jpg"
        , width=1000)



## PARTE 01 - CAMPANHAS DOS TIMES #########################################################################################################
st.title(f'{selected_option}')


# create a filter selection widget
filter_value = st.selectbox("Selecione Time 1:", df3['Time'].unique())
filter_value2 = st.selectbox("Selecione Time 2:", df3['Time'].unique())

st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Campanha dos Times por Rodada</h1>    """,    unsafe_allow_html=True,)


st.write('Legenda: ') 

st.markdown(f"<span style='color:red'>{filter_value}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:blue'>{filter_value2}</span>", unsafe_allow_html=True)


# filter the dataframe based on the selected column and value
filtered_df3 = df3[df3['Time'] == filter_value]
filtered_df4 = df3[df3['Time'] == filter_value2]

# Create a chart with multiple line encodings
line = alt.Chart(filtered_df3, width=1000, height=500).mark_line().encode(
    x='Rodada',
    y='Pontos_Acum', color=alt.value('red')
) + alt.Chart(filtered_df4).mark_line().encode(
    x='Rodada',
    y='Pontos_Acum', color=alt.value('blue')
)


st.altair_chart(line)


## PARTE 02 - COMO FOI A RODADA? ##########################################################################################################
st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Como foi a rodada?</h1>    """,    unsafe_allow_html=True,)

# Display filtered dataframe as a table
df10 = df1[['Home','Score','Away','Attendance','Venue','Rodada']]

filter_value3 = st.selectbox("Selecione a Rodada:", df10['Rodada'].unique())

# Filter dataframe based on a condition
filter_condition = df10["Rodada"] == filter_value3
filtered_df = df10[filter_condition]

# Display filtered dataframe as a table
st.dataframe(filtered_df, width=1000)


## PARTE 03 - ANALISE MELHOR ATAQUE - MELHOR DEFESA DO CAMPEONADO #########################################################################
## 03.1 - ATAQUE
st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Melhor Ataque do Campeonato</h1>    """,    unsafe_allow_html=True,)

# Plot the bar chart
bar_chart = alt.Chart(df55_sorted, width=1000, height=500).mark_bar(color='green').encode(
   alt.X('Time:N', sort='-y'),
   alt.Y('Gols_Feitos:Q'))

st.altair_chart(bar_chart)

## 03.2 - ATAQUE
st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Melhor Defesa do Campeonato</h1>    """,    unsafe_allow_html=True,)

# Plot the bar chart
bar_chart2 = alt.Chart(dfee_sorted, width=1000, height=500).mark_bar(color='red').encode(
   alt.X('Time:N', sort='y'),
   alt.Y('Gols_Sofridos:Q'))

st.altair_chart(bar_chart2)


## PARTE 04 - ANALISE POR JUIZ ############################################################################################################

st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Análise dos Juizes</h1>    """,    unsafe_allow_html=True,)

# Tratando o DataFrame Original
dfrr_empate = dfrr1[dfrr1['RESULT_FINAL'] == 'EMPATE']
dfrr_win_casa = dfrr1[dfrr1['RESULT_FINAL'] == 'VITORIA_MANDANTE']
dfrr_win_visit = dfrr1[dfrr1['RESULT_FINAL'] == 'VITORIA_VISITANTE']

dfrr_empate2 = dfrr_empate.groupby(['Referee'])['RESULT_FINAL'].count()
dfrr_win_casa2 = dfrr_win_casa.groupby(['Referee'])['RESULT_FINAL'].count()
dfrr_win_visit2 = dfrr_win_visit.groupby(['Referee'])['RESULT_FINAL'].count()

dfrr_empate2_s = dfrr_empate2.sort_values()
dfrr_win_casa2_s = dfrr_win_casa2.sort_values()
dfrr_win_visit2 = dfrr_win_visit2.sort_values()

dfrr_empate2_s = pd.DataFrame(dfrr_empate2_s)
dfrr_empate2_s.reset_index(inplace=True)

dfrr_win_casa2_s = pd.DataFrame(dfrr_win_casa2_s)
dfrr_win_casa2_s.reset_index(inplace=True)

dfrr_win_visit2 = pd.DataFrame(dfrr_win_visit2)
dfrr_win_visit2.reset_index(inplace=True)

# Plot the bar chart - JUIZ SEGURA JOGO
bar_chart3 = alt.Chart(dfrr_empate2_s, width=300, height=500).mark_bar(color='yellow').encode(
    alt.X('RESULT_FINAL:Q'),
    alt.Y('Referee:N', sort='-x')
   )

# Plot the bar chart - JUIZ CASEIRO
bar_chart4 = alt.Chart(dfrr_win_casa2_s, width=300, height=500).mark_bar(color='blue').encode(
    alt.X('RESULT_FINAL:Q'),
    alt.Y('Referee:N', sort='-x')
   )


# Plot the bar chart - JUIZ FAVORECE VISITANTE

bar_chart5 = alt.Chart(dfrr_win_visit2, width=300, height=500).mark_bar(color='grey').encode(
    alt.X('RESULT_FINAL:Q'),
    alt.Y('Referee:N', sort='-x')
   )

# COLOCAR OS GRAFICOS LADO A LADO COM COLUNAS DO STREAMLIT
col1, col2, col3 = st.columns(3, gap="large")

with col1:
   st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>QTD EMPATES x JUIZ</h1>    """,    unsafe_allow_html=True,)
   st.altair_chart(bar_chart3)

with col2:
   st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>QTD VITORIAS MANDANTE x JUIZ</h1>    """,    unsafe_allow_html=True,)
   st.altair_chart(bar_chart4)

with col3:
   st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>QTD VITORIAS VISITANTE x JUIZ</h1>    """,    unsafe_allow_html=True,)
   st.altair_chart(bar_chart5)

    
## PARTE 05 - TESTE DE HIPOTESE ###########################################################################################################
st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Torcida Ganha Jogo?</h1>    """,    unsafe_allow_html=True,)



# Preparando o DataFrame
dfx = pd.DataFrame(df1A[['Attendance', 'RESULT_FINAL']])

## FILTRANDO NÃO VAZIO
filtro1  = dfx['Attendance'] != ''
dfx2 = dfx[filtro1]

dfx3 = dfx2.dropna()

# Replace the commas in the 'col' column
dfx3['Attendance'] = dfx3['Attendance'].str.replace(',', '')
dfx3['Attendance'] = dfx3['Attendance'].astype(int)

# Plot the scatter plot using altair
chart_dsip = alt.Chart(dfx3, width=1000, height=500).mark_point().encode(
    x='Attendance',
    y='RESULT_FINAL',
    color='RESULT_FINAL'
)

chart_dsip = chart_dsip.configure_axisY(labelFontSize=10)

# Show the plot in Streamlit
st.altair_chart(chart_dsip)
 
st.markdown("""    <style>    h1 {        font-size: 18pt;    }    </style>
    <h1>Teste de Hipotese:</h1>    """,    unsafe_allow_html=True,)

st.text("HNull - Jogos com bom Attendence favorecem vitoria")
st.text("HAlt - O Attendence não interfere no resultado do jogos")

Publico = dfx2['Attendance']
Resultado_Favoravel = dfx2['RESULT_FINAL']

r = ranksums('Publico', 'Resultado_Favoravel')

st.text("O Valor do P-Value é:")
st.markdown(f"<span style>{r.pvalue}</span>", unsafe_allow_html=True)
st.text("")
st.text("Conclusão: A diferença é insignificante (Pvalue > 0,05)")
st.text("Desta forma descartamos a hipótese alternativa")
st.text("Se mantém a hipótese nula (Jogos com bom Attendence favorecem vitoria)")



## PARTE 06 - OPINIÃO DO ESPECIALISTA ####################################################################################################

# Define a dictionary of label and URL pairs
options2 = {"Campeonato Brasileiro 2022": "Fala Casão",
           "Premier League 2021-2022": "Speak-out Big House",
           "La Liga 2021-2022": "Habla Casa Grande",
          "Serie A 2021-2022": "Parla Grande Casa"}

options3 = {"Campeonato Brasileiro 2022": 
            "O futebol brasileiro vive um momento\nde reflexão, em meio aos escândalos\nenvolvendo sua entidade máxima, à\ncrise política envolvendo todo o\nseu arranjo institucional e ao\ndescontentamento expresso pelos\ntorcedores, sobretudo pela\ndesvalorização das competições\ndo país enquanto produto. Não há\nmomento melhor para se discutir a\nnecessidade de reestruturação do\nfutebol brasileiro",
            
            
            
           "Premier League 2021-2022": 
            "Brazilian football is going\nthrough a moment of reflection,\namid the scandals involving its\nhighest body, the political crisis\ninvolving its entire institutional\narrangement and the discontent\nexpressed by fans, especially\ndue to the devaluation of the\ncountry's competitions as a\nproduct. There is no better\ntime to discuss the need to\nrestructure Brazilian football",
            
            
           "La Liga 2021-2022": "El fútbol brasileño atraviesa\nun momento de reflexión, en\nmedio de los escándalos que\ninvolucran a su máximo órgano,\nla crisis política que involucra\na todo su arreglo institucional\ny el descontento expresado por\nlos hinchas, especialmente por\nla devaluación de las competencias\ndel país como producto. No hay mejor\nmomento para discutir la necesidad\nde reestructurar el fútbol brasileño.",
            
            
            
          "Serie A 2021-2022": "Il calcio brasiliano sta\nattraversando un momento di\nriflessione, tra gli scandali\nche hanno coinvolto il suo\nmassimo organo, la crisi politica\nche ha coinvolto tutto il suo\nassetto istituzionale e il\nmalcontento espresso dai\ntifosi, soprattutto per la\nsvalutazione del prodotto\ndelle competizioni del Paese.\nNon c'è momento migliore per\ndiscutere della necessità di\nristrutturare il calcio brasiliano"}


selected_header = options2[selected_option]

selected_comment = options3[selected_option]

col1, col2 = st.columns(2)

with col1:
   st.header("Opinião do Especialista!")
   st.image("https://placar.abril.com.br/wp-content/uploads/2021/09/casagrande.jpg?quality=70&strip=info&w=750&h=500&crop=1")

with col2:
   st.header(f"{selected_header}")
   st.text(f"{selected_comment}")

