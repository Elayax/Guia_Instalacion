import math
import json
import urllib.request

# --- AQUÍ DEBE DECIR EXACTAMENTE ESTO: ---
class CalculadoraUPS: 
    # Base de datos de Cables (NOM-001 Tabla 310-15(b)(16))
    # Formato: 'AWG': {'75C': amps, '90C': amps, 'Z_eff': ohms/km (aprox FP 0.9 en tubo acero)}
    CABLE_DB = {
        '14': {'75C': 20, '90C': 25, 'Z_eff': 10.2},
        '12': {'75C': 25, '90C': 30, 'Z_eff': 6.6},
        '10': {'75C': 35, '90C': 40, 'Z_eff': 3.9},
        '8': {'75C': 50, '90C': 55, 'Z_eff': 2.56},
        '6': {'75C': 65, '90C': 75, 'Z_eff': 1.61},
        '4': {'75C': 85, '90C': 95, 'Z_eff': 1.02},
        '3': {'75C': 100, '90C': 115, 'Z_eff': 0.82},
        '2': {'75C': 115, '90C': 130, 'Z_eff': 0.66},
        '1': {'75C': 130, '90C': 145, 'Z_eff': 0.52},
        '1/0': {'75C': 150, '90C': 170, 'Z_eff': 0.43},
        '2/0': {'75C': 175, '90C': 195, 'Z_eff': 0.36},
        '3/0': {'75C': 200, '90C': 225, 'Z_eff': 0.29},
        '4/0': {'75C': 230, '90C': 260, 'Z_eff': 0.24},
        '250': {'75C': 255, '90C': 290, 'Z_eff': 0.21},
        '350': {'75C': 310, '90C': 350, 'Z_eff': 0.16},
        '500': {'75C': 380, '90C': 430, 'Z_eff': 0.12}
    }

    # Tabla 250-122 (Tierra mínima basada en Breaker)
    GND_TABLE = {
        15: '14', 20: '12', 60: '10', 100: '8',
        200: '6', 300: '4', 400: '3', 500: '2',
        600: '1', 800: '1/0'
    }

    # Breakers comerciales (Tabla 240-6(A))
    STANDARD_BREAKERS = [15, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                         125, 150, 175, 200, 225, 250, 300, 350, 400, 500, 600]

    def calcular(self, datos):
        # 1. Extracción de variables
        kva = float(datos.get('kva') or 0)
        voltaje = int(datos.get('voltaje') or 0)
        fases = int(datos.get('fases') or 0)
        longitud = float(datos.get('longitud') or 0)
        tiempo_respaldo = datos.get('tiempo_respaldo')
        lat = datos.get('lat')
        lon = datos.get('lon')
        
        # Valores por defecto para variables ambientales
        altitud = 2240 
        temp_amb = 30 # °C

        # --- Consulta a API externa para datos ambientales ---
        if lat and lon:
            try:
                # 1. Obtener altitud
                url_alt = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
                with urllib.request.urlopen(url_alt, timeout=5) as response:
                    data_alt = json.loads(response.read())
                    if data_alt.get('elevation'):
                        altitud = int(data_alt['elevation'][0])

                # 2. Obtener temperatura actual
                url_temp = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"
                with urllib.request.urlopen(url_temp, timeout=5) as response:
                    data_temp = json.loads(response.read())
                    if data_temp.get('current') and 'temperature_2m' in data_temp['current']:
                        temp_amb = int(data_temp['current']['temperature_2m'])

            except Exception as e:
                print(f"WARN: No se pudo obtener datos ambientales de la API. Usando valores por defecto. Error: {e}")
                # En caso de error (timeout, sin internet, etc.), se usan los valores por defecto ya definidos.
                pass

        # Validación de seguridad para evitar división por cero
        if voltaje <= 0:
            return {
                'i_nom': 0,
                'i_diseno': 0,
                'fase_sel': "Error: Voltaje 0",
                'gnd_sel': "N/A",
                'breaker_sel': 0,
                'dv_pct': 0,
                'i_real_cable': 0,
                'nota_altitud': "Voltaje inválido",
                'altitud': altitud,
                'temp': temp_amb,
                'tiempo_respaldo': tiempo_respaldo
            }

        # PASO 2: Cálculo de Corriente Nominal (I_nom)
        if fases == 1:
            v_calc = 127 if voltaje < 200 else voltaje
            i_nom = (kva * 1000) / v_calc
        elif fases == 2:
            i_nom = (kva * 1000) / voltaje
        else:
            i_nom = (kva * 1000) / (math.sqrt(3) * voltaje)

        # PASO 3: Corriente de Diseño (I_diseno)
        i_diseno = i_nom * 1.25

        # PASO 4: Selección de Conductor y Derrateo
        if temp_amb <= 30: f_temp = 1.00
        elif temp_amb <= 35: f_temp = 0.96
        elif temp_amb <= 40: f_temp = 0.91
        elif temp_amb <= 45: f_temp = 0.87
        else: f_temp = 0.82

        if fases == 3:
            f_agrup = 0.80 
        else:
            f_agrup = 1.00

        seleccion_fase = "Fuera de Rango"
        seleccion_tierra = "N/A"
        seleccion_breaker = 0
        dv_real = 0.0
        i_real_cable = 0.0

        calibres = ['14', '12', '10', '8', '6', '4', '3', '2', '1', '1/0', '2/0', '3/0', '4/0', '250', '350', '500']

        for cal in calibres:
            specs = self.CABLE_DB[cal]
            if specs['75C'] >= i_diseno:
                amp_derrateada = specs['90C'] * f_temp * f_agrup
                if amp_derrateada >= i_diseno:
                    k_factor = 2 if fases == 1 else math.sqrt(3)
                    v_base = 127 if fases == 1 else voltaje
                    dv_pct = (k_factor * longitud * i_diseno * specs['Z_eff']) / (10 * v_base)
                    
                    if dv_pct < 3.0:
                        seleccion_fase = cal
                        dv_real = dv_pct
                        i_real_cable = min(amp_derrateada, specs['75C'])
                        break

        # PASO 6: Selección de Breaker
        for b in self.STANDARD_BREAKERS:
            if b >= i_diseno:
                seleccion_breaker = b
                break
        
        nota_altitud = ""
        if altitud > 2000:
            f_alt_breaker = 0.99 
            if altitud > 2500: f_alt_breaker = 0.98
            capacidad_breaker_sitio = seleccion_breaker * f_alt_breaker
            if capacidad_breaker_sitio < i_diseno:
                nota_altitud = f"⚠️ ALERTA: Por altitud ({altitud}m), el breaker de {seleccion_breaker}A baja a {capacidad_breaker_sitio:.1f}A reales."

        # PASO 7: Selección de Tierra (GND)
        cal_gnd_base = "1/0"
        for amp_limite, cal_gnd in self.GND_TABLE.items():
            if seleccion_breaker <= amp_limite:
                cal_gnd_base = cal_gnd
                break
        seleccion_tierra = cal_gnd_base

        return {
            'i_nom': round(i_nom, 2),
            'i_diseno': round(i_diseno, 2),
            'fase_sel': seleccion_fase,
            'gnd_sel': seleccion_tierra,
            'breaker_sel': seleccion_breaker,
            'dv_pct': round(dv_real, 2),
            'i_real_cable': round(i_real_cable, 2),
            'nota_altitud': nota_altitud,
            'altitud': altitud,
            'temp': temp_amb,
            'tiempo_respaldo': tiempo_respaldo
        }

