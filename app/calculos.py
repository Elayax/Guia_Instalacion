import math

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
        
        # Simulación de variables ambientales
        altitud = 2240 
        temp_amb = 30 # °C

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
        n_celdas = v_dc / 2.0 # Estándar plomo-ácido (2V/celda)
        
        try:
            v_bat_nom = float(bat_voltaje_nominal)
            if v_bat_nom <= 0: v_bat_nom = 12.0
        except:
            v_bat_nom = 12.0
            
        bloques_serie = int(round(v_dc / v_bat_nom))
        w_celda_req = potencia_dc_total / n_celdas
        
        # 3. Curvas (Filtrar W)
        curvas_w = [c for c in curvas if c['unidad'] == 'W']
        if not curvas_w: raise ValueError("La batería no tiene curvas en Watts.")
        
        # 4. Seleccionar FV (Norma/Estándar: 1.70V o 1.75V)
        target_fv = 1.70
        curvas_fv = [c for c in curvas_w if abs(c['voltaje_corte_fv'] - target_fv) < 0.03]
        if not curvas_fv:
            target_fv = 1.75
            curvas_fv = [c for c in curvas_w if abs(c['voltaje_corte_fv'] - target_fv) < 0.03]
        if not curvas_fv and curvas_w: # Fallback
            target_fv = curvas_w[0]['voltaje_corte_fv']
            curvas_fv = [c for c in curvas_w if abs(c['voltaje_corte_fv'] - target_fv) < 0.03]
            
        if not curvas_fv: raise ValueError("No se encontraron curvas compatibles para el cálculo.")
        
        # 5. Interpolación Tiempo
        curvas_fv.sort(key=lambda x: x['tiempo_minutos'])
        tiempos = [c['tiempo_minutos'] for c in curvas_fv]
        valores = [c['valor'] for c in curvas_fv]
        
        w_disponible = 0
        if tiempo_min in tiempos:
            w_disponible = valores[tiempos.index(tiempo_min)]
        elif tiempo_min < tiempos[0]:
            w_disponible = valores[0] # Conservador
        elif tiempo_min > tiempos[-1]:
            raise ValueError(f"Tiempo solicitado ({tiempo_min} min) excede el rango de la batería ({tiempos[-1]} min).")
        else:
            for i in range(len(tiempos)-1):
                if tiempos[i] < tiempo_min < tiempos[i+1]:
                    # Interpolación Lineal
                    t1, t2 = tiempos[i], tiempos[i+1]
                    v1, v2 = valores[i], valores[i+1]
                    w_disponible = v1 + (tiempo_min - t1) * (v2 - v1) / (t2 - t1)
                    break
                    
        num_strings = math.ceil(w_celda_req / w_disponible)
        total_baterias = num_strings * bloques_serie
        
        # Cálculos eléctricos finales
        v_corte_total = n_celdas * target_fv
        i_descarga_nom = potencia_dc_total / v_dc
        i_descarga_max = potencia_dc_total / v_corte_total
        
        justificacion = f"""
        <div style="font-size: 0.9rem;">
        <p><strong>1. Potencia DC Requerida:</strong><br>
        $$ P_{{DC}} = \\frac{{P_{{load}}}}{{\\eta}} = \\frac{{{potencia_carga:.0f}W}}{{{eff:.2f}}} = {potencia_dc_total:.0f} W $$</p>
        
        <p><strong>2. Requerimiento por Celda:</strong><br>
        $$ N_{{celdas}} = \\frac{{{v_dc}V}}{{2V}} = {int(n_celdas)} \\text{{ celdas}} $$<br>
        $$ W_{{req}} = \\frac{{{potencia_dc_total:.0f} W}}{{{int(n_celdas)}}} = {w_celda_req:.2f} \\text{{ W/celda}} $$</p>
        
        <p><strong>3. Capacidad Disponible (Interpolación):</strong><br>
        $$ W_{{disp}} (@{tiempo_min}min, {target_fv}V/c) = {w_disponible:.2f} \\text{{ W/celda}} $$</p>
        
        <p><strong>4. Configuración del Banco:</strong><br>
        $$ Strings = \\lceil \\frac{{{w_celda_req:.2f}}}{{{w_disponible:.2f}}} \\rceil = \\mathbf{{{num_strings}}} \\text{{ (Paralelo)}} $$<br>
        $$ Bloques_{{serie}} = \\frac{{{v_dc}V}}{{{v_bat_nom}V}} = \\mathbf{{{bloques_serie}}} \\text{{ (Serie)}} $$<br>
        $$ Total_{{baterias}} = {num_strings} \\times {bloques_serie} = \\mathbf{{{total_baterias}}} \\text{{ Unidades}} $$</p>
        
        <p><strong>5. Parámetros Eléctricos Finales:</strong><br>
        $$ V_{{corte\_total}} = {int(n_celdas)} \\times {target_fv}V = {v_corte_total:.1f} V $$<br>
        $$ I_{{descarga}} = {i_descarga_nom:.1f}A \\text{{ (Nom)}} \\to {i_descarga_max:.1f}A \\text{{ (Max)}} $$</p>
        </div>
        """
        
        return {
            'bat_strings': num_strings, 
            'bat_series': bloques_serie,
            'bat_total': total_baterias,
            'bat_justificacion': justificacion, 
            'bat_fv': target_fv,
            'bat_i_max': round(i_descarga_max, 1)
        }