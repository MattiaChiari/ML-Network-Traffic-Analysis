import os
import pandas as pd
import numpy as np
import time
import joblib

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.metrics import accuracy_score,f1_score

def main():
    start_time = time.time()
    DATASET_DIRECTORY ="../../Data/"
    
    df = pd.concat([pd.read_csv(os.path.join(DATASET_DIRECTORY, f)) for f in ["Merged01.csv", "Merged02.csv", "Extra.csv"]],
        axis=0,
        ignore_index=True
    )
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    
    X_columns = [
        'Header_Length', 'Time_To_Live', 
        'Rate', 'fin_flag_number', 'syn_flag_number', 
        'rst_flag_number', 'psh_flag_number', 'ack_flag_number', 
        'ece_flag_number', 'cwr_flag_number', 'ack_count', 
        'syn_count', 'fin_count', 'rst_count', 'HTTP', 'HTTPS', 
        'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP', 'UDP', 'DHCP',
        'ARP', 'ICMP', 'IGMP', 'IPv', 'Tot sum', 'Min', 'Max', 
        'AVG', 'Std', 'Tot size', 'IAT', 'Number'
    ]
    df['Label'] = np.where(df['Label'] == 'BENIGN', 0, 1)
    y_column = 'Label'
    
    X = df[X_columns]
    y = df[y_column]
    
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

    lgbm_bin = lgb.LGBMClassifier(
        n_estimators=2000, 
        learning_rate=0.02, 
        num_leaves=63,
        min_child_samples=5, 
        subsample=0.8, 
        colsample_bytree=0.8,
        reg_alpha=0.1, 
        reg_lambda=0.1,
        objective='binary', 
        random_state=42,
        n_jobs = -1,
        verbose = -1  
    )   
    
    callbacks_bin = [
        lgb.early_stopping(stopping_rounds=50, verbose=False),
        lgb.log_evaluation(period=100)
    ]
    
    lgbm_bin.fit(
        X_train, y_train,               
        eval_set=[(X_val, y_val)],
        callbacks=callbacks_bin
    )
    
    calibrated_lgbm_bin = CalibratedClassifierCV(
        FrozenEstimator(lgbm_bin),   
        method='isotonic'
    )
    calibrated_lgbm_bin.fit(X_val, y_val) 
    y_probs = calibrated_lgbm_bin.predict_proba(X_test)[:, 1]
    y_pred  = calibrated_lgbm_bin.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    brier   = brier_score_loss(y_test, y_probs)
    roc_auc = roc_auc_score(y_test, y_probs)
    
    # -- Salvataggio Modello --
    joblib.dump(calibrated_lgbm_bin, "model_binary.pkl")

    
    print(f"Accuracy: {accuracy:.2f}")
    print(f"F1-Score: {f1:.2f}")
    print(f"Brier Score : {brier:.4f}")   
    print(f"ROC-AUC Score : {roc_auc:.4f}")
    end_time = time.time()
    print(f"\nTempo totale di esecuzione: {(end_time - start_time)/60:.2f} minuti.")


if __name__ == "__main__":
    main()