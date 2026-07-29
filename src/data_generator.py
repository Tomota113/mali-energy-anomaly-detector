import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_energy_data(days=90, meters_count=5, anomaly_ratio=0.05, random_seed=42):
    """
    Génère un jeu de données synthétique réaliste de consommation électrique.
    Simule des compteurs intelligents avec des données horaires et l'injection d'anomalies (fraudes/surcharges).
    """
    np.random.seed(random_seed)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='h')
    
    records = []
    
    for meter_idx in range(1, meters_count + 1):
        meter_id = f"METER-ML-{1000 + meter_idx}"
        base_consumption = 2.5 + np.random.uniform(0.5, 2.0)
        
        for dt in dates:
            # Variations temporelles (cycles jour/nuit et semaine)
            hour = dt.hour
            is_weekend = dt.weekday() >= 5
            
            # Motif quotidien de consommation (pic le soir)
            daily_pattern = np.sin((hour - 6) * np.pi / 12) if 6 <= hour <= 23 else -0.5
            weekend_factor = 1.2 if is_weekend else 1.0
            
            # Consommation normale en kWh
            kwh = max(0.2, base_consumption + daily_pattern * 1.5 + np.random.normal(0, 0.4)) * weekend_factor
            
            # Tension nominale autour de 230V avec fluctuations légères (220V - 240V)
            voltage = 230.0 + np.random.normal(0, 3.5)
            
            # Facteur de puissance habituel (0.85 à 0.98)
            power_factor = np.clip(np.random.normal(0.92, 0.03), 0.70, 0.99)
            
            # Courant en Ampères P = U * I * cos(phi) => I = P / (U * cos(phi))
            current = (kwh * 1000) / (voltage * power_factor)
            
            # Injection d'anomalies (ex: fraude par dérivation ou surconsommation suspecte)
            is_anomaly = False
            anomaly_type = "NORMAL"
            
            if np.random.rand() < anomaly_ratio:
                is_anomaly = True
                rand_val = np.random.rand()
                if rand_val < 0.4:
                    # Fraude type dérivation : consommation chute à zéro alors que la tension reste normale
                    kwh = np.random.uniform(0.0, 0.1)
                    current = 0.1
                    anomaly_type = "CHUTE_SUSPECTE_FRAUDE"
                elif rand_val < 0.7:
                    # Surcharge / Pic inhabituel : pic de consommation anormal
                    kwh = kwh * np.random.uniform(3.5, 6.0)
                    current = (kwh * 1000) / (voltage * power_factor)
                    anomaly_type = "SURCHARGE_ANORMALE"
                else:
                    # Chute de tension critique / Facteur de puissance dégradé
                    voltage = np.random.uniform(150.0, 180.0)
                    power_factor = np.random.uniform(0.40, 0.60)
                    anomaly_type = "ANOMALIE_TENSION_FP"

            records.append({
                'timestamp': dt,
                'meter_id': meter_id,
                'consumption_kwh': round(float(kwh), 3),
                'voltage_v': round(float(voltage), 2),
                'current_a': round(float(current), 2),
                'power_factor': round(float(power_factor), 3),
                'is_anomaly_ground_truth': int(is_anomaly),
                'anomaly_type': anomaly_type
            })
            
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_energy_data(days=60, meters_count=5)
    df.to_csv("/home/ibrahim-tomota/Documents/code/mali-energy-anomaly-detector/data/energy_consumption_sample.csv", index=False)
    print(f"Dataset synthétique généré avec succès ({len(df)} lignes).")
