###################################################################################
############################## Importamos librerías ###############################
###################################################################################
import pandas as pd # Análisis y procesamiento de datos
from datetime import date, timedelta, datetime
import dash # Creación de app web
from dash import html, dcc, Input, Output, dash_table # elementos de la app web (Dash)
import dash_bootstrap_components as dbc # Más elementos visuales del Dash
import plotly.graph_objs as go # Creación de scatter plots, barras y líneas
# **********************************************************************************


#####################################################################
############### Importación de datos del Dash ######################
#####################################################################

# Carga y adecuación de datos de Capacidad Instalada
df_CI = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/ultimo Capacidad instalada.xlsx", header=0,
                   sheet_name="Base Información")
df_CI.loc[:, df_CI.dtypes == 'object'] = df_CI.loc[:, df_CI.dtypes == 'object'].apply(lambda row: row.str.upper())

# Escogemos las columnas de interés
df_CI = df_CI[["Año", "Mes", "Cliente", "UEN", "Producto", "pais Analista", "Capacida origen", "Area", "Ingresos"]]# Creamos una columna con un valor numérico para cada mes para poder filtrar los datos por meses
df_CI = df_CI[(df_CI["Area"]=="OPERACIÓN") & (df_CI["Ingresos"]!=1)]
df_CI.rename(columns={"pais Analista": "Pais"}, inplace=True)

