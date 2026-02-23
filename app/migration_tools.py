"""
Script de migración de proyectos antiguos con datos incompletos.
Recupera automáticamente id_ups desde modelo_snap y permite completar datos manualmente.
Usa PostgreSQL (configurado en app/config.py)
"""
import os
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from app.config import BaseConfig


class MigradorProyectos:
    def __init__(self, database_url=None):
        self.database_url = database_url or BaseConfig.DATABASE_URL

    def _conectar(self):
        conn = psycopg.connect(self.database_url)
        return conn
    
    def obtener_proyectos_incompletos(self):
        """Retorna lista de proyectos con datos faltantes"""
        conn = self._conectar()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute("""
            SELECT id, pedido, cliente_snap, sucursal_snap, modelo_snap, potencia_snap,
                   id_ups, voltaje, fases, longitud, tiempo_respaldo, id_bateria
            FROM proyectos_publicados
            WHERE id_ups IS NULL OR voltaje IS NULL OR fases IS NULL
            ORDER BY id
        """)
        proyectos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return proyectos
    
    def buscar_ups_por_nombre(self, nombre_ups):
        """Busca UPS en catálogo por nombre aproximado"""
        conn = self._conectar()
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute("""
            SELECT id, "Nombre_del_Producto", "Capacidad_kVA", "Serie"
            FROM ups_specs
            WHERE "Nombre_del_Producto" ILIKE %s
            ORDER BY "Capacidad_kVA"
        """, (f'%{nombre_ups}%',))
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return resultados
    
    def recuperar_id_ups_automatico(self, proyecto):
        """Intenta recuperar id_ups automáticamente desde modelo_snap"""
        modelo_snap = proyecto.get('modelo_snap') or ''
        if not modelo_snap:
            return None
        
        # Buscar UPS por nombre exacto o similar
        resultados = self.buscar_ups_por_nombre(modelo_snap)
        
        if len(resultados) == 1:
            # Match único - confianza alta
            return {
                'id_ups': resultados[0]['id'],
                'confianza': 'alta',
                'ups_encontrado': resultados[0]
            }
        elif len(resultados) > 1:
            # Múltiples matches - verificar potencia
            potencia_snap = proyecto.get('potencia_snap')
            if potencia_snap:
                for ups in resultados:
                    # Tolerancia de ±0.5 kVA
                    if abs(ups['Capacidad_kVA'] - potencia_snap) < 0.5:
                        return {
                            'id_ups': ups['id'],
                            'confianza': 'media',
                            'ups_encontrado': ups,
                            'alternativas': resultados
                        }
            
            # No hay match por potencia, retornar primer resultado
            return {
                'id_ups': resultados[0]['id'],
                'confianza': 'baja',
                'ups_encontrado': resultados[0],
                'alternativas': resultados
            }
        
        return None
    
    def actualizar_proyecto(self, pedido, datos):
        """Actualiza datos de un proyecto"""
        conn = self._conectar()
        try:
            set_parts = []
            values = []
            
            for key, value in datos.items():
                if key in ['id_ups', 'voltaje', 'fases', 'longitud', 'tiempo_respaldo', 'id_bateria']:
                    set_parts.append(f"{key} = %s")
                    values.append(value)

            if not set_parts:
                return False

            values.append(pedido)
            sql = f"UPDATE proyectos_publicados SET {', '.join(set_parts)} WHERE pedido = %s"
            
            conn.execute(sql, values)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando proyecto {pedido}: {e}")
            return False
        finally:
            conn.close()
    
    def ejecutar_migracion_automatica(self, auto_aplicar=False):
        """
        Ejecuta migración automática de proyectos.
        Si auto_aplicar=True, actualiza directamente en BD.
        Si False, solo retorna plan de migración.
        """
        proyectos = self.obtener_proyectos_incompletos()
        plan_migracion = []
        
        for proyecto in proyectos:
            recuperacion = self.recuperar_id_ups_automatico(proyecto)
            
            plan_item = {
                'proyecto': proyecto,
                'id_ups_recuperado': None,
                'ups_sugerido': None,
                'confianza': None,
                'accion': 'manual',  # Por defecto requiere intervención manual
                'datos_faltantes': []
            }
            
            # Verificar datos faltantes
            if not proyecto.get('id_ups'):
                plan_item['datos_faltantes'].append('id_ups')
            if not proyecto.get('voltaje'):
                plan_item['datos_faltantes'].append('voltaje')
            if not proyecto.get('fases'):
                plan_item['datos_faltantes'].append('fases')
            if not proyecto.get('longitud'):
                plan_item['datos_faltantes'].append('longitud')
            
            # Si se recuperó id_ups
            if recuperacion:
                plan_item['id_ups_recuperado'] = recuperacion['id_ups']
                plan_item['ups_sugerido'] = recuperacion['ups_encontrado']
                plan_item['confianza'] = recuperacion['confianza']
                
                # Si confianza es alta, podemos auto-aplicar
                if recuperacion['confianza'] == 'alta' and auto_aplicar:
                    datos_update = {'id_ups': recuperacion['id_ups']}
                    if self.actualizar_proyecto(proyecto['pedido'], datos_update):
                        plan_item['accion'] = 'actualizado_auto'
                else:
                    plan_item['accion'] = 'requiere_confirmacion'
            
            plan_migracion.append(plan_item)
        
        return plan_migracion
    
    def generar_reporte_migracion(self, plan_migracion):
        """Genera reporte legible del plan de migración"""
        print("\n" + "="*80)
        print("REPORTE DE MIGRACIÓN DE PROYECTOS")
        print("="*80 + "\n")
        
        total = len(plan_migracion)
        auto_ok = sum(1 for p in plan_migracion if p['accion'] == 'actualizado_auto')
        requiere_conf = sum(1 for p in plan_migracion if p['accion'] == 'requiere_confirmacion')
        manual = sum(1 for p in plan_migracion if p['accion'] == 'manual')
        
        print(f"Total de proyectos: {total}")
        print(f"  - Actualizados automáticamente: {auto_ok}")
        print(f"  - Requieren confirmación: {requiere_conf}")
        print(f"  - Requieren intervención manual: {manual}\n")
        
        for i, item in enumerate(plan_migracion, 1):
            proyecto = item['proyecto']
            print(f"\n{i}. Pedido: {proyecto['pedido']} | {proyecto['cliente_snap']} - {proyecto['sucursal_snap']}")
            print(f"   UPS guardado: {proyecto['modelo_snap']} ({proyecto['potencia_snap']} kVA)")
            print(f"   Datos faltantes: {', '.join(item['datos_faltantes'])}")
            
            if item['ups_sugerido']:
                ups = item['ups_sugerido']
                print(f"   OK UPS encontrado: ID={ups['id']} | {ups['Nombre_del_Producto']} ({ups['Capacidad_kVA']} kVA)")
                print(f"   Confianza: {item['confianza'].upper()}")
            else:
                print(f"   X No se pudo recuperar UPS automáticamente")
            
            print(f"   Acción: {item['accion']}")
        
        print("\n" + "="*80)
        print("FIN DEL REPORTE")
        print("="*80 + "\n")

# Ejecutar análisis
if __name__ == "__main__":
    migrador = MigradorProyectos()
    
    print("Analizando proyectos incompletos...")
    plan = migrador.ejecutar_migracion_automatica(auto_aplicar=False)
    
    migrador.generar_reporte_migracion(plan)
    
    print("\nPara aplicar cambios automáticos, ejecutar:")
    print("  plan = migrador.ejecutar_migracion_automatica(auto_aplicar=True)")
