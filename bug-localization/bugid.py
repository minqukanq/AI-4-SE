import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from lxml import html


AspectJ = pd.read_excel('dataset/AspectJ.xlsx', engine='openpyxl')
AspectJ_id_df = AspectJ['bug_id']
AspectJ_id_df.to_csv('AspectJ.txt', index=False, sep='\n')

Birt = pd.read_excel('dataset/Birt.xlsx', engine='openpyxl')
Birt_id_df = Birt['bug_id']
Birt_id_df.to_csv('Birt.txt', index=False, sep='\n')

Eclipse_Platform_UI = pd.read_excel('dataset/Eclipse_Platform_UI.xlsx', engine='openpyxl')
Eclipse_Platform_UI_id_df = Eclipse_Platform_UI['bug_id']
Eclipse_Platform_UI_id_df.to_csv('Eclipse_Platform_UI.txt', index=False, sep='\n')

JDT = pd.read_excel('dataset/JDT.xlsx', engine='openpyxl')
JDT_id_df = JDT['bug_id']
JDT_id_df.to_csv('JDT.txt', index=False, sep='\n')

SWT = pd.read_excel('dataset/SWT.xlsx', engine='openpyxl')
SWT_id_df = SWT['bug_id']
SWT_id_df.to_csv('SWT.txt', index=False, sep='\n')



