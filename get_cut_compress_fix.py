import sys
import argparse
import GOES
from netCDF4 import Dataset
from pyproj import Proj
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Función principal para descargar, recortar y comprimir datos de radiancia
def get_Rad(date_ini, date_fin):
    """
    Descarga datos de radiancia del satélite GOES en las bandas 08-09-10-13-14,
    recorta las imágenes alrededor del territorio colombiano y comprime los archivos NETCDF.

    Parámetros
    ----------
    date_ini : str ['YY-MM-DD HH:MM']
        Fecha inicial de descarga.
    date_fin : str ['YY-MM-DD HH:MM']
        Fecha final de descarga.
    """

    # Crear un DataFrame con un rango de fechas cada 60 minutos
    df = pd.DataFrame()
    df['Tiempo'] = pd.to_datetime(np.arange(
        datetime(int(date_ini[:4]), int(date_ini[5:7]), int(date_ini[8:10]),
                 int(date_ini[11:13]), int(date_ini[14:])),
        datetime(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]),
                 int(date_fin[11:13]), int(date_fin[14:])),
        timedelta(minutes=60)
    ).astype(datetime))

    # Directorios de salida para los archivos de radiancia
    path_out = 'radiances/'
    path_out_c = 'radiances_c/'
    canales = ['08', '09', '10', '13', '14']  # Bandas de interés

    # Crear directorios si no existen
    parent_dir = os.getcwd()
    original_path = os.path.join(parent_dir, path_out)
    path_c = os.path.join(parent_dir, path_out_c)

    if not os.path.exists(original_path):
        os.mkdir(original_path)

    if not os.path.exists(path_c):
        os.mkdir(path_c)

    print("Directory '%s' created" % original_path)
    print("Directory '%s' created" % path_c)

    # Iterar sobre cada fecha en el rango
    for dd in (df['Tiempo']):
        try:
            print('Datetime:', dd)
            print("\n")

            # Formatear las fechas para la descarga
            T_ini = str(dd).replace('-', '').replace(':', '').replace(' ', '-')
            T_fin = str(dd + pd.to_timedelta(9, 'min')).replace('-', '').replace(':', '').replace(' ', '-')

            # Descargar las imágenes de radiancia
            GOES.download('goes16', 'ABI-L1b-RadF', DateTimeIni=T_ini, DateTimeFin=T_fin,
                          channel=canales, rename_fmt='%Y%m%d%H%M%S', path_out=path_out)
            print("All radiance images were downloaded")
            print("\n")

            # Listar los archivos descargados
            lista_paths = os.listdir(path_out)
            # banda = [lista_paths[i][19:21] for i in range(len(lista_paths))]

            if lista_paths[0][0] == 'O':
                name = lista_paths[0][:19]  # Extraer el nombre base del archivo
                date = lista_paths[0][27:]  # Extraer la fecha del archivo
            else:
                print(f"No hay radianzas descargadas en la carpeta: {path_out}")
                print("\n")
                continue
            # Abrir los archivos NETCDF descargados
            try:
                ds8 = Dataset(path_out + name + '08_G16_s' + date)
                print("Archivo ds8 abierto correctamente")
            except Exception as e:
                print(f"No se pudo abrir ds8: {e}")
            try:
                ds9 = Dataset(path_out + name + '09_G16_s' + date)
                print("Archivo ds9 abierto correctamente")
            except Exception as e:
                print(f"No se pudo abrir ds9: {e}")
            try:
                ds10 = Dataset(path_out + name + '10_G16_s' + date)
                print("Archivo ds10 abierto correctamente")
            except Exception as e:
                print(f"No se pudo abrir ds10: {e}")
            try:
                ds13 = Dataset(path_out + name + '13_G16_s' + date)
                print("Archivo ds13 abierto correctamente")
            except Exception as e:
                print(f"No se pudo abrir ds13: {e}")
            try:
                ds14 = Dataset(path_out + name + '14_G16_s' + date)
                print("Archivo ds14 abierto correctamente")
            except Exception as e:
                print(f"No se pudo abrir ds14: {e}")

            # Obtener parámetros de proyección del satélite
            sat_h, sat_lon, sat_sweep = None, None, None
            try:
                sat_h = ds8.variables['goes_imager_projection'].perspective_point_height
                sat_lon = ds8.variables['goes_imager_projection'].longitude_of_projection_origin
                sat_sweep = ds8.variables['goes_imager_projection'].sweep_angle_axis
                print("Parámetros de proyección obtenidos de ds8")
            except Exception as e:
                print(f"No se pudieron obtener los parámetros de proyección de ds8: {e}") 
            try:
                sat_h = ds9.variables['goes_imager_projection'].perspective_point_height
                sat_lon = ds9.variables['goes_imager_projection'].longitude_of_projection_origin
                sat_sweep = ds9.variables['goes_imager_projection'].sweep_angle_axis
                print("Parámetros de proyección obtenidos de ds9")
            except Exception as e:
                print(f"No se pudieron obtener los parámetros de proyección de ds9: {e}")
            try:
                sat_h = ds10.variables['goes_imager_projection'].perspective_point_height
                sat_lon = ds10.variables['goes_imager_projection'].longitude_of_projection_origin
                sat_sweep = ds10.variables['goes_imager_projection'].sweep_angle_axis
                print("Parámetros de proyección obtenidos de ds10")
            except Exception as e:
                print(f"No se pudieron obtener los parámetros de proyección de ds10: {e}")
            try:    
                sat_h = ds13.variables['goes_imager_projection'].perspective_point_height
                sat_lon = ds13.variables['goes_imager_projection'].longitude_of_projection_origin
                sat_sweep = ds13.variables['goes_imager_projection'].sweep_angle_axis
                print("Parámetros de proyección obtenidos de ds13")
            except Exception as e:  
                print(f"No se pudieron obtener los parámetros de proyección de ds13: {e}")
            try:    
                sat_h = ds14.variables['goes_imager_projection'].perspective_point_height
                sat_lon = ds14.variables['goes_imager_projection'].longitude_of_projection_origin
                sat_sweep = ds14.variables['goes_imager_projection'].sweep_angle_axis
                print("Parámetros de proyección obtenidos de ds14")
            except Exception as e:
                print(f"No se pudieron obtener los parámetros de proyección de ds14: {e}")
            # Crear una proyección geostacionaria
            p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep)
            # Crear una malla de coordenadas
            # Crear una malla de coordenadas
            x, y, XX, YY, lons, lats = None, None, None, None, None, None
            try:
                x = ds8.variables['x'][:]
                y = ds8.variables['y'][:]
                XX, YY = np.meshgrid(x, y)
                lons, lats = p(XX, YY, inverse=True)
                print("Malla de coordenadas creada")
            except Exception as e:
                print(f"No se pudo crear la malla de coordenadas: {e}")
            try:
                x = ds9.variables['x'][:]
                y = ds9.variables['y'][:]
                XX, YY = np.meshgrid(x, y)
                lons, lats = p(XX, YY, inverse=True)
                print("Malla de coordenadas creada")
            except Exception as e:
                print(f"No se pudo crear la malla de coordenadas: {e}")
            try:
                x = ds10.variables['x'][:]
                y = ds10.variables['y'][:]
                XX, YY = np.meshgrid(x, y)
                lons, lats = p(XX, YY, inverse=True)
                print("Malla de coordenadas creada")
            except Exception as e:
                print(f"No se pudo crear la malla de coordenadas: {e}")
            try:
                x = ds13.variables['x'][:]
                y = ds13.variables['y'][:]
                XX, YY = np.meshgrid(x, y)
                lons, lats = p(XX, YY, inverse=True)
                print("Malla de coordenadas creada")
            except Exception as e:
                print(f"No se pudo crear la malla de coordenadas: {e}")
            try:
                x = ds14.variables['x'][:]
                y = ds14.variables['y'][:]
                XX, YY = np.meshgrid(x, y)
                lons, lats = p(XX, YY, inverse=True)
                print("Malla de coordenadas creada")
            except Exception as e:
                print(f"No se pudo crear la malla de coordenadas: {e}")
            # Definir los límites geográficos de Colombia
            bound = {'lon': [-81.03, -64], 'lat': [-4.1, 12.78]}
            xmin, ymin = p(bound['lon'][0], bound['lat'][0]) / sat_h
            xmax, ymax = p(bound['lon'][1], bound['lat'][1]) / sat_h
            # Seleccionar los píxeles dentro de los límites
            sel_x = np.where((x >= xmin) & (x <= xmax))
            sel_y = np.where((y >= ymin) & (y <= ymax))
            x_col = x[sel_x]
            y_col = x[sel_y]
            print("Croping radiance images...")
            print("\n")
            # Recortar las imágenes de radiancia
            Rad8 = ds8.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            Rad9 = ds9.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            Rad10 = ds10.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            Rad13 = ds13.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            Rad14 = ds14.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            # Crear un nuevo archivo NETCDF con las imágenes recortadas
            print("Creating new NETCDF file with all bands radiances...")
            print("\n")
            file_name = 'RadF_' + date
            ds = Dataset(file_name, 'w', format='NETCDF4')
            ds.createDimension('y', len(y_col))
            ds.createDimension('x', len(x_col))
            # Agregar variables al archivo NETCDF
            fill = ds8.variables['Rad']._FillValue
            dsRad8 = ds.createVariable('Rad8', 'i2', ('y', 'x',), fill_value=fill)
            dsRad9 = ds.createVariable('Rad9', 'i2', ('y', 'x',), fill_value=fill)
            dsRad10 = ds.createVariable('Rad10', 'i2', ('y', 'x',), fill_value=fill)
            dsRad13 = ds.createVariable('Rad13', 'i2', ('y', 'x',), fill_value=fill)
            dsRad14 = ds.createVariable('Rad14', 'i2', ('y', 'x',), fill_value=fill)
            # Copiar atributos de las variables originales
            dsRad8.setncatts({k: ds8.variables['Rad'].getncattr(k) for k in ds8.variables['Rad'].ncattrs()})
            dsRad9.setncatts({k: ds9.variables['Rad'].getncattr(k) for k in ds9.variables['Rad'].ncattrs()})
            dsRad10.setncatts({k: ds10.variables['Rad'].getncattr(k) for k in ds10.variables['Rad'].ncattrs()})
            dsRad13.setncatts({k: ds13.variables['Rad'].getncattr(k) for k in ds13.variables['Rad'].ncattrs()})
            dsRad14.setncatts({k: ds14.variables['Rad'].getncattr(k) for k in ds14.variables['Rad'].ncattrs()})
            # Guardar datos en el archivo NETCDF
            print("Saving data in the new NETCDF file...")
            print("\n")
            dsRad8[:] = Rad8
            dsRad9[:] = Rad9
            dsRad10[:] = Rad10
            dsRad13[:] = Rad13
            dsRad14[:] = Rad14
            ds.close()
            # Comprimir el archivo NETCDF
            print("Compressing file...")
            comman_line_compression = os.system(
                f"nccopy -d9 {file_name} {path_c + 'RadFC_' + date}")
            if comman_line_compression == 0:
                print(f"The file {file_name} was compressed")
                print("\n")
            else:
                print(f"ERROR TRYING TO COMPRESS THE FILES. TRY RUN THE FOLLOWING COMMAND IN THE COMMAND LINE: nccopy -d9 {file_name} {path_c + 'RadFC_' + date}")
                break

            # Eliminar archivos temporales
            if os.path.isfile(f"{file_name}"):
                os.remove(f"{file_name}")
                print(f"Archivo temporal eliminado: {file_name}")

            # Lista de archivos temporales a eliminar
            temp_files = [
                f"{path_out + name + '08_G16_s' + date}",
                f"{path_out + name + '09_G16_s' + date}",
                f"{path_out + name + '10_G16_s' + date}",
                f"{path_out + name + '13_G16_s' + date}",
                f"{path_out + name + '14_G16_s' + date}"
            ]

            # Iterar sobre la lista y eliminar los archivos que existan
            for temp_file in temp_files:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    print(f"Archivo temporal eliminado: {temp_file}")
            # # Eliminar archivos temporales
            # if os.path.isfile(f"{file_name}"):
            #     os.remove(f"{file_name}")
            #     if os.path.isfile(f"{path_out + name + '08_G16_s' + date}"):
            #         os.remove(f"{path_out + name + '08_G16_s' + date}")
            #         os.remove(f"{path_out + name + '09_G16_s' + date}")
            #         os.remove(f"{path_out + name + '10_G16_s' + date}")
            #         os.remove(f"{path_out + name + '13_G16_s' + date}")
            #         os.remove(f"{path_out + name + '14_G16_s' + date}")


            # # Abrir los archivos NETCDF descargados
            # ds8  = Dataset(path_out + name + '08_G16_s' + date)
            # ds9  = Dataset(path_out + name + '09_G16_s' + date)
            # ds10 = Dataset(path_out + name + '10_G16_s' + date)
            # ds13 = Dataset(path_out + name + '13_G16_s' + date)
            # ds14 = Dataset(path_out + name + '14_G16_s' + date)

        except Exception as e:
                    print(f"An exception occurred downloading the {dd} radiance {e}")
                    print("\n")
                    continue
        else:
            print(f"Execution was successful, the radiance image was created")
            print("\n") 
            print(canales)


                



























            
            # #Abrir los archivos NETCDF descargados
            # for canal in canales:
            #     file_path = f"{path_out}{name}{canal}_G16_s{date}"
            #     if os.path.isfile(file_path):
            #         try:
            #             with Dataset(file_path) as ds:
            #                 # Lógica para procesar el archivo si es necesario
            #                 print(f"Processed dataset for band {canal} and date {date}")
            #         except Exception as e:
            #             print(f"Error processing file for band {canal}: {e}")
            #     else:
            #         print(f"File for band {canal} not found: {file_path}. Skipping...")
            #         continue  # Saltar al siguiente canal si el archivo no existe
            

            # Abrir los archivos NETCDF descargados

            

            # ds8 = Dataset(path_out + name + '08_G16_s' + date)
            # ds9 = Dataset(path_out + name + '09_G16_s' + date)
            # ds10 = Dataset(path_out + name + '10_G16_s' + date)
            # ds13 = Dataset(path_out + name + '13_G16_s' + date)
            # ds14 = Dataset(path_out + name + '14_G16_s' + date)
        
            # # Obtener parámetros de proyección del satélite
            # sat_h = ds8.variables['goes_imager_projection'].perspective_point_height
            # sat_lon = ds8.variables['goes_imager_projection'].longitude_of_projection_origin
            # sat_sweep = ds8.variables['goes_imager_projection'].sweep_angle_axis

            # # Crear una proyección geostacionaria
            # p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep)

            # # Crear una malla de coordenadas
            # x = ds8.variables['x'][:]
            # y = ds8.variables['y'][:]
            # XX, YY = np.meshgrid(x, y)
            # lons, lats = p(XX, YY, inverse=True)

            # # Definir los límites geográficos de Colombia
            # bound = {'lon': [-81.03, -64], 'lat': [-4.1, 12.78]}
            # xmin, ymin = p(bound['lon'][0], bound['lat'][0]) / sat_h
            # xmax, ymax = p(bound['lon'][1], bound['lat'][1]) / sat_h

            # # Seleccionar los píxeles dentro de los límites
            # sel_x = np.where((x >= xmin) & (x <= xmax))
            # sel_y = np.where((y >= ymin) & (y <= ymax))

            # x_col = x[sel_x]
            # y_col = x[sel_y]

            # print("Croping radiance images...")
            # print("\n")

            
            # # Recortar las imágenes de radiancia
            # Rad8 = ds8.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            # Rad9 = ds9.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            # Rad10 = ds10.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            # Rad13 = ds13.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]
            # Rad14 = ds14.variables['Rad'][sel_y[0].min():sel_y[0].max() + 1, sel_x[0].min():sel_x[0].max() + 1]

            # # Crear un nuevo archivo NETCDF con las imágenes recortadas
            # print("Creating new NETCDF file with all bands radiances...")
            # print("\n")
            # file_name = 'RadF_' + date
            # ds = Dataset(file_name, 'w', format='NETCDF4')
            # ds.createDimension('y', len(y_col))
            # ds.createDimension('x', len(x_col))

            # # Agregar variables al archivo NETCDF
            # fill = ds8.variables['Rad']._FillValue
            # dsRad8 = ds.createVariable('Rad8', 'i2', ('y', 'x',), fill_value=fill)
            # dsRad9 = ds.createVariable('Rad9', 'i2', ('y', 'x',), fill_value=fill)
            # dsRad10 = ds.createVariable('Rad10', 'i2', ('y', 'x',), fill_value=fill)
            # dsRad13 = ds.createVariable('Rad13', 'i2', ('y', 'x',), fill_value=fill)
            # dsRad14 = ds.createVariable('Rad14', 'i2', ('y', 'x',), fill_value=fill)

            # # Copiar atributos de las variables originales
            # dsRad8.setncatts({k: ds8.variables['Rad'].getncattr(k) for k in ds8.variables['Rad'].ncattrs()})
            # dsRad9.setncatts({k: ds9.variables['Rad'].getncattr(k) for k in ds9.variables['Rad'].ncattrs()})
            # dsRad10.setncatts({k: ds10.variables['Rad'].getncattr(k) for k in ds10.variables['Rad'].ncattrs()})
            # dsRad13.setncatts({k: ds13.variables['Rad'].getncattr(k) for k in ds13.variables['Rad'].ncattrs()})
            # dsRad14.setncatts({k: ds14.variables['Rad'].getncattr(k) for k in ds14.variables['Rad'].ncattrs()})

            # # Guardar datos en el archivo NETCDF
            # print("Saving data in the new NETCDF file...")
            # print("\n")
            # dsRad8[:] = Rad8
            # dsRad9[:] = Rad9
            # dsRad10[:] = Rad10
            # dsRad13[:] = Rad13
            # dsRad14[:] = Rad14
            # ds.close()

            # # Comprimir el archivo NETCDF
            # print("Compressig file...")
            # comman_line_compression = os.system(f"nccopy -d9 {file_name} {path_out_c + 'RadFC_' + date}")
            # if comman_line_compression == 0:
            #     print(f"The file {file_name} was compressed")
            #     print("\n")
            # else:
            #     print(f"ERROR TRYING TO COMPRESS THE FILES. TRY RUN THE FOLLOWING COMMAND IN THE COMMAND LINE: nccopy -d9 {file_name} {path_out_c + 'LSTFC_' + date}")
            #     break

            # # Eliminar archivos temporales
            # if os.path.isfile(f"{file_name}"):
            #     os.remove(f"{file_name}")
            # if os.path.isfile(f"{path_out + name + '08_G16_s' + date}"):
            #     os.remove(f"{path_out + name + '08_G16_s' + date}")
            #     os.remove(f"{path_out + name + '09_G16_s' + date}")
            #     os.remove(f"{path_out + name + '10_G16_s' + date}")
            #     os.remove(f"{path_out + name + '13_G16_s' + date}")
            #     os.remove(f"{path_out + name + '14_G16_s' + date}")

       
