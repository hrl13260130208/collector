import pandas as pd
from pandas import DataFrame


def read():
    data=pd.read_excel(r"C:\Users\zhaozhijie.CNPIEC\Desktop\1.xls")
    print(type(data))
    print(data.ix[1]["FULL_PATH"])

    # data["FULL_PATH"][data["AID"]==24332361]="No pdf"
    # data.to_excel(r"C:\Users\zhaozhijie.CNPIEC\Desktop\1.xls")


if __name__ == '__main__':
    read()