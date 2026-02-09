import sys
import os

# Ajustar path para importar modulos de la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.base_datos import GestorDB

gestor = GestorDB()

datos_personal = [
    ("Gustavo Velazquillo Zamora", "Ingeniero de Soporte"),
    ("David Zuñiga", "Tecnico de Servicio"),
    ("Pedro Ramirez Vazquez", "Gerente de Servicio"),
    ("Remigio Gutiérrez Gutierrez", "Técnico de Servicio"),
    ("Juan Daniel Benítez Olivarez", "Técnico de Servicio"),
    ("Victor Hugo Dominguez Alvarez", "Técnico de Servicio"),
    ("Mario Ceballos Lopez", "Técnico de Servicio"),
    ("Braulio Rodriguez Acosta", "Técnico de Servicio"),
    ("Juan Ivan Sanchez Burgos", "Técnico de Servicio"),
    ("Esteban Gutiérrez Chavero", "Técnico de Servicio"),
    ("Israel Villagrán Maldonado", "Técnico de Servicio"),
    ("Antonio de Jesus Hernandez Amaya", "Técnico de Servicio"),
    ("Juan Alberto Rosales", "Técnico de Servicio"),
    ("Saul Alejandro Escarcega Nava", "Técnico de Servicio"),
    ("Erik Omar Flores Soto", "Técnico de Servicio"),
    ("Fancisco Dominguez Maya", "Técnico de Servicio"),
    ("Jose Luis Dorantes Nava", "Técnico de Servicio"),
    ("Sergio Arturo Franco Tellez", "Tecnico de Servicio"),
    ("Ricardo Zarate", "Tecnico de Apoyo"),
    ("Aldair Ortega Hernández", "Tecnico de Apoyo"),
    ("Alberto Zavala Perez", "Maniobrista"),
    ("Oswaldo Davalos", "Gerente de Almacén"),
    ("Carlos Sandoval", "Coordinador de Embarques"),
    ("Joel Mendez", "Almacenista"),
    ("Alberto Sanchez", "Almacenista"),
    ("Cristhoper Cuevas", "Gerente de Producción"),
    ("Samuel Elias Martinez Garcia", "Becario"),
    ("Luis Damian Vazquez Gonzalez", "Becario"),
    ("Emmanuel Hernandez", "Becario"),
    ("Vangelis Angeles", "Técnico de Apoyo"),
    ("Oscar Nolasco", "Personal de Almacen"),
    ("Alma San Vicente", "Coordinadora de Servicio")
]

print("Iniciando carga de personal...")
count = 0
for nombre, puesto in datos_personal:
    if gestor.agregar_personal(nombre, puesto):
        count += 1
        print(f"Agregado: {nombre}")
    else:
        print(f"Error al agregar: {nombre}")

print(f"Total agregados: {count}")