# # Eliminar todos los archivos en el directorio radiances
#     if os.path.exists(path_out):
#         for file in os.listdir(path_out):
#             file_path = os.path.join(path_out, file)
#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"Deleted file: {file_path}")
#             except Exception as e:
#                 print(f"Error deleting file {file_path}: {e}")

   

        

        

        

# # Comprimir el archivo NETCDF
#     print("Compressig file...")
#     comman_line_compression = os.system(
#         f"nccopy -d9 {file_name} {path_out_c + 'RadFC_' + date}")
    
#     if comman_line_compression == 0:
#         print(f"The file {file_name} was compressed")
#         print("\n")
#     else:
#         print(
#             f"Error compressing the file. You can try running the following command manually:\n"
#             f"nccopy -d9 {file_name} {path_out_c + 'RadFC_' + date}"
#         )
#         return

    #     # Eliminar archivos temporales
    # if os.path.isfile(f"{file_name}"):
    #     os.remove(f"{file_name}")
    #     if os.path.isfile(f"{path_out + name + '08_G16_s' + date}"):
    #         os.remove(f"{path_out + name + '08_G16_s' + date}")
    #         os.remove(f"{path_out + name + '09_G16_s' + date}")
    #         os.remove(f"{path_out + name + '10_G16_s' + date}")
    #         os.remove(f"{path_out + name + '13_G16_s' + date}")
    #         os.remove(f"{path_out + name + '14_G16_s' + date}")
            

# Bloque principal para ejecutar el script desde la línea de comandos
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that processes satellite radiance data"
    )
    parser.add_argument("--function", required=True, type=str)
    parser.add_argument("--date_ini", required=False, type=str)
    parser.add_argument("--date_fin", required=True, type=str)
    args = parser.parse_args()

    func = args.function
    date_ini = args.date_ini
    date_fin = args.date_fin

    # Invocar funciones según el argumento proporcionado
    if func == "get_Rad":
        get_Rad(date_ini, date_fin)
    elif func == "get_LST":
        get_LST(date_ini, date_fin)
    elif func == "get_TPW":
        get_TPW(date_ini, date_fin)
    else:
        print("Unknown parameters. Use 'get_Rad', 'get_LST', or 'get_TPW'")