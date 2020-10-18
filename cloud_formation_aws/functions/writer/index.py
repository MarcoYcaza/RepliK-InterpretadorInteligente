import json
import boto3
import os
import pg8000
from trp import Document
import re
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from Levenshtein import distance
import itertools
import string
import pandas as pd
from io import StringIO
from functools import reduce
import numpy as np

def getJobResultsAllinOne(jobid):
    """
    Get readed pages based on jobId
    """
    textract = boto3.client('textract')
    
    doc_response = textract.get_document_analysis(JobId=jobid)

    return doc_response
def getDocConfidence(doc):
    temp=[[line.confidence for line in page.lines] for page in doc.pages][0]
    return sum(temp)/len(temp)
       
def return_coincidence(df,mypatterns):

    if not (type(df) == 'NoneType'):
       
        if df.columns[0] == 'COL1':
            
            for pattern in mypatterns:
                
                fngs = list(df[df['COL1'].str.match(pattern)][df.columns[1]].values)    
                
                if len(fngs)> 0 :

                    return fngs[0]
        else:
            return None    

    return None
    
########LAS DE CSV#########################################################################
def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows
def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text
def get_table_csv_results(response,page_number):
    # Get the text blocks
    blocks=response['Blocks']

    blocks_map = {}
    table_blocks = []

    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''

    csv += generate_table_csv(table_blocks[page_number-1], blocks_map)
    csv += '\n\n'

    return csv
def generate_table_csv(table_result, blocks_map):
    rows = get_rows_columns_map(table_result, blocks_map)

    # get cells.
    csv = ''

    for row_index, cols in rows.items():
        
        for col_index, text in cols.items():
            csv += '{}'.format(text) + ";"
        csv += '\n'
        
    csv += '\n\n\n'
    return csv

####### NUEVAS #########################################################################################
def drop_Nota(df):
    for col in df.columns:
        try:
            if (any(df[col].str.contains("^nota$",regex=True)) |
                any(df[col].str.contains("^notal$",regex=True)) |
                any(df[col].str.contains("^notas$",regex=True)) ):
                return col
        except:
            return None

def n_of_tables(doc):
    tables = [[table for table in page.tables] for page in doc.pages]
    tables = list(itertools.chain.from_iterable(tables)) 
    return len(tables)

def get_tables(doc):
    return [[table for table in page.tables] for page in doc.pages]
    
def mydataframe(doc_response,table_index):
        
        temp0 = get_table_csv_results(doc_response,table_index)
        
        temp1 =  reduce(lambda  a,b : a+","+b ,[i.replace('.','') for i in temp0.split(",")])
        temp1 =  reduce(lambda  a,b : a+","+b ,[i.replace(',','') for i in temp1.split(",")])
        temp1 =  reduce(lambda  a,b : a+","+b ,[i.replace('$','') for i in temp1.split(",")])
        temp1 =  reduce(lambda  a,b : a+","+b ,[i.replace(')','') for i in temp1.split(",")])
        temp1 =  reduce(lambda  a,b : a+","+b ,[i.replace('(','') for i in temp1.split(",")])

        df = pd.read_csv(StringIO(temp1), sep=";")

        df.columns= df.columns.str.strip().str.lower()

        df.fillna("null",inplace=True)

        df.drop(columns=[ col for col in df.columns if (len(pd.unique(df[col])) == 1) ],inplace=True)

        for col in df.columns:
            df[col]=df[col].astype(str)

        df = df.rename(columns={df.columns[0]: 'COL1'})

        for col_name in df.columns:
            df[col_name] = df[col_name].map(lambda x: x if type(x)!=str else x.lower())
            df[col_name] = df[col_name].map(lambda x: x if type(x)!=str else "".join(x.split()))

        if (r:=[x for x in df.columns if x.find("nota")>=0]):
            df.drop(columns=r,inplace=True)
        
        if (r:=[x for x in df.columns if x=="14"]):
            df.drop(columns=r,inplace=True)

        if (x := drop_Nota(df)):
            df.drop(columns=x,inplace=True)
    
        return df
        
def clean_trashchar(texto): #no space and no puntuation
    alpha = set(string.ascii_lowercase)
    
    return ''.join(ch for ch in texto if ch not in alpha)
    
def cleaned_text(texto): #no space and no puntuation
    exclude = set(string.punctuation)
    temp = "".join(texto.split())
    temp= ''.join(ch for ch in temp if ch not in exclude)
    return temp
        
### NUEVAS  ################################################################################################

