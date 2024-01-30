###################################################################################
############################## Importamos librerías ###############################
###################################################################################
import pandas as pd  # Análisis y procesamiento de datos
from datetime import date, timedelta, datetime
import dash  # Creación de app web
from dash import html, dcc, Input, Output, dash_table  # elementos de la app web (Dash)
import dash_bootstrap_components as dbc  # Más elementos visuales del Dash
import plotly.graph_objs as go  # Creación de scatter plots, barras y líneas
import plotly.express as px  # Creación de de timelines y pie charts
from sklearn.model_selection import train_test_split  # Análisis de regresión lineal
from sklearn.linear_model import LinearRegression  # Análisis de regresión lineal


# **********************************************************************************

# Es una buena práctica llamar a la clase con una función
def start_dash():
    """Activación de la clase que contiene el Dash"""
    Indicadores()


class Indicadores():
    def __init__(self):
        """Definición del contenido de la clase"""
        self.run_dash_indicadores()

    def run_dash_indicadores(self):
        """Creación del Dash"""

        #####################################################################
        ############### Importación de datos del Dash ######################
        #####################################################################

        def replace_vowels(df):
            df = df.infer_objects()
            df.loc[:, df.dtypes == 'object'] = df.loc[:, df.dtypes == 'object'].apply(lambda row: row.str.upper())
            cols = df.select_dtypes(include=[object]).columns
            df[cols] = df[cols].apply(
                lambda x: x.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))
            return df

        NumMes = {'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
                  'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12}
        MesCorto = {'ENERO': 'ENE', 'FEBRERO': 'FEB', 'MARZO': 'MAR', 'ABRIL': 'ABR', 'MAYO': 'MAY', 'JUNIO': 'JUN',
                    'JULIO': 'JUL', 'AGOSTO': 'AGO', 'SEPTIEMBRE': 'SEP', 'OCTUBRE': 'OCT', 'NOVIEMBRE': 'NOV',
                    'DICIEMBRE': 'DIC'}
        NombMes = {1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO', 7: 'JULIO',
                   8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'}
        def load_data_CI():
            # Cargamos los datos del Excel un un Dataframe de Pandas
            df_CI_tab = pd.read_excel("Z:/Services and Products/Controles/Gestion capacidad/Colaboradores/ultimo Capacidad instalada.xlsx",
                                      header=0, sheet_name="Base Información")
            df_CI_tab.loc[:, df_CI_tab.dtypes == 'object'] = df_CI_tab.loc[:, df_CI_tab.dtypes == 'object'].apply(
                lambda row: row.str.upper())

            df_CI_tab = df_CI_tab[(df_CI_tab["Area"] == "OPERACIÓN")]
            df_CI_tab.rename(columns={"pais Analista": "Pais"}, inplace=True)
            df_CI_tab.loc[df_CI_tab["Pais"]=="PERÚ", "Pais"] = "PERU"
            df_CI_tab = replace_vowels(df_CI_tab)
            df_CI_tab["NumMes"] = df_CI_tab["Mes"].map(NumMes)
            df_CI_tab["MesCorto"] = df_CI_tab["Mes"].map(MesCorto)
            return df_CI_tab

        df_CI_tab_raw = load_data_CI()
        df_CI = df_CI_tab_raw.copy()

        def load_data_rotacion():
            """Importa los datos de SQL a un Dataframe de pandas"""
            df_rotacion_tab = pd.read_excel("Z:/Services and Products/Controles/Gestion capacidad/Colaboradores/Rotacion.xlsx",
                                            header=0, sheet_name="Base")
            df_rotacion_tab.rename(columns={"Año egreso": "Año", "Mes egreso": "Mes"}, inplace=True)
            df_rotacion_tab["NumMes"] = df_rotacion_tab["Mes"].map(NumMes)
            df_rotacion_tab["MesCorto"] = df_rotacion_tab["Mes"].map(MesCorto)
            return df_rotacion_tab

        df_rotacion_tab = load_data_rotacion()
        df_rotacion = df_rotacion_tab.copy()

        # Carga datos de panorama

        def load_data_panorama(sheet="CLIENTE"):
            df_panorama = pd.read_excel(
                "Z:/Services and Products/Controles/Gestion capacidad/Colaboradores/Panorama Personal Operaciones Choucair V3.1.xlsx",
                sheet_name=sheet, header=0)
            #df_panorama = replace_vowels(df_panorama)
            return df_panorama
        df_panorama = load_data_panorama()

        def load_data_inicial_Liberaciones():
            df_liberaciones = pd.read_excel(
                "Z:/Services and Products/Controles/Solicitudes/Administración de la Capacidad/Solicitudes Generalistas/Liberaciones v3.2.xlsm", header=0,
                sheet_name="Liberaciones")
            df_liberaciones.rename(columns={"FechaLiberacion": "Fecha"}, inplace=True)
            df_liberaciones.loc[:, df_liberaciones.dtypes == 'object'] = df_liberaciones.loc[:,
                                                                         df_liberaciones.dtypes == 'object'].apply(
                lambda row: row.str.upper())
            df_liberaciones["NumMes"] = df_liberaciones["Mes"]
            df_liberaciones.drop('Mes', axis=1, inplace=True)
            df_liberaciones['Mes'] = df_liberaciones['NumMes'].map(NombMes)
            df_liberaciones["MesCorto"] = df_liberaciones["Mes"].map(MesCorto)
            cargo_to_producto = {
                "ANALISTA AFT": "AFT",
                "AUTOMATIZADOR": "AUTOMATIZACION",
                "ARQUITECTO DE AUTOMATIZACION": "AUTOMATIZACION",
                "ANALISTA DPM": "DPM",
                "ARQUITECTO DPM": "DPM",
                "ANALISTA DPM EN ADAPTACION": "DPM",
                "ANALISTA DE PRUEBAS": "GENERALISTA",
                "ANALISTA DE PRUEBAS EN FORMACION": "GENERALISTA",
                "APRENDIZ OPERATIVO": "GENERALISTA",
                "PROFESIONAL EN FORMACION": "GENERALISTA",
                "ANALISTA DE PRUEBAS EN ADAPTACION": "GENERALISTA",
                "GERENTE DE PROYECTOS": "GERENTE",
                "GERENTE DE SERVICIO COORDINADOR": "GERENTE",
                "GERENTE DE SERVICIO COORDINADOR EN ADAPTACION": "GERENTE",
                "SERVICE MANAGER": "GERENTE",
                "SERVICE MANAGER EN ADAPTACION": "GERENTE",
                "LIDER DE PRODUCTO": "LIDER PRODUCTO",
                "LIDER DE PRODUCTO EN ADAPTACION": "LIDER PRODUCTO",
                "ANALISTA DE PRUEBAS DE MIGRACION": "MIGRACION",
                "ANALISTA DE PRUEBAS DE MIGRACIÓN": "MIGRACION",
                "ARQUITECTO DE MIGRACIÓN": "MIGRACION",
                "ANALISTA DE PRUEBAS DE MIGRACIÓN EN ADAPTACIÓN": "MIGRACION",
                "ANALISTA DE PRUEBAS MOVILES": "MOVILES",
                "ANALISTA DE PRUEBAS MOVILES EN ADAPTACION": "MOVILES",
                "ARQUITECTO DE MOVILES": "MOVILES",
                "ANALISTA DE PRUEBAS PERFORMANCE": "PERFORMANCE",
                "ANALISTA DE PRUEBAS PERFORMANCE EN ADAPTACION": "PERFORMANCE",
                "ARQUITECTO DE PERFORMANCE": "PERFORMANCE",
                "AUTOMATIZADOR DE PRUEBAS TRANSACCIONALES": "TRANSACCIONAL"
            }
            df_liberaciones["Producto"] = df_liberaciones["CargoColaborador"].map(cargo_to_producto)
            df_ciudad = df_panorama[["CLIENTE", "CIUDAD"]]
            #df_liberaciones = replace_vowels(df_liberaciones)
            df_liberaciones["Cliente"] = df_liberaciones["Cliente"].apply(lambda row: row.replace('Á', 'A'))
            df_liberaciones["Cliente"] = df_liberaciones["Cliente"].apply(lambda row: row.replace('É', 'E'))
            df_liberaciones["Cliente"] = df_liberaciones["Cliente"].apply(lambda row: row.replace('Í', 'I'))
            df_liberaciones["Cliente"] = df_liberaciones["Cliente"].apply(lambda row: row.replace('Ó', 'O'))
            df_liberaciones["Cliente"] = df_liberaciones["Cliente"].apply(lambda row: row.replace('Ú', 'U'))
            df_liberaciones["UEN"] = df_liberaciones["UEN"].apply(lambda row: row.replace(' ', ''))
            df_liberaciones = df_liberaciones.merge(df_ciudad, left_on="Cliente", right_on="CLIENTE", how="inner")
            cliente_to_pais = {
                "BOGOTA": "COLOMBIA",
                "MEDELLIN": "COLOMBIA",
                "LIMA": "PERU",
                "PANAMA": "PANAMA"
            }
            df_liberaciones["Pais"] = df_liberaciones["CIUDAD"].map(cliente_to_pais)
            df_liberaciones.loc[df_liberaciones["Pais"].isna(), "Pais"] = "PAÍS POR ASIGNAR"

            return df_liberaciones
        df_tabla_inicial_Liberaciones = load_data_inicial_Liberaciones()
        df_liberaciones = df_tabla_inicial_Liberaciones.copy()

        def load_data_Liberaciones():
            df_Liberaciones_tab = load_data_inicial_Liberaciones()
            df_Liberaciones_tab = df_Liberaciones_tab[(df_Liberaciones_tab["EstadoSolicitud"] == "ABIERTO") |
                                                      (df_Liberaciones_tab["EstadoSolicitud"] == "EN PROCESO")]
            return df_Liberaciones_tab
        df_Liberaciones_tab = load_data_Liberaciones()

        paises = df_rotacion["Pais"].unique()  # Lista de países que harán parte del filtro por país

        # Carga y adecuación de datos de Solicitudes
        def load_data_inicial_Solicitudes():
            df_Solicitudes_tab = pd.read_excel("Z:/Services and Products/Controles/Solicitudes/Administración de la Capacidad/Solicitudes Generalistas/Informe Solicitud v9.xlsb",
                                               header=0, sheet_name="Base")
            df_Solicitudes_tab.loc[:, df_Solicitudes_tab.dtypes=='object'] = df_Solicitudes_tab.loc[:,
                                                                             df_Solicitudes_tab.dtypes=='object'].apply(
                lambda row: row.str.upper())
            df_Solicitudes_tab.rename(columns={"País": "Pais"}, inplace=True)

            df_Solicitudes_tab["FechaNecesidadSolicitud"] = pd.TimedeltaIndex(df_Solicitudes_tab["FechaNecesidadSolicitud"] - 2,
                                                                     unit='d') + datetime(1900, 1, 1)
            df_Solicitudes_tab["Año"] = pd.DatetimeIndex(df_Solicitudes_tab["FechaNecesidadSolicitud"]).year
            df_Solicitudes_tab["NumMes"] = pd.DatetimeIndex(df_Solicitudes_tab["FechaNecesidadSolicitud"]).month

            df_Solicitudes_tab['Mes'] = df_Solicitudes_tab['NumMes'].map(NombMes)
            df_Solicitudes_tab["MesCorto"] = df_Solicitudes_tab["Mes"].map(MesCorto)
            df_Solicitudes_tab["Pais"] = df_Solicitudes_tab["Pais"].apply(lambda row: row.replace('Ú', 'U'))
            df_Solicitudes_tab["Pais"] = df_Solicitudes_tab["Pais"].apply(lambda row: row.replace('Á', 'A'))
            df_Solicitudes_tab["Pais"] = df_Solicitudes_tab["Pais"].apply(lambda row: "COLOMBIA" if row not in paises else row)
            df_Solicitudes_tab["UEN"] = df_Solicitudes_tab["UEN"].apply(lambda row: row.replace(' ', ''))
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].astype(str)
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].apply(lambda row: row.replace('Á', 'A'))
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].apply(lambda row: row.replace('É', 'E'))
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].apply(lambda row: row.replace('Í', 'I'))
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].apply(lambda row: row.replace('Ó', 'O'))
            df_Solicitudes_tab["Cliente"] = df_Solicitudes_tab["Cliente"].apply(lambda row: row.replace('Ú', 'U'))

            df_Solicitudes_tab = df_Solicitudes_tab[(df_Solicitudes_tab["EstadoSolicitudSeleccion"] == "ABIERTO") |
                                                    (df_Solicitudes_tab["EstadoSolicitudSeleccion"] == "EN PROCESO") |
                                                    (df_Solicitudes_tab["EstadoSolicitudSeleccion"].isna())]
            df_Solicitudes_tab = df_Solicitudes_tab[(df_Solicitudes_tab['EstrategiaAtencionCO'].str.contains('CONVOCATORIA') == False) &
            (df_Solicitudes_tab['Cliente'].str.contains('CHOUCAIR') == False)]

            return df_Solicitudes_tab
        df_tabla_inicial_Solicitudes = load_data_inicial_Solicitudes()
        df_solicitudes = df_tabla_inicial_Solicitudes.copy()

        def load_data_Solicitudes():
            df_Solicitudes_tab = load_data_inicial_Solicitudes()
            df_Solicitudes_tab = df_Solicitudes_tab[(df_Solicitudes_tab["EstadoSolicitudCO"] == "ABIERTO") |
                                                    (df_Solicitudes_tab["EstadoSolicitudCO"] == "EN PROCESO")]

            return df_Solicitudes_tab
        df_Solicitudes_tab = load_data_Solicitudes()

        # Elementos de selección en los filtros
        years = df_liberaciones["Año"].unique()  # Lista de años que harán parte del filtro por año
        clientes = df_panorama["CLIENTE"].unique()  # Lista de clientes que harán parte del filtro por cliente
        UEN = df_rotacion["UEN"].unique()  # Lista de UEN que harán parte del filtro por UEN
        productos = df_rotacion["Producto"].unique()  # Lista de productos que harán parte del filtro por producto
        #max_mes = df_liberaciones[df_liberaciones["Año"] == years[-1]]["NumMes"].max()
        buffer_min_mes = datetime.today().month
        buffer_max_mes = max([max(df_liberaciones["FechaTentativaLiberacion"]), max(df_solicitudes["FechaNecesidadSolicitud"])])
        buffer_max_mes = buffer_max_mes.month

        df_ingresos = df_solicitudes.copy()
        df_ingresos["FechaIngresoOP"] = pd.TimedeltaIndex(df_ingresos["FechaIngresoOP"] - 2, unit='d') + datetime(
            1900, 1, 1)
        df_ingresos["FechaIngresoOP"] = pd.to_datetime(df_ingresos["FechaIngresoOP"], errors='coerce')
        df_ingresos.dropna(subset=["FechaIngresoOP"], inplace=True)
        df_ingresos["Año"] = pd.DatetimeIndex(df_ingresos["FechaIngresoOP"]).year
        df_ingresos["NumMes"] = pd.DatetimeIndex(df_ingresos["FechaIngresoOP"]).month
        df_ingresos['Mes'] = df_ingresos['NumMes'].map(NombMes)
        df_ingresos["MesCorto"] = df_ingresos["Mes"].map(MesCorto)

        ##################################### DATOS BUFFER ###########################################
        def load_disponibles():
            df_disponibles = pd.read_excel("Z:/Services and Products/Controles/Solicitudes/Administración de la Capacidad/Solicitudes Generalistas/Backup Analistas 3.0.xlsx",
                                           sheet_name="Back Up", header=0)

            df_disponibles = df_disponibles[(df_disponibles["Estado"] == "Disponibles") &
                                            ((df_disponibles["Estatus"] == "Analistas de Pruebas en Formación") |
                                             (df_disponibles["Estatus"] == "Semillero") |
                                             (df_disponibles["Estatus"].isna()))]
            df_disponibles['UEN'] = df_disponibles['UEN'].apply(lambda row: row.upper())
            df_disponibles.loc[df_disponibles["Pais"]=="PERÚ", "Pais"] = "PERU"

            return df_disponibles
        df_disponibles = load_disponibles()

        def load_vacaciones():
            df_vacaciones = pd.read_excel("Z:/Services and Products/Controles/Gestion operacion/Vacaciones/2024/Reporte Aplicativo Vacaciones.xlsm")
            df_vacaciones = df_vacaciones[df_vacaciones["EstadoSolicitud"] == "APROBADA"]
            df_vacaciones = df_vacaciones[
                ["Identificacion", "Fecha_inicio_vacaciones", "Fecha_fin_vacaciones", "Fecha_reingreso"]]
            df_vacaciones["Fecha_inicio_vacaciones"] = pd.to_datetime(df_vacaciones["Fecha_inicio_vacaciones"],
                                                                      errors='coerce')
            df_vacaciones["Fecha_fin_vacaciones"] = pd.to_datetime(df_vacaciones["Fecha_fin_vacaciones"],
                                                                   errors='coerce')
            df_vacaciones["Fecha_reingreso"] = pd.to_datetime(df_vacaciones["Fecha_reingreso"], errors='coerce')
            return df_vacaciones

        df_vacaciones = load_vacaciones()

        def backup(UEN_drop=None, slider=(0, 12)):
            df_disponibles = load_disponibles()
            if UEN_drop is not None:
                df_disponibles = df_disponibles[df_disponibles['UEN'] == UEN_drop]
            df_vacaciones = pd.read_excel("Z:/Services and Products/Controles/Gestion operacion/Vacaciones/2024/Reporte Aplicativo Vacaciones.xlsm")
            df_vacaciones["Fecha_inicio_vacaciones"] = pd.to_datetime(df_vacaciones["Fecha_inicio_vacaciones"],
                                                                      errors='coerce')
            df_vacaciones["Fecha_fin_vacaciones"] = pd.to_datetime(df_vacaciones["Fecha_fin_vacaciones"],
                                                                   errors='coerce')
            df_vacaciones["Fecha_reingreso"] = pd.to_datetime(df_vacaciones["Fecha_reingreso"], errors='coerce')
            hoy = datetime.today()
            hoy = datetime.strftime(hoy, "%d-%m-%Y")
            hoy = datetime.strptime(hoy, "%d-%m-%Y")

            df_vacaciones["EstadoSolicitud"] = df_vacaciones.apply(
                lambda row: "FINALIZADA" if hoy > row["Fecha_fin_vacaciones"] else row["EstadoSolicitud"], axis=1)

            df_vacaciones = df_vacaciones[df_vacaciones["EstadoSolicitud"] == "APROBADA"]
            df_vacaciones = df_vacaciones[
                ["Identificacion", "Fecha_inicio_vacaciones", "Fecha_fin_vacaciones", "Fecha_reingreso"]]
            df_vacaciones["Identificacion"] = df_vacaciones["Identificacion"].astype(str)
            df_disponibles["Identificación"] = df_disponibles["Identificación"].astype(str)
            df_disponibles_vacaciones = df_disponibles.merge(df_vacaciones, left_on="Identificación",
                                                             right_on="Identificacion", how="left")
            df_disponibles_vacaciones["Vacaciones"] = df_disponibles_vacaciones.apply(lambda row: 'SI' if (
                    row["Fecha_inicio_vacaciones"] <= hoy and row["Fecha_fin_vacaciones"] >= hoy) else 'NO', axis=1)
            df_disponibles_asignacion = df_disponibles_vacaciones[df_disponibles_vacaciones["Vacaciones"] == "NO"]
            df_disponibles_en_vacaciones = df_disponibles_vacaciones[df_disponibles_vacaciones["Vacaciones"] == "SI"]

            df_disponibles_asignacion = df_disponibles_asignacion.groupby(["Pais", "Producto"])[
                "Analista"].count().reset_index()
            df_disponibles_asignacion.rename(columns={"Analista": "Esperando asignación"}, inplace=True)
            df_disponibles_en_vacaciones = df_disponibles_en_vacaciones.groupby(["Pais", "Producto"])[
                "Analista"].count().reset_index()
            df_disponibles_en_vacaciones.rename(columns={"Analista": "En vacaciones"}, inplace=True)

            df_disponibles = df_disponibles_asignacion.merge(df_disponibles_en_vacaciones, on=["Pais", "Producto"],
                                                             how="outer").fillna(0)

            df_panorama = load_data_panorama("BD Empleados")

            df_panorama = df_panorama[df_panorama["Estado"] == "A"]
            df_panorama = df_panorama[["Cedula", "PAÍS ANALISTA"]]


            df_pendientes = df_liberaciones[(df_liberaciones["EstadoSolicitud"] == "ABIERTO") |
                                            (df_liberaciones["EstadoSolicitud"] == "EN PROCESO")]
            df_pendientes = df_pendientes[(df_pendientes["NumMes"] >= slider[0]) &
                                           (df_pendientes["NumMes"] <= slider[1])]

            if UEN_drop is not None:
                df_pendientes = df_pendientes[df_pendientes['UEN'] == UEN_drop]
            df_panorama["Cedula"] = df_panorama["Cedula"].apply(lambda x: str(x))
            df_pendientes["IdentificacionColaborador"] = df_pendientes["IdentificacionColaborador"].apply(lambda x: str(x))

            df_pendientes = df_pendientes.merge(df_panorama, left_on="IdentificacionColaborador", right_on="Cedula", how="inner")

            df_pendientes = df_pendientes.groupby(["PAÍS ANALISTA", "Producto"])[
                "IdentificacionColaborador"].count().reset_index()
            df_pendientes.rename(
                columns={"IdentificacionColaborador": "Pendientes de liberación", "PAÍS ANALISTA": "Pais"},
                inplace=True)

            df_pendientes.loc[df_pendientes["Producto"] == "MIGRACIÓN", "Producto"] = "MIGRACION"
            df_disponibles.loc[df_disponibles["Producto"] == "MIGRACIÓN", "Producto"] = "MIGRACION"

            df_solicitudes_firme = df_solicitudes[((df_solicitudes["EstadoSolicitudCO"] == "ABIERTO") |
                                                   (df_solicitudes["EstadoSolicitudCO"] == "EN PROCESO")) & (
                                                              df_solicitudes['Cliente'].str.contains(
                                                                  'CHOUCAIR') == False) &
                                                  (df_solicitudes['EstrategiaAtencionCO'].str.contains(
                                                      'CONVOCATORIA') == False)]
            df_solicitudes_firme = df_solicitudes_firme[(df_solicitudes_firme["NumMes"] >= slider[0]) &
                                                        (df_solicitudes_firme["NumMes"] <= slider[1])]
            if UEN_drop is not None:
                df_solicitudes_firme = df_solicitudes_firme[df_solicitudes_firme['UEN'] == UEN_drop]
            df_solicitudes_firme = df_solicitudes_firme.groupby(["Pais", "Producto"])["Año"].count().reset_index()
            df_solicitudes_firme.rename(columns={"Año": "Solicitudes en firme"}, inplace=True)

            df_buffer = pd.read_excel(
                "Z:/Services and Products/Controles/Solicitudes/Administración de la Capacidad/Solicitudes Generalistas/Buffer.xlsx",
                sheet_name="Hoja1", header=0)
            df_buffer.loc[:, df_buffer.dtypes == 'object'] = df_buffer.loc[:, df_buffer.dtypes == 'object'].apply(
                lambda row: row.str.upper())
            df_buffer.loc[df_buffer["Producto"] == "MIGRACIÓN", "Producto"] = "MIGRACION"

            if UEN_drop is not None:
                df_buffer = df_buffer[df_buffer['UEN'] == UEN_drop]
            df_buffer.loc[df_buffer["Pais"] == "PERÚ", "Pais"] = 'PERU'
            df_buffer = df_buffer.groupby(["Pais", "Producto"])["TOTAL"].count().reset_index()
            df_buffer.rename(columns={"TOTAL": "Buffer"}, inplace=True)

            df_backup = df_disponibles.merge(df_pendientes, on=['Pais', 'Producto'], how='outer').merge(
                df_solicitudes_firme, on=['Pais', 'Producto'], how='outer').merge(
                df_buffer, on=['Pais', 'Producto'], how='outer').fillna(0)
            df_backup["Neto"] = (df_backup["Esperando asignación"] + df_backup["En vacaciones"] +
                                 df_backup["Pendientes de liberación"] - df_backup["Solicitudes en firme"] -
                                 df_backup["Buffer"])
            df_backup = df_backup.sort_values(by=["Pais", "Neto"], ascending=[True, False])

            return df_backup

        def tabla_resumen(years_drop=2023, meses_slider=[1, 12], clientes_drop=None, UEN_drop=None,
                          paises_drop=None, productos_drop=None):
            df_CI_tabla = df_CI[(df_CI["Año"] == years_drop) &
                                (df_CI["NumMes"] >= meses_slider[0]) &
                                (df_CI["NumMes"] <= meses_slider[1]) &
                                (df_CI["Egresos"] != 1)]
            df_rotacion_tabla = df_rotacion[(df_rotacion["Año"] == years_drop) &
                                            (df_rotacion["NumMes"] >= meses_slider[0]) &
                                            (df_rotacion["NumMes"] <= meses_slider[1])]
            df_liberaciones_tabla = df_liberaciones[(df_liberaciones["Año"] == years_drop) &
                                                    (df_liberaciones["NumMes"] >= meses_slider[0]) &
                                                    (df_liberaciones["NumMes"] <= meses_slider[1])]
            df_solicitudes_tabla = df_solicitudes[(df_solicitudes["Año"] == years_drop) &
                                                  (df_solicitudes["NumMes"] >= meses_slider[0]) &
                                                  (df_solicitudes["NumMes"] <= meses_slider[1]) &
                                                  (df_solicitudes["EstadoSolicitudCO"] != "CANCELADO")]
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

            df_liberaciones_tabla = df_liberaciones_tabla.groupby(["NumMes", "MesCorto"])[
                "Cliente"].count().reset_index()
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
            if df.iloc[0, 1:-1].sum():
                df.iloc[0, -1] = round(df.iloc[0, 1:-1].sum() / (len(df.columns) - 2))
            else:
                df.iloc[0, -1] = 0
            df.rename(columns={'index': 'INDICADOR'}, inplace=True)

            df_rotacion_tabla_spikeline = df_rotacion_tabla
            df_liberaciones_tabla_spikeline = df_liberaciones_tabla
            df_solicitudes_tabla_spikeline = df_solicitudes_tabla
            df_CI_tabla_spikeline = df_CI_tabla
            df_ingresos_tabla_spikeline = df_ingresos_tabla

            return (df, df_rotacion_tabla_spikeline, df_liberaciones_tabla_spikeline, df_solicitudes_tabla_spikeline,
                    df_CI_tabla_spikeline, df_ingresos_tabla_spikeline)

        df, _, _, _, _, _ = tabla_resumen()

        #######################################################################################
        ########################### DATOS DE ROTACIÓN #########################################
        #######################################################################################

        def data_filtros(df, years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                         paises_drop_rotacion, productos_drop_rotacion):
            """Filtra el dataframe segín los filtros activados en el Dash"""
            df_chart = df[(df["Año"] == years_drop_rotacion) & (df["NumMes"] >= meses_slider_rotacion[0]) & (
                    df["NumMes"] <= meses_slider_rotacion[1])]

            title_list = []  # Creamos una lista que contiene los filtros seleccionados para desplegarlos en el título de la gráfica

            # Filtramos el dataframe con la posibilidad de acumular las opciones de filtrado
            if clientes_drop_rotacion is not None:
                df_chart = df_chart[df_chart["Cliente"] == clientes_drop_rotacion]
                title_list.append(clientes_drop_rotacion)

            if UEN_drop_rotacion is not None:
                df_chart = df_chart[df_chart["UEN"] == UEN_drop_rotacion]
                title_list.append(UEN_drop_rotacion)

            if paises_drop_rotacion is not None:
                df_chart = df_chart[df_chart["Pais"] == paises_drop_rotacion]
                title_list.append(paises_drop_rotacion)

            if productos_drop_rotacion is not None:
                df_chart = df_chart[df_chart["Producto"] == productos_drop_rotacion]
                title_list.append(productos_drop_rotacion)

            for t in title_list:
                title = "-".join(title_list)

            # Si no hay un filtro activado, se muestra el año en el título de la gráfica
            title = title if len(title_list) > 0 else years_drop_rotacion

            return df_chart, title

        def df_data_chart(df_chart, categoria):
            """Agrupa el dataframe por mesy la categoría escogida, cuenta la cantidad de registros y crea una tabla
            pivot cuyas columnas la categoría escogida (por ejemplo, producto) y los valores son la cantidad de registro
            de la categoría escogida por mes."""
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Rotación"}, inplace=True)
            df_chart = pd.pivot_table(df_chart, columns=categoria, values="Rotación",
                                      index="Mes", sort=False)
            df_chart.fillna(0, inplace=True)

            return df_chart

        def df_data_table(df_chart, categoria):
            """Agrupa el dataframe por mesy la categoría escogida, cuenta la cantidad de registros y crea una tabla
                pivot cuyas columnas los meses y los valores son la cantidad de registro
                de la categoría escogida."""
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Rotación"}, inplace=True)

            df_tabla = pd.pivot_table(df_chart, columns="Mes", values="Rotación",
                                      index=categoria, sort=False).reset_index()
            df_tabla.fillna(0, inplace=True)

            # Adicionamos una fila con el total de registros por mes y una columna con el total de registros por categoría
            df_tabla["TOTAL"] = df_tabla.iloc[:, 1:].sum(axis=1)
            df_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_tabla.sum()).T
            df_tabla = pd.concat([df_tabla, sum_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "TOTAL"

            return df_tabla

        parametros = ["Pais", "UEN", "Producto", "Cliente",
                      "CAUSAL / ESTRATEGIA"]  # Parámetros a filtrar en la gráfica de datos acumulados
        colors = ['#EF553B', '#636EFA', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF',
                  '#FECB52']  # Colores a usar en los gráficos

        #######################################################################################
        ########################### DATOS DE CAPACIDAD INSTALADA ##############################
        #######################################################################################

        def data_filtros_CI(df, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                            paises_cliente_drop_CI=None, productos_drop_CI=None):
            df_chart = df[(df["Año"] == years_drop_CI) & (df["NumMes"] >= meses_slider_CI[0]) & (
                    df["NumMes"] <= meses_slider_CI[1])]

            title_list = []
            if clientes_drop_CI is not None:
                df_chart = df_chart[df_chart["Cliente"] == clientes_drop_CI]
                title_list.append(clientes_drop_CI)

            if UEN_drop_CI is not None:
                df_chart = df_chart[df_chart["UEN"] == UEN_drop_CI]
                title_list.append(UEN_drop_CI)

            if paises_drop_CI is not None:
                df_chart = df_chart[df_chart["Pais"] == paises_drop_CI]
                title_list.append(paises_drop_CI)

            if paises_cliente_drop_CI is not None:
                df_chart = df_chart[df_chart["Pais Cliente"] == paises_cliente_drop_CI]
                title_list.append(paises_cliente_drop_CI)

            if productos_drop_CI is not None:
                df_chart = df_chart[df_chart["Producto"] == productos_drop_CI]
                title_list.append(productos_drop_CI)

            for t in title_list:
                title = "-".join(title_list)

            title = title if len(title_list) > 0 else years_drop_CI

            return df_chart, title

        def df_data_chart_CI(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Capacidad instalada"}, inplace=True)
            df_chart = pd.pivot_table(df_chart, columns=categoria, values="Capacidad instalada",
                                      index="Mes", sort=False)
            df_chart.fillna(0, inplace=True)

            return df_chart

        def df_data_table_CI(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Capacidad instalada"}, inplace=True)

            df_tabla = pd.pivot_table(df_chart, columns="Mes", values="Capacidad instalada",
                                      index=categoria, sort=False).reset_index()
            df_tabla.fillna(0, inplace=True)

            df_tabla["TOTAL"] = df_tabla.iloc[:, 1:].sum(axis=1)
            df_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_tabla.sum()).T
            df_tabla = pd.concat([df_tabla, sum_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "TOTAL"

            return df_tabla

        def tabla_resumen_CI(df_CI, years_drop_CI=2023, meses_slider_CI=[1, 12], clientes_drop_CI=None,
                             UEN_drop_CI=None, paises_drop_CI=None, paises_cliente_drop_CI=None, productos_drop_CI=None):
            df_inicial = df_CI[(df_CI["Año"] == years_drop_CI) & (df_CI["NumMes"] >= meses_slider_CI[0]) &
                               (df_CI["NumMes"] <= meses_slider_CI[1]) & (df_CI["Ingresos"] != 1)]
            df_ingresos = df_CI[(df_CI["Año"] == years_drop_CI) & (df_CI["NumMes"] >= meses_slider_CI[0]) &
                                (df_CI["NumMes"] <= meses_slider_CI[1]) & (df_CI["Ingresos"] == 1)]
            df_egresos = df_CI[(df_CI["Año"] == years_drop_CI) & (df_CI["NumMes"] >= meses_slider_CI[0]) &
                               (df_CI["NumMes"] <= meses_slider_CI[1]) & (df_CI["Egresos"] == 1)]
            df_final = df_CI[(df_CI["Año"] == years_drop_CI) & (df_CI["NumMes"] >= meses_slider_CI[0]) &
                             (df_CI["NumMes"] <= meses_slider_CI[1]) & (df_CI["Egresos"] != 1)]

            if clientes_drop_CI is not None:
                df_inicial = df_inicial[df_inicial["Cliente"] == clientes_drop_CI]
                df_ingresos = df_ingresos[df_ingresos["Cliente"] == clientes_drop_CI]
                df_final = df_final[df_final["Cliente"] == clientes_drop_CI]
                df_final = df_final[df_final["Cliente"] == clientes_drop_CI]

            if UEN_drop_CI is not None:
                df_inicial = df_inicial[df_inicial["UEN"] == UEN_drop_CI]
                df_ingresos = df_ingresos[df_ingresos["UEN"] == UEN_drop_CI]
                df_egresos = df_egresos[df_egresos["UEN"] == UEN_drop_CI]
                df_final = df_final[df_final["UEN"] == UEN_drop_CI]

            if paises_drop_CI is not None:
                df_inicial = df_inicial[df_inicial["Pais"] == paises_drop_CI]
                df_ingresos = df_ingresos[df_ingresos["Pais"] == paises_drop_CI]
                df_egresos = df_egresos[df_egresos["Pais"] == paises_drop_CI]
                df_final = df_final[df_final["Pais"] == paises_drop_CI]

            if paises_cliente_drop_CI is not None:
                df_inicial = df_inicial[df_inicial["Pais Cliente"] == paises_cliente_drop_CI]
                df_ingresos = df_ingresos[df_ingresos["Pais Cliente"] == paises_cliente_drop_CI]
                df_egresos = df_egresos[df_egresos["Pais Cliente"] == paises_cliente_drop_CI]
                df_final = df_final[df_final["Pais Cliente"] == paises_cliente_drop_CI]

            if productos_drop_CI is not None:
                df_inicial = df_inicial[df_inicial["Producto"] == productos_drop_CI]
                df_ingresos = df_ingresos[df_ingresos["Producto"] == productos_drop_CI]
                df_egresos = df_egresos[df_egresos["Producto"] == productos_drop_CI]
                df_final = df_final[df_final["Producto"] == productos_drop_CI]

            df_inicial = df_inicial.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_inicial.sort_values(by="NumMes", ascending=True, inplace=True)
            df_inicial.rename(columns={"Cliente": "CI INICIAL"}, inplace=True)

            df_ingresos = df_ingresos.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_ingresos.sort_values(by="NumMes", ascending=True, inplace=True)
            df_ingresos.rename(columns={"Cliente": "INGRESOS"}, inplace=True)

            df_egresos = df_egresos.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_egresos.sort_values(by="NumMes", ascending=True, inplace=True)
            df_egresos.rename(columns={"Cliente": "RETIROS"}, inplace=True)

            df_final = df_final.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_final.sort_values(by="NumMes", ascending=True, inplace=True)
            df_final.rename(columns={"Cliente": "CI FINAL"}, inplace=True)

            df_CI_tab = df_inicial.merge(df_ingresos, on=['Mes', 'NumMes'], how='outer').merge(
                df_egresos, on=['Mes', 'NumMes'], how='outer').merge(
                df_final, on=['Mes', 'NumMes'], how='outer').fillna(0)
            df_CI_tab['% TASA DE ROTACIÓN'] = df_CI_tab.apply(
                lambda row: round(row["RETIROS"] * 100 / (row["CI INICIAL"] + row["INGRESOS"])), axis=1)
            df_CI_tab.drop("NumMes", axis=1, inplace=True)
            df_spikeline = df_inicial.copy()

            return df_CI_tab, df_spikeline

        df_CI_tab = df_CI_tab_raw[df_CI_tab_raw["Egresos"] != 1]

        #######################################################################################
        ########################### DATOS DE SOLICITUD ########################################
        #######################################################################################

        def data_filtros_Solicitudes(df, years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                     UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes):
            df_chart = df[(df["Año"] == years_drop_Solicitudes) & (df["NumMes"] >= meses_slider_Solicitudes[0]) & (
                    df["NumMes"] <= meses_slider_Solicitudes[1])]

            title_list = []
            if clientes_drop_Solicitudes is not None:
                df_chart = df_chart[df_chart["Cliente"] == clientes_drop_Solicitudes]
                title_list.append(clientes_drop_Solicitudes)

            if UEN_drop_Solicitudes is not None:
                df_chart = df_chart[df_chart["UEN"] == UEN_drop_Solicitudes]
                title_list.append(UEN_drop_Solicitudes)

            if paises_drop_Solicitudes is not None:
                df_chart = df_chart[df_chart["Pais"] == paises_drop_Solicitudes]
                title_list.append(paises_drop_Solicitudes)

            if productos_drop_Solicitudes is not None:
                df_chart = df_chart[df_chart["Producto"] == productos_drop_Solicitudes]
                title_list.append(productos_drop_Solicitudes)

            for t in title_list:
                title = "-".join(title_list)

            title = title if len(title_list) > 0 else years_drop_Solicitudes

            return df_chart, title

        def df_data_chart_Solicitudes(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Solicitudes"}, inplace=True)
            df_chart = pd.pivot_table(df_chart, columns=categoria, values="Solicitudes",
                                      index="Mes", sort=False)
            df_chart.fillna(0, inplace=True)

            return df_chart

        def df_data_table_Solicitudes(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Solicitudes"}, inplace=True)

            df_tabla = pd.pivot_table(df_chart, columns="Mes", values="Solicitudes",
                                      index=categoria, sort=False).reset_index()
            df_tabla.fillna(0, inplace=True)

            df_tabla["TOTAL"] = df_tabla.iloc[:, 1:].sum(axis=1)
            df_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_tabla.sum()).T
            df_tabla = pd.concat([df_tabla, sum_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "TOTAL"

            return df_tabla

        #######################################################################################
        ########################### DATOS DE LIBERACIONES #####################################
        #######################################################################################
        def data_filtros_Liberaciones(df, years_drop_Liberaciones, meses_slider_Liberaciones,
                                      clientes_drop_Liberaciones, UEN_drop_Liberaciones, paises_drop_Liberaciones,
                                      productos_drop_Liberaciones):
            df_chart = df[(df["Año"] == years_drop_Liberaciones) & (df["NumMes"] >= meses_slider_Liberaciones[0]) & (
                    df["NumMes"] <= meses_slider_Liberaciones[1])]

            title_list = []
            if clientes_drop_Liberaciones is not None:
                df_chart = df_chart[df_chart["Cliente"] == clientes_drop_Liberaciones]
                title_list.append(clientes_drop_Liberaciones)

            if UEN_drop_Liberaciones is not None:
                df_chart = df_chart[df_chart["UEN"] == UEN_drop_Liberaciones]
                title_list.append(UEN_drop_Liberaciones)

            if paises_drop_Liberaciones is not None:
                df_chart = df_chart[df_chart["Pais"] == paises_drop_Liberaciones]
                title_list.append(paises_drop_Liberaciones)

            if productos_drop_Liberaciones is not None:
                df_chart = df_chart[df_chart["Producto"] == productos_drop_Liberaciones]
                title_list.append(productos_drop_Liberaciones)

            for t in title_list:
                title = "-".join(title_list)

            title = title if len(title_list) > 0 else years_drop_Liberaciones

            return df_chart, title

        def df_data_chart_Liberaciones(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Liberaciones"}, inplace=True)
            df_chart = pd.pivot_table(df_chart, columns=categoria, values="Liberaciones",
                                      index="Mes", sort=False)
            df_chart.fillna(0, inplace=True)

            return df_chart

        def df_data_table_Liberaciones(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Liberaciones"}, inplace=True)

            df_tabla = pd.pivot_table(df_chart, columns="Mes", values="Liberaciones",
                                      index=categoria, sort=False).reset_index()
            df_tabla.fillna(0, inplace=True)

            df_tabla["TOTAL"] = df_tabla.iloc[:, 1:].sum(axis=1)
            df_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_tabla.sum()).T
            df_tabla = pd.concat([df_tabla, sum_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "TOTAL"

            return df_tabla

        #######################################################################################
        ########################### DATOS DE CONTRATACIONES ###################################
        #######################################################################################
        # Cargamos los datos del Excel un un Dataframe de Pandas
        def load_data_inicial_Contrataciones():
            df_Contrataciones_tab = pd.read_excel(
                "Z:/Services and Products/Controles/Solicitudes/Administración de la Capacidad/Solicitudes Generalistas/Informe Solicitud v9.xlsb", header=0,
                sheet_name="Base")
            df_Contrataciones_tab.loc[:, df_Contrataciones_tab.dtypes == 'object'] = df_Contrataciones_tab.loc[:,
                                                                                     df_Contrataciones_tab.dtypes == 'object'].apply(
                lambda row: row.str.upper())

            # Escogemos las columnas de interés
            df_Contrataciones_tab.rename(columns={"País": "Pais"}, inplace=True)
            df_Contrataciones_tab["Fecha"] = df_Contrataciones_tab.apply(lambda row: row["FechaIngresoOP"] if row["FechaIngresoOP"] > 0 else row["FechaNecesidadSolicitud"], axis=1)
            df_Contrataciones_tab["Fecha"] = pd.TimedeltaIndex(df_Contrataciones_tab["Fecha"] - 2,
                                                                        unit='d') + datetime(1900, 1, 1)
            df_Contrataciones_tab["Año"] = pd.DatetimeIndex(df_Contrataciones_tab["Fecha"]).year
            df_Contrataciones_tab["NumMes"] = pd.DatetimeIndex(df_Contrataciones_tab["Fecha"]).month

            df_Contrataciones_tab['Mes'] = df_Contrataciones_tab['NumMes'].map(NombMes)
            df_Contrataciones_tab["Pais"] = df_Contrataciones_tab["Pais"].apply(lambda row: row.replace('Ú', 'U'))
            df_Contrataciones_tab["Pais"] = df_Contrataciones_tab["Pais"].apply(lambda row: row.replace('Á', 'A'))
            df_Contrataciones_tab["Pais"] = df_Contrataciones_tab["Pais"].apply(
                lambda row: "COLOMBIA" if row not in paises else row)
            df_Contrataciones_tab["UEN"] = df_Contrataciones_tab["UEN"].apply(lambda row: row.replace(' ', ''))
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].astype(str)
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].apply(lambda row: row.replace('Á', 'A'))
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].apply(lambda row: row.replace('É', 'E'))
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].apply(lambda row: row.replace('Í', 'I'))
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].apply(lambda row: row.replace('Ó', 'O'))
            df_Contrataciones_tab["Cliente"] = df_Contrataciones_tab["Cliente"].apply(lambda row: row.replace('Ú', 'U'))

            df_Contrataciones_tab = df_Contrataciones_tab[
                df_Contrataciones_tab["EstrategiaAtencionCO"] == "CONTRATACIÓN"]

            return df_Contrataciones_tab

        df_tabla_inicial_Contrataciones = load_data_inicial_Contrataciones()

        def load_data_Contrataciones(option="EN FIRME"):
            df_Contrataciones_tab = load_data_inicial_Contrataciones()
            if option == "EN FIRME":
                df_Contrataciones_tab = df_Contrataciones_tab[
                    (df_Contrataciones_tab["EstadoSolicitudSeleccion"] == "ABIERTO") |
                    (df_Contrataciones_tab["EstadoSolicitudSeleccion"] == "EN PROCESO")]
            if option == "FINALIZADAS":
                df_Contrataciones_tab = df_Contrataciones_tab[
                    (df_Contrataciones_tab["EstadoSolicitudSeleccion"] == "FINALIZADO")]
            return df_Contrataciones_tab

        df_Contrataciones_tab = load_data_Contrataciones()
        df_Contrataciones_tab_finalizado = load_data_Contrataciones("FINALIZADAS")

        def data_filtros_Contrataciones(df, years_drop_Contrataciones, meses_slider_Contrataciones,
                                        clientes_drop_Contrataciones, UEN_drop_Contrataciones,
                                        paises_drop_Contrataciones, productos_drop_Contrataciones):
            df_chart = df[
                (df["Año"] == years_drop_Contrataciones) & (df["NumMes"] >= meses_slider_Contrataciones[0]) & (
                        df["NumMes"] <= meses_slider_Contrataciones[1])]

            title_list = []
            if clientes_drop_Contrataciones is not None:
                df_chart = df_chart[df_chart["Cliente"] == clientes_drop_Contrataciones]
                title_list.append(clientes_drop_Contrataciones)

            if UEN_drop_Contrataciones is not None:
                df_chart = df_chart[df_chart["UEN"] == UEN_drop_Contrataciones]
                title_list.append(UEN_drop_Contrataciones)

            if paises_drop_Contrataciones is not None:
                df_chart = df_chart[df_chart["Pais"] == paises_drop_Contrataciones]
                title_list.append(paises_drop_Contrataciones)

            if productos_drop_Contrataciones is not None:
                df_chart = df_chart[df_chart["Producto"] == productos_drop_Contrataciones]
                title_list.append(productos_drop_Contrataciones)

            for t in title_list:
                title = "-".join(title_list)

            title = title if len(title_list) > 0 else years_drop_Contrataciones

            return df_chart, title

        def df_data_chart_Contrataciones(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Contrataciones"}, inplace=True)
            df_chart = pd.pivot_table(df_chart, columns=categoria, values="Contrataciones",
                                      index="Mes", sort=False)
            df_chart.fillna(0, inplace=True)

            return df_chart

        def df_data_table_Contrataciones(df_chart, categoria):
            df_chart = df_chart.groupby(["NumMes", "Mes", categoria])[
                "Año"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Año": "Contrataciones"}, inplace=True)

            df_tabla = pd.pivot_table(df_chart, columns="Mes", values="Contrataciones",
                                      index=categoria, sort=False).reset_index()
            df_tabla.fillna(0, inplace=True)

            df_tabla["TOTAL"] = df_tabla.iloc[:, 1:].sum(axis=1)
            df_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_tabla.sum()).T
            df_tabla = pd.concat([df_tabla, sum_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "TOTAL"

            return df_tabla

        def crecimiento_real(years_drop=2023, clientes_drop=None, UEN_drop=None, paises_drop=None, productos_drop=None,
                             option_crecimiento=None):
            df_Solicitudes = df_tabla_inicial_Solicitudes.copy()

            df_Liberaciones = load_data_inicial_Liberaciones()
            if option_crecimiento == 'EN FIRME':
                df_Liberaciones = df_Liberaciones[(df_Liberaciones["EstadoSolicitud"] == "ABIERTO") |
                                                  (df_Liberaciones["EstadoSolicitud"] == "EN PROCESO")]
            elif option_crecimiento == 'FINALIZADAS':
                df_Liberaciones = df_Liberaciones[(df_Liberaciones["EstadoSolicitud"] == "FINALIZADO")]
            else:
                df_Liberaciones = df_Liberaciones[(df_Liberaciones["EstadoSolicitud"] != "CANCELADO")]
            df_Rotacion = df_rotacion_tab.copy()

            if clientes_drop is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Cliente"] == clientes_drop]
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Cliente"] == clientes_drop]
                df_Rotacion = df_Rotacion[df_Rotacion["Cliente"] == clientes_drop]

            if UEN_drop is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["UEN"] == UEN_drop]
                df_Liberaciones = df_Liberaciones[df_Liberaciones["UEN"] == UEN_drop]
                df_Rotacion = df_Rotacion[df_Rotacion["UEN"] == UEN_drop]

            if paises_drop is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Pais"] == paises_drop]
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Pais"] == paises_drop]
                df_Rotacion = df_Rotacion[df_Rotacion["Pais"] == paises_drop]

            if productos_drop is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Producto"] == productos_drop]
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Producto"] == productos_drop]
                df_Rotacion = df_Rotacion[df_Rotacion["Producto"] == productos_drop]

            df_Solicitudes = df_Solicitudes[(df_Solicitudes['EstrategiaAtencionCO'].str.contains(
                'CONVOCATORIA') == False)]
            df_Solicitudes = df_Solicitudes[(df_Solicitudes['Cliente'].str.contains('CHOUCAIR') == False) &
                                            (df_Solicitudes["EstadoSolicitudCO"] != "CANCELADO") &
                                            (df_Solicitudes["Año"] == years_drop)]
            df_Solicitudes = df_Solicitudes[(df_Solicitudes["EstadoSolicitudSeleccion"] == "ABIERTO") |
                                            (df_Solicitudes["EstadoSolicitudSeleccion"] == "EN PROCESO")|
                                            (df_Solicitudes["EstadoSolicitudSeleccion"].isna())]

            df_Liberaciones = df_Liberaciones[(df_Liberaciones["EstadoSolicitud"] != "CANCELADO") &
                                              (df_Liberaciones["Año"] == years_drop)]
            df_Rotacion = df_Rotacion[((df_Rotacion['Cliente'].str.contains('CHOUCAIR') == False)) &
                                      (df_Rotacion["Año"] == years_drop)]
            df_Solicitudes = df_Solicitudes.groupby(["Año", "Mes", "NumMes"])["Cliente"].count().reset_index()
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Liberaciones = df_Liberaciones.groupby(["Año", "Mes", "NumMes"])["Cliente"].count().reset_index()
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Rotacion = df_Rotacion.groupby(["Año", "Mes", "NumMes"])["Cliente"].count().reset_index()
            df_Rotacion.rename(columns={"Cliente": "Rotación"}, inplace=True)

            df_crecimiento = df_Solicitudes.merge(df_Liberaciones, on=['Año', 'Mes', 'NumMes'], how='outer').merge(
                df_Rotacion, on=['Año', 'Mes', 'NumMes'], how='outer').fillna(0)
            df_crecimiento["Crecimiento"] = df_crecimiento["Solicitudes"] - df_crecimiento["Liberaciones"] - df_crecimiento["Rotación"]
            df_crecimiento.sort_values(by='NumMes', ascending=True, inplace=True)
            return df_crecimiento

        #####################################################################
        ############### Creación de elementos del Dash ######################
        #####################################################################

        external_stylesheets = [dbc.themes.SPACELAB]  # Definición de la plantilla que da estilo al Dash
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)  # Creación del objeto Dash
        app.title = "Indicadores PVO"
        tab_resumen = dbc.Row([
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
            ######################## SLIDER DE RANGO DE MESES #############################
            dbc.Card([
                dcc.RangeSlider(id='meses_slider', min=1, max=12, value=[1, 12], dots=True, step=1,
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
                                       12: {'label': 'Diciembre', 'style': {'color': 'black', 'font-size': '16px'}}})],
                body=True, color='light'),

            ########################### TABLA DE INDICADORES Y GRÁFICOS ###########################
            dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id='resumen'), color='#119DFF', type='dot',
                                                              fullscreen=True)),
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

            dbc.Card(dbc.CardBody([dcc.Dropdown(
                                       id='Estado_Liberaciones_drop',  # Estado de las liberaciones en tabla de crecimiento
                                       multi=False,
                                       clearable=True,
                                       disabled=False,
                                       style={'display': True, 'width':'250px'},
                                       placeholder='Estado de liberaciones',
                                       options=['FINALIZADAS']
                                   ),
                                   dcc.Loading(dcc.Graph(id='crecimiento'), color='#119DFF', type='dot', fullscreen=True),
                                   dash_table.DataTable(
                                       id='tabla_crecimiento',
                                       style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                                     'backgroundColor': 'lightgrey'},
                                       style_data={'color': 'black', 'text-align': 'center', 'height': '25px',
                                                   'width': '750px'})
                                   ]),
                     color='light'),

            dbc.Card(dbc.CardBody([html.H5("ESTRATEGIA DE BUFFER", style={'text-align': 'center',
                                                                          'color': 'black', 'font-weight': 'bold'},
                                           className="card-title"),
                                   dcc.RangeSlider(id='buffer_slider', min=buffer_min_mes, max=buffer_max_mes,
                                                   value=[buffer_min_mes, buffer_max_mes], dots=True,
                                                   step=1,
                                                   marks={0: {'style': {'color': 'white'}},
                                                          1: {'label': 'Enero',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          2: {'label': 'Febrero',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          3: {'label': 'Marzo',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          4: {'label': 'Abril',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          5: {'label': 'Mayo',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          6: {'label': 'Junio',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          7: {'label': 'Julio',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          8: {'label': 'Agosto',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          9: {'label': 'Septiembre',
                                                              'style': {'color': 'black', 'font-size': '16px'}},
                                                          10: {'label': 'Octubre',
                                                               'style': {'color': 'black', 'font-size': '16px'}},
                                                          11: {'label': 'Noviembre',
                                                               'style': {'color': 'black', 'font-size': '16px'}},
                                                          12: {'label': 'Diciembre',
                                                               'style': {'color': 'black', 'font-size': '16px'}}}),
                                   dcc.Loading(dash_table.DataTable(
                                       id='tabla_buffer',
                                       style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                                     'backgroundColor': 'lightgrey'},
                                       style_data={'color': 'black', 'text-align': 'center', 'height': '25px',
                                                   'width': '750px'}), color='#119DFF', type='dot',
                                               fullscreen=True)]),
                     color='light'),
            dcc.Interval(id='interval', interval=7200000, n_intervals=0)
        ]),
        tab_rotacion = html.Div([

            # Los Div son contenedores. Usarlos nos ayudará a posicionar los elementos como deseemos
            html.Div([html.H1("ROTACIÓN CHOUCAIR", style={'text-align': 'center',
                                                          'font-family': 'Arial', 'font-weight': 'bold',
                                                          'margin-bottom': '12px'})]),
            # El parámetro style sirve para asignar fuente, tamaño y alineación a los textos.
            # Más abajo verás que sirve también para psicionar elementos

            ##################################### DROPDOWNS DE FILTROS ############################################
            dbc.Row([
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='years_drop_rotacion',  # Dropwdown para el filtro de años
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
                        id='clientes_drop_rotacion',  # Dropwdown para el filtro de clientes
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
                        id='UEN_drop_rotacion',  # Dropwdown para el filtro de UEN
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
                        id='paises_drop_rotacion',  # Dropwdown para el filtro de países
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
                        id='productos_drop_rotacion',  # Dropwdown para el filtro de productos
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='Producto',
                        options=[{'label': p, 'value': p} for p in productos]
                    ), body=True, color="light"
                )),
            ]),

            # dbc.Card Crea un cuadro en el que posicionamos elementos. Ayuda visualemente a diferenciarlos
            dbc.Card([dcc.RangeSlider(id='meses_slider_rotacion', min=1, max=12, value=[1, 12], dots=True, step=1,
                                      marks={0: {'style': {'color': 'white'}},
                                             1: {'label': 'Enero', 'style': {'color': 'black', 'font-size': '16px'}},
                                             2: {'label': 'Febrero', 'style': {'color': 'black', 'font-size': '16px'}},
                                             3: {'label': 'Marzo', 'style': {'color': 'black', 'font-size': '16px'}},
                                             4: {'label': 'Abril', 'style': {'color': 'black', 'font-size': '16px'}},
                                             5: {'label': 'Mayo', 'style': {'color': 'black', 'font-size': '16px'}},
                                             6: {'label': 'Junio', 'style': {'color': 'black', 'font-size': '16px'}},
                                             7: {'label': 'Julio', 'style': {'color': 'black', 'font-size': '16px'}},
                                             8: {'label': 'Agosto', 'style': {'color': 'black', 'font-size': '16px'}},
                                             9: {'label': 'Septiembre',
                                                 'style': {'color': 'black', 'font-size': '16px'}},
                                             10: {'label': 'Octubre', 'style': {'color': 'black', 'font-size': '16px'}},
                                             11: {'label': 'Noviembre',
                                                  'style': {'color': 'black', 'font-size': '16px'}},
                                             12: {'label': 'Diciembre',
                                                  'style': {'color': 'black', 'font-size': '16px'}}})], body=True,
                     color='light'),

            html.Div([
                html.Div([
                    # dbc.Card crea marcos en los que insertar elementos como tablas y gráficos para separarlos visualmente
                    dbc.Card(dbc.CardBody([
                        # dcc.Loading despliega una animación de espera minetras actualiza el elemento
                        dcc.Loading(dcc.Graph(id='total-pais'), color='#119DFF', type='dot', fullscreen=True),
                        # dcc.Graph crea un gráfico
                        # dbc.Accordeon inserta otros elementos en un botón desplegable
                        dbc.Accordion([dbc.AccordionItem([
                            dash_table.DataTable(  # dash_table.DataTable crea una tabla en la que insertar un dataframe
                                id='tabla-pais',
                                style_header={'font-weight': 'bold', 'color': 'black',
                                              'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                style_table={'width': '750px'})],
                            title="Abrir tabla por País")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='total-UEN'), color='#119DFF', type='dot', fullscreen=True),
                         dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                             id='tabla-UEN',
                             style_header={'font-weight': 'bold', 'color': 'black',
                                           'text-align': 'center',
                                           'backgroundColor': 'lightgrey'},
                             style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                             style_table={'width': '750px'}),
                             title="Abrir tabla por UEN")], start_collapsed=True)
                         ]), color='light'),

                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='total-producto'), color='#119DFF', type='dot', fullscreen=True),
                         dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                             id='tabla-producto',
                             style_header={'font-weight': 'bold', 'color': 'black',
                                           'text-align': 'center',
                                           'backgroundColor': 'lightgrey'},
                             style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                             style_table={'width': '750px'}),
                             title="Abrir tabla por producto"),
                             dbc.AccordionItem(dash_table.DataTable(
                                 id='tabla-cliente',
                                 style_header={'font-weight': 'bold', 'color': 'black',
                                               'text-align': 'center',
                                               'backgroundColor': 'lightgrey'},
                                 style_data={'color': 'black', 'text-align': 'center',
                                             'height': '30px'},
                                 style_table={'width': '750px'}),
                                 title="Abrir tabla por cliente"),
                             dbc.AccordionItem(dash_table.DataTable(
                                 id='tabla-internalizaciones',
                                 style_header={'font-weight': 'bold', 'color': 'black',
                                               'text-align': 'center',
                                               'backgroundColor': 'lightgrey'},
                                 style_data={'color': 'black', 'text-align': 'center',
                                             'height': '30px'},
                                 style_table={'width': '750px'}),
                                 title="Abrir tabla de internalizaciones")
                         ], start_collapsed=True)
                         ]), color='light'),

                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='total-motivos'), color='#119DFF', type='dot', fullscreen=True),
                         dbc.Accordion(dbc.AccordionItem(dash_table.DataTable(
                             id='tabla-motivos',
                             style_header={'font-weight': 'bold', 'color': 'black',
                                           'text-align': 'center',
                                           'backgroundColor': 'lightgrey'},
                             style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                             style_table={'width': '750px'}),
                             title="Abrir tabla"), start_collapsed=True)
                         ]), color='light'),

                    dbc.Card(dbc.CardBody([
                        html.H5("Rango de meses de antigüedad:", className='card-title'),
                        # dcc.Slider funciona igual que RangeSlider, pero el rango siempre empieza en el primer valor
                        dcc.Slider(id='histogram_slider', min=1, max=12, dots=True, step=1, value=1),
                        dcc.Loading(dcc.Graph(id='histograma'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion(dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-antiguedad',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'},
                            page_size=10),
                            title="Abrir tabla"), start_collapsed=True)
                    ]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-reemplazos'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion(dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-reemplazos',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla"), start_collapsed=True)
                    ]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='reemplazo_si'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion(dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-reemplazos_si',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla"), start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='reemplazo_no'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-reemplazos_no',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla"),
                            dbc.AccordionItem(dash_table.DataTable(
                                id='clientes-reemplazo_no',
                                style_header={'font-weight': 'bold', 'color': 'black',
                                              'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                style_table={'width': '750px'}),
                                title="Abrir tabla de No Reemplazos por cliente")
                        ], start_collapsed=True)
                    ]), color='light'),

                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='tiempo_reemplazo'), color='#119DFF', type='dot', fullscreen=True),
                         dbc.Accordion(dbc.AccordionItem(dash_table.DataTable(
                             id='tabla-tiempo_reemplazo',
                             style_header={'font-weight': 'bold', 'color': 'black',
                                           'text-align': 'center',
                                           'backgroundColor': 'lightgrey'},
                             style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                             style_table={'width': '750px'}),
                             title="Abrir tabla"), start_collapsed=True)
                         ]), color='light'),

                    dbc.Card(dbc.CardBody([
                        html.H6("Escoja un parámetro",
                                style={'color': 'black', 'font-family': 'Sans-serif'},
                                className='card-title'),
                        # dcc.Dropdown crea listas desplegables que podemos usar para filtrar por parámetro
                        dcc.Dropdown(
                            id='param_drop_rotacion',
                            multi=False,
                            clearable=False,
                            disabled=False,
                            style={'display': True},
                            placeholder='Rotación acumulada por',
                            options=[{'label': 'Rotación acumulada por ' + p, 'value': p} for p in parametros]),
                        dcc.Loading(dcc.Graph(id='parametros'), color='#119DFF', type='dot', fullscreen=True),
                        dcc.Loading(dcc.Graph(id='parametros_box'), color='#119DFF', type='dot', fullscreen=True)
                    ]), color='light')

                ], style={'width': '80%', 'margin-left': '0px'}),
                # Aquí los parámetros style ayudan a posicionar los elementos

                html.Div([
                    dbc.Card(dbc.CardBody([
                        dcc.Dropdown(
                            id='param_drop_rotacion_download',
                            multi=False,
                            clearable=True,
                            disabled=False,
                            style={'display': True},
                            placeholder='Rotación por',
                            options=[{'label': "Rotación por " + p, 'value': p} for p in parametros[:-1]]),
                        # Botón que activa la descarga de datos a Excel
                        dbc.Button("Descargar Excel", id="download_button", style={'width': '100%'}),
                        dcc.Download(id="download_rotacion")  # Permite exportar datos a Excel
                    ]), color='light'),
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '20%', 'margin-right': '0px'})
            ], style={'display': 'flex', 'margin-right': '0px'}),
        ], style={'display': 'flex', 'flex-direction': 'column'})
        tab_CI = html.Div([

            # Los Div son contenedores. Usarlos nos ayudará a posicionar los elementos como deseemos
            html.Div([html.H1("CAPACIDAD INSTALADA CHOUCAIR", style={'text-align': 'center',
                                                                     'font-family': 'Arial', 'font-weight': 'bold',
                                                                     'margin-bottom': '12px'})]),
            # El parámetro style sirve para asignar fuente, tamaño y alineación a los textos.
            # Más abajo verás que sirve también para psicionar elementos

            ##################################### DROPDOWNS DE FILTROS ############################################
            dbc.Row([
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='years_drop_CI',
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
                        id='clientes_drop_CI',
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
                        id='UEN_drop_CI',
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
                        id='paises_drop_CI',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='País analista',
                        options=[{'label': p, 'value': p} for p in paises]
                    ), body=True, color="light"
                )),
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='paises_cliente_drop_CI',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='País cliente',
                        options=[{'label': p, 'value': p} for p in paises]
                    ), body=True, color="light"
                )),
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='productos_drop_CI',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='Producto',
                        options=[{'label': p, 'value': p} for p in productos]
                    ), body=True, color="light"
                )),
            ]),

            # dbc.Card Crea un cuadro en el que posicionamos elementos. Ayuda visualemente a diferenciarlos
            dbc.Card([dcc.RangeSlider(id='meses_slider_CI', min=1, max=12, value=[1, 12], dots=True, step=1,
                                      marks={0: {'style': {'color': 'white'}},
                                             1: {'label': 'Enero', 'style': {'color': 'black', 'font-size': '16px'}},
                                             2: {'label': 'Febrero', 'style': {'color': 'black', 'font-size': '16px'}},
                                             3: {'label': 'Marzo', 'style': {'color': 'black', 'font-size': '16px'}},
                                             4: {'label': 'Abril', 'style': {'color': 'black', 'font-size': '16px'}},
                                             5: {'label': 'Mayo', 'style': {'color': 'black', 'font-size': '16px'}},
                                             6: {'label': 'Junio', 'style': {'color': 'black', 'font-size': '16px'}},
                                             7: {'label': 'Julio', 'style': {'color': 'black', 'font-size': '16px'}},
                                             8: {'label': 'Agosto', 'style': {'color': 'black', 'font-size': '16px'}},
                                             9: {'label': 'Septiembre',
                                                 'style': {'color': 'black', 'font-size': '16px'}},
                                             10: {'label': 'Octubre', 'style': {'color': 'black', 'font-size': '16px'}},
                                             11: {'label': 'Noviembre',
                                                  'style': {'color': 'black', 'font-size': '16px'}},
                                             12: {'label': 'Diciembre',
                                                  'style': {'color': 'black', 'font-size': '16px'}}})], body=True,
                     color='light'),

            html.Div([
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            dbc.Col(
                                [dcc.Loading(dcc.Graph(id="CI_tab"), color='#119DFF', type='dot', fullscreen=True)]),
                            dbc.Col(dash_table.DataTable(
                                id='tabla_inicial_CI',
                                style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                style_table={'width': '1000px'},
                                style_data_conditional=[{'if': {'column_id': 'CI FINAL'},
                                                         'backgroundColor': '#E6E6FA',
                                                         'fontWeight': 'bold',
                                                         'color': 'black'}]))
                        ], className="g-0")]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-pais_CI'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem([dash_table.DataTable(
                            id='tabla-pais_CI',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            dbc.Badge("Creció", color="#F9A09C", className="me-1", text_color="black"),
                            dbc.Badge("Decreció", color="#9CF9B3", className="me-1", text_color="black"),
                            dbc.Badge("Estable", color="#F9F69C", className="me-1", text_color="black"),
                        ],
                            title="Abrir tabla por País")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dbc.Accordion([
                            dbc.AccordionItem(dash_table.DataTable(
                                id='tabla-analistas_CI',
                                page_size=10,
                                style_header={'font-weight': 'bold', 'color': 'black',
                                              'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                style_table={'width': '750px'}),
                                title="Abrir tabla analistas Choucair")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='total-producto_CI'), color='#119DFF', type='dot', fullscreen=True),
                         dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                             id='tabla-producto_CI',
                             style_header={'font-weight': 'bold', 'color': 'black',
                                           'text-align': 'center',
                                           'backgroundColor': 'lightgrey'},
                             style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                             style_table={'width': '750px'}),
                             title="Abrir tabla por producto"),
                             dbc.AccordionItem(dash_table.DataTable(
                                 id='tabla-cliente_CI',
                                 style_header={'font-weight': 'bold', 'color': 'black',
                                               'text-align': 'center',
                                               'backgroundColor': 'lightgrey'},
                                 style_data={'color': 'black', 'text-align': 'center',
                                             'height': '30px'},
                                 style_table={'width': '750px'}),
                                 title="Abrir tabla por cliente")
                         ], start_collapsed=True)
                         ]), color='light'),
                    dbc.Row(dbc.Col(
                        dbc.Card(dcc.Loading(dcc.Graph(id="apoyo"), color='#119DFF', type='dot', fullscreen=True),
                                 body=True, color="light")))
                ], style={'width': '80%', 'margin-right': '0px'}),
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dcc.Dropdown(
                            id='param_drop_CI_download',
                            multi=False,
                            clearable=True,
                            disabled=False,
                            style={'display': True},
                            placeholder='Capacidad instalada por',
                            options=[{'label': 'CI por ' + p, 'value': p} for p in parametros[:-1]]),
                        dbc.Button("Descargar Excel", id="download_CI_button", style={'width': '100%'}),
                        dcc.Download(id="download_CI")
                    ]), color='light')
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '20%', 'margin-right': '0px'})
            ], style={'display': 'flex', 'margin-top': '0px'})

        ], style={'display': 'flex', 'flex-direction': 'column'})
        tab_solicitudes = html.Div([

            # Los Div son contenedores. Usarlos nos ayudará a posicionar los elementos como deseemos
            dbc.Row([html.H1("SOLICITUDES CHOUCAIR", style={'text-align': 'center', 'color': 'black',
                                                            'font-weight': 'bold', 'margin-bottom': '12px'})]),
            # El parámetro style sirve para asignar fuente, tamaño y alineación a los textos.
            # Más abajo verás que sirve también para psicionar elementos

            ##################################### DROPDOWNS DE FILTROS ############################################
            dbc.Row([
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='years_drop_Solicitudes',
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
                        id='clientes_drop_Solicitudes',
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
                        id='UEN_drop_Solicitudes',
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
                        id='paises_drop_Solicitudes',
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
                        id='productos_drop_Solicitudes',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='Producto',
                        options=[{'label': p, 'value': p} for p in productos]
                    ), body=True, color="light"
                )),
            ]),

            # dbc.Card Crea un cuadro en el que posicionamos elementos. Ayuda visualemente a diferenciarlos
            dbc.Card(
                [dcc.RangeSlider(id='meses_slider_Solicitudes', min=1, max=12, value=[1, 12], dots=True, step=1,
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
                                        12: {'label': 'Diciembre', 'style': {'color': 'black', 'font-size': '16px'}}})],
                body=True, color='light'),

            html.Div([
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="Solicitudes")]),
                            dbc.Col([dash_table.DataTable(
                                id='tabla_inicial_Solicitudes',
                                style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                style_table={'width': '1000px'})])
                        ], className="g-0")]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-pais_Solicitudes'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem([dash_table.DataTable(
                            id='tabla-pais_Solicitudes',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            dbc.Badge("Subió", color="#F9A09C", className="me-1", text_color="black"),
                            dbc.Badge("Bajó", color="#9CF9B3", className="me-1", text_color="black"),
                            dbc.Badge("Estable", color="#F9F69C", className="me-1", text_color="black"),
                        ],
                            title="Abrir tabla por País")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Graph(id='total-UEN_Solicitudes'),
                        dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-UEN_Solicitudes',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla por UEN")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-producto_Solicitudes'),
                                           dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                                               id='tabla-producto_Solicitudes',
                                               style_header={'font-weight': 'bold', 'color': 'black',
                                                             'text-align': 'center',
                                                             'backgroundColor': 'lightgrey'},
                                               style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                               style_table={'width': '750px'}),
                                               title="Abrir tabla por producto"),
                                               dbc.AccordionItem(dash_table.DataTable(
                                                   id='tabla-cliente_Solicitudes',
                                                   style_header={'font-weight': 'bold', 'color': 'black',
                                                                 'text-align': 'center',
                                                                 'backgroundColor': 'lightgrey'},
                                                   style_data={'color': 'black', 'text-align': 'center',
                                                               'height': '30px'},
                                                   style_table={'width': '750px'}),
                                                   title="Abrir tabla por cliente")
                                           ], start_collapsed=True)
                                           ]), color='light'),
                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-evento_Solicitudes')]), color='light'),
                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-producto_Solicitudes-sun')]), color='light'),
                ], style={'width': '80%', 'margin-right': '0px'}),
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dcc.Dropdown(
                            id='param_drop_Solicitudes_download_Solicitudes',
                            multi=False,
                            clearable=True,
                            disabled=False,
                            style={'display': True},
                            placeholder='Solicitudes por',
                            options=[{'label': 'Solicitudes por ' + p, 'value': p} for p in parametros[:-1]]),
                        dbc.Button("Descargar Excel", id="download_button_Solicitudes", style={'width': '100%'}),
                        dcc.Download(id="download_Solicitudes")
                    ]), color='light'),
                    dbc.Button("PowerBI Dashboard", id="BI_button_Solicitudes", style={'width': '100%'},
                               href='https://plotly.com/', target='_blank')
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '20%', 'margin-right': '0px'})
            ], style={'display': 'flex', 'margin-top': '0px'})

        ], style={'display': 'flex', 'flex-direction': 'column'})
        tab_Liberaciones = html.Div([

            # Los Div son contenedores. Usarlos nos ayudará a posicionar los elementos como deseemos
            dbc.Row([html.H1("LIBERACIONES CHOUCAIR", style={'text-align': 'center', 'color': 'black',
                                                             'font-weight': 'bold', 'margin-bottom': '12px'})]),
            # El parámetro style sirve para asignar fuente, tamaño y alineación a los textos.
            # Más abajo verás que sirve también para psicionar elementos

            ##################################### DROPDOWNS DE FILTROS ############################################
            dbc.Row([
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='years_drop_Liberaciones',
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
                        id='clientes_drop_Liberaciones',
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
                        id='UEN_drop_Liberaciones',
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
                        id='paises_drop_Liberaciones',
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
                        id='productos_drop_Liberaciones',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='Producto',
                        options=[{'label': p, 'value': p} for p in productos]
                    ), body=True, color="light"
                )),
            ]),

            # dbc.Card Crea un cuadro en el que posicionamos elementos. Ayuda visualemente a diferenciarlos
            dbc.Card(
                [dcc.RangeSlider(id='meses_slider_Liberaciones', min=1, max=12, value=[1, 12], dots=True, step=1,
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
                                        12: {'label': 'Diciembre', 'style': {'color': 'black', 'font-size': '16px'}}})],
                body=True, color='light'),

            html.Div([
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="Liberaciones")]),
                            dbc.Col([dash_table.DataTable(
                                id='tabla_inicial_Liberaciones',
                                style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                style_table={'width': '1000px'})])
                        ], className="g-0")]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Analistas disponibles y por liberar"),
                                dbc.Button("Analistas disponibles", id="button_analistas_disponibles",
                                           style={'width': '20%', 'margin-right': '5px'}),
                                dcc.Download(id="download_analistas_disponibles"),
                                dbc.Button("Analistas por liberar", id="button_analistas_por_liberar",
                                           style={'width': '20%'}),
                                dcc.Download(id="download_analistas_por_liberar"),
                                dash_table.DataTable(
                                    id='tabla_analistas_pais',
                                    style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                                  'backgroundColor': 'lightgrey'},
                                    style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                    style_table={'width': '1000px'})]),
                            dbc.Col([html.H5("Analistas liberados por cliente", style={"margin-top": "12px"}),
                                     dash_table.DataTable(
                                         id='tabla_analistas_cliente',
                                         page_size=10,
                                         style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                                       'backgroundColor': 'lightgrey'},
                                         style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                         style_table={'width': '1000px'})])
                        ], className="g-0")]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-pais_Liberaciones'), color='#119DFF', type='dot', fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem([dash_table.DataTable(
                            id='tabla-pais_Liberaciones',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            dbc.Badge("Subió", color="#F9A09C", className="me-1", text_color="black"),
                            dbc.Badge("Bajó", color="#9CF9B3", className="me-1", text_color="black"),
                            dbc.Badge("Estable", color="#F9F69C", className="me-1", text_color="black"),
                        ],
                            title="Abrir tabla por Pais")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Graph(id='total-UEN_Liberaciones'),
                        dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-UEN_Liberaciones',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla por UEN")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-producto_Liberaciones'),
                                           dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                                               id='tabla-producto_Liberaciones',
                                               style_header={'font-weight': 'bold', 'color': 'black',
                                                             'text-align': 'center',
                                                             'backgroundColor': 'lightgrey'},
                                               style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                               style_table={'width': '750px'}),
                                               title="Abrir tabla por producto"),
                                               dbc.AccordionItem(dash_table.DataTable(
                                                   id='tabla-cliente_Liberaciones',
                                                   style_header={'font-weight': 'bold', 'color': 'black',
                                                                 'text-align': 'center',
                                                                 'backgroundColor': 'lightgrey'},
                                                   style_data={'color': 'black', 'text-align': 'center',
                                                               'height': '30px'},
                                                   style_table={'width': '750px'}),
                                                   title="Abrir tabla por cliente")
                                           ], start_collapsed=True)
                                           ]), color='light'),
                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-evento_Liberaciones')]), color='light'),
                    dbc.Card(dbc.CardBody([dcc.Graph(id='total-producto-sun_Liberaciones')]), color='light'),
                ], style={'width': '80%', 'margin-right': '0px'}),
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dcc.Dropdown(
                            id='param_drop_Liberaciones_download',
                            multi=False,
                            clearable=True,
                            disabled=False,
                            style={'display': True},
                            placeholder='Liberaciones por',
                            options=[{'label': 'Liberaciones por ' + p, 'value': p} for p in parametros[:-1]]),
                        dbc.Button("Descargar Excel", id="download_button_Liberaciones", style={'width': '100%'}),
                        dcc.Download(id="download_Liberaciones")
                    ]), color='light'),
                    dbc.Button("PowerBI Dashboard", id="BI_button", style={'width': '100%'},
                               href='https://plotly.com/', target='_blank')
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '20%', 'margin-right': '0px'})
            ], style={'display': 'flex', 'margin-top': '0px'})

        ], style={'display': 'flex', 'flex-direction': 'column'})
        tab_contrataciones = html.Div([

            # Los Div son contenedores. Usarlos nos ayudará a posicionar los elementos como deseemos
            dbc.Row([html.H1("CONTRATACIONES CHOUCAIR", style={'text-align': 'center', 'color': 'black',
                                                               'font-weight': 'bold', 'margin-bottom': '12px'})]),
            # El parámetro style sirve para asignar fuente, tamaño y alineación a los textos.
            # Más abajo verás que sirve también para psicionar elementos

            ##################################### DROPDOWNS DE FILTROS ############################################
            dbc.Row([
                dbc.Col(dbc.Card(
                    dcc.Dropdown(
                        id='years_drop_Contrataciones',
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
                        id='clientes_drop_Contrataciones',
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
                        id='UEN_drop_Contrataciones',
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
                        id='paises_drop_Contrataciones',
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
                        id='productos_drop_Contrataciones',
                        multi=False,
                        clearable=True,
                        disabled=False,
                        style={'display': True},
                        placeholder='Producto',
                        options=[{'label': p, 'value': p} for p in productos]
                    ), body=True, color="light"
                )),
            ]),

            # dbc.Card Crea un cuadro en el que posicionamos elementos. Ayuda visualemente a diferenciarlos
            dbc.Card(
                [dcc.RangeSlider(id='meses_slider_Contrataciones', min=1, max=12, value=[1, 12], dots=True, step=1,
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
                                        12: {'label': 'Diciembre', 'style': {'color': 'black', 'font-size': '16px'}}})],
                body=True, color='light'),

            html.Div([
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            dbc.Col([dcc.Loading(dcc.Graph(id="Contrataciones"), color='#119DFF', type='dot',
                                                 fullscreen=True)]),
                            dbc.Col([dash_table.DataTable(
                                id='tabla_inicial_Contrataciones',
                                style_header={'font-weight': 'bold', 'color': 'black', 'text-align': 'center',
                                              'backgroundColor': 'lightgrey'},
                                style_data={'color': 'black', 'text-align': 'center', 'height': '25px'},
                                style_table={'width': '1000px'})])
                        ], className="g-0")]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-pais_Contrataciones'), color='#119DFF', type='dot',
                                    fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem([dash_table.DataTable(
                            id='tabla-pais_Contrataciones',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            dbc.Badge("Subió", color="#F9A09C", className="me-1", text_color="black"),
                            dbc.Badge("Bajó", color="#9CF9B3", className="me-1", text_color="black"),
                            dbc.Badge("Estable", color="#F9F69C", className="me-1", text_color="black"),
                        ],
                            title="Abrir tabla por País")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([
                        dcc.Loading(dcc.Graph(id='total-UEN_Contrataciones'), color='#119DFF', type='dot',
                                    fullscreen=True),
                        dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                            id='tabla-UEN_Contrataciones',
                            style_header={'font-weight': 'bold', 'color': 'black',
                                          'text-align': 'center',
                                          'backgroundColor': 'lightgrey'},
                            style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                            style_table={'width': '750px'}),
                            title="Abrir tabla por UEN")
                        ], start_collapsed=True)]), color='light'),

                    dbc.Card(dbc.CardBody([dcc.Loading(dcc.Graph(id='total-producto_Contrataciones'), color='#119DFF',
                                                       type='dot', fullscreen=True),
                                           dbc.Accordion([dbc.AccordionItem(dash_table.DataTable(
                                               id='tabla-producto_Contrataciones',
                                               style_header={'font-weight': 'bold', 'color': 'black',
                                                             'text-align': 'center',
                                                             'backgroundColor': 'lightgrey'},
                                               style_data={'color': 'black', 'text-align': 'center', 'height': '30px'},
                                               style_table={'width': '750px'}),
                                               title="Abrir tabla por producto"),
                                               dbc.AccordionItem(dash_table.DataTable(
                                                   id='tabla-cliente_Contrataciones',
                                                   style_header={'font-weight': 'bold', 'color': 'black',
                                                                 'text-align': 'center',
                                                                 'backgroundColor': 'lightgrey'},
                                                   style_data={'color': 'black', 'text-align': 'center',
                                                               'height': '30px'},
                                                   style_table={'width': '750px'}),
                                                   title="Abrir tabla por cliente")
                                           ], start_collapsed=True)
                                           ]), color='light'),
                    dbc.Card(dbc.CardBody(
                        [dcc.Loading(dcc.Graph(id='total-evento'), color='#119DFF', type='dot', fullscreen=True)]),
                             color='light'),
                    dbc.Card(dbc.CardBody([dcc.Loading(dcc.Graph(id='total-producto_Contrataciones-sun'),
                                                       color='#119DFF', type='dot', fullscreen=True)]), color='light'),
                ], style={'width': '80%', 'margin-right': '0px'}),
                html.Div([
                    dbc.Card(dbc.CardBody([
                        dcc.Dropdown(
                            id='param_drop_Contrataciones_download',
                            multi=False,
                            clearable=True,
                            disabled=False,
                            style={'display': True},
                            placeholder='Contrataciones por',
                            options=[{'label': 'Contrataciones por ' + p, 'value': p} for p in parametros[:-1]]),
                        dbc.Button("Descargar Excel", id="download_button_Contrataciones", style={'width': '100%'}),
                        dcc.Download(id="download_Contrataciones")
                    ]), color='light'),
                    dbc.Button("PowerBI Dashboard", id="BI_button_Contrataciones", style={'width': '100%'},
                               href='https://plotly.com/', target='_blank'),
                    dcc.RadioItems(['FINALIZADAS', 'EN FIRME'], 'FINALIZADAS', id="radio_option_Contrataciones")
                ], style={'display': 'flex', 'flex-direction': 'column', 'width': '20%', 'margin-right': '0px'})
            ], style={'display': 'flex', 'margin-top': '0px'})

        ], style={'display': 'flex', 'flex-direction': 'column'})

        app.layout = dbc.Tabs([
            dbc.Tab(tab_resumen, label="PVO"),
            dbc.Tab(tab_CI, label="Capacidad instalada"),
            dbc.Tab(tab_rotacion, label="Rotación"),
            dbc.Tab(tab_Liberaciones, label="Liberaciones"),
            dbc.Tab(tab_solicitudes, label="Solicitudes"),
            dbc.Tab(tab_contrataciones, label="Contrataciones")
        ])

        ##################### CALLBACKS DE TABLA PRINCIPAL ###############################
        @app.callback(Output('years_drop', 'value'),
                      Input('years_drop', 'options'))
        def get_year_value(years_drop):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop][-1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('tabla_rotacion', 'data'),
                      [Input('years_drop', 'value')],
                      [Input('meses_slider', 'value')],
                      [Input('clientes_drop', 'value')],
                      [Input('UEN_drop', 'value')],
                      [Input('paises_drop', 'value')],
                      [Input('productos_drop', 'value')])
        def scatter_chart(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df, _, _, _, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop,
                                              productos_drop)

            return df.to_dict('records')

        @app.callback(Output('CI', 'figure'),
                      [Input('years_drop', 'value')],
                      [Input('meses_slider', 'value')],
                      [Input('clientes_drop', 'value')],
                      [Input('UEN_drop', 'value')],
                      [Input('paises_drop', 'value')],
                      [Input('productos_drop', 'value')])
        def update_spikeline(years_drop, meses_slider, clientes_drop, UEN_drop, paises_drop, productos_drop):
            _, _, _, _, df_CI_tabla_spikeline, _ = tabla_resumen(years_drop, meses_slider, clientes_drop, UEN_drop,
                                                                 paises_drop, productos_drop)
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
            _, df_rotacion_tabla_spikeline, _, _, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop,
                                                                       UEN_drop, paises_drop, productos_drop)
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
            _, _, df_liberaciones_tabla_spikeline, _, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop,
                                                                           UEN_drop, paises_drop, productos_drop)
            df_spikeline = df_liberaciones_tabla_spikeline

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
            _, _, _, df_solicitudes_tabla_spikeline, _, _ = tabla_resumen(years_drop, meses_slider, clientes_drop,
                                                                          UEN_drop, paises_drop, productos_drop)
            df_spikeline = df_solicitudes_tabla_spikeline

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
            _, _, _, _, _, df_ingresos_tabla_spikeline = tabla_resumen(years_drop, meses_slider, clientes_drop,
                                                                       UEN_drop, paises_drop, productos_drop)
            df_spikeline = df_ingresos_tabla_spikeline

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
            df, df_rotacion, df_liberaciones, df_solicitudes, df_CI, df_ingresos = tabla_resumen(years_drop,
                                                                                                 meses_slider,
                                                                                                 clientes_drop,
                                                                                                 UEN_drop, paises_drop,
                                                                                                 productos_drop)
            CI = df[df['INDICADOR'] == 'CI'].iloc[:, 1:-1].T

            return {'data': [go.Bar(x=CI.index,
                                    y=CI[0],
                                    text=CI[0],
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
                    'layout': {'title': {'text': f'<b>RESUMEN DE INDICADORES DE OPERACIÓN</b>', 'font': {'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis2': {'overlaying': 'y',
                                          'side': 'right',
                                          'tickfont': {'size': 16, 'color': 'black'}}}}

        @app.callback(Output('tabla_buffer', 'data'),
                      [Input('UEN_drop', 'value')],
                      [Input('paises_drop', 'value')],
                      [Input('productos_drop', 'value')],
                      [Input('buffer_slider', 'value')])
        def scatter_chart(UEN_drop, pais, producto, buffer_slider):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df = backup(UEN_drop, buffer_slider)

            if pais is not None:
                df = df[df["Pais"] == pais]
            if producto is not None:
                df = df[df["Producto"] == producto]

            df["Producto"] = df["Producto"].astype(str)

            sum_row = pd.DataFrame(df.sum()).T
            df = pd.concat([df, sum_row], ignore_index=True)
            df.iloc[-1, 0] = "TOTAL"
            df.iloc[-1, 1] = ""

            return df.to_dict('records')

        @app.callback(Output('crecimiento', 'figure'),
                      [Input('years_drop', 'value')],
                      [Input('clientes_drop', 'value')],
                      [Input('UEN_drop', 'value')],
                      [Input('paises_drop', 'value')],
                      [Input('productos_drop', 'value')],
                      [Input('Estado_Liberaciones_drop', 'value')])
        def update_crecimiento(years_drop, clientes_drop, UEN_drop, paises_drop, productos_drop, option_crecimiento):
            df = crecimiento_real(years_drop, clientes_drop, UEN_drop, paises_drop, productos_drop, option_crecimiento)

            if df["Crecimiento"].sum() > 0:
                title = "CRECIMIENTO EN CLIENTE"
            elif df["Crecimiento"].sum() == 0:
                title = "SIN CRECIMIENTO EN CLIENTE"
            else:
                title = "DECRECIMIENTO EN CLIENTE"

            # Creamos la tendencia haciendo una regresión lineal simple
            X = df[['NumMes']]
            Y = df['Crecimiento']
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
            lm = LinearRegression()
            lm.fit(X_train, Y_train)
            Y_pred = lm.predict(X_test)
            #mse = mean_squared_error(Y_test, Y_pred)
            #r2 = r2_score(Y_test, Y_pred)

            df['Reg'] = lm.predict(X)


            #X_range = np.linspace(X.min(), X.max(), 9).reshape(-1, 1)
            #y_range = lm.predict(X_range)

            return {'data': [go.Bar(x=df["Mes"],
                                    y=df["Crecimiento"],
                                    text=df["Crecimiento"],
                                    texttemplate='%{text: .2s}',
                                    textposition='auto',
                                    marker_color=["#F9A09C" if (y <= 0) else "#9CF9B3" for y in df["Crecimiento"].values],
                                    name="Crecimiento"
                                    ),

                             go.Scatter(x=df["Mes"],
                                        y=df["Reg"],
                                        mode='lines',
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3},
                                        name='Regresión lineal')],
                    'layout': {'title': {'text': f'<b>{title}</b>', 'font':{'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont':{'size':16, 'color':'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}}}}

        @app.callback(Output('tabla_crecimiento', 'data'),
                      [Input('years_drop', 'value')],
                      [Input('clientes_drop', 'value')],
                      [Input('UEN_drop', 'value')],
                      [Input('paises_drop', 'value')],
                      [Input('productos_drop', 'value')],
                      [Input('Estado_Liberaciones_drop', 'value')])
        def scatter_chart(years_drop, clientes_drop, UEN_drop, paises_drop, productos_drop, option_crecimiento):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_crecimiento = crecimiento_real(years_drop, clientes_drop, UEN_drop, paises_drop, productos_drop,
                                              option_crecimiento)
            df_crecimiento.drop(['NumMes', 'Año'], axis=1, inplace=True)
            df_crecimiento = pd.pivot_table(df_crecimiento, columns="Mes", sort=False).reset_index()
            df_crecimiento.rename(columns={"index": "Indicador"}, inplace=True)

            return df_crecimiento.to_dict('records')

        ################################ CALLBACKS DE ROTACIÓN ########################################
        @app.callback(Output('years_drop_rotacion', 'value'),
                      Input('years_drop_rotacion', 'options'))
        def get_year_value(years_drop_rotacion):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop_rotacion][-1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('param_drop_rotacion', 'value'),
                      Input('param_drop_rotacion', 'options'))
        def get_param_value(param_drop_rotacion):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de parámetros"""
            return [p['value'] for p in param_drop_rotacion][0]  # el 0 indica que escoge el prmer parámetro de la lista

        @app.callback(Output('download_rotacion', 'data', ),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('param_drop_rotacion_download', 'value')],
                      [Input('download_button', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                        paises_drop_rotacion, productos_drop_rotacion, param_drop_rotacion_download, n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'download_button' in changed_id:
                df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                               clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                               productos_drop_rotacion)
                if param_drop_rotacion_download is not None:
                    df_chart = df_data_table(df_chart, f"{param_drop_rotacion_download}")
                    return dcc.send_data_frame(df_chart.to_excel,
                                               filename=f"Rotación por {param_drop_rotacion_download}.xlsx")
                else:
                    return dcc.send_data_frame(df_chart.to_excel, filename="Rotación.xlsx")

        @app.callback(Output('total-pais', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_data_chart(df_chart, "Pais")

            chart = [go.Bar(x=df_chart.index,
                            y=df_chart[col],
                            text=df_chart[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_chart.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN POR PAÍS Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-pais', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "Pais")

            return df_tabla.to_dict('records')

        @app.callback(Output('total-UEN', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_data_chart(df_chart, "UEN")

            chart = [go.Bar(x=df_chart.index,
                            y=df_chart[col],
                            text=df_chart[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_chart.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN POR UEN Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-UEN', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "UEN")
            return df_tabla.to_dict('records')

        @app.callback(Output('tabla-cliente', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "Cliente")

            return df_tabla.to_dict('records')

        @app.callback(Output('tabla-internalizaciones', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_chart[df_chart["CAUSAL / ESTRATEGIA"] == "Internalización"]
            df_tabla = df_data_table(df_chart, "Cliente")

            return df_tabla.to_dict('records')

        @app.callback(Output('tabla-internalizaciones', 'style_data_conditional'),
                      [Input('tabla-internalizaciones', 'data')])
        def update_cell_style(data):
            style_data_conditional = []
            if data is not None:
                for i, row in enumerate(data):
                    for col_name, cell_value in row.items():
                        if isinstance(cell_value, (int, float)) and col_name != "TOTAL":
                            if cell_value == 0:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#9CF9B3',
                                    'color': 'black'
                                })
                            elif cell_value > 0:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9A09C',
                                    'color': 'black'
                                })
            return style_data_conditional

        @app.callback(Output('total-producto', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_data_chart(df_chart, "Producto")

            chart = [go.Bar(x=df_chart.index,
                            y=df_chart[col],
                            text=df_chart[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_chart.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN POR PRODUCTO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-producto', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "Producto")

            return df_tabla.to_dict('records')

        @app.callback(Output('total-motivos', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_data_chart(df_chart, "Tipo de egreso")

            chart = [go.Scatter(x=df_chart.index,
                                y=df_chart[col],
                                mode='lines+markers+text',
                                text=df_chart[col],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': colors},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'color': colors, 'width': 2}},
                                name=col,
                                hovertemplate='%{y}') for col, colors in zip(df_chart.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN POR MOTIVO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                    }}

        @app.callback(Output('tabla-motivos', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "Tipo de egreso")

            return df_tabla.to_dict('records')

        @app.callback(Output('histograma', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('histogram_slider', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def histogram_chart(years_drop_rotacion, meses_slider_rotacion, histogram_slider, clientes_drop_rotacion,
                            UEN_drop_rotacion, paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función sigue en construcción. Será un histograma con la antigüedad de los colaboradores"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            datos1, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                         clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                         productos_drop_rotacion)

            datos1 = datos1[['Fecha Egreso', 'Fecha de ingreso']]
            datos1['Fecha Egreso'] = pd.to_datetime(datos1['Fecha Egreso'])
            datos1['Fecha de ingreso'] = pd.to_datetime(datos1['Fecha de ingreso'])
            datos1['Antigüedad'] = ((datos1['Fecha Egreso'] - datos1['Fecha de ingreso']) / pd.Timedelta(days=30.44)).astype(int)
            trace = go.Histogram(x=datos1['Antigüedad'],
                                 xbins=dict(start=min(datos1['Antigüedad']),
                                            end=max(datos1['Antigüedad']),
                                            size=histogram_slider),
                                 hovertemplate="Rango de meses: %{x}<br>Cantidad: %{y}",
                                 name="Antigüedad")

            layout = go.Layout(title={'text': f'<b>HISTOGRAMA DE ANTIGÜEDAD PARA {title}</b>', 'font': {'size': 26}},
                               xaxis={'title': 'MESES DE ANTIGÜEDAD', 'tickfont': {'size': 16, 'color': 'black'}},
                               yaxis={'title': 'CANTIDAD', 'tickfont': {'size': 16, 'color': 'black'}},
                               bargap=0.1)
            return {'data': [trace], 'layout': layout}

        @app.callback(Output('tabla-antiguedad', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('histogram_slider', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, histogram_slider, clientes_drop_rotacion,
                          UEN_drop_rotacion, paises_drop_rotacion,
                          productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            datos1, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                         clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                         productos_drop_rotacion)

            datos1 = datos1[['Fecha Egreso', 'Fecha de ingreso']]
            datos1['Fecha Egreso'] = pd.to_datetime(datos1['Fecha Egreso'])
            datos1['Fecha de ingreso'] = pd.to_datetime(datos1['Fecha de ingreso'])
            datos1['Meses de antigüedad'] = (
                    (datos1['Fecha Egreso'] - datos1['Fecha de ingreso']) / pd.Timedelta(days=30.44)).astype(int)
            datos_tabla = datos1[["Meses de antigüedad"]].value_counts().reset_index()
            datos_tabla.sort_values(by="Meses de antigüedad", inplace=True)
            datos_tabla.rename(columns={'count': "Cantidad"}, inplace=True)

            datos_tabla["Rango de meses"] = (datos_tabla["Meses de antigüedad"] // histogram_slider) * histogram_slider
            datos_tabla = datos_tabla.groupby("Rango de meses")["Cantidad"].sum().reset_index()
            if histogram_slider > 1:
                datos_tabla["Rango de meses"] = datos_tabla["Rango de meses"].apply(
                    lambda x: f'{x}-{x + histogram_slider - 1}')

            return datos_tabla.to_dict('records')

        @app.callback(Output('total-reemplazos', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_data_chart(df_chart, "Remplazo SI/NO")

            chart = [go.Scatter(x=df_chart.index,
                                y=df_chart[col],
                                mode='lines+markers+text',
                                text=df_chart[col],
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': colors},
                                marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                        'line': {'color': colors, 'width': 2}},
                                name=col,
                                hovertemplate='%{y}') for col, colors in zip(df_chart.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN POR REEMPLAZO SI/NO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                    }}

        @app.callback(Output('tabla-reemplazos', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_tabla = df_data_table(df_chart, "Remplazo SI/NO")

            return df_tabla.to_dict('records')

        @app.callback(Output('reemplazo_si', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_chart[df_chart["Remplazo SI/NO"] == 'SI']

            df_chart = df_chart.groupby(["NumMes", "Mes", 'CAUSAL / ESTRATEGIA'])["Cliente"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Cliente": "Rotación"}, inplace=True)

            df_chart_suma = df_chart.groupby(["NumMes"])["Rotación"].sum().reset_index()
            df_chart_suma.rename(columns={"Rotación": "Suma"}, inplace=True)

            df_chart_porcentaje = pd.merge(df_chart, df_chart_suma, on="NumMes", how='inner')
            df_chart_porcentaje["Porcentaje"] = df_chart_porcentaje["Rotación"] / df_chart_porcentaje["Suma"]
            df_chart_porcentaje = pd.pivot_table(df_chart_porcentaje, columns='CAUSAL / ESTRATEGIA',
                                                 values="Porcentaje", index="Mes", sort=False)

            df_chart = pd.pivot_table(df_chart, columns='CAUSAL / ESTRATEGIA', values="Rotación", index="Mes",
                                      sort=False)
            df_chart.fillna(0, inplace=True)

            chart = [go.Bar(x=df_chart.index,
                            y=df_chart[col],
                            text=round(df_chart_porcentaje[col] * 100),
                            texttemplate='%{text: .2s}%',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate=", ".join(['%{text}%', '%{y}'])) for col in df_chart.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>REEMPLAZOS PARA {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-reemplazos_si', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_chart[df_chart["Remplazo SI/NO"] == 'SI']
            df_tabla = df_data_table(df_chart, "CAUSAL / ESTRATEGIA")

            return df_tabla.to_dict('records')

        @app.callback(Output('reemplazo_no', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_chart[df_chart["Remplazo SI/NO"] == 'NO']

            df_chart_cliente = df_chart.groupby(["NumMes", "Mes", 'CAUSAL / ESTRATEGIA', "Cliente"])[
                "Producto"].count().reset_index()
            df_chart_cliente.rename(columns={"Producto": "Rotación"}, inplace=True)
            df_chart_cliente["Lista"] = df_chart_cliente.apply(
                lambda row: f'{row["Cliente"]}: {row["Rotación"]}<br>', axis=1)
            df_chart_cliente = df_chart_cliente.groupby(["NumMes", "Mes", 'CAUSAL / ESTRATEGIA'])[
                "Lista"].apply(list).reset_index()
            df_chart_cliente.sort_values(by="NumMes", ascending=True, inplace=True)

            df_chart = df_chart.groupby(["NumMes", "Mes", 'CAUSAL / ESTRATEGIA'])[
                "Cliente"].count().reset_index()
            df_chart.sort_values(by="NumMes", ascending=True, inplace=True)
            df_chart.rename(columns={"Cliente": "Rotación"}, inplace=True)

            df_chart_suma = df_chart.groupby(["NumMes"])["Rotación"].sum().reset_index()
            df_chart_suma.rename(columns={"Rotación": "Suma"}, inplace=True)

            df_chart_porcentaje = pd.merge(df_chart, df_chart_suma, on="NumMes", how='inner')
            df_chart_porcentaje["Porcentaje"] = df_chart_porcentaje["Rotación"] / df_chart_porcentaje["Suma"]
            df_chart_porcentaje = pd.pivot_table(df_chart_porcentaje, columns='CAUSAL / ESTRATEGIA',
                                                 values="Porcentaje", index="Mes", sort=False)

            df_chart = pd.pivot_table(df_chart, columns='CAUSAL / ESTRATEGIA', values="Rotación",
                                      index="Mes", sort=False)

            df_chart.fillna(0, inplace=True)

            chart = [go.Bar(x=df_chart.index,
                            y=df_chart[col],
                            text=round(df_chart_porcentaje[col] * 100),
                            texttemplate='%{text: .2s}%',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            customdata=df_chart_cliente.loc[df_chart_cliente["CAUSAL / ESTRATEGIA"] == col, "Lista"],
                            hovertemplate=", ".join(['%{text}%', '%{y}']) + "<br>%{customdata}",
                            ) for col, colors in zip(df_chart.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>NO REEMPLAZOS PARA {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'}}

        @app.callback(Output('tabla-reemplazos_no', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)
            df_chart = df_chart[df_chart["Remplazo SI/NO"] == 'NO']
            df_tabla = df_data_table(df_chart, "CAUSAL / ESTRATEGIA")

            return df_tabla.to_dict('records')

        @app.callback(Output('clientes-reemplazo_no', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_chart, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion,
                                           clientes_drop_rotacion, UEN_drop_rotacion, paises_drop_rotacion,
                                           productos_drop_rotacion)

            df_chart_cliente = df_chart.groupby(["NumMes", "Mes", 'CAUSAL / ESTRATEGIA', "Cliente"])[
                "Producto"].count().reset_index()
            df_chart_cliente.rename(columns={"Producto": "Rotación"}, inplace=True)
            df_chart_cliente.sort_values(by=["NumMes", "Rotación"], ascending=[True, False], inplace=True)
            df_chart_cliente.drop("NumMes", inplace=True, axis=1)
            return df_chart_cliente.to_dict('records')

        @app.callback(Output('tiempo_reemplazo', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')]
                      )
        def histogram_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                            paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función sigue en construcción. Será un histograma con la antigüedad de los colaboradores"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            datos, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion,
                                        UEN_drop_rotacion, paises_drop_rotacion, productos_drop_rotacion)
            datos = datos[["Tiempo para asignación"]].dropna()
            datos1 = datos[datos["Tiempo para asignación"] <= 5].value_counts().reset_index()
            datos1 = datos1[datos1["Tiempo para asignación"] >= 0]
            datos1["Tiempo para asignación"] = datos1["Tiempo para asignación"].apply(lambda x: str(int(x)) + ' días')
            datos1.rename(columns={"count": "Cantidad"}, inplace=True)
            datos2 = datos[datos["Tiempo para asignación"] > 5]
            datos2["Tiempo para asignación"] = '>5 días'
            datos2 = datos2["Tiempo para asignación"].value_counts().reset_index()
            datos2.rename(columns={"index": "Tiempo para asignación", "count": "Cantidad"},
                          inplace=True)
            datos3 = pd.concat([datos1, datos2], join="outer").reset_index()
            trace = go.Bar(x=datos3["Tiempo para asignación"],
                           y=datos3["Cantidad"],
                           name="Días para reemplazo",
                           hovertemplate='Días: %{x} <br>Cantidad: %{y}')

            layout = go.Layout(
                title={'text': f'<b>HISTOGRAMA DE TIEMPO DE REEMPLAZOS PARA {title}</b>', 'font': {'size': 26}},
                xaxis={'title': 'DÍAS PARA REEMPLAZO', 'tickfont': {'size': 16, 'color': 'black'}},
                yaxis={'title': 'CANTIDAD', 'tickfont': {'size': 16, 'color': 'black'}},
                bargap=0.1)
            return {'data': [trace], 'layout': layout}

        @app.callback(Output('tabla-tiempo_reemplazo', 'data'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('clientes_drop_rotacion', 'value')],
                      [Input('UEN_drop_rotacion', 'value')],
                      [Input('paises_drop_rotacion', 'value')],
                      [Input('productos_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion, UEN_drop_rotacion,
                          paises_drop_rotacion, productos_drop_rotacion, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            datos, title = data_filtros(df_rotacion, years_drop_rotacion, meses_slider_rotacion, clientes_drop_rotacion,
                                        UEN_drop_rotacion, paises_drop_rotacion, productos_drop_rotacion)
            datos = datos[["Tiempo para asignación"]].dropna()
            datos1 = datos[datos["Tiempo para asignación"] <= 5].value_counts().reset_index()
            datos1 = datos1[datos1["Tiempo para asignación"] >= 0]
            datos1["Tiempo para asignación"] = datos1["Tiempo para asignación"].apply(lambda x: str(int(x)) + ' días')
            datos1.rename(columns={"count": 'Cantidad'}, inplace=True)
            datos2 = datos[datos["Tiempo para asignación"] > 5]
            datos2["Tiempo para asignación"] = '>5 días'
            datos2 = datos2["Tiempo para asignación"].value_counts().reset_index()
            datos2.rename(columns={"index": "Tiempo para asignación", "count": "Cantidad"}, inplace=True)
            datos3 = pd.concat([datos1, datos2], join="outer").reset_index()
            datos3.drop('index', axis=1, inplace=True)
            datos3.rename(columns={"Tiempo para asignación": "Días para reemplazo"}, inplace=True)
            return datos3.to_dict('records')

        @app.callback(Output('parametros', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('param_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def pareto_chart(years_drop_rotacion, meses_slider_rotacion, param_drop_rotacion, n):
            """Esta función crea un gráfico de pareto con los egresos por cliente y su porcentaje acumulado
             en el año y rango de meses seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_filtrado = df_rotacion[(df_rotacion["Año"] == years_drop_rotacion) &
                                      (df_rotacion["NumMes"] >= meses_slider_rotacion[0]) &
                                      (df_rotacion["NumMes"] <= meses_slider_rotacion[1])]
            datos1 = df_filtrado[[f"{param_drop_rotacion}"]].value_counts().reset_index()
            datos1.rename(columns={'count': 'Conteo'}, inplace=True)
            datos1['cummpercentage'] = datos1['Conteo'].cumsum() * 100 / datos1['Conteo'].sum()
            return {'data': [go.Bar(x=datos1[f"{param_drop_rotacion}"],
                                    y=datos1["Conteo"],
                                    text=datos1['Conteo'],
                                    texttemplate='%{text: .2s}',
                                    textangle=0,
                                    textposition='auto',
                                    name=f"{param_drop_rotacion}",
                                    hoverinfo='text',
                                    hovertext=
                                    f'<b>{param_drop_rotacion}</b>:' + datos1[f"{param_drop_rotacion}"].astype(
                                        str) + '<br>' +
                                    '<b>Conteo</b>:' + [f'{x}' for x in datos1['Conteo']] + '<br>'
                                    ),
                             go.Scatter(x=datos1[f"{param_drop_rotacion}"],
                                        y=datos1['cummpercentage'],
                                        yaxis='y2',
                                        mode='lines+markers',
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'OrangeRed'},
                                        marker={'size': 10, 'symbol': 'circle', 'color': 'white',
                                                'line': {'width': 2, 'color': 'OrangeRed'}},
                                        name='Acumulado',
                                        hoverinfo='text',
                                        hovertext=
                                        f'<b>{param_drop_rotacion}</b>:' + datos1[f"{param_drop_rotacion}"].astype(
                                            str) + '<br>' +
                                        '<b>Acumulado</b>:' + [f'{round(x, 2)}%' for x in
                                                               datos1['cummpercentage']] + '<br>')],
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN ACUMULADA POR {param_drop_rotacion.upper()}</b>',
                                  'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 14, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis2': {
                            'overlaying': 'y',
                            'side': 'right',
                            'tickfont': {'size': 16, 'color': 'black'}
                        }
                    }}

        @app.callback(Output('parametros_box', 'figure'),
                      [Input('years_drop_rotacion', 'value')],
                      [Input('meses_slider_rotacion', 'value')],
                      [Input('param_drop_rotacion', 'value')],
                      [Input('interval', 'n_intervals')])
        def pareto_chart(years_drop_rotacion, meses_slider_rotacion, param_drop_rotacion, n):
            """Esta función crea un gráfico de pareto con los egresos por cliente y su porcentaje acumulado
             en el año y rango de meses seleccionado"""
            df_rotacion = df_rotacion_tab.copy()
            if n:
                df_rotacion = load_data_rotacion()
            df_filtrado = df_rotacion_tab[(df_rotacion["Año"] == years_drop_rotacion) &
                                          (df_rotacion["NumMes"] >= meses_slider_rotacion[0]) &
                                          (df_rotacion["NumMes"] <= meses_slider_rotacion[1])]
            df_filtrado = df_filtrado.groupby(["NumMes", "Mes", f"{param_drop_rotacion}"])[
                "Año"].count().reset_index()
            df_filtrado.sort_values(by="Año", ascending=True, inplace=True)
            df_filtrado.rename(columns={"Año": "Rotación"}, inplace=True)
            df_filtrado = pd.pivot_table(df_filtrado, columns=f"{param_drop_rotacion}", values="Rotación",
                                         index="Mes", sort=False)
            df_filtrado.fillna(0, inplace=True)
            return {'data': [go.Box(y=df_filtrado[col],
                                    name=col) for col in df_filtrado.columns],
                    'layout': {
                        'title': {'text': f'<b>ROTACIÓN ACUMULADA POR {param_drop_rotacion.upper()}</b>',
                                  'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 14, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}}
                    }}

        ################################# CALLBACKS DE CAPACIDAD INSTALADA ##############################
        @app.callback(Output('years_drop_CI', 'value'),
                      Input('years_drop_CI', 'options'))
        def get_year_value(years_drop_CI):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop_CI][-1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('download_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('param_drop_CI_download', 'value')],
                      [Input('download_CI_button', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                        paises_cliente_drop_CI, productos_drop_CI, param_drop_CI_download, n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'download_CI_button' in changed_id:
                df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                               paises_drop_CI, paises_cliente_drop_CI,
                                               productos_drop_CI)
                if param_drop_CI_download is not None:
                    df_CI = df_data_table_CI(df_CI, f"{param_drop_CI_download}")
                    return dcc.send_data_frame(df_CI.to_excel,
                                               filename=f"Capacidad instalada por {param_drop_CI_download}.xlsx")
                else:
                    return dcc.send_data_frame(df_CI.to_excel, filename="Capacidad instalada.xlsx")

        @app.callback(Output('CI_tab', 'figure'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def update_spikeline(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                             paises_cliente_drop_CI, productos_drop_CI, n):
            df_CI = df_CI_tab_raw.copy()
            if n:
                df_CI = load_data_CI()
            df_tabla, _ = tabla_resumen_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)
            return {'data': [go.Bar(x=df_tabla["Mes"],
                                    y=df_tabla["CI FINAL"],
                                    text=df_tabla["CI FINAL"],
                                    texttemplate='%{text: .2s}',
                                    textposition='auto',
                                    hovertemplate='%{x}, %{y}',
                                    name="CI FINAL"),
                             go.Scatter(x=df_tabla["Mes"],
                                        y=df_tabla["INGRESOS"],
                                        yaxis='y2',
                                        mode='lines+markers+text',
                                        text=df_tabla["INGRESOS"],
                                        texttemplate='%{text: .2s}',
                                        textfont={'family': 'Open Sans', 'color': 'black'},
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Red'},
                                        marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                                'line': {'color': 'Red', 'width': 2}},
                                        hovertemplate='%{x}, %{y}',
                                        name="INGRESOS"),
                             go.Scatter(x=df_tabla["Mes"],
                                        y=df_tabla["RETIROS"],
                                        yaxis='y2',
                                        mode='lines+markers+text',
                                        text=df_tabla["RETIROS"],
                                        texttemplate='%{text: .2s}',
                                        textfont={'family': 'Open Sans', 'color': 'black'},
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'green'},
                                        marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                                'line': {'color': 'green', 'width': 2}},
                                        hovertemplate='%{x}, %{y}',
                                        name="RETIROS")
                             ],
                    'layout': {'title': {'text': "<b>CAPACIDAD INSTALADA FINAL</b>", 'font': {'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis2': {
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'tickfont': {'size': 16, 'color': 'black'}
                               }
                               }}

        @app.callback(Output('tabla_inicial_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab_raw.copy()
            if n:
                df_CI = load_data_CI()
            df_tabla, _ = tabla_resumen_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)
            avg_row = pd.DataFrame(round(df_tabla.iloc[:, 1:].sum() / (len(df_tabla)))).T
            df_tabla = pd.concat([df_tabla, avg_row], ignore_index=True)
            df_tabla.iloc[-1, 0] = "PROMEDIO SIMPLE"
            df_tabla['% TASA DE ROTACIÓN'] = df_tabla['% TASA DE ROTACIÓN'].apply(lambda row: str(row) + '%')

            return df_tabla.to_dict('records')

        @app.callback(Output('total-pais_CI', 'figure'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)
            df_CI = df_data_chart_CI(df_CI, "Pais")

            chart = [go.Bar(x=df_CI.index,
                            y=df_CI[col],
                            text=df_CI[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_CI.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CAPACIDAD INSTALADA POR PAÍS Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-pais_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI,
                                           productos_drop_CI)
            df_CI_tabla = df_data_table_CI(df_CI, "Pais")
            df_CI_tabla["COMPARATIVO"] = df_CI_tabla.iloc[:, -1] - df_CI_tabla.iloc[:, 1]
            return df_CI_tabla.to_dict('records')

        @app.callback(Output('tabla-pais_CI', 'style_data_conditional'),
                      [Input('tabla-pais_CI', 'data')])
        def update_cell_style(data):
            style_data_conditional = []
            if data is not None:
                for i, row in enumerate(data):
                    columnas = [col_name for col_name, _ in row.items()][1:]
                    valores = [value for _, value in row.items()][1:]
                    contador = 0
                    for col_name, cell_value in row.items():
                        if isinstance(cell_value, (int, float)):
                            if col_name == columnas[0]:
                                contador = + 1
                            elif col_name == "COMPARATIVO":
                                if cell_value > 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#9CF9B3',
                                        'color': 'black'
                                    })
                                elif cell_value < 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9A09C',
                                        'color': 'black'
                                    })
                                else:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9F69C',
                                        'color': 'black'})
                            elif cell_value > valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#9CF9B3',
                                    'color': 'black'
                                })
                                contador = + 1
                            elif cell_value < valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9A09C',
                                    'color': 'black'
                                })
                                contador += 1
                            else:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9F69C',
                                    'color': 'black'
                                })
                                contador += 1

            return style_data_conditional


        @app.callback(Output('tabla-analistas_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()

            max_mes = max(df_CI[df_CI["Año"]==years_drop_CI]["NumMes"])
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, (max_mes, max_mes), clientes_drop_CI, None,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)
            df_CI = df_CI[df_CI["UEN"]=="CHOUCAIR"]
            df_CI_tabla = df_CI[["Nombre", "Ciudad del analista", "Cargo", "Producto", "Capacida origen"]]

            return df_CI_tabla.to_dict('records')

        @app.callback(Output('tabla-cliente_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)

            df_CI = df_CI.groupby(["NumMes", "Mes", "Cliente"])["Producto"].count().reset_index()
            df_CI.sort_values(by="NumMes", ascending=True, inplace=True)
            df_CI.rename(columns={"Producto": "Capacidad instalada"}, inplace=True)

            df_CI_tabla = pd.pivot_table(df_CI, columns="Mes", values="Capacidad instalada",
                                         index="Cliente", sort=False).reset_index()
            df_CI_tabla.fillna(0, inplace=True)
            df_CI_tabla["TOTAL"] = df_CI_tabla.iloc[:, 1:].sum(axis=1)
            df_CI_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_CI_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_CI_tabla.sum()).T
            df_CI_tabla = pd.concat([df_CI_tabla, sum_row], ignore_index=True)
            df_CI_tabla.iloc[-1, 0] = "TOTAL"

            return df_CI_tabla.to_dict('records')

        @app.callback(Output('total-producto_CI', 'figure'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)

            df_CI = df_CI.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_CI.sort_values(by="NumMes", ascending=True, inplace=True)
            df_CI.rename(columns={"Cliente": "Capacidad instalada"}, inplace=True)
            df_CI = pd.pivot_table(df_CI, columns="Producto", values="Capacidad instalada",
                                   index="Mes", sort=False)
            df_CI.fillna(0, inplace=True)

            chart = [go.Bar(x=df_CI.index,
                            y=df_CI[col],
                            text=df_CI[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_CI.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CAPACIDAD INSTALADA POR PRODUCTO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-producto_CI', 'data'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)

            df_CI = df_CI.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_CI.sort_values(by="NumMes", ascending=True, inplace=True)
            df_CI.rename(columns={"Cliente": "Capacidad instalada"}, inplace=True)

            df_CI_tabla = pd.pivot_table(df_CI, columns="Mes", values="Capacidad instalada",
                                         index="Producto", sort=False).reset_index()
            df_CI_tabla.fillna(0, inplace=True)
            df_CI_tabla["TOTAL"] = df_CI_tabla.iloc[:, 1:].sum(axis=1)
            df_CI_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_CI_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_CI_tabla.sum()).T
            df_CI_tabla = pd.concat([df_CI_tabla, sum_row], ignore_index=True)
            df_CI_tabla.iloc[-1, 0] = "TOTAL"

            return df_CI_tabla.to_dict('records')

        @app.callback(Output('apoyo', 'figure'),
                      [Input('years_drop_CI', 'value')],
                      [Input('meses_slider_CI', 'value')],
                      [Input('clientes_drop_CI', 'value')],
                      [Input('UEN_drop_CI', 'value')],
                      [Input('paises_drop_CI', 'value')],
                      [Input('paises_cliente_drop_CI', 'value')],
                      [Input('productos_drop_CI', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI, paises_drop_CI,
                          paises_cliente_drop_CI, productos_drop_CI, n):
            """Esta función crea un gráfico de líneas con la rotación del año seleccionado"""
            df_CI = df_CI_tab.copy()
            if n:
                df_CI = load_data_CI()
            df_CI, title = data_filtros_CI(df_CI, years_drop_CI, meses_slider_CI, clientes_drop_CI, UEN_drop_CI,
                                           paises_drop_CI, paises_cliente_drop_CI, productos_drop_CI)

            df_apoyo = df_CI[df_CI["Capacida origen"] != "CAPACIDAD INSTALADA"]
            df_apoyo = df_apoyo.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_apoyo.sort_values(by="NumMes", ascending=True, inplace=True)
            df_apoyo.rename(columns={"Cliente": "Apoyo"}, inplace=True)

            df_instalada = df_CI[(df_CI["Capacida origen"] == "CAPACIDAD INSTALADA") &
                                 (df_CI['Cliente'].str.contains('CHOUCAIR') == False)]
            df_instalada = df_instalada.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_instalada.sort_values(by="NumMes", ascending=True, inplace=True)
            df_instalada.rename(columns={"Cliente": "Instalada"}, inplace=True)

            df_asignacion = df_CI[(df_CI["Capacida origen"] == "CAPACIDAD INSTALADA") &
                                 (df_CI['Cliente'].str.contains('CHOUCAIR') == True)]
            df_asignacion = df_asignacion.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_asignacion.sort_values(by="NumMes", ascending=True, inplace=True)
            df_asignacion.rename(columns={"Cliente": "Esperando asignación"}, inplace=True)

            df_CI = df_CI.groupby(["NumMes", "Mes"])["Cliente"].count().reset_index()
            df_CI.sort_values(by="NumMes", ascending=True, inplace=True)
            df_CI.rename(columns={"Cliente": "Capacidad instalada"}, inplace=True)

            df_apoyo = df_apoyo.merge(df_CI, on=["NumMes", "Mes"], how="inner")
            df_apoyo["% Apoyo"] = df_apoyo.apply(lambda row: round(row["Apoyo"] / row["Capacidad instalada"], 2) * 100,
                                                 axis=1)

            chart = [go.Bar(x=df_CI["Mes"],
                            y=df_CI["Capacidad instalada"],
                            text=df_CI["Capacidad instalada"],
                            texttemplate='%{text: .2s}',
                            textposition='outside',
                            textangle=0,
                            name="Capacidad instalada",
                            hovertemplate='%{y}'),
                     go.Scatter(x=df_apoyo["Mes"],
                                y=df_apoyo["Apoyo"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_apoyo["Apoyo"],
                                texttemplate='%{text: .2s}',
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Green'},
                                marker={'size': 18, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'Green'}},
                                name='Capcidad de apoyo'),
                     go.Scatter(x=df_instalada["Mes"],
                                y=df_instalada["Instalada"],
                                #yaxis='y2',
                                mode='lines+markers+text',
                                text=df_instalada["Instalada"],
                                texttemplate='%{text: .2s}',
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'OrangeRed'},
                                marker={'size': 20, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'OrangeRed'}},
                                name='Capacidad facturable'),
                     go.Scatter(x=df_asignacion["Mes"],
                                y=df_asignacion["Esperando asignación"],
                                yaxis='y2',
                                mode='lines+markers+text',
                                text=df_asignacion["Esperando asignación"],
                                texttemplate='%{text: .2s}',
                                textfont={'family': 'Open Sans', 'color': 'black'},
                                line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Purple'},
                                marker={'size': 18, 'symbol': 'circle', 'color': 'white',
                                        'line': {'width': 2, 'color': 'Purple'}},
                                name='Esperando asignación')
                     ]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CAPACIDAD INSTALADA TOTAL Y DE APOYO {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack',
                        'yaxis2': {'overlaying': 'y',
                                   'side': 'right',
                                   'tickfont': {'size': 16, 'color': 'black'}}
                    }}

        ################################# CALLBACKS DE SOLICITUDES ###########################
        @app.callback(Output('years_drop_Solicitudes', 'value'),
                      Input('years_drop_Solicitudes', 'options'))
        def get_year_value(years_drop_Solicitudes):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop_Solicitudes][-1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('download_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('param_drop_Solicitudes_download_Solicitudes', 'value')],
                      [Input('download_button_Solicitudes', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                        UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes,
                        param_drop_Solicitudes_download, n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()

            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'download_button_Solicitudes' in changed_id:
                df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                                 meses_slider_Solicitudes,
                                                                 clientes_drop_Solicitudes, UEN_drop_Solicitudes,
                                                                 paises_drop_Solicitudes,
                                                                 productos_drop_Solicitudes)
                if param_drop_Solicitudes_download is not None:
                    df_Solicitudes = df_data_table_Solicitudes(df_Solicitudes, f"{param_drop_Solicitudes_download}")
                    return dcc.send_data_frame(df_Solicitudes.to_excel,
                                               filename=f"Solicitudes por {param_drop_Solicitudes_download}.xlsx")
                else:
                    return dcc.send_data_frame(df_Solicitudes.to_excel, filename="Solicitudes.xlsx")

        @app.callback(Output('Solicitudes', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def update_spikeline(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                             UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            df_Solicitudes = df_tabla_inicial_Solicitudes.copy()
            if n:
                df_Solicitudes = load_data_inicial_Solicitudes()
            df_Solicitudes = df_Solicitudes[(df_Solicitudes["Año"] == years_drop_Solicitudes) &
                                            (df_Solicitudes["NumMes"] >= meses_slider_Solicitudes[0]) &
                                            (df_Solicitudes["NumMes"] <= meses_slider_Solicitudes[1])]

            title_list = []
            if clientes_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Cliente"] == clientes_drop_Solicitudes]
                title_list.append(clientes_drop_Solicitudes)

            if UEN_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["UEN"] == UEN_drop_Solicitudes]
                title_list.append(UEN_drop_Solicitudes)

            if paises_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Pais"] == paises_drop_Solicitudes]
                title_list.append(paises_drop_Solicitudes)

            if productos_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Producto"] == productos_drop_Solicitudes]
                title_list.append(productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "EstadoSolicitudCO"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes = pd.pivot_table(df_Solicitudes, columns="EstadoSolicitudCO", values="Solicitudes",
                                            index="Mes", sort=False)
            df_Solicitudes.fillna(0, inplace=True)
            df_Solicitudes["TOTAL"] = df_Solicitudes.iloc[:, :].sum(axis=1)

            chart = [go.Bar(x=df_Solicitudes.index,
                            y=df_Solicitudes[col],
                            text=df_Solicitudes[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Solicitudes.columns[:-1]]
            scatter_chart = go.Scatter(x=df_Solicitudes.index,
                                       y=df_Solicitudes["TOTAL"],
                                       mode='lines+markers+text',
                                       text=df_Solicitudes["TOTAL"],
                                       texttemplate='%{text: .2s}',
                                       textfont={'family': 'Open Sans', 'color': 'black'},
                                       line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Green'},
                                       marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                               'line': {'width': 2, 'color': 'Green'}},
                                       name='TOTAL')

            chart.append(scatter_chart)

            return {'data': chart,
                    'layout': {'title': {'text': "<b>ESTADO DE SOLICITUDES</b>", 'font': {'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}}
                               }}

        @app.callback(Output('tabla_inicial_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_tabla_inicial_Solicitudes.copy()
            if n:
                df_Solicitudes = load_data_inicial_Solicitudes()
            df_Solicitudes = df_Solicitudes[(df_Solicitudes["Año"] == years_drop_Solicitudes) &
                                            (df_Solicitudes["NumMes"] >= meses_slider_Solicitudes[0]) &
                                            (df_Solicitudes["NumMes"] <= meses_slider_Solicitudes[1])]

            title_list = []
            if clientes_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Cliente"] == clientes_drop_Solicitudes]
                title_list.append(clientes_drop_Solicitudes)

            if UEN_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["UEN"] == UEN_drop_Solicitudes]
                title_list.append(UEN_drop_Solicitudes)

            if paises_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Pais"] == paises_drop_Solicitudes]
                title_list.append(paises_drop_Solicitudes)

            if productos_drop_Solicitudes is not None:
                df_Solicitudes = df_Solicitudes[df_Solicitudes["Producto"] == productos_drop_Solicitudes]
                title_list.append(productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "EstadoSolicitudCO"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes", "EstadoSolicitudCO": "Estado"}, inplace=True)
            df_Solicitudes_tabla = pd.pivot_table(df_Solicitudes, columns="Mes", values="Solicitudes",
                                                  index="Estado", sort=False).reset_index()
            df_Solicitudes_tabla.fillna(0, inplace=True)
            df_Solicitudes_tabla["TOTAL"] = df_Solicitudes_tabla.iloc[:, 1:].sum(axis=1)
            df_Solicitudes_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_Solicitudes_tabla.sum()).T
            df_Solicitudes_tabla = pd.concat([df_Solicitudes_tabla, sum_row], ignore_index=True)
            df_Solicitudes_tabla.iloc[-1, 0] = "TOTAL"

            return df_Solicitudes_tabla.to_dict('records')

        @app.callback(Output('total-pais_Solicitudes', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes = pd.pivot_table(df_Solicitudes, columns="Pais", values="Solicitudes",
                                            index="Mes", sort=False)
            df_Solicitudes.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Solicitudes.index,
                            y=df_Solicitudes[col],
                            text=df_Solicitudes[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Solicitudes.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>SOLICITUDES POR PAÍS Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-pais_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)

            df_Solicitudes_tabla = pd.pivot_table(df_Solicitudes, columns="Mes", values="Solicitudes",
                                                  index="Pais", sort=False).reset_index()
            df_Solicitudes_tabla.fillna(0, inplace=True)
            df_Solicitudes_tabla["TOTAL"] = df_Solicitudes_tabla.iloc[:, 1:].sum(axis=1)
            df_Solicitudes_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Solicitudes_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Solicitudes_tabla.sum()).T
            df_Solicitudes_tabla = pd.concat([df_Solicitudes_tabla, sum_row], ignore_index=True)
            df_Solicitudes_tabla.iloc[-1, 0] = "TOTAL"
            df_Solicitudes_tabla["COMPARATIVO"] = df_Solicitudes_tabla.iloc[:, -1] - df_Solicitudes_tabla.iloc[:, 1]
            return df_Solicitudes_tabla.to_dict('records')

        @app.callback(Output('tabla-pais_Solicitudes', 'style_data_conditional'),
                      [Input('tabla-pais_Solicitudes', 'data')])
        def update_cell_style(data):
            style_data_conditional = []
            if data is not None:
                for i, row in enumerate(data):
                    columnas = [col_name for col_name, _ in row.items()][1:]
                    valores = [value for _, value in row.items()][1:]
                    contador = 0
                    for col_name, cell_value in row.items():
                        if isinstance(cell_value, (int, float)):
                            if col_name == columnas[0]:
                                contador = + 1
                            elif col_name == "COMPARATIVO":
                                if cell_value > 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#9CF9B3',
                                        'color': 'black'
                                    })
                                elif cell_value < 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9A09C',
                                        'color': 'black'
                                    })
                                else:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9F69C',
                                        'color': 'black'})
                            elif cell_value > valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#9CF9B3',
                                    'color': 'black'
                                })
                                contador = + 1
                            elif cell_value < valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9A09C',
                                    'color': 'black'
                                })
                                contador += 1
                            else:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9F69C',
                                    'color': 'black'
                                })
                                contador += 1

            return style_data_conditional

        @app.callback(Output('total-UEN_Solicitudes', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes = pd.pivot_table(df_Solicitudes, columns="UEN", values="Solicitudes",
                                            index="Mes", sort=False)
            df_Solicitudes.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Solicitudes.index,
                            y=df_Solicitudes[col],
                            text=df_Solicitudes[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Solicitudes.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>SOLICITUDES POR UEN Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-UEN_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)

            df_Solicitudes_tabla = pd.pivot_table(df_Solicitudes, columns="Mes", values="Solicitudes",
                                                  index="UEN", sort=False).reset_index()
            df_Solicitudes_tabla.fillna(0, inplace=True)
            df_Solicitudes_tabla["TOTAL"] = df_Solicitudes_tabla.iloc[:, 1:].sum(axis=1)
            df_Solicitudes_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Solicitudes_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Solicitudes_tabla.sum()).T
            df_Solicitudes_tabla = pd.concat([df_Solicitudes_tabla, sum_row], ignore_index=True)
            df_Solicitudes_tabla.iloc[-1, 0] = "TOTAL"

            return df_Solicitudes_tabla.to_dict('records')

        @app.callback(Output('tabla-cliente_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "Cliente"])["Producto"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Producto": "Solicitudes"}, inplace=True)

            df_Solicitudes_tabla = pd.pivot_table(df_Solicitudes, columns="Mes", values="Solicitudes",
                                                  index="Cliente", sort=False).reset_index()
            df_Solicitudes_tabla.fillna(0, inplace=True)
            df_Solicitudes_tabla["TOTAL"] = df_Solicitudes_tabla.iloc[:, 1:].sum(axis=1)
            df_Solicitudes_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Solicitudes_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Solicitudes_tabla.sum()).T
            df_Solicitudes_tabla = pd.concat([df_Solicitudes_tabla, sum_row], ignore_index=True)
            df_Solicitudes_tabla.iloc[-1, 0] = "TOTAL"

            return df_Solicitudes_tabla.to_dict('records')

        @app.callback(Output('total-producto_Solicitudes', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes = pd.pivot_table(df_Solicitudes, columns="Producto", values="Solicitudes",
                                            index="Mes", sort=False)
            df_Solicitudes.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Solicitudes.index,
                            y=df_Solicitudes[col],
                            text=df_Solicitudes[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Solicitudes.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>SOLICITUDES POR PRODUCTO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-producto_Solicitudes', 'data'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)

            df_Solicitudes_tabla = pd.pivot_table(df_Solicitudes, columns="Mes", values="Solicitudes",
                                                  index="Producto", sort=False).reset_index()
            df_Solicitudes_tabla.fillna(0, inplace=True)
            df_Solicitudes_tabla["TOTAL"] = df_Solicitudes_tabla.iloc[:, 1:].sum(axis=1)
            df_Solicitudes_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Solicitudes_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Solicitudes_tabla.sum()).T
            df_Solicitudes_tabla = pd.concat([df_Solicitudes_tabla, sum_row], ignore_index=True)
            df_Solicitudes_tabla.iloc[-1, 0] = "TOTAL"

            return df_Solicitudes_tabla.to_dict('records')

        @app.callback(Output('total-evento_Solicitudes', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["NumMes", "Mes", "EventoSolicitud"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes = pd.pivot_table(df_Solicitudes, columns="EventoSolicitud", values="Solicitudes",
                                            index="Mes", sort=False)
            df_Solicitudes.fillna(0, inplace=True)

            chart = chart = [go.Scatter(x=df_Solicitudes.index,
                                        y=df_Solicitudes[col],
                                        mode='lines+markers+text',
                                        text=df_Solicitudes[col],
                                        textfont={'family': 'Open Sans', 'color': 'black'},
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': colors},
                                        marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                                'line': {'color': colors, 'width': 2}},
                                        name=col,
                                        hovertemplate='%{y}') for col, colors in zip(df_Solicitudes.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>EVENTO DE LA SOLICITUD PARA {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('total-producto_Solicitudes-sun', 'figure'),
                      [Input('years_drop_Solicitudes', 'value')],
                      [Input('meses_slider_Solicitudes', 'value')],
                      [Input('clientes_drop_Solicitudes', 'value')],
                      [Input('UEN_drop_Solicitudes', 'value')],
                      [Input('paises_drop_Solicitudes', 'value')],
                      [Input('productos_drop_Solicitudes', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Solicitudes, meses_slider_Solicitudes, clientes_drop_Solicitudes,
                          UEN_drop_Solicitudes, paises_drop_Solicitudes, productos_drop_Solicitudes, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_Solicitudes = df_Solicitudes_tab.copy()
            if n:
                df_Solicitudes = load_data_Solicitudes()
            df_Solicitudes, title = data_filtros_Solicitudes(df_Solicitudes, years_drop_Solicitudes,
                                                             meses_slider_Solicitudes, clientes_drop_Solicitudes,
                                                             UEN_drop_Solicitudes, paises_drop_Solicitudes,
                                                             productos_drop_Solicitudes)

            df_Solicitudes = df_Solicitudes.groupby(["Pais", "UEN", "Producto"])[
                "Cliente"].count().reset_index()
            df_Solicitudes.rename(columns={"Cliente": "Solicitudes"}, inplace=True)
            df_Solicitudes['Porcentaje'] = df_Solicitudes['Solicitudes'].apply(
                lambda row: round(row * 100 / df_Solicitudes["Solicitudes"].sum()))

            chart = px.sunburst(df_Solicitudes, path=["Pais", "UEN", "Producto"], values="Porcentaje", maxdepth=2)
            chart.update_layout(title={"text": "SOLICITUDES GENERAL",
                                       'font': {'color': 'black', 'size': 26, 'family': 'Arial'},
                                       'x': 0.5, 'y': 0.95,
                                       'xanchor': 'center', 'yanchor': 'top'},
                                legend_title="Legend Title",
                                width=800,
                                height=600)

            return chart

        ################################ CALLBACKS DE LIBERACIONES ##########################################
        @app.callback(Output('years_drop_Liberaciones', 'value'),
                      Input('years_drop_Liberaciones', 'options'))
        def get_year_value(years_drop_Liberaciones):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop_Liberaciones][
                -1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('download_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('param_drop_Liberaciones_download', 'value')],
                      [Input('download_button_Liberaciones', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                        UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones,
                        param_drop_Liberaciones_download, n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'download_button_Liberaciones' in changed_id:
                df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                                   meses_slider_Liberaciones,
                                                                   clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                                   paises_drop_Liberaciones,
                                                                   productos_drop_Liberaciones)
                if param_drop_Liberaciones_download is not None:
                    df_Liberaciones = df_data_table_Liberaciones(df_Liberaciones, f"{param_drop_Liberaciones_download}")
                    return dcc.send_data_frame(df_Liberaciones.to_excel,
                                               filename=f"Liberaciones por {param_drop_Liberaciones_download}.xlsx")
                else:
                    return dcc.send_data_frame(df_Liberaciones.to_excel, filename="Liberaciones.xlsx")

        @app.callback(Output('Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def update_spikeline(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                             UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            df_tabla_inicial = df_tabla_inicial_Liberaciones.copy()
            if n:
                df_tabla_inicial = load_data_inicial_Liberaciones()

            df_Liberaciones = df_tabla_inicial[
                (df_tabla_inicial["Año"] == years_drop_Liberaciones) &
                (df_tabla_inicial["NumMes"] >= meses_slider_Liberaciones[0]) &
                (df_tabla_inicial["NumMes"] <= meses_slider_Liberaciones[1])]

            title_list = []
            if clientes_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Cliente"] == clientes_drop_Liberaciones]
                title_list.append(clientes_drop_Liberaciones)

            if UEN_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["UEN"] == UEN_drop_Liberaciones]
                title_list.append(UEN_drop_Liberaciones)

            if paises_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Pais"] == paises_drop_Liberaciones]
                title_list.append(paises_drop_Liberaciones)

            if productos_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Producto"] == productos_drop_Liberaciones]
                title_list.append(productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "EstadoSolicitud"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones = pd.pivot_table(df_Liberaciones, columns="EstadoSolicitud", values="Liberaciones",
                                             index="Mes", sort=False)
            df_Liberaciones.fillna(0, inplace=True)
            df_Liberaciones["TOTAL"] = df_Liberaciones.iloc[:, :].sum(axis=1)

            chart = [go.Bar(x=df_Liberaciones.index,
                            y=df_Liberaciones[col],
                            text=df_Liberaciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Liberaciones.columns[:-1]]
            scatter_chart = go.Scatter(x=df_Liberaciones.index,
                                       y=df_Liberaciones["TOTAL"],
                                       mode='lines+markers+text',
                                       text=df_Liberaciones["TOTAL"],
                                       texttemplate='%{text: .2s}',
                                       textfont={'family': 'Open Sans', 'color': 'black'},
                                       line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Green'},
                                       marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                               'line': {'width': 2, 'color': 'Green'}},
                                       name='TOTAL')

            chart.append(scatter_chart)

            return {'data': chart,
                    'layout': {'title': {'text': "<b>ESTADO DE LIBERACIONES</b>", 'font': {'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}}
                               }}

        @app.callback(Output('tabla_inicial_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_tabla_inicial = df_tabla_inicial_Liberaciones.copy()
            if n:
                df_tabla_inicial = load_data_inicial_Liberaciones()

            df_Liberaciones = df_tabla_inicial[
                (df_tabla_inicial["Año"] == years_drop_Liberaciones) &
                (df_tabla_inicial["NumMes"] >= meses_slider_Liberaciones[0]) &
                (df_tabla_inicial["NumMes"] <= meses_slider_Liberaciones[1])]

            title_list = []
            if clientes_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Cliente"] == clientes_drop_Liberaciones]
                title_list.append(clientes_drop_Liberaciones)

            if UEN_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["UEN"] == UEN_drop_Liberaciones]
                title_list.append(UEN_drop_Liberaciones)

            if paises_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Pais"] == paises_drop_Liberaciones]
                title_list.append(paises_drop_Liberaciones)

            if productos_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Producto"] == productos_drop_Liberaciones]
                title_list.append(productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "EstadoSolicitud"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones", "EstadoSolicitud": "Estado"}, inplace=True)
            df_Liberaciones_tabla = pd.pivot_table(df_Liberaciones, columns="Mes", values="Liberaciones",
                                                   index="Estado", sort=False).reset_index()
            df_Liberaciones_tabla.fillna(0, inplace=True)
            df_Liberaciones_tabla["TOTAL"] = df_Liberaciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Liberaciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_Liberaciones_tabla.sum()).T
            df_Liberaciones_tabla = pd.concat([df_Liberaciones_tabla, sum_row], ignore_index=True)
            df_Liberaciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Liberaciones_tabla.to_dict('records')

        @app.callback(Output('tabla_analistas_pais', 'data'),
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                          paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_disponibles_ = df_disponibles.copy()
            df_disponibles_.loc[df_disponibles["Producto"] == "MIGRACIÓN", "Producto"] = 'MIGRACION'
            df_disponibles_.loc[df_disponibles["Pais"] == "PERÚ", "Pais"] = 'PERU'

            if n:
                df_disponibles_ = load_disponibles()

            df_pendientes = df_liberaciones[(df_liberaciones["EstadoSolicitud"] == "ABIERTO") |
                                            (df_liberaciones["EstadoSolicitud"] == "EN PROCESO")]

            df_vacaciones["Identificacion"] = df_vacaciones["Identificacion"].astype(str)
            df_disponibles_["Identificación"] = df_disponibles_["Identificación"].astype(str)
            df_disponibles_vacaciones = df_disponibles_.merge(df_vacaciones, left_on="Identificación", right_on="Identificacion", how="left")
            #hoy = datetime.today()
            hoy = datetime(2023, 9, 10)
            df_disponibles_vacaciones["Vacaciones"]=df_disponibles_vacaciones.apply(lambda row: 'SI' if (row["Fecha_inicio_vacaciones"] <= hoy and row["Fecha_fin_vacaciones"] >= hoy) else 'NO', axis=1)
            df_disponibles_asignacion=df_disponibles_vacaciones[df_disponibles_vacaciones["Vacaciones"]=="NO"]
            df_disponibles_en_vacaciones=df_disponibles_vacaciones[df_disponibles_vacaciones["Vacaciones"]=="SI"]

            if clientes_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Ultimo Cliente"] == clientes_drop_Liberaciones]
                df_pendientes = df_pendientes[df_pendientes["Cliente"] == clientes_drop_Liberaciones]
            if UEN_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["UEN"] == UEN_drop_Liberaciones]
                df_pendientes = df_pendientes[df_pendientes["UEN"] == UEN_drop_Liberaciones]
            if paises_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Pais"] == paises_drop_Liberaciones]
                df_pendientes = df_pendientes[df_pendientes["Pais"] == paises_drop_Liberaciones]
            if productos_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Producto"] == productos_drop_Liberaciones]
                df_pendientes = df_pendientes[df_pendientes["Producto"] == productos_drop_Liberaciones]

            df_disponibles_asignacion = df_disponibles_asignacion.groupby(["Pais", "Producto"])["Analista"].count().reset_index()
            df_disponibles_asignacion.rename(columns={"Analista": "Esperando asignación"}, inplace=True)
            df_disponibles_en_vacaciones = df_disponibles_en_vacaciones.groupby(["Pais", "Producto"])[
                "Analista"].count().reset_index()
            df_disponibles_en_vacaciones.rename(columns={"Analista": "En vacaciones"}, inplace=True)

            df_disponibles_ = df_disponibles_asignacion.merge(df_disponibles_en_vacaciones, on=["Pais", "Producto"], how="outer").fillna(0)

            df_pendientes = df_pendientes.groupby(["Pais", "Producto"])["Contador"].sum().reset_index()
            df_pendientes.rename(columns={"Contador": "Pendientes de liberación"}, inplace=True)


            df1 = df_disponibles_.merge(df_pendientes, on=["Pais", "Producto"], how="outer").fillna(0)
            df1["Total"] = df1["Pendientes de liberación"] + df1["En vacaciones"] + df1["Pendientes de liberación"]

            sum_row = pd.DataFrame(df1.sum()).T
            df1 = pd.concat([df1, sum_row], ignore_index=True)
            df1.iloc[-1, 0] = "TOTAL"
            df1.iloc[-1, 1] = ""

            return df1.to_dict('records')

        @app.callback(Output('download_analistas_disponibles', 'data'),
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('button_analistas_disponibles', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                          paises_drop_Liberaciones, productos_drop_Liberaciones, n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_disponibles_ = df_disponibles.copy()

            if n:
                df_disponibles_ = load_disponibles()

            if clientes_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Ultimo Cliente"] == clientes_drop_Liberaciones]

            if UEN_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["UEN"] == UEN_drop_Liberaciones]

            if paises_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Pais"] == paises_drop_Liberaciones]

            if productos_drop_Liberaciones is not None:
                df_disponibles_ = df_disponibles_[df_disponibles_["Producto"] == productos_drop_Liberaciones]

            df_vacaciones["Identificacion"] = df_vacaciones["Identificacion"].astype(str)
            df_disponibles_["Identificación"] = df_disponibles_["Identificación"].astype(str)
            df_disponibles_vacaciones = df_disponibles_.merge(df_vacaciones, left_on="Identificación",
                                                              right_on="Identificacion", how="left")
            # hoy = datetime.today()
            hoy = datetime(2023, 9, 10)
            df_disponibles_vacaciones["Vacaciones"] = df_disponibles_vacaciones.apply(lambda row: 'SI' if (
                    row["Fecha_inicio_vacaciones"] <= hoy and row["Fecha_fin_vacaciones"] >= hoy) else 'NO', axis=1)

            df_disponibles_vacaciones = df_disponibles_vacaciones.merge(df_panorama[["Cedula", "Ciudad residencia"]],
                                                                        left_on='Identificación', right_on="Cedula",
                                                                        how='left')
            df_disponibles_vacaciones = df_disponibles_vacaciones[["Analista", "Ultimo cliente", "UEN",
                                                                   "MotivoLiberacion", "dtFechaLiberacion", "Producto",
                                                                   "Ciudad residencia", "Vacaciones"]]

            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            if 'button_analistas_disponibles' in changed_id:
                return dcc.send_data_frame(df_disponibles_vacaciones.to_excel,
                                           filename=f"Analistas disponibles.xlsx")

        @app.callback(Output('download_analistas_por_liberar', 'data'),
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('button_analistas_por_liberar', 'n_clicks')],
                      [Input('interval', 'n_intervals')])
        def download_df(clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                          paises_drop_Liberaciones, productos_drop_Liberaciones,n_clicks, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            df_panorama = load_data_panorama("BD Empleados")

            df_panorama = df_panorama[df_panorama["Estado"] == "A"]
            df_panorama["Cedula"] = df_panorama["Cedula"].astype(str)
            df_panorama = df_panorama[["Cedula", "Ciudad residencia"]]

            df_liberaciones_en_firme = df_liberaciones[(df_liberaciones["EstadoSolicitud"] == "ABIERTO") |
                                                       (df_liberaciones["EstadoSolicitud"] == "EN PROCESO")]
            df_liberaciones_en_firme["IdentificacionColaborador"] = df_liberaciones_en_firme["IdentificacionColaborador"].astype(str)

            if clientes_drop_Liberaciones is not None:
                df_liberaciones_en_firme = df_liberaciones_en_firme[df_liberaciones_en_firme["Cliente"] == clientes_drop_Liberaciones]

            if UEN_drop_Liberaciones is not None:
                df_liberaciones_en_firme = df_liberaciones_en_firme[df_liberaciones_en_firme["UEN"] == UEN_drop_Liberaciones]

            if paises_drop_Liberaciones is not None:
                df_liberaciones_en_firme = df_liberaciones_en_firme[df_liberaciones_en_firme["Pais"] == paises_drop_Liberaciones]

            if productos_drop_Liberaciones is not None:
                df_liberaciones_en_firme = df_liberaciones_en_firme[df_liberaciones_en_firme["Producto"] == productos_drop_Liberaciones]


            df_liberaciones_en_firme = df_liberaciones_en_firme.merge(df_panorama, left_on=df_liberaciones_en_firme["IdentificacionColaborador"],
                                                                      right_on=df_panorama["Cedula"], how="inner")

            df_liberaciones_en_firme_exp = df_liberaciones_en_firme[
                ["Colaborador", "Cliente", "UEN", "MotivoLib", "Fecha", "Producto", "Ciudad residencia"]]

            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'button_analistas_por_liberar' in changed_id:
                return dcc.send_data_frame(df_liberaciones_en_firme_exp.to_excel,
                                               filename=f"Analistas por liberar.xlsx")

        @app.callback(Output('tabla_analistas_cliente', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_tabla_inicial = df_Liberaciones_tab.copy()
            if n:
                df_tabla_inicial = load_data_Liberaciones()

            df_Liberaciones = df_tabla_inicial[
                (df_tabla_inicial["Año"] == years_drop_Liberaciones) &
                (df_tabla_inicial["NumMes"] >= meses_slider_Liberaciones[0]) &
                (df_tabla_inicial["NumMes"] <= meses_slider_Liberaciones[1])]

            if clientes_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Cliente"] == clientes_drop_Liberaciones]

            if UEN_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["UEN"] == UEN_drop_Liberaciones]

            if paises_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Pais"] == paises_drop_Liberaciones]

            if productos_drop_Liberaciones is not None:
                df_Liberaciones = df_Liberaciones[df_Liberaciones["Producto"] == productos_drop_Liberaciones]

            df_Liberaciones = df_Liberaciones.groupby(["Cliente", "Mes"])["Contador"].count().reset_index()
            df_Liberaciones = pd.pivot(df_Liberaciones, columns="Mes", values="Contador", index="Cliente").fillna(0).reset_index()

            return df_Liberaciones.to_dict('records')

        @app.callback(Output('total-pais_Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones = pd.pivot_table(df_Liberaciones, columns="Pais", values="Liberaciones",
                                             index="Mes", sort=False)
            df_Liberaciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Liberaciones.index,
                            y=df_Liberaciones[col],
                            text=df_Liberaciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Liberaciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>LIBERACIONES POR PAÍS Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-pais_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()

            data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones, meses_slider_Liberaciones,
                                      clientes_drop_Liberaciones, UEN_drop_Liberaciones, paises_drop_Liberaciones,
                                      productos_drop_Liberaciones)
            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)

            df_Liberaciones_tabla = pd.pivot_table(df_Liberaciones, columns="Mes", values="Liberaciones",
                                                   index="Pais", sort=False).reset_index()
            df_Liberaciones_tabla.fillna(0, inplace=True)
            df_Liberaciones_tabla["TOTAL"] = df_Liberaciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Liberaciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Liberaciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Liberaciones_tabla.sum()).T
            df_Liberaciones_tabla = pd.concat([df_Liberaciones_tabla, sum_row], ignore_index=True)
            df_Liberaciones_tabla.iloc[-1, 0] = "TOTAL"
            df_Liberaciones_tabla["COMPARATIVO"] = df_Liberaciones_tabla.iloc[:, -1] - df_Liberaciones_tabla.iloc[:, 1]
            return df_Liberaciones_tabla.to_dict('records')

        @app.callback(Output('tabla-pais_Liberaciones', 'style_data_conditional'),
                      [Input('tabla-pais_Liberaciones', 'data')])
        def update_cell_style(data):
            style_data_conditional = []
            if data is not None:
                for i, row in enumerate(data):
                    columnas = [col_name for col_name, _ in row.items()][1:]
                    valores = [value for _, value in row.items()][1:]
                    contador = 0
                    for col_name, cell_value in row.items():
                        if isinstance(cell_value, (int, float)):
                            if col_name == columnas[0]:
                                contador = + 1
                            elif col_name == "COMPARATIVO":
                                if cell_value > 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#9CF9B3',
                                        'color': 'black'
                                    })
                                elif cell_value < 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9A09C',
                                        'color': 'black'
                                    })
                                else:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9F69C',
                                        'color': 'black'})
                            elif cell_value > valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#9CF9B3',
                                    'color': 'black'
                                })
                                contador = + 1
                            elif cell_value < valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9A09C',
                                    'color': 'black'
                                })
                                contador += 1
                            else:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9F69C',
                                    'color': 'black'
                                })
                                contador += 1

            return style_data_conditional

        @app.callback(Output('total-UEN_Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones = pd.pivot_table(df_Liberaciones, columns="UEN", values="Liberaciones",
                                             index="Mes", sort=False)
            df_Liberaciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Liberaciones.index,
                            y=df_Liberaciones[col],
                            text=df_Liberaciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Liberaciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>LIBERACIONES POR UEN Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-UEN_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)

            df_Liberaciones_tabla = pd.pivot_table(df_Liberaciones, columns="Mes", values="Liberaciones",
                                                   index="UEN", sort=False).reset_index()
            df_Liberaciones_tabla.fillna(0, inplace=True)
            df_Liberaciones_tabla["TOTAL"] = df_Liberaciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Liberaciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Liberaciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Liberaciones_tabla.sum()).T
            df_Liberaciones_tabla = pd.concat([df_Liberaciones_tabla, sum_row], ignore_index=True)
            df_Liberaciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Liberaciones_tabla.to_dict('records')

        @app.callback(Output('tabla-cliente_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "Cliente"])["Producto"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Producto": "Liberaciones"}, inplace=True)

            df_Liberaciones_tabla = pd.pivot_table(df_Liberaciones, columns="Mes", values="Liberaciones",
                                                   index="Cliente", sort=False).reset_index()
            df_Liberaciones_tabla.fillna(0, inplace=True)
            df_Liberaciones_tabla["TOTAL"] = df_Liberaciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Liberaciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Liberaciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Liberaciones_tabla.sum()).T
            df_Liberaciones_tabla = pd.concat([df_Liberaciones_tabla, sum_row], ignore_index=True)
            df_Liberaciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Liberaciones_tabla.to_dict('records')

        @app.callback(Output('total-producto_Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones = pd.pivot_table(df_Liberaciones, columns="Producto", values="Liberaciones",
                                             index="Mes", sort=False)
            df_Liberaciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Liberaciones.index,
                            y=df_Liberaciones[col],
                            text=df_Liberaciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Liberaciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>LIBERACIONES POR PRODUCTO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-producto_Liberaciones', 'data'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)

            df_Liberaciones_tabla = pd.pivot_table(df_Liberaciones, columns="Mes", values="Liberaciones",
                                                   index="Producto", sort=False).reset_index()
            df_Liberaciones_tabla.fillna(0, inplace=True)
            df_Liberaciones_tabla["TOTAL"] = df_Liberaciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Liberaciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Liberaciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Liberaciones_tabla.sum()).T
            df_Liberaciones_tabla = pd.concat([df_Liberaciones_tabla, sum_row], ignore_index=True)
            df_Liberaciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Liberaciones_tabla.to_dict('records')

        @app.callback(Output('total-evento_Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones,
                                                               clientes_drop_Liberaciones, UEN_drop_Liberaciones,
                                                               paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["NumMes", "Mes", "MotivoLib"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones = pd.pivot_table(df_Liberaciones, columns="MotivoLib", values="Liberaciones",
                                             index="Mes", sort=False)
            df_Liberaciones.fillna(0, inplace=True)

            chart = chart = [go.Scatter(x=df_Liberaciones.index,
                                        y=df_Liberaciones[col],
                                        mode='lines+markers+text',
                                        text=df_Liberaciones[col],
                                        textfont={'family': 'Open Sans', 'color': 'black'},
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': colors},
                                        marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                                'line': {'color': colors, 'width': 2}},
                                        name=col,
                                        hovertemplate='%{y}') for col, colors in zip(df_Liberaciones.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>MOTIVO DE LA LIBERACIÓN PARA {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('total-producto-sun_Liberaciones', 'figure'),
                      [Input('years_drop_Liberaciones', 'value')],
                      [Input('meses_slider_Liberaciones', 'value')],
                      [Input('clientes_drop_Liberaciones', 'value')],
                      [Input('UEN_drop_Liberaciones', 'value')],
                      [Input('paises_drop_Liberaciones', 'value')],
                      [Input('productos_drop_Liberaciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Liberaciones, meses_slider_Liberaciones, clientes_drop_Liberaciones,
                          UEN_drop_Liberaciones, paises_drop_Liberaciones, productos_drop_Liberaciones, n):
            """Esta función crea un gráfico de líneas con la Liberaciones del año seleccionado"""
            df_Liberaciones = df_Liberaciones_tab.copy()
            if n:
                df_Liberaciones = load_data_Liberaciones()
            df_Liberaciones, title = data_filtros_Liberaciones(df_Liberaciones, years_drop_Liberaciones,
                                                               meses_slider_Liberaciones, clientes_drop_Liberaciones,
                                                               UEN_drop_Liberaciones, paises_drop_Liberaciones,
                                                               productos_drop_Liberaciones)

            df_Liberaciones = df_Liberaciones.groupby(["Pais", "UEN", "Producto"])[
                "Cliente"].count().reset_index()
            df_Liberaciones.rename(columns={"Cliente": "Liberaciones"}, inplace=True)
            df_Liberaciones['Porcentaje'] = df_Liberaciones['Liberaciones'].apply(
                lambda row: round(row * 100 / df_Liberaciones["Liberaciones"].sum()))

            chart = px.sunburst(df_Liberaciones, path=["Pais", "UEN", "Producto"], values="Porcentaje", maxdepth=2)
            chart.update_layout(title={"text": "LIBERACIONES GENERAL",
                                       'font': {'color': 'black', 'size': 26, 'family': 'Arial'},
                                       'x': 0.5, 'y': 0.95,
                                       'xanchor': 'center', 'yanchor': 'top'},
                                legend_title="Legend Title",
                                width=800,
                                height=600)

            return chart

        ################################ CALLBACKS DE CONTRATACIONES ######################################
        @app.callback(Output('years_drop_Contrataciones', 'value'),
                      Input('years_drop_Contrataciones', 'options'))
        def get_year_value(years_drop_Contrataciones):
            """Esta función nos retorna el valor que indiquemos a la lista desplegable de años"""
            return [y['value'] for y in years_drop_Contrataciones][
                -1]  # el -1 indica que escoge el último año de la lista

        @app.callback(Output('download_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('param_drop_Contrataciones_download', 'value')],
                      [Input('download_button_Contrataciones', 'n_clicks')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def download_df(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                        UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones,
                        param_drop_Contrataciones_download, n_clicks, option, n):
            """Descarga el datframe seleccionado al hacer click en el botón de descargas"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option != "EN FIRME":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()

            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

            if 'download_button_Contrataciones' in changed_id:
                df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                       meses_slider_Contrataciones,
                                                                       clientes_drop_Contrataciones,
                                                                       UEN_drop_Contrataciones,
                                                                       paises_drop_Contrataciones,
                                                                       productos_drop_Contrataciones)
                if param_drop_Contrataciones_download is not None:
                    df_Contrataciones = df_data_table_Contrataciones(df_Contrataciones,
                                                                     f"{param_drop_Contrataciones_download}")
                    return dcc.send_data_frame(df_Contrataciones.to_excel,
                                               filename=f"Contrataciones por {param_drop_Contrataciones_download}.xlsx")
                else:
                    return dcc.send_data_frame(df_Contrataciones.to_excel, filename="Contrataciones.xlsx")

        @app.callback(Output('Contrataciones', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def update_spikeline(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                             UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, n):
            df_tabla_inicial = df_tabla_inicial_Contrataciones.copy()
            if n:
                df_tabla_inicial = load_data_inicial_Contrataciones()

            df_Contrataciones = df_tabla_inicial[
                (df_tabla_inicial["Año"] == years_drop_Contrataciones) &
                (df_tabla_inicial["NumMes"] >= meses_slider_Contrataciones[0]) &
                (df_tabla_inicial["NumMes"] <= meses_slider_Contrataciones[1])]

            title_list = []
            if clientes_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Cliente"] == clientes_drop_Contrataciones]
                title_list.append(clientes_drop_Contrataciones)

            if UEN_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["UEN"] == UEN_drop_Contrataciones]
                title_list.append(UEN_drop_Contrataciones)

            if paises_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Pais"] == paises_drop_Contrataciones]
                title_list.append(paises_drop_Contrataciones)

            if productos_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Producto"] == productos_drop_Contrataciones]
                title_list.append(productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "EstadoSolicitudSeleccion"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones = pd.pivot_table(df_Contrataciones, columns="EstadoSolicitudSeleccion", values="Contrataciones",
                                               index="Mes", sort=False)
            df_Contrataciones.fillna(0, inplace=True)
            df_Contrataciones["TOTAL"] = df_Contrataciones.iloc[:, :].sum(axis=1)

            chart = [go.Bar(x=df_Contrataciones.index,
                            y=df_Contrataciones[col],
                            text=df_Contrataciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Contrataciones.columns[:-1]]
            scatter_chart = go.Scatter(x=df_Contrataciones.index,
                                       y=df_Contrataciones["TOTAL"],
                                       mode='lines+markers+text',
                                       text=df_Contrataciones["TOTAL"],
                                       texttemplate='%{text: .2s}',
                                       textfont={'family': 'Open Sans', 'color': 'black'},
                                       line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': 'Green'},
                                       marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                               'line': {'width': 2, 'color': 'Green'}},
                                       name='TOTAL')

            chart.append(scatter_chart)

            return {'data': chart,
                    'layout': {'title': {'text': "<b>ESTADO DE CONTRATACIONES</b>", 'font': {'size': 26}},
                               'xaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}},
                               'yaxis': {'automargin': True,
                                         'tickfont': {'size': 16, 'color': 'black'}}
                               }}

        @app.callback(Output('tabla_inicial_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            df_tabla_inicial = df_tabla_inicial_Contrataciones.copy()
            if n:
                df_tabla_inicial = load_data_inicial_Contrataciones()
            df_Contrataciones = df_tabla_inicial[
                (df_tabla_inicial["Año"] == years_drop_Contrataciones) &
                (df_tabla_inicial["NumMes"] >= meses_slider_Contrataciones[0]) &
                (df_tabla_inicial["NumMes"] <= meses_slider_Contrataciones[1])]

            title_list = []
            if clientes_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Cliente"] == clientes_drop_Contrataciones]
                title_list.append(clientes_drop_Contrataciones)

            if UEN_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["UEN"] == UEN_drop_Contrataciones]
                title_list.append(UEN_drop_Contrataciones)

            if paises_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Pais"] == paises_drop_Contrataciones]
                title_list.append(paises_drop_Contrataciones)

            if productos_drop_Contrataciones is not None:
                df_Contrataciones = df_Contrataciones[df_Contrataciones["Producto"] == productos_drop_Contrataciones]
                title_list.append(productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "EstadoSolicitudSeleccion"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones", "EstadoSolicitudSeleccion": "Estado"}, inplace=True)
            df_Contrataciones_tabla = pd.pivot_table(df_Contrataciones, columns="Mes", values="Contrataciones",
                                                     index="Estado", sort=False).reset_index()
            df_Contrataciones_tabla.fillna(0, inplace=True)
            df_Contrataciones_tabla["TOTAL"] = df_Contrataciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Contrataciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            sum_row = pd.DataFrame(df_Contrataciones_tabla.sum()).T
            df_Contrataciones_tabla = pd.concat([df_Contrataciones_tabla, sum_row], ignore_index=True)
            df_Contrataciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Contrataciones_tabla.to_dict('records')

        @app.callback(Output('total-pais_Contrataciones', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Solicitudes del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()

            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()

            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones = pd.pivot_table(df_Contrataciones, columns="Pais", values="Contrataciones",
                                               index="Mes", sort=False)
            df_Contrataciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Contrataciones.index,
                            y=df_Contrataciones[col],
                            text=df_Contrataciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Contrataciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CONTRATACIONES POR PAÍS Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'yaxis': {'automargin': True,
                                  'tickfont': {'size': 16, 'color': 'black'}},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-pais_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "Pais"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)

            df_Contrataciones_tabla = pd.pivot_table(df_Contrataciones, columns="Mes", values="Contrataciones",
                                                     index="Pais", sort=False).reset_index()
            df_Contrataciones_tabla.fillna(0, inplace=True)
            df_Contrataciones_tabla["TOTAL"] = df_Contrataciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Contrataciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Contrataciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Contrataciones_tabla.sum()).T
            df_Contrataciones_tabla = pd.concat([df_Contrataciones_tabla, sum_row], ignore_index=True)
            df_Contrataciones_tabla.iloc[-1, 0] = "TOTAL"
            df_Contrataciones_tabla["COMPARATIVO"] = df_Contrataciones_tabla.iloc[:, -1] - df_Contrataciones_tabla.iloc[:, 1]
            return df_Contrataciones_tabla.to_dict('records')

        @app.callback(Output('tabla-pais_Contrataciones', 'style_data_conditional'),
                      [Input('tabla-pais_Contrataciones', 'data')])
        def update_cell_style(data):
            style_data_conditional = []
            if data is not None:
                for i, row in enumerate(data):
                    columnas = [col_name for col_name, _ in row.items()][1:]
                    valores = [value for _, value in row.items()][1:]
                    contador = 0
                    for col_name, cell_value in row.items():
                        if isinstance(cell_value, (int, float)):
                            if col_name == columnas[0]:
                                contador = + 1
                            elif col_name == "COMPARATIVO":
                                if cell_value > 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#9CF9B3',
                                        'color': 'black'
                                    })
                                elif cell_value < 0:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9A09C',
                                        'color': 'black'
                                    })
                                else:
                                    style_data_conditional.append({
                                        'if': {'row_index': i, 'column_id': col_name},
                                        'backgroundColor': '#F9F69C',
                                        'color': 'black'})
                            elif cell_value > valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#9CF9B3',
                                    'color': 'black'
                                })
                                contador = + 1
                            elif cell_value < valores[contador - 1]:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9A09C',
                                    'color': 'black'
                                })
                                contador += 1
                            else:
                                style_data_conditional.append({
                                    'if': {'row_index': i, 'column_id': col_name},
                                    'backgroundColor': '#F9F69C',
                                    'color': 'black'
                                })
                                contador += 1

            return style_data_conditional

        @app.callback(Output('total-UEN_Contrataciones', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones = pd.pivot_table(df_Contrataciones, columns="UEN", values="Contrataciones",
                                               index="Mes", sort=False)
            df_Contrataciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Contrataciones.index,
                            y=df_Contrataciones[col],
                            text=df_Contrataciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Contrataciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CONTRATACIONES POR UEN Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-UEN_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)
            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "UEN"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)

            df_Contrataciones_tabla = pd.pivot_table(df_Contrataciones, columns="Mes", values="Contrataciones",
                                                     index="UEN", sort=False).reset_index()
            df_Contrataciones_tabla.fillna(0, inplace=True)
            df_Contrataciones_tabla["TOTAL"] = df_Contrataciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Contrataciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Contrataciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Contrataciones_tabla.sum()).T
            df_Contrataciones_tabla = pd.concat([df_Contrataciones_tabla, sum_row], ignore_index=True)
            df_Contrataciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Contrataciones_tabla.to_dict('records')

        @app.callback(Output('tabla-cliente_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)

            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "Cliente"])[
                "Producto"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Producto": "Contrataciones"}, inplace=True)

            df_Contrataciones_tabla = pd.pivot_table(df_Contrataciones, columns="Mes", values="Contrataciones",
                                                     index="Cliente", sort=False).reset_index()
            df_Contrataciones_tabla.fillna(0, inplace=True)
            df_Contrataciones_tabla["TOTAL"] = df_Contrataciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Contrataciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Contrataciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Contrataciones_tabla.sum()).T
            df_Contrataciones_tabla = pd.concat([df_Contrataciones_tabla, sum_row], ignore_index=True)
            df_Contrataciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Contrataciones_tabla.to_dict('records')

        @app.callback(Output('total-producto_Contrataciones', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)
            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones = pd.pivot_table(df_Contrataciones, columns="Producto", values="Contrataciones",
                                               index="Mes", sort=False)
            df_Contrataciones.fillna(0, inplace=True)

            chart = [go.Bar(x=df_Contrataciones.index,
                            y=df_Contrataciones[col],
                            text=df_Contrataciones[col],
                            texttemplate='%{text: .2s}',
                            textposition='auto',
                            textangle=0,
                            name=col,
                            hovertemplate='%{y}') for col in df_Contrataciones.columns]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>CONTRATACIONES POR PRODUCTO Y {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('tabla-producto_Contrataciones', 'data'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)
            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "Producto"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)

            df_Contrataciones_tabla = pd.pivot_table(df_Contrataciones, columns="Mes", values="Contrataciones",
                                                     index="Producto", sort=False).reset_index()
            df_Contrataciones_tabla.fillna(0, inplace=True)
            df_Contrataciones_tabla["TOTAL"] = df_Contrataciones_tabla.iloc[:, 1:].sum(axis=1)
            df_Contrataciones_tabla.sort_values(by="TOTAL", ascending=False, inplace=True)
            df_Contrataciones_tabla.drop('TOTAL', axis=1, inplace=True)
            sum_row = pd.DataFrame(df_Contrataciones_tabla.sum()).T
            df_Contrataciones_tabla = pd.concat([df_Contrataciones_tabla, sum_row], ignore_index=True)
            df_Contrataciones_tabla.iloc[-1, 0] = "TOTAL"

            return df_Contrataciones_tabla.to_dict('records')

        @app.callback(Output('total-evento', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones, title = data_filtros_Contrataciones(df_Contrataciones, years_drop_Contrataciones,
                                                                   meses_slider_Contrataciones,
                                                                   clientes_drop_Contrataciones,
                                                                   UEN_drop_Contrataciones,
                                                                   paises_drop_Contrataciones,
                                                                   productos_drop_Contrataciones)
            df_Contrataciones = df_Contrataciones.groupby(["NumMes", "Mes", "EventoSolicitud"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.sort_values(by="NumMes", ascending=True, inplace=True)
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones = pd.pivot_table(df_Contrataciones, columns="EventoSolicitud", values="Contrataciones",
                                               index="Mes", sort=False)
            df_Contrataciones.fillna(0, inplace=True)

            chart = chart = [go.Scatter(x=df_Contrataciones.index,
                                        y=df_Contrataciones[col],
                                        mode='lines+markers+text',
                                        text=df_Contrataciones[col],
                                        textfont={'family': 'Open Sans', 'color': 'black'},
                                        line={'shape': 'spline', 'smoothing': 1.3, 'width': 3, 'color': colors},
                                        marker={'size': 16, 'symbol': 'circle', 'color': 'white',
                                                'line': {'color': colors, 'width': 2}},
                                        name=col,
                                        hovertemplate='%{y}') for col, colors in zip(df_Contrataciones.columns, colors)]

            return {'data': chart,
                    'layout': {
                        'title': {'text': f'<b>EVENTO DE LA CONTRATACIÓN PARA {title}</b>', 'font': {'size': 26}},
                        'xaxis': {'automargin': True},
                        'barmode': 'stack'
                    }}

        @app.callback(Output('total-producto_Contrataciones-sun', 'figure'),
                      [Input('years_drop_Contrataciones', 'value')],
                      [Input('meses_slider_Contrataciones', 'value')],
                      [Input('clientes_drop_Contrataciones', 'value')],
                      [Input('UEN_drop_Contrataciones', 'value')],
                      [Input('paises_drop_Contrataciones', 'value')],
                      [Input('productos_drop_Contrataciones', 'value')],
                      [Input('radio_option_Contrataciones', 'value')],
                      [Input('interval', 'n_intervals')])
        def scatter_chart(years_drop_Contrataciones, meses_slider_Contrataciones, clientes_drop_Contrataciones,
                          UEN_drop_Contrataciones, paises_drop_Contrataciones, productos_drop_Contrataciones, option,
                          n):
            """Esta función crea un gráfico de líneas con la Contrataciones del año seleccionado"""
            if n:
                if option != "EN FIRME":
                    df_Contrataciones = load_data_Contrataciones("FINALIZADO")
                else:
                    df_Contrataciones = load_data_Contrataciones()
            if option == "FINALIZADAS":
                df_Contrataciones = df_Contrataciones_tab_finalizado.copy()
            else:
                df_Contrataciones = df_Contrataciones_tab.copy()
            df_Contrataciones = df_Contrataciones[(df_Contrataciones["Año"] == years_drop_Contrataciones) &
                                                  (df_Contrataciones["NumMes"] >= meses_slider_Contrataciones[0]) &
                                                  (df_Contrataciones["NumMes"] <= meses_slider_Contrataciones[1])]
            df_Contrataciones = df_Contrataciones.groupby(["Pais", "UEN", "Producto"])[
                "Cliente"].count().reset_index()
            df_Contrataciones.rename(columns={"Cliente": "Contrataciones"}, inplace=True)
            df_Contrataciones['Porcentaje'] = df_Contrataciones['Contrataciones'].apply(
                lambda row: round(row * 100 / df_Contrataciones["Contrataciones"].sum()))

            chart = px.sunburst(df_Contrataciones, path=["Pais", "UEN", "Producto"], values="Porcentaje", maxdepth=2)
            chart.update_layout(title={"text": "CONTRATACIONES GENERAL",
                                       'font': {'color': 'black', 'size': 26, 'family': 'Arial'},
                                       'x': 0.5, 'y': 0.95,
                                       'xanchor': 'center', 'yanchor': 'top'},
                                legend_title="Legend Title",
                                width=800,
                                height=600)

            return chart

        def run_app_indicadores():
            """Esta función inicia el Dash y abre el explorador donde se despliega la app"""
            import webbrowser
            webbrowser.open("http://127.0.0.1:8008")
            app.run(port=8008)#, debug=True) ayuda a identificar errores en el codigo

        run_app_indicadores()


if __name__ == '__main__':
    start_dash()