NumMes = {'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
          'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12}
MesCorto = {'ENERO': 'ENE', 'FEBRERO': 'FEB', 'MARZO': 'MAR', 'ABRIL': 'ABR', 'MAYO': 'MAY', 'JUNIO': 'JUN',
            'JULIO': 'JUL', 'AGOSTO': 'AGO', 'SEPTIEMBRE': 'SEP', 'OCTUBRE': 'OCT', 'NOVIEMBRE': 'NOV',
            'DICIEMBRE': 'DIC'}
df_CI["NumMes"] = df_CI["Mes"].map(NumMes)
df_CI["MesCorto"] = df_CI["Mes"].map(MesCorto)

# Carga y adecuación de datoa de Rotación
df_rotacion = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/Rotacion.xlsx", header=0, sheet_name="Base")
df_rotacion.rename(columns={"Año egreso": "Año", "Mes egreso": "Mes", "Fecha Egreso": "Fecha"}, inplace=True)
df_rotacion["NumMes"] = df_rotacion["Mes"].map(NumMes)
df_rotacion["MesCorto"] = df_rotacion["Mes"].map(MesCorto)

# Carga y adecuación de datos de Liberaciones
df_liberaciones = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/Informe Liberaciones V2.0.xlsm", header=0, sheet_name="ConsultaOrigen")
df_liberaciones.rename(columns={"Año de liberación": "Año", "Mes liberación ": "Mes", "FechaLiberacion": "Fecha"}, inplace=True)
mes_completo = {"ene": "ENERO", "feb": "FEBRERO", "mar": "MARZO", "abr": "ABRIL", "may": "MAYO", "jun": "JUNIO",
                "jul": "JULIO", "ago": "AGOSTO", "sep": "SEPTIEMBRE", "oct": "OCTUBRE", "nov": "NOVIEMBRE",
                "dic": "DICIEMBRE"}
df_liberaciones["Mes"] = df_liberaciones["Mes"].map(mes_completo)
df_liberaciones["NumMes"] = df_liberaciones["Mes"].map(NumMes)
df_liberaciones["MesCorto"] = df_liberaciones["Mes"].map(MesCorto)
cargo_to_producto = {
    "ANALISTA AFT": "AFT",
    "AUTOMATIZADOR": "AUTOMATIZACION",
    "ARQUITECTO DE AUTOMATIZACION": "AUTOMATIZACION",
    "ANALISTA DPM": "DPM",
    "Arquitecto DPM": "DPM",
    "ANALISTA DPM EN ADAPTACION": "DPM",
    "ANALISTA DE PRUEBAS": "GENERALISTA",
    "ANALISTA DE PRUEBAS EN FORMACION": "GENERALISTA",
    "Aprendiz Operativo": "GENERALISTA",
    "PROFESIONAL EN FORMACION": "GENERALISTA",
    "ANALISTA DE PRUEBAS EN ADAPTACION": "GENERALISTA",
    "Gerente de Proyectos": "GERENTE",
    "GERENTE DE SERVICIO COORDINADOR": "GERENTE",
    "GERENTE DE SERVICIO COORDINADOR EN ADAPTACION": "GERENTE",
    "SERVICE MANAGER": "GERENTE",
    "SERVICE MANAGER EN ADAPTACION": "GERENTE",
    "LIDER DE PRODUCTO": "LIDER PRODUCTO",
    "LIDER DE PRODUCTO EN ADAPTACION": "LIDER PRODUCTO",
    "ANALISTA DE PRUEBAS DE MIGRACION": "MIGRACION",
    "ANALISTA DE PRUEBAS DE MIGRACIÓN": "MIGRACION",
    "Arquitecto de Migración": "MIGRACION",
    "ANALISTA DE PRUEBAS DE MIGRACIÓN EN ADAPTACIÓN": "MIGRACION",
    "ANALISTA DE PRUEBAS MOVILES": "MOVILES",
    "ANALISTA DE PRUEBAS MOVILES EN ADAPTACION": "MOVILES",
    "ARQUITECTO DE MOVILES": "MOVILES",
    "ANALISTA DE PRUEBAS PERFORMANCE": "PERFORMANCE",
    "ANALISTA DE PRUEBAS PERFORMANCE EN ADAPTACION": "PERFORMANCE",
    "ARQUITECTO DE PERFORMANCE": "PERFORMANCE",
    "Automatizador de Pruebas Transaccionales": "TRANSACCIONAL"
}
df_liberaciones["Producto"] = df_liberaciones["CargoColaborador"].map(cargo_to_producto)
df_liberaciones.loc[:, df_liberaciones.dtypes=='object'] = df_liberaciones.loc[:, df_liberaciones.dtypes=='object'].apply(lambda row: row.str.upper())
cliente_to_pais={
    "CHOUCAIR": "COLOMBIA",
    "BANCOLOMBIA": "COLOMBIA",
    "CLARO": "COLOMBIA",
    "LEASING BANCOLOMBIA": "COLOMBIA",
    "SUFI": "COLOMBIA",
    "FACTORING": "COLOMBIA",
    "ATH": "COLOMBIA",
    "ABINBEV": "COLOMBIA",
    "COLPATRIA": "COLOMBIA",
    "PROTECCION": "COLOMBIA",
    "DIRECTV": "COLOMBIA",
    "PUBLICAR": "COLOMBIA",
    "BCS": "COLOMBIA",
    "TUYA": "COLOMBIA",
    "COMPENSAR": "COLOMBIA",
    "REDEBAN": "COLOMBIA",
    "RENTING": "COLOMBIA",
    "INNOVA": "COLOMBIA",
    "BANCO DE LA REPUBLICA": "COLOMBIA",
    "CONCESION RUNT": "COLOMBIA",
    "DAVIVIENDA": "COLOMBIA",
    "EFECTY": "COLOMBIA",
    "EL TIEMPO": "COLOMBIA",
    "PROCESSA": "COLOMBIA",
    "MEGASOFT": "COLOMBIA",
    "ESTUDIO DE MODA": "COLOMBIA",
    "ICFES": "COLOMBIA",
    "CREDIBANCO-VISA": "COLOMBIA",
    "EMTELCO": "COLOMBIA",
    "DANN REGIONAL": "COLOMBIA",
    "ALFAGL": "COLOMBIA",
    "MAPFRE": "COLOMBIA",
    "U TADEO": "COLOMBIA",
    "GNP MEXICO": "COLOMBIA",
    "PORVENIR": "COLOMBIA",
    "FALABELLA": "COLOMBIA",
    "BANCO GANADERO S.A BOLIVIA": "COLOMBIA",
    "COLOMBIA MOVIL S.A.": "COLOMBIA",
    "BANCO POPULAR": "COLOMBIA",
    "CAJA DE COMPENSACION COMFAMA": "COLOMBIA",
    "CARVAJAL TECNOLOGIA Y SERVICIO": "COLOMBIA",
    "CLINICA SAN DIEGO": "COLOMBIA",
    "BTG PACTUAL": "COLOMBIA",
    "THOMAS GREG & SONS LIMITED": "COLOMBIA",
    "BELCORP": "COLOMBIA",
    "COLTABACO": "COLOMBIA",
    "GONET": "COLOMBIA",
    "TODO1": "COLOMBIA",
    "INCOLMOTOS YAMAHA": "COLOMBIA",
    "CONVEL": "COLOMBIA",
    "ENLACE OPERATIVO": "COLOMBIA",
    "AVIANCA": "COLOMBIA",
    "AMERIKA TI": "COLOMBIA",
    "TCC": "COLOMBIA",
    "QUIPUX": "COLOMBIA",
    "BANCO CENCOSUD": "COLOMBIA",
    "STA CONSULTING INC.": "COLOMBIA",
    "GETRONICS": "COLOMBIA",
    "BIZAGI": "COLOMBIA",
    "AVANTEL": "COLOMBIA",
    "MANPOWER": "COLOMBIA",
    "COLMENA ARL": "COLOMBIA",
    "ARGOS": "COLOMBIA",
    "CORONA": "COLOMBIA",
    "BANCO FALABELLA COLOMBIA": "COLOMBIA",
    "BOLSA MERCANTIL COLOMBIA": "COLOMBIA",
    "COLSANITAS": "COLOMBIA",
    "CORFICOLOMBIANA": "COLOMBIA",
    "PRODUCTOS FAMILIA": "COLOMBIA",
    "COMERCIAL ECCSA S.A.": "COLOMBIA",
    "1CERO1": "COLOMBIA",
    "NUTRESA": "COLOMBIA",
    "GRUPO AVAL": "COLOMBIA",
    "BANBIF (REMOTO)": "COLOMBIA",
    "ACH": "COLOMBIA",
    "BANCOMPARTIR": "COLOMBIA",
    "SYMPLIFICA": "COLOMBIA",
    "HACEB": "COLOMBIA",
    "CNT": "COLOMBIA",
    "UNIVERSIDAD DEL ROSARIO": "COLOMBIA",
    "GCO GRUPO URIBE": "COLOMBIA",
    "CELERIX": "COLOMBIA",
    "SATRACK": "COLOMBIA",
    "ALKOSTO": "COLOMBIA",
    "HOMECENTER SODIMAC": "COLOMBIA",
    "EVERTEC": "COLOMBIA",
    "SURA": "COLOMBIA",
    "SERVIENTREGA ": "COLOMBIA",
    "BBVA COLOMBIA": "COLOMBIA",
    "CABIFY": "COLOMBIA",
    "GRUPO EXITO": "COLOMBIA",
    "LINEA DIRECTA ": "COLOMBIA",
    "BANCO PICHINCHA ": "COLOMBIA",
    "BANCO AGRARIO ": "COLOMBIA",
    "PROMERICA": "COLOMBIA",
    "BANCO DE COSTA RICA": "COLOMBIA",
    "FISA GROUP-MODINTER": "COLOMBIA",
    "INTERNEXA": "COLOMBIA",
    "CREDIFINANCIERA": "COLOMBIA",
    "STEFANINI": "COLOMBIA",
    "CASSE SEGUROS ": "COLOMBIA",
    "ASEGURADORA SOLIDARIA": "COLOMBIA",
    "ITIS SUPPORT": "COLOMBIA",
    "DIGITAL  WARE": "COLOMBIA",
    "SISA": "COLOMBIA",
    "ALIANZA FIDUCIARIA": "COLOMBIA",
    "WHITE CLOUD SAS": "COLOMBIA",
    "AXEDE-EPM": "COLOMBIA",
    "CRYSTAL": "COLOMBIA",
    "EAFIT": "COLOMBIA",
    "SUAM": "COLOMBIA",
    "MAS GLOBAL CONSULTING": "COLOMBIA",
    "CORREDOR EMPRESARIAL S.A.": "COLOMBIA",
    "REDEBAN MULTICOLOR S.A.": "COLOMBIA",
    "DIGIT SAS": "COLOMBIA",
    "MC DONALDS": "COLOMBIA",
    "HDI": "COLOMBIA",
    "SERVICIOS INTEGRALES": "COLOMBIA",
    "KOBA COLOMBIA D1": "COLOMBIA",
    "SOLUCIONES BOLIVAR": "COLOMBIA",
    "UNIVERSIDAD EAN": "COLOMBIA",
    "CORREDORES DAVIVIENDA": "COLOMBIA",
    "POSTOBON S.A.": "COLOMBIA",
    "BANCO ITAU": "COLOMBIA",
    "CONFECAMARAS": "COLOMBIA",
    "VERIFONE": "COLOMBIA",
    "DOCTUS": "COLOMBIA",
    "UNIVERSIDAD PONTIFICIA BOLIVARIANA": "COLOMBIA",
    "STOP JEANS": "COLOMBIA",
    "FANALCA": "COLOMBIA",
    "TEKUS": "COLOMBIA",
    "LABORATORIOS LEGRAND": "COLOMBIA",
    "GNB SUDAMERIS": "COLOMBIA",
    "LLEVALOYA": "COLOMBIA",
    "ARKIX": "COLOMBIA",
    "XELERICA": "COLOMBIA",
    "MICRONOTES": "COLOMBIA",
    "BANISTMO COLOMBIA": "COLOMBIA",
    "PARTNERS TELECOM COLOMBIA SAS": "COLOMBIA",
    "INDIE LEVEL": "COLOMBIA",
    "SISTECREDITO S.A.S": "COLOMBIA",
    "IP COM": "COLOMBIA",
    "NEQUI": "COLOMBIA",
    "PRATECH": "COLOMBIA",
    "SUPPORTICAL": "COLOMBIA",
    "GRUPO REDITOS": "COLOMBIA",
    "PAGALO": "COLOMBIA",
    "COBELEN": "COLOMBIA",
    "AXA COLPATRIA": "COLOMBIA",
    "NOVAVENTA": "COLOMBIA",
    "INTCOMEX": "COLOMBIA",
    "GIROS Y FINANZAS": "COLOMBIA",
    "ROCA": "COLOMBIA",
    "DAVIPLATA": "COLOMBIA",
    "LEONISA": "COLOMBIA",
    "XEGMENTA": "COLOMBIA",
    "PRAGMATIC": "COLOMBIA",
    "FENIXPUNTONET": "COLOMBIA",
    "CARDIF": "COLOMBIA",
    "JP GLOBAL DIGITAL": "COLOMBIA",
    "XM": "COLOMBIA",

    "CHOUCAIR PERU": "PERU",
    "BANCO DE COMERCIO": "PERU",
    "LA POSITIVA SEGUROS": "PERU",
    "INTERBANK": "PERU",
    "MI BANCO": "PERU",
    "BANCO FALABELLA": "PERU",
    "INNOVACION": "PERU",
    "TELEFONICA": "PERU",
    "ARPL TECNOLOGIA INDUSTRIAL": "PERU",
    "INTERSEGUROS": "PERU",
    "RIPLEY": "PERU",
    "CAVALI": "PERU",
    "BCP": "PERU",
    "LA POSITIVA SANITAS S.A": "PERU",
    "BANCO CENCOSUD": "PERU",
    "RIPLEY CHILE": "PERU",
    "BBVA Continental Perú": "PERU",
    "RIMAC SA": "PERU",
    "FERREYROS": "PERU",
    "FINANCIERA COMPARTAMOS S.A": "PERU",
    "BANCO SANTANDER PERU": "PERU",
    "CUIDA DIGITAL": "PERU",
    "MAPFRE PERU": "PERU",
    "PARTNERS TELECOM COLOMBIA SAS": "PERU",
    "LAUREATE": "PERU",

    "BANCO GENERAL": "PANAMA",
    "BANISTMO": "PANAMA",
    "GENERAL DE SEGUROS": "PANAMA",
    "GMB": "PANAMA",
    "GLOBAL BANK": "PANAMA",
    "ATLANTIC SECURITY BANK": "PANAMA",
    "DAVIVIENDA PANAMA": "PANAMA",
    "MI BUS": "PANAMA",
    "CREDICORP": "PANAMA",
    "GRUPO CORPORATIVO PEREZ": "PANAMA",
    "TELERED SA": "PANAMA",
    "TOWERBANK": "PANAMA",
    "TOTAL SYNERGY TECH": "PANAMA",
    "FARMACIAS ARROCHA": "PANAMA"
}
df_liberaciones["Pais"] = df_liberaciones["Cliente"].map(cliente_to_pais)

# Carga y adecuación de datos de Solicitudes
df_solicitudes = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/Informe Solicitud v9.xlsb", header=0, sheet_name="Base")
df_solicitudes["FechaSolicitud"] = pd.TimedeltaIndex(df_solicitudes["FechaSolicitud"]-2, unit='d') + datetime(1900,1,1)
df_solicitudes["Año"] = pd.DatetimeIndex(df_solicitudes["FechaSolicitud"]).year
df_solicitudes["NumMes"] = pd.DatetimeIndex(df_solicitudes["FechaSolicitud"]).month
NombMes = {1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
           9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'}
df_solicitudes['Mes'] = df_solicitudes['NumMes'].map(NombMes)
df_solicitudes["MesCorto"] = df_solicitudes["Mes"].map(MesCorto)
df_solicitudes.loc[:, df_solicitudes.dtypes=='object'] = df_solicitudes.loc[:, df_solicitudes.dtypes=='object'].apply(lambda row: row.str.upper())
df_solicitudes.rename(columns={"País": "Pais"}, inplace=True)
df_solicitudes["Pais"] = df_solicitudes["Pais"].apply(lambda row: row.replace('Ú', 'U'))
df_solicitudes["Pais"] = df_solicitudes["Pais"].apply(lambda row: row.replace('Á', 'A'))

df_ingresos = df_solicitudes.copy()
df_ingresos["FechaIngresoOP"] = pd.TimedeltaIndex(df_ingresos["FechaIngresoOP"]-2, unit='d') + datetime(
    1900,1,1)
df_ingresos["FechaIngresoOP"] = pd.to_datetime(df_ingresos["FechaIngresoOP"], errors='coerce')
df_ingresos.dropna(subset=["FechaIngresoOP"],inplace=True)
df_ingresos["Año"] = pd.DatetimeIndex(df_ingresos["FechaIngresoOP"]).year
df_ingresos["NumMes"] = pd.DatetimeIndex(df_ingresos["FechaIngresoOP"]).month
df_ingresos['Mes'] = df_ingresos['NumMes'].map(NombMes)
df_ingresos["MesCorto"] = df_ingresos["Mes"].map(MesCorto)

df_disponibles = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/Backup Analistas 3.0.xlsx",
                          sheet_name="Back Up", header=0)
df_disponibles = df_disponibles[(df_disponibles["Estado"]=="Disponibles") &
                      ((df_disponibles["Estatus"]=="Analistas de Pruebas en Formación") |
                       (df_disponibles["Estatus"]=="Semillero") | (df_disponibles["Estatus"].isna()))]
df_disponibles = df_disponibles.groupby(["Pais", "Producto"])["Analista"].count().reset_index()
df_disponibles.rename(columns={"Analista": "Disponibles"}, inplace=True)

df_pendientes = df_liberaciones[(df_liberaciones["EstadoSolicitud"]=="ABIERTO") |
                              (df_liberaciones["EstadoSolicitud"]=="EN PROCESO")]
df_pendientes = df_pendientes.groupby(["Pais", "Producto"])["Contador"].count().reset_index()
df_pendientes.rename(columns={"Contador": "Pendientes de liberación"}, inplace=True)

df_solicitudes_firme = df_solicitudes[((df_solicitudes["EstadoSolicitudCO"] == "ABIERTO") |
                                      (df_solicitudes["EstadoSolicitudCO"] == "EN PROCESO")) &
                                      (df_solicitudes['Cliente'].str.contains('CHOUCAIR')==False) &
                                      (df_solicitudes['EstrategiaAtencionCO'].str.contains('CONVOCATORIA')==False)]
print(df_solicitudes_firme["EstrategiaAtencionCO"])
df_solicitudes_firme = df_solicitudes_firme.groupby(["Pais", "Producto"])["Año"].count().reset_index()
df_solicitudes_firme.rename(columns={"Año": "Solicitudes en firme"}, inplace=True)

df_buffer = pd.read_excel("C:/Users/fborrerom/Documents/Archivos Listos/Buffer.xlsx",
                          sheet_name="Hoja1", header=0)
df_buffer = df_buffer.groupby(["Pais", "Producto"])["TOTAL"].count().reset_index()
df_buffer.rename(columns={"TOTAL": "Buffer"}, inplace=True)

df_backup = df_disponibles.merge(df_pendientes, on=['Pais', 'Producto'], how='outer').merge(
    df_solicitudes_firme, on=['Pais', 'Producto'], how='outer').merge(
    df_buffer, on=['Pais', 'Producto'], how='outer').fillna(0)

df_backup["Neto"] = (df_backup["Disponibles"] + df_backup["Pendientes de liberación"] -
                     df_backup["Solicitudes en firme"] - df_backup["Buffer"])
df_backup = df_backup.sort_values(by=["Pais", "Disponibles"], ascending=[True, False])
df_backup.loc[df_backup["Pais"]=="PERÚ", "Pais"]='PERU'
sum_row = pd.DataFrame(df_backup.sum()).T
df_backup = pd.concat([df_backup, sum_row], ignore_index=True)
df_backup.iloc[-1, 0] = "TOTAL"
df_backup.iloc[-1, 1] = ""
pais_backup = df_backup["Pais"].unique()

# Elementos de selección en los filtros
years = df_rotacion["Año"].unique()  # Lista de años que harán parte del filtro por año
clientes = df_rotacion["Cliente"].unique()  # Lista de clientes que harán parte del filtro por cliente
UEN = df_rotacion["UEN"].unique()  # Lista de UEN que harán parte del filtro por UEN
paises = df_rotacion["Pais"].unique()  # Lista de países que harán parte del filtro por país
productos = df_rotacion["Producto"].unique()  # Lista de productos que harán parte del filtro por producto
max_mes = df_rotacion[df_rotacion["Año"]==years[-1]]["NumMes"].max()

def tabla_resumen(years_drop=2023, meses_slider=[1, max_mes], clientes_drop=None, UEN_drop=None, paises_drop=None, productos_drop=None):
    df_CI_tabla = df_CI[(df_CI["Año"] == years_drop) &
                                    (df_CI["NumMes"] >= meses_slider[0]) &
                                    (df_CI["NumMes"] <= meses_slider[1])]
    df_rotacion_tabla = df_rotacion[(df_rotacion["Año"] == years_drop) &
                                    (df_rotacion["NumMes"] >= meses_slider[0]) &
                                    (df_rotacion["NumMes"] <= meses_slider[1])]
    df_liberaciones_tabla = df_liberaciones[(df_liberaciones["Año"] == years_drop) &
                                    (df_liberaciones["NumMes"] >= meses_slider[0]) &
                                    (df_liberaciones["NumMes"] <= meses_slider[1])]
    df_solicitudes_tabla = df_solicitudes[(df_solicitudes["Año"] == years_drop) &
                                    (df_solicitudes["NumMes"] >= meses_slider[0]) &
                                    (df_solicitudes["NumMes"] <= meses_slider[1])]
    df_ingresos_tabla = df_ingresos[(df_ingresos["Año"] == years_drop) &
                              (df_ingresos["NumMes"] >= meses_slider[0]) &
                              (df_ingresos["NumMes"] <= meses_slider[1])]

    if clientes_drop is not None:
        df_CI_tabla = df_CI_tabla[df_CI_tabla["Cliente"] == clientes_drop]
        df_rotacion_tabla = df_rotacion_tabla[df_rotacion_tabla["Cliente"] == clientes_drop]
        df_liberaciones_tabla = df_liberaciones_tabla[df_liberaciones_tabla["Cliente"] == clientes_drop]
        df_solicitudes_tabla = df_solicitudes_tabla[df_solicitudes_tabla["Cliente"] == clientes_drop]
        df_ingresos_tabla = df_ingresos_tabla[df_ingresos_tabla["Cliente"] == clientes_drop]


    if UEN_drop is not None:
        df_CI_tabla = df_CI_tabla[df_CI_tabla["UEN"] == UEN_drop]
        df_rotacion_tabla = df_rotacion_tabla[df_rotacion_tabla["UEN"] == UEN_drop]
        df_liberaciones_tabla = df_liberaciones_tabla[df_liberaciones_tabla["UEN"] == UEN_drop]
        df_solicitudes_tabla = df_solicitudes_tabla[df_solicitudes_tabla["UEN"] == UEN_drop]
        df_ingresos_tabla = df_ingresos_tabla[df_ingresos_tabla["UEN"] == UEN_drop]


    if paises_drop is not None:
        df_CI_tabla = df_CI_tabla[df_CI_tabla["Pais"] == paises_drop]
        df_rotacion_tabla = df_rotacion_tabla[df_rotacion_tabla["Pais"] == paises_drop]
        df_liberaciones_tabla = df_liberaciones_tabla[df_liberaciones_tabla["Pais"] == paises_drop]
        df_solicitudes_tabla = df_solicitudes_tabla[df_solicitudes_tabla["Pais"] == paises_drop]
        df_ingresos_tabla = df_ingresos_tabla[df_ingresos_tabla["Pais"] == paises_drop]

    if productos_drop is not None:
        df_CI_tabla = df_CI_tabla[df_CI_tabla["Producto"] == productos_drop]
        df_rotacion_tabla = df_rotacion_tabla[df_rotacion_tabla["Producto"] == productos_drop]
        df_liberaciones_tabla = df_liberaciones_tabla[df_liberaciones_tabla["Producto"] == productos_drop]
        df_solicitudes_tabla = df_solicitudes_tabla[df_solicitudes_tabla["Producto"] == productos_drop]
        df_ingresos_tabla = df_ingresos_tabla[df_ingresos_tabla["Producto"] == productos_drop]

    df_CI_tabla = df_CI_tabla.groupby(["NumMes", "MesCorto"])["Cliente"].count().reset_index()
    df_CI_tabla.sort_values(by="NumMes", ascending=True, inplace=True)
    df_CI_tabla.rename(columns={"Cliente": "CI"}, inplace=True)

    df_rotacion_tabla = df_rotacion_tabla.groupby(["NumMes", "MesCorto"])["Cliente"].count().reset_index()
    df_rotacion_tabla.sort_values(by="NumMes", ascending=True, inplace=True)
    df_rotacion_tabla.rename(columns={"Cliente": "Rotación"}, inplace=True)

    df_liberaciones_tabla = df_liberaciones_tabla.groupby(["NumMes", "MesCorto"])["Cliente"].count().reset_index()
    df_liberaciones_tabla.sort_values(by="NumMes", ascending=True, inplace=True)
    df_liberaciones_tabla.rename(columns={"Cliente": "Liberaciones"}, inplace=True)

    df_solicitudes_tabla = df_solicitudes_tabla.groupby(["NumMes", "MesCorto"])["Cliente"].count().reset_index()
    df_solicitudes_tabla.sort_values(by="NumMes", ascending=True, inplace=True)
    df_solicitudes_tabla.rename(columns={"Cliente": "Solicitudes"}, inplace=True)

    df_ingresos_tabla = df_ingresos_tabla.groupby(["NumMes", "MesCorto"])["Cliente"].count().reset_index()
    df_ingresos_tabla.sort_values(by="NumMes", ascending=True, inplace=True)
    df_ingresos_tabla.rename(columns={"Cliente": "Contrataciones"}, inplace=True)

    df = df_CI_tabla.merge(df_rotacion_tabla, on=['MesCorto', 'NumMes'], how='outer').merge(
        df_liberaciones_tabla, on=['MesCorto', 'NumMes'], how='outer').merge(
        df_solicitudes_tabla, on=['MesCorto', 'NumMes'], how='outer').merge(
        df_ingresos_tabla, on=['MesCorto', 'NumMes'], how='outer').fillna(0)

    df.sort_values(by='NumMes', inplace=True)
    df.drop('NumMes', axis=1, inplace=True)
    df = pd.pivot_table(df, columns="MesCorto", sort=False).reset_index()
    df['ACUM'] = df.iloc[:, 1:].sum(axis=1)
    df.iloc[0, -1] =  round(df.iloc[0, 1:-1].sum()/(len(df.columns)-2))
    df.rename(columns={'index': 'INDICADOR'}, inplace=True)

    df_rotacion_tabla_spikeline = df_rotacion_tabla
    df_liberaciones_tabla_spikeline = df_liberaciones_tabla
    df_solicitudes_tabla_spikeline = df_solicitudes_tabla
    df_CI_tabla_spikeline = df_CI_tabla
    df_ingresos_tabla_spikeline = df_ingresos_tabla

    return (df, df_rotacion_tabla_spikeline, df_liberaciones_tabla_spikeline, df_solicitudes_tabla_spikeline,
            df_CI_tabla_spikeline, df_ingresos_tabla_spikeline)

df, _, _, _, _, _ = tabla_resumen()

#####################################################################
############### Creación de elementos del Dash ######################
#####################################################################

external_stylesheets = [dbc.themes.SPACELAB]  # Definición de la plantilla que da estilo al Dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)  # Creación del objeto Dash
server = app.server
app.title = "Resumen General"
app.layout = html.Div([
    ##################################### DROPDOWNS DE FILTROS ############################################
    dbc.Row([
        dbc.Col(dbc.Card(
            dcc.Dropdown(
                id='years_drop',
                multi=False,
                clearable=False,
                disabled=False,
                style={'display': True},
                placeholder='Año',
                options=[{'label': y, 'value': y} for y in years]
            ), body=True, color="light"
        )),
        dbc.Col(dbc.Card(
            dcc.Dropdown(
                id='clientes_drop',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display': True},
                placeholder='Cliente',
                options=[{'label': c, 'value': c} for c in clientes]
            ), body=True, color="light"
        )),
        dbc.Col(dbc.Card(
            dcc.Dropdown(
                id='UEN_drop',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display': True},
                placeholder='UEN',
                options=[{'label': u, 'value': u} for u in UEN]
            ), body=True, color="light"
        )),
        dbc.Col(dbc.Card(
            dcc.Dropdown(
                id='paises_drop',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display': True},
                placeholder='País',
                options=[{'label': p, 'value': p} for p in paises]
            ), body=True, color="light"
        )),
        dbc.Col(dbc.Card(
            dcc.Dropdown(
                id='productos_drop',
                multi=False,
                clearable=True,
                disabled=False,
                style={'display': True},
                placeholder='Producto',
                options=[{'label': p, 'value': p} for p in productos]
            ), body=True, color="light"
        )),
    ]),

    ######################## SLIDER DE RANGO DE MESES #############################
    dbc.Card([
              dcc.RangeSlider(id='meses_slider', min=1, max=12, value=[1, max_mes], dots=True, step=1,
                  marks={0: {'style': {'color': 'white'}},
                         1: {'label': 'Enero', 'style': {'color': 'black', 'font-size': '16px'}},
                         2: {'label': 'Febrero', 'style': {'color': 'black', 'font-size': '16px'}},
                         3: {'label': 'Marzo', 'style': {'color': 'black', 'font-size': '16px'}},
                         4: {'label': 'Abril', 'style': {'color': 'black', 'font-size': '16px'}},
                         5: {'label': 'Mayo', 'style': {'color': 'black', 'font-size': '16px'}},
                         6: {'label': 'Junio', 'style': {'color': 'black', 'font-size': '16px'}},
                         7: {'label': 'Julio', 'style': {'color': 'black', 'font-size': '16px'}},
                         8: {'label': 'Agosto', 'style': {'color': 'black', 'font-size': '16px'}},
                         9: {'label': 'Septiembre', 'style': {'color': 'black', 'font-size': '16px'}},
                         10: {'label': 'Octubre', 'style': {'color': 'black', 'font-size': '16px'}},
                         11: {'label': 'Noviembre', 'style': {'color': 'black', 'font-size': '16px'}},
                         12: {'label': 'Diciembre', 'style': {'color': 'black', 'font-size': '16px'}}})], body=True, color='light'),

    ########################### TABLA DE INDICADORES Y GRÁFICOS ###########################
    dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="resumen")),
        color="light"), width=12)),
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col(dash_table.DataTable(
                id='tabla_rotacion',
                style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                              'backgroundColor': 'lightgrey'},
                style_data={'color': 'black', 'text-align': 'center', 'height': '75px'},
                style_table={'width': '750px'}
            )),
            dbc.Col([
                dcc.Graph(id="CI"),
                dcc.Graph(id="rotacion"),
                dcc.Graph(id="liberaciones"),
                dcc.Graph(id="solicitudes"),
                dcc.Graph(id="contrataciones")
            ])
        ], className="g-0")
             ]), color='light'),

    dbc.Card(dbc.CardBody([html.H5("TOTAL ANALISTAS", style={'text-align': 'center', 'color': 'black',
                                                             'font-weight': 'bold'}, className="card-title"),
        dcc.Dropdown(id='paises_backup_drop',
                    multi=False,
                    clearable=True,
                    disabled=False,
                    style={'display': True},
                    placeholder='Analistas por país',
                    options=[{'label': "ANALISTAS EN " + p, 'value': p} for p in pais_backup]),
        dash_table.DataTable(
        id='tabla_backup',
        style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                      'backgroundColor': 'lightgrey'},
        style_data={'color': 'black', 'text-align': 'center', 'height': '25px'})]), color='light'),

    html.Div(id='dash_rotacion'),
    html.Div(id='dash_CI'),
    html.Div(id='dash_solicitudes'),
    dcc.Interval(id='interval', interval=7200000, n_intervals=0)
])