def findMeasUnit(text):
    stemmer = SnowballStemmer('spanish')

    for t in text.split():
        if (w:=re.search('pesos',stemmer.stem(t))):
            return "COP"
    for t in text.split():
        if (w:=re.search('dolar',stemmer.stem(t))):
            return "USD"
    for t in text.split():
        if (w:=re.search('soles',stemmer.stem(t))):
            return "PEN"
    for t in text.split():
        if (w:=re.search('mx',stemmer.stem(t))):
            return "MXN"
    for t in text.split():
        if (w:=re.search('col',stemmer.stem(t))):
           return "COP"

    for t in text.split():
        if (w:=re.search('colon',stemmer.stem(t))):
           return "CRC"

    for t in text.split():
        if (w:=re.search('chilen',stemmer.stem(t))):
           return "CLP"

    for t in text.split():
        if (w:=re.search('\$',stemmer.stem(t))):
           return "USD"
    for t in text.split():
        if (w:=re.search('s/',stemmer.stem(t))):
           return "PEN"
    
    for t in text.split():
        if (w:=re.search('€',stemmer.stem(t))):
           return "EUR"

    for t in text.split():
        if (w:=re.search('₡',stemmer.stem(t))):
           return "CRC"

    for t in text.split():
        if (w:=re.search('cop',stemmer.stem(t))):
            return "COP"
    for t in text.split():
        if (w:=re.search('usd',stemmer.stem(t))):
            return "USD"

    for t in text.split():
        if (w:=re.search('eur',stemmer.stem(t))):
           return "EUR"

    return "NA"

def myDateMapper(date,actualYear="2020"):
    
    """
    Esta función solo funciona con python 3.8 dado que utilizamos el operador Walrus.
    
    Requiere módulos re.

    myDateMapper devuelve la fecha detectada con búsquedas regulares en string , de no encontrar 
    una fecha , devuelve por defecto "no date data"

    Si no se pasa como argumento el año actual , se pone por defecto el presente año en el que genero
    el código:

    Ejemplo de uso:
    
    myDateMapper("12 23 2021")
    myDateMapper("lunes 25 de octubre del 2031")
    myDateMapper("Al 2020")
    myDateMapper("2020")
    myDateMapper('en 29/10/2011')
    myDateMapper('el 29-10-2020')
    myDateMapper('al 29-10-10')
    myDateMapper("24 de octubre del 2005")
    myDateMapper("Lunes 02 de octubre de 1994")

    > myDateMapper(g,"2020") 
    > 24 oct 2005
    """
    date = date.lower()
    
    day =""
    month=""
    year=""

    #year
    if (w:=re.search('\d\d \d\d \d\d',date)): year = w.group(0)[-2:]           
    if (w:=re.search('\d\d-\d\d-\d\d',date)): year = actualYear[0:2]+w.group(0)[-2:]
    if (w:=re.search('\d\d/\d\d/\d\d',date)): year = actualYear[0:2]+w.group(0)[-2:]
    if (w:=re.search('\d\d \d\d \d\d\d\d',date)): year = w.group(0)[-4:]           
    if (w:=re.search('\d\d-\d\d-\d\d\d\d',date)): year = w.group(0)
    if (w:=re.search('\d\d/\d\d/\d\d\d\d',date)): year = w.group(0)
    if (w:=re.search('\d\d\d\d',date)): year = w.group(0)
    if (w:=re.search('\d\d\d\d',date)): year = w.group(0)
    #month
    if (w:=re.search('\d\d \d\d \d\d\d\d',date)): month = w.group(0)[3:5]       
    if (w:=re.search('\d\d-\d\d-\d\d\d\d',date)): month = w.group(0)[3:5] 
    if (w:=re.search('\d\d/\d\d/\d\d\d\d',date)): month = w.group(0)[3:5]
    if (w:=re.search('jan|feb|mar|apr|may|jun|jul|ago|set|sep|oct|nov|dec',date)): month = w.group(0)
    if (w:=re.search('ene|feb|mar|abr|may|jun|jul|ago|set|sep|oct|nov|dic',date)): month = w.group(0)
    if (w:=re.search('\d\d-\d\d-\d\d',date)): month = w.group(0)[3:5]
    if (w:=re.search('\d\d/\d\d/\d\d',date)): month = w.group(0)[3:5]
    #day
    if (w:=re.search('\d\d de',date)): day = w.group(0)[0:2]         
    if (w:=re.search('\d\d de',date)): day = w.group(0)[0:2]
    if (w:=re.search('\d\d de',date)): day = w.group(0)[0:2]
    if (w:=re.search('\d\d \d\d \d\d\d\d',date)): day = w.group(0)[0:2]         
    if (w:=re.search('\d\d-\d\d-\d\d\d\d',date)): day = w.group(0)[0:2]
    if (w:=re.search('\d\d/\d\d/\d\d\d\d',date)): day = w.group(0)[0:2]
    if (w:=re.search('\d\d-\d\d-\d\d',date)) : day=w.group(0)[0:2]
    if (w:=re.search('\d\d/\d\d/\d\d',date)): day=w.group(0)[0:2]
    
    if ((day == "") & (month == "") & (year =="")):
        return ""
    
    return f"{day} {month} {year}"