class CalculadoraBaterias:
    def calcular(self, kva, kw, eficiencia, v_dc, tiempo_min, curvas, bat_voltaje_nominal=12):
        if not curvas:
            raise ValueError("No hay curvas de descarga asociadas a esta batería.")
        
        # 1. Potencia
        potencia_carga = float(kw) * 1000 if kw else float(kva) * 0.9 * 1000
        eff = float(eficiencia) / 100.0 if eficiencia and float(eficiencia) > 1 else 0.96
        potencia_dc_total = potencia_carga / eff
        
        # 2. Celdas y Series
        if not v_dc: raise ValueError("El UPS no tiene voltaje DC configurado.")
        v_dc = float(v_dc)
        n_celdas = v_dc / 2.0
        
        try:
            v_bat_nom = float(bat_voltaje_nominal)
            if v_bat_nom <= 0: v_bat_nom = 12.0
        except (ValueError, TypeError):
            v_bat_nom = 12.0
            
        bloques_serie = int(round(v_dc / v_bat_nom))
        w_celda_req = potencia_dc_total / n_celdas
        
        # 3. Curvas (Filtrar W y seleccionar FV)
        curvas_w = [c for c in curvas if c['unidad'] == 'W']
        if not curvas_w: raise ValueError("La batería no tiene curvas en Watts.")
        
        target_fv = 1.75
        curvas_fv_list = [c for c in curvas_w if abs(c['voltaje_corte_fv'] - target_fv) < 0.03]
        if not curvas_fv_list: # Fallback a otro FV si 1.75 no existe
            if curvas_w:
                target_fv = curvas_w[0]['voltaje_corte_fv']
                curvas_fv_list = [c for c in curvas_w if abs(c['voltaje_corte_fv'] - target_fv) < 0.03]
            else:
                raise ValueError("No se encontraron curvas de potencia (W) para la batería.")

        curvas_fv_list.sort(key=lambda x: x['tiempo_minutos'])
        
        # 4. Encontrar W/celda disponible para el tiempo solicitado
        tiempos = [c['tiempo_minutos'] for c in curvas_fv_list]
        valores_w_celda = [c['valor'] for c in curvas_fv_list]
        
        w_disponible_punto_solicitado = 0
        if not tiempo_min or tiempo_min <= 0:
            tiempo_min = 1 # Evitar división por cero
        
        if tiempo_min > tiempos[-1]:
             raise ValueError(f"Tiempo solicitado ({tiempo_min} min) excede el rango máximo de la batería ({tiempos[-1]} min).")
        
        w_disponible_punto_solicitado = self._interpolar(tiempos, valores_w_celda, tiempo_min)
        
        # 5. Calcular configuración del banco
        num_strings = math.ceil(w_celda_req / w_disponible_punto_solicitado) if w_disponible_punto_solicitado > 0 else float('inf')
        total_baterias = num_strings * bloques_serie
        
        # 6. Calcular curva de rendimiento del BANCO COMPLETO
        potencia_total_disponible_banco = [w * num_strings * n_celdas for w in valores_w_celda]
        
        # 7. Interpolar para encontrar el tiempo máximo de respaldo
        tiempo_maximo_calculado = self._interpolar_inverso(potencia_total_disponible_banco, tiempos, potencia_dc_total)
        tiempo_extra = tiempo_maximo_calculado - tiempo_min
        
        # 8. Preparar datos para la gráfica
        grafica_data = {
            'tiempos': tiempos,
            'potencia_disponible': potencia_total_disponible_banco,
            'potencia_requerida': potencia_dc_total,
            'tiempo_solicitado': tiempo_min,
            'tiempo_maximo': tiempo_maximo_calculado,
        }

        return {
            'bat_strings': num_strings, 
            'bat_series': bloques_serie,
            'bat_total': total_baterias,
            'bat_justificacion': "", # Justificación se genera en el reporte
            'bat_fv': target_fv,
            'bat_i_max': round(potencia_dc_total / (n_celdas * target_fv), 1),
            'tiempo_maximo_calculado': round(tiempo_maximo_calculado, 1),
            'tiempo_extra': round(tiempo_extra, 1),
            'grafica_data': grafica_data
        }

    def _interpolar(self, x_puntos, y_puntos, x_valor):
        if x_valor in x_puntos:
            return y_puntos[x_puntos.index(x_valor)]
        if x_valor < x_puntos[0]:
            return y_puntos[0] # Conservador
        if x_valor > x_puntos[-1]:
            return y_puntos[-1] # Extrapolación simple

        for i in range(len(x_puntos)-1):
            if x_puntos[i] < x_valor < x_puntos[i+1]:
                x1, x2 = x_puntos[i], x_puntos[i+1]
                y1, y2 = y_puntos[i], y_puntos[i+1]
                return y1 + (x_valor - x1) * (y2 - y1) / (x2 - x1)
        return y_puntos[-1]

    def _interpolar_inverso(self, y_puntos, x_puntos, y_valor):
        # Asumimos que y_puntos es decreciente
        if y_valor > y_puntos[0]:
            return x_puntos[0] # Si se requiere más potencia de la que da al inicio, el tiempo es el mínimo
        if y_valor < y_puntos[-1]:
            return x_puntos[-1] # Si se requiere menos que al final, el tiempo es el máximo
        
        for i in range(len(y_puntos)-1):
            if y_puntos[i] > y_valor >= y_puntos[i+1]:
                y1, y2 = y_puntos[i], y_puntos[i+1]
                x1, x2 = x_puntos[i], x_puntos[i+1]
                # Interpolación lineal inversa
                return x1 + (y_valor - y1) * (x2 - x1) / (y2 - y1)
        return x_puntos[0] # Fallback