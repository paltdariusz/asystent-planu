import plotly.express as px
import pandas as pd
from datetime import datetime
import os.path


def plot(kursy, tab, zapis, title, length):
    temp = kursy[kursy['Tydzień'].isin(tab)].copy()
    temp['Typ'] = temp['Kod kursu'].str[-1]
    temp.loc[temp['Typ'] == 'W', 'Typ'] = 'Wykład'
    temp.loc[temp['Typ'] == 'C', 'Typ'] = 'Ćwiczenia'
    temp.loc[temp['Typ'] == 'L', 'Typ'] = 'Laboratorium'
    temp.loc[temp['Typ'] == 'S', 'Typ'] = 'Seminarium'
    temp.loc[temp['Typ'] == 'P', 'Typ'] = 'Projekt'
    date = datetime.today().strftime("%Y-%m-%d")
    df = pd.DataFrame({
        'Dni tygodnia': temp['Dzień'],
        'Start': date + ' ' + temp['Godzina rozpoczęcia'],
        'Finish': date + ' ' + temp['Godzina zakończenia'],
        'Forma zajęć': temp['Typ'],
        'Annotations': temp['Grupa kursu'] + ' ' + temp['Nazwa kursu']
    })
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Dni tygodnia", color="Forma zajęć", text='Annotations')
    fig.update_layout(yaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4, 5],
                                 ticktext=['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']), title=title)
    fig.update_traces(textposition='inside', textfont_size=12, textfont_color='black')
    fig.update_yaxes(autorange="reversed")
    fig.update_yaxes(type="category")
    # fig.show()
    directory = f'results/{str(length)}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    fig.write_image(f'{directory}/{zapis}.svg', width=1920, height=1080)


def visualize(kursy, length):

    plot(kursy, ['P', 'C'], 'TP', 'Tydzień parzysty', length)
    plot(kursy, ['N', 'C'], 'TN', 'Tydzień nieparzysty', length)
