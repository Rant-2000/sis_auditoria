import os
from pathlib import Path,PurePath
# Se define el nombre de la carpeta o directorio a crear

def crea_dir(anho,gru,nom,act):
    directorio = PurePath(Path.cwd(),'Archivos_PDF')
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)
    
    directorio=PurePath(directorio,anho)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,gru)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,nom)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    directorio=PurePath(directorio,act)
    print(directorio)
    Path(directorio).mkdir(exist_ok=True)

    return directorio

crea_dir('2021','INFO','Juancho_PEREZ','DCOM')
