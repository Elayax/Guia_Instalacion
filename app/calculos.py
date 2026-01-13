import math

# --- AQUÍ DEBE DECIR EXACTAMENTE ESTO: ---
class CalculadoraUPS: 
    def __init__(self):
        # Base de datos de Cables (NOM-001 Tabla 310-15(b)(16))
        # Formato: 'AWG': {'75C': amps, '90C': amps, 'Z_eff': ohms/km (aprox FP 0.9 en tubo acero)}
        self.cable_db = {
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
        self.gnd_table = {
            15: '14', 20: '12', 60: '10', 100: '8',
            200: '6', 300: '4', 400: '3', 500: '2',
            600: '1', 800: '1/0'
        }

        # Breakers comerciales (Tabla 240-6(A))
        self.standard_breakers = [15, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                                  125, 150, 175, 200, 225, 250, 300, 350, 400, 500, 600]

    def calcular(self, datos):
        # 1. Extracción de variables
        kva = float(datos.get('kva'))
        voltaje = int(datos.get('voltaje'))
        fases = int(datos.get('fases'))
        longitud = float(datos.get('longitud'))
        
        # Simulación de variables ambientales
        altitud = 2240 
        temp_amb = 30 # °C

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
            specs = self.cable_db[cal]
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
        for b in self.standard_breakers:
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
        for amp_limite, cal_gnd in self.gnd_table.items():
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
            'temp': temp_amb
        }