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
    df = df[df['Label'] != 'BENIGN'].copy()
    
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
    mappatura_label = {
        'DDOS-PSHACK_FLOOD': 1,
        'MIRAI-GREIP_FLOOD': 2,
        'DOS-UDP_FLOOD': 3,
        'DNS_SPOOFING': 4,
        'DDOS-ICMP_FLOOD': 5,
        'DDOS-TCP_FLOOD': 6,
        'DDOS-SYN_FLOOD': 7,
        'DDOS-UDP_FLOOD': 8,
        'MITM-ARPSPOOFING': 9,
        'DDOS-SYNONYMOUSIP_FLOOD': 10,
        'DOS-TCP_FLOOD': 11,
        'VULNERABILITYSCAN': 12,
        'DOS-SYN_FLOOD': 13,
        'DDOS-RSTFINFLOOD': 14,
        'DDOS-SLOWLORIS': 15,
        'DDOS-ICMP_FRAGMENTATION': 16,
        'MIRAI-GREETH_FLOOD': 17,
        'RECON-HOSTDISCOVERY': 18,
        'MIRAI-UDPPLAIN': 19,
        'RECON-PORTSCAN': 20,
        'DDOS-ACK_FRAGMENTATION': 21,
        'DDOS-UDP_FRAGMENTATION': 22,
        'RECON-OSSCAN': 23,
        'BACKDOOR_MALWARE': 24,
        'DOS-HTTP_FLOOD': 25,
        'XSS': 26,
        'DDOS-HTTP_FLOOD': 27,
        'BROWSERHIJACKING': 28,
        'SQLINJECTION': 29,
        'DICTIONARYBRUTEFORCE': 30,
        'COMMANDINJECTION': 31,
        'RECON-PINGSWEEP': 32,
        'UPLOADING_ATTACK': 33
    }
    df['Label'] = df['Label'].map(mappatura_label)
    y_column = 'Label' 
    
    print(df.info(), "\n")
    print(df[y_column].unique(), "\n")
    
    X = df[X_columns]
    y = df[y_column]
    
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

    model_lgbm = lgb.LGBMClassifier(
        n_estimators = 2000,      
        learning_rate = 0.02,
        num_leaves = 63,               
        max_depth = -1,                 
        min_child_samples = 5,          
        subsample = 0.8,               
        colsample_bytree = 0.8,        
        reg_alpha = 0.1,                
        reg_lambda = 0.1,               
        n_jobs = -1,        
        random_state = 42,
        verbose = -1         
    )
    
    callbacks_lgbm = [
        lgb.early_stopping(stopping_rounds=100, verbose=True),
        lgb.log_evaluation(period=100)
    ]
    
    model_lgbm.fit(
        X_train, y_train,       
        eval_set = [(X_val, y_val)],  
        callbacks = callbacks_lgbm
    )

    calibrated_lgbm = CalibratedClassifierCV(
        FrozenEstimator(model_lgbm),
        method='sigmoid'    
    )
    
    calibrated_lgbm.fit(X_val, y_val) 
    y_probs = calibrated_lgbm.predict_proba(X_test)
    y_pred  = calibrated_lgbm.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    roc_auc = roc_auc_score(y_test, y_probs,multi_class='ovr',average='weighted')
    
    # -- Salvataggio Modello --
    joblib.dump(calibrated_lgbm, "model_multi.pkl")
    
    print(f"Accuracy: {accuracy:.2f}")
    print(f"F1-Score: {f1:.2f}")
    print(f"ROC-AUC Score : {roc_auc:.4f}")
    end_time = time.time()
    print(f"\nTempo totale di esecuzione: {(end_time - start_time)/60:.2f} minuti.")

    
if __name__ == "__main__":
    main()