import requests
from bs4 import BeautifulSoup
import pandas as pd
import solara
import solara.lab
from solara.website.utils import apidoc

url = "https://www.fdic.gov/buying/historical/structured/oil-gas-sales/"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', attrs = {'class': 'standard'})

data = []
for row in table.find_all('tr'):
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

df = pd.DataFrame(data)
df.columns = ['lot', 'name', 'sale_price', 'sale_date']
df = df.drop([0])



@solara.component
def Page():

    with solara.Column() as main:
        with solara.AppBarTitle():
            solara.Text("Energy Net Previous Sales")
        with solara.Sidebar():
            solara.Markdown("## I am in the sidebar")
            #solara.SliderInt(label="Ideal for placing controls")
        with solara.Card(margin=4) as column_header_info:
            solara.DataFrame(df, items_per_page=10)  # main content
    return main




