import pandas as pd
from os import environ, listdir
from os.path import join
from re import search
from mysql.connector import connect
from enum import Enum

file = join(environ["USERPROFILE"], "Desktop/concatenated_scraps.csv")

pd.set_option("display.max_columns", None)
df = pd.read_csv(file)
df = df.drop(df.columns[0],  axis = 1)
for cn in df.keys():
    df[cn] = df[cn].replace("tbd", "")
    df[cn] = df[cn].replace("", None)
df['releasedate'] = pd.to_datetime(df['releasedate']).dt.strftime('%Y-%m-%d')
df = df.drop_duplicates(subset=['gamename'])

def return_droped_na():
    df['metarating'] = pd.to_numeric(df['metarating'], errors='coerce')
    df['userrating'] = pd.to_numeric(df['userrating'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['ESRB'])
    df = df.dropna(subset=['metarating', 'userrating', 'price'])
    return df

class mysqlLogin(Enum):
    USER = "root"
    PASSWORD = "12345"
    HOST = "127.0.0.1"
    DATABASE = "scraper_videojuegos"
mysql_conn = connect(user = mysqlLogin.USER.value, password = mysqlLogin.PASSWORD.value, host = mysqlLogin.HOST.value, database = mysqlLogin.DATABASE.value)
mysql_cur = mysql_conn.cursor()

def parse_arguments_for_gen_procedure():
    result = list(zip(df['gamename'], df['platform'], df["releasedate"], df['metarating'], df['userrating'], df['developer'], df['publisher'], df['genre'], df['ESRB'], df['price']))
    return result

if __name__ == "__main__":
    r = parse_arguments_for_gen_procedure()

    for data_parsed in r:
        #query = f"insert into Juegos(nombre, fecha_lanzamiento, precio) values (\"{data_parsed[0].replace('"', "'")}\",\"{data_parsed[2]}\",{data_parsed[9]});"
        #print(query)
        #mysql_cur.execute(query)
        print(data_parsed)
        data_parsed = tuple(None if pd.isna(item) else item for item in data_parsed)
        mysql_cur.callproc("fill_from_tuple", data_parsed)
    mysql_conn.commit()
    # plataformas no estan normalizadas PC,PS5,PS4 (valores atomicos)
    for data_parsed in r:
        for platform in data_parsed[1].split(","):
            data_parsed = tuple(None if pd.isna(item) else item for item in data_parsed)
            data_parsed = (data_parsed[0], platform)
            print(data_parsed)
            mysql_cur.callproc("fill_consoles_from_tuple", data_parsed)
    mysql_conn.commit()

#df.to_csv(join(environ["USERPROFILE"], "Desktop/concatenated_scraps.NumericRemove.csv"))