##################### CALLBACKS DE ACTUALIZACIÓN POR FILTRO ###############################
@app.callback(Output('years_drop', 'value'),
             Input('years_drop', 'options'))
def get_year_value(years_drop):
    """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
    return [y['value'] for y in years_drop][-1] # el -1 indica que escoge el último año de la lista

@app.callback(Output('tabla_rotacion', 'data'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def scatter_chart(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
    df, _, _, _, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)

    return df.to_dict('records')

@app.callback(Output('dash_rotacion', 'children'),
              [Input('tabla_rotacion', 'active_cell')])
def start_dash_rotacion(active_cell):
    """Inicia el Dash de indicadores de Rotación al dar click en la celda Rotación de la tabla de resumen"""
    if active_cell is not None:
        row = active_cell['row']
        col = active_cell['column']
        cell_value = df.iloc[row][col]
        if cell_value=='Rotación':
            from rotacion import start_dash
            start_dash()
    return ''

@app.callback(Output('dash_CI', 'children'),
              [Input('tabla_rotacion', 'active_cell')])
def start_dash_rotacion(active_cell):
    """Inicia el Dash de indicadores de Rotación al dar click en la celda Rotación de la tabla de resumen"""
    if active_cell is not None:
        row = active_cell['row']
        col = active_cell['column']
        cell_value = df.iloc[row][col]
        if cell_value=='CI':
            from CI import start_dash
            start_dash()
    return ''

@app.callback(Output('dash_solicitudes', 'children'),
              [Input('tabla_rotacion', 'active_cell')])
def start_dash_rotacion(active_cell):
    """Inicia el Dash de indicadores de Rotación al dar click en la celda Rotación de la tabla de resumen"""
    if active_cell is not None:
        row = active_cell['row']
        col = active_cell['column']
        cell_value = df.iloc[row][col]
        if cell_value=='Solicitudes':
            from Solicitudes import start_dash
            start_dash()
    return ''


@app.callback(Output('CI', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, _, _, _, df_CI_tabla_spikeline, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)
    df_spikeline = df_CI_tabla_spikeline
    return {'data': [{'x': df_spikeline["MesCorto"],
                                            'y': df_spikeline["CI"],
                                            'type': 'line'}],
                                  'layout': {'margin': {'l': 5, 'r': 5, 't': 35, 'b': 5},
                                             'height': 110,
                                             'width': 500,
                                             'title': {'text': "<b>COMPORTAMIENTO</b>"},
                                             'xaxis': {'showticklabels': False,
                                                       'showline': True,
                                                       'linecolor': 'gray'},
                                             'yaxis': {'showticklabels': False}}}


@app.callback(Output('rotacion', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, df_rotacion_tabla_spikeline, _, _, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)
    df_spikeline = df_rotacion_tabla_spikeline
    return {'data': [{'x': df_spikeline["MesCorto"],
                    'y': df_spikeline["Rotación"],
                    'type': 'line'}],
                                  'layout': {'margin': {'l': 5, 'r': 5, 't': 35, 'b': 5},
                                             'height': 75,
                                             'width': 500,
                                             'xaxis': {'showticklabels': False,
                                                       'showline': True,
                                                       'linecolor': 'gray'},
                                             'yaxis': {'showticklabels': False}}}

@app.callback(Output('liberaciones', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, _, df_liberaciones_tabla_spikeline,_, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)
    df_spikeline=df_liberaciones_tabla_spikeline

    return {'data': [{'x': df_spikeline["MesCorto"],
                      'y': df_spikeline["Liberaciones"],
                      'type': 'line'}],
            'layout': {'margin': {'l': 5, 'r': 5, 't': 10, 'b': 5},
                                             'height': 75,
                                             'width': 500,
                                             'xaxis': {'showticklabels': False,
                                                       'showline': True,
                                                       'linecolor': 'gray'},
                                             'yaxis': {'showticklabels': False}}}

@app.callback(Output('solicitudes', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, _, _, df_solicitudes_tabla_spikeline, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)
    df_spikeline=df_solicitudes_tabla_spikeline

    return {'data': [{'x': df_spikeline["MesCorto"],
                      'y': df_spikeline["Solicitudes"],
                      'type': 'line'}],
            'layout': {'margin': {'l': 5, 'r': 5, 't': 5, 'b': 5},
                                             'height': 75,
                                             'width': 500,
                                             'xaxis': {'showticklabels': False,
                                                       'showline': True,
                                                       'linecolor': 'gray'},
                                             'yaxis': {'showticklabels': False}}}

@app.callback(Output('contrataciones', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, _, _, _, _, df_ingresos_tabla_spikeline = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)
    df_spikeline=df_ingresos_tabla_spikeline

    return {'data': [{'x': df_spikeline["MesCorto"],
                      'y': df_spikeline["Contrataciones"],
                      'type': 'line'}],
            'layout': {'margin': {'l': 5, 'r': 5, 't': 5, 'b': 5},
                                             'height': 75,
                                             'width': 500,
                                             'xaxis': {'showticklabels': False,
                                                       'showline': True,
                                                       'linecolor': 'gray'},
                                             'yaxis': {'showticklabels': False}}}


@app.callback(Output('resumen', 'figure'),
              [Input('years_drop', 'value')],
              [Input('meses_slider', 'value')],
              [Input('clientes_drop', 'value')],
              [Input('UEN_drop', 'value')],
              [Input('paises_drop', 'value')],
              [Input('productos_drop', 'value')])
def update_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
    _, df_rotacion, df_liberaciones, df_solicitudes, df_CI, df_ingresos = tabla_resumen(years_drop,
                                            meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop)

    return {'data': [go.Bar(x=df_CI["MesCorto"],
                            y=df_CI["CI"],
                            text=df_CI["CI"],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            name="Capacidad instalada"),
                     go.Scatter(x=df_rotacion["MesCorto"],
                                y=df_rotacion["Rotación"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_rotacion["Rotación"],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'OrangeRed'},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'OrangeRed'}},
                                name='Rotación'),
                     go.Scatter(x=df_liberaciones["MesCorto"],
                                y=df_liberaciones["Liberaciones"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_liberaciones["Liberaciones"],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Orange'},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'Orange'}},
                                name='Liberaciones'),
                     go.Scatter(x=df_solicitudes["MesCorto"],
                                y=df_solicitudes["Solicitudes"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_solicitudes["Solicitudes"],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Cyan'},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'Cyan'}},
                                name='Solicitudes'),
                     go.Scatter(x=df_ingresos["MesCorto"],
                                y=df_ingresos["Contrataciones"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_ingresos["Contrataciones"],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Green'},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'Green'}},
                                name='Contrataciones')
                     ],
            'layout': {'title': {'text': f'<b>RESUMEN DE INDICADORES DE OPERACIÓN</b>', 'font':{'size': 26}},
                       'xaxis': {'automargin': True,
                                 'tickfont':{'size':16, 'color':'black'}},
                       'yaxis': {'automargin': True,
                                 'tickfont': {'size': 16, 'color': 'black'}},
                       'yaxis2': {'overlaying': 'y',
                                  'side': 'right',
                                  'tickfont':{'size':16, 'color':'black'}}}}

@app.callback(Output('paises_backup_drop', 'value'),
              Input('paises_backup_drop', 'options'))
def get_year_value(pais_backup):
    """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
    return [p['value'] for p in pais_backup][-1]  # el -1 indica que escoge el último año de la lista

@app.callback(Output('tabla_backup', 'data'),
              [Input('paises_backup_drop', 'value')])
def scatter_chart(pais):
    """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
    df= df_backup

    if pais !="TOTAL" and pais is not None:
        df = df[df["Pais"]==pais]
        sum_row = pd.DataFrame(df.sum()).T
        df = pd.concat([df, sum_row], ignore_index=True)
        df.iloc[-1, 0] = "TOTAL"
        df.iloc[-1, 1] = ""

    return df.to_dict('records')