def getJobResults(jobId):
    """
    Get readed pages based on jobId
    """

    pages = []
    textract = boto3.client('textract')
    response = textract.get_document_analysis(JobId=jobId)
    
    pages.append(response)

    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):
        response = textract.get_document_analysis(JobId=jobId, NextToken=nextToken)
        pages.append(response)
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages
    
def get_connection():
    """
    Method to establish the connection to RDS using IAM Role based authentication.
    """
    try:
        print ('Connecting to database')
        client = boto3.client('rds')
        DBEndPoint = os.environ.get('DBEndPoint')
        DatabaseName = os.environ.get('DatabaseName')
        DBUserName = os.environ.get('DBUserName')
        # Generates an auth token used to connect to a db with IAM credentials.
        password = client.generate_db_auth_token(
            DBHostname=DBEndPoint, Port=5432, DBUsername=DBUserName
        )
        # Establishes the connection with the server using the token generated as password
        conn = pg8000.connect(
            host=DBEndPoint,
            user=DBUserName,
            database=DatabaseName,
            password=password,
            ssl={'sslmode': 'verify-full', 'sslrootcert': 'rds-ca-2015-root.pem'},
        )
        print ("Succesful connection!")
        return conn
    except Exception as e:
        print ("While connecting failed due to :{0}".format(str(e)))
        return None

