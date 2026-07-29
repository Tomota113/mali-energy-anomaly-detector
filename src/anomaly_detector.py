import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class EnergyAnomalyDetector:
    """
    Moteur de détection d'anomalies basé sur l'algorithme Isolation Forest (scikit-learn).
    Calcule des descripteurs statistiques (features) et prédit les comportements anormaux.
    """
    
    def __init__(self, contamination=0.05, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=150
        )
        self.scaler = StandardScaler()
        self.feature_cols = [
            'consumption_kwh', 'voltage_v', 'current_a', 'power_factor',
            'rolling_avg_kwh', 'rolling_std_kwh', 'hour_of_day'
        ]
        
    def prepare_features(self, df):
        """
        Extrait et construit les caractéristiques pour le modèle ML.
        """
        data = df.copy()
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data = data.sort_values(['meter_id', 'timestamp'])
        
        # Extraction de caractéristiques temporelles
        data['hour_of_day'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        # Moyennes mobiles et écart-types par compteur
        data['rolling_avg_kwh'] = data.groupby('meter_id')['consumption_kwh'].transform(
            lambda x: x.rolling(window=6, min_periods=1).mean()
        )
        data['rolling_std_kwh'] = data.groupby('meter_id')['consumption_kwh'].transform(
            lambda x: x.rolling(window=6, min_periods=1).std().fillna(0)
        )
        
        return data

    def fit_predict(self, df):
        """
        Entraîne le modèle et retourne le DataFrame enrichi des prédictions d'anomalies.
        """
        data = self.prepare_features(df)
        X = data[self.feature_cols].copy()
        
        # Normalisation des données
        X_scaled = self.scaler.fit_transform(X)
        
        # Prédiction : -1 pour anomalie, 1 pour normal
        predictions = self.model.fit_predict(X_scaled)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        # Conversion des prédictions : True si anomalie, False sinon
        data['is_detected_anomaly'] = (predictions == -1)
        # Normalisation du score entre 0 (très normal) et 1 (anomalie sévère)
        data['anomaly_score'] = np.round(1 - (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min()), 3)
        
        return data

    def compute_summary_kpis(self, df_processed, price_per_kwh_xof=120):
        """
        Calcule les métriques clés de performance (KPIs).
        """
        total_readings = len(df_processed)
        anomalies_df = df_processed[df_processed['is_detected_anomaly']]
        anomalies_count = len(anomalies_df)
        anomaly_rate = (anomalies_count / total_readings) * 100 if total_readings > 0 else 0
        
        total_kwh = df_processed['consumption_kwh'].sum()
        suspicious_kwh = anomalies_df['consumption_kwh'].sum()
        estimated_financial_risk_xof = suspicious_kwh * price_per_kwh_xof
        
        return {
            'total_readings': total_readings,
            'anomalies_count': anomalies_count,
            'anomaly_rate_percent': round(anomaly_rate, 2),
            'total_kwh_consumed': round(total_kwh, 2),
            'suspicious_kwh': round(suspicious_kwh, 2),
            'estimated_financial_risk_xof': round(estimated_financial_risk_xof, 0)
        }