def make_query(doc,doc_response,doc_key,mypatterns):
       
    #Name of the document
    pyme_document = doc_key
    n_totalAssets = 0.0
    n_Liabilities = 0.0
    n_coherency   = 0.0
    n_caja        = 0.0
    n_sales       = 0.0
    n_totalEquity = 0.0
    n_costSales = 0.0
    n_grossProfit = 0.0
    n_netProfit = 0.0
    n_operatingProfit = 0.0
    profitBeforeTax = 0.0
    
    n_accuracy      = getDocConfidence(doc)
    
    print(n_accuracy)
    
    #Algorithm to find variables ######################################################################################
    #Date Finder
    found_dates = []
    
    for n_pag in range(len(doc.pages)):
        temp=[ myDateMapper(ln) for ln in [line.text for line in doc.pages[n_pag].lines] if myDateMapper(ln) != ""]
        if len(temp) > 0:
            found_dates.append(temp[0]) #una ocurrencia de fecha en página
        
    my_date = found_dates[0] if len(found_dates)>0 else "NA"
    
    temp = 0
    #Unit Finder
    found_measunit = []

    for n_pag in range(len(doc.pages)):
        temp=[ findMeasUnit(ln) for ln in [line.text for line in doc.pages[n_pag].lines] if findMeasUnit(ln) != "NA"]
        
        if len(temp) > 0:
            found_measunit.append(temp[0]) #una ocurrencia de unidad en página

    units   = found_measunit[0] if len(found_measunit)>0 else "NA"
    
    #Total Activo Finder###############################################################################################
    ###################################################################################################################
    
    #doc_response = doc_response[0]
    
    #print(doc_response)
    
    #print(doc_response)
    try:
        qTables = n_of_tables(doc)
    except:
        qTables = 3
        
    print(qTables)
    
    #ACTIVOS
    for i in range(qTables):
        try:
    
            df = mydataframe(doc_response,i)        
            try:
                if return_coincidence(df,mypatterns['p_activos']):
                    temp = str(return_coincidence(df,mypatterns['p_activos']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        
                        n_totalAssets = 0.0
                    else:
                        n_totalAssets = float(temp)
                    #break
            except:
                    print("error en returnTA")
                    n_totalAssets = 0.0
        except:
                pass    
    print(f"activos es: {n_totalAssets}")
    
    #PASIVOS    
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_pasivos']):
                    temp = str(return_coincidence(df,mypatterns['p_pasivos']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_Liabilities = 0.0
                    else:
                        n_Liabilities = float(temp)
                    #break   
            except:
                    n_Liabilities = 0.0
        except:
                pass  
    
    print(f"los pasivos son: {n_Liabilities}")
    
    #VENTAS E INGRESOS
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:
                print(f"la tabla donde crashea es: {i}")
                print(return_coincidence(df,mypatterns['p_ingreso']))
                
                if return_coincidence(df,mypatterns['p_ingreso']):
                
                    temp = str(return_coincidence(df,mypatterns['p_ingreso']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_sales = 0.0
                    else:
                        n_sales = float(temp)
                    #break   
            except:
                    n_sales = 0.0
        except:
                pass
        
    print(f"ventas es: {n_sales}")
    #CAJA Y EFECTIVO
    
    for i in range(qTables):
        try:
            
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_caja']):
                    temp = str(return_coincidence(df,mypatterns['p_caja']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_caja = 0.0
                    else:
                        n_caja = float(temp)
                    #break   
            except:
                    n_caja = 0.0
        except:
                pass 
    print(f"CAJA es: {n_caja}")        
    #PATRIMONIO   
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_patrimonio']):
                
                    temp = str(return_coincidence(df,mypatterns['p_patrimonio']))
                    temp =cleaned_text(temp)
                    temp =clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_totalEquity = 0.0
                    else:
                        n_totalEquity = float(temp)
                    #break   
            except:
                    n_totalEquity = 0.0   
        except:
                pass
    print(f"patrimonio es: {n_totalEquity}") 
    #COSTO_VENTAS   
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_cventas']):
                    temp = str(return_coincidence(df,mypatterns['p_cventas']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_costSales = 0.0
                    else:
                        n_costSales = float(temp)
                    #break   
            except:
                    n_costSales = 0.0   
        except:
                pass    
    print(f"costo ventas es: {n_costSales}") 
    #UTILIDAD_BRUTA   
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_ubruta']):
                    temp = str(return_coincidence(df,mypatterns['p_ubruta']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_grossProfit = 0.0
                    else:
                        n_grossProfit = float(temp)
                    #break   
            except:
                    n_grossProfit = 0.0   
        except:
                pass
    print(f"utilidad bruta es: {n_grossProfit}") 
    #UTILIDAD_OPERACIONAL   
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_utopera']):
                    temp = str(return_coincidence(df,mypatterns['p_utopera']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_operatingProfit = 0.0
                    else:
                        n_operatingProfit = float(temp)
                    #break   
            except:
                    n_operatingProfit = 0.0   
        except:
                pass
                
    print(f"utilidad operacional es: {n_operatingProfit}") 
    #UTILIDAD ANTES DE IMPUESTOS   
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_antesimp']):
                    temp = str(return_coincidence(df,mypatterns['p_antesimp']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        profitBeforeTax = 0.0
                    else:
                        profitBeforeTax = float(temp)
                    #break   
            except:
                    profitBeforeTax = 0.0   
        except:
                pass
    print(f"utilidad antes del impuesto es: {profitBeforeTax}")           
    #UTILIDAD NETA  
    for i in range(qTables):
        try:
            df = mydataframe(doc_response,i)
            try:    
                if return_coincidence(df,mypatterns['p_uneta']):
                    temp = str(return_coincidence(df,mypatterns['p_uneta']))
                    temp=cleaned_text(temp)
                    temp=clean_trashchar(temp)
                    if ((temp == "")|(temp == "null")):
                        n_netProfit = 0.0
                    else:
                        n_netProfit = float(temp)
                    #break   
            except:
                    n_netProfit = 0.0   
        except:
                pass       
    print(f"utilidad neta es: {n_netProfit}")  
    
    
    n_coherency  = n_coherency + 10.0 if n_totalAssets > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_Liabilities > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_totalEquity > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_sales       > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_caja       > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_costSales > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_grossProfit > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_operatingProfit > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if profitBeforeTax > 0.0 else n_coherency
    n_coherency  = n_coherency + 10.0 if n_netProfit > 0.0 else n_coherency
    
    
    ###################################################################################################################
    ### Setting variables #############################################################################################
    
    date = my_date
    mnt_units = units
    
    #Text
    if( n_accuracy >= 95):
        more_info = "información adicional"
    else:
        more_info = "la precisión de detección es inferior al 95% ,se sugiere re-escanear para tener más nitides."
    
    #Pyme document
    pyme_document =  "'"+ pyme_document +"'"    
    date          =  "'" + date +"'"
    mnt_units     =  "'" + mnt_units +"'"
    more_info     =  "'" + more_info +"'"

    #Double precision
    cashResources = n_caja
    accuracy = n_accuracy
    ventas = n_sales
    costSales = n_costSales
    grossProfit = n_grossProfit
    netProfit = n_netProfit
    operatingProfit = n_operatingProfit
    profitBeforeTax = profitBeforeTax
    totalAssets = n_totalAssets
    totalEquity = n_totalEquity
    totalLiabilities =  n_Liabilities
    coherency = n_coherency

    isProcessed = True
    ####################################################################################################################

    query = f'''update hackaton_pyme set 
    
    "date"  = {date},
    "cashResources" = {cashResources},
    "accuracy" ={accuracy},
    "more_info" = {more_info},
    "costSales" ={costSales},
    "grossProfit" ={grossProfit},
    "netProfit" ={netProfit},
    "sales" ={ventas},
    "operatingProfit" ={operatingProfit},
    "profitBeforeTax" ={profitBeforeTax},
    "totalAssets" ={totalAssets},
    "totalEquity" ={totalEquity},
    "mnt_units" ={mnt_units},
    "isProcessed"={isProcessed},
    "coherency"={coherency},
    "totalLiabilities" ={totalLiabilities} where pyme_document={pyme_document} '''
    
    return query

def lambda_handler(event, context):
    """
    Get Extraction Status, JobTag and JobId from SNS. 
    If the Status is SUCCEEDED then create a dict of the values and write those to the RDS database.
    """
    #print(event)
    
    pattern_caja= ['efectivoyvalore','efectiv..equiv','efectivoyrequiv','cajaydisponible','efectivoequivalentesalefectivo''efectivoybancos','vequivalentesdeefectivo','^efectivo$']

    pattern_ingreso = ['totaldeingresosoperacionales','totalingresosoperacionales','ingresosporventa',"ingresosdeactividadesordinarias",'ingreso.*ordinaria']

    pattern_patrimonio =["^totalpatrimoni.$","patrimoni.de","totalcapital","^patrimonia$","patrimoni.neto","patrimoni.total"]

    pattern_activos = [ "^totalactivo$","totalactiv.s$","totaldeactiv.s$","totaldelactiv.$","tolallactiv.$","activototal$","activototal$","activototal$",]

    pattern_pasivos = [ "^pasivototal$","^totalpasivo$","t.t.lpasiv.s$","t.t.lpasiv.$","t.t.ldelp.siv.$""t.t.ldep.siv.s$"]

    pattern_costosventas = ["costodeventa","costodeproduccion","totaldecostos","gastosdeventas","gastosdeventa","costosfinancieros","costosdeventas"]
    
    pattern_utopera = ["resultadosporactividadesdeoperacion","utilidadopera","utilidaddeoperacion","gananciaporactividadesdeoperacion","perdidaopera","utilidad.*perdida.*opera"]
    
    pattern_ubruta  = ["utilidadbruta","ganancia.*bruta","utilidad.*delperiodo","utilidadporactividadesoperacionales","margen.*brut","EBITDA","utilidad.*antes.*impuesto.*ganancias"]
    
    pattern_antes_imp= ["antes"]

    pattern_uneta= ["utilidadneta","ganancianeta","Ganancia.*perdida*neto","utilidadnetaconsolidada","resultadonetodelano","resultadointegral"]
    

    mypatterns =  { 'p_caja':       pattern_caja,
                    'p_ingreso':    pattern_ingreso,
                    'p_patrimonio': pattern_patrimonio,
                    'p_activos':    pattern_activos,
                    'p_pasivos':    pattern_pasivos,
                    'p_cventas':    pattern_costosventas,
                    'p_utopera':    pattern_utopera,
                    'p_antesimp':   pattern_antes_imp,
                    'p_uneta':      pattern_uneta,
                    'p_ubruta':     pattern_ubruta
                  }
    notificationMessage = json.loads(json.dumps(event))['Records'][0]['Sns']['Message']
    
    pdfTextExtractionStatus = json.loads(notificationMessage)['Status']
    pdfTextExtractionJobTag = json.loads(notificationMessage)['JobTag']
    pdfTextExtractionJobId = json.loads(notificationMessage)['JobId']
    
    #print(pdfTextExtractionJobTag + ' : ' + pdfTextExtractionStatus)
    
    
    try:
        if(pdfTextExtractionStatus == 'SUCCEEDED'):
            response = getJobResultsAllinOne(pdfTextExtractionJobId)
            doc = Document(response)
    except:
        if(pdfTextExtractionStatus == 'SUCCEEDED'):
            response = getJobResults(pdfTextExtractionJobId)
            doc = Document(response)
            response = response[0]
                 
    
    doc_key = pdfTextExtractionJobTag[:-4]
    
    query = make_query(doc,response,doc_key,mypatterns)
  
    connection = get_connection()      
    
    cursor = connection.cursor()
    
    cursor.execute(query)
    
    connection.commit()

    cursor.close()

