import os
import pandas as pd
import numpy as np
import time
import joblib

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import brier_score_loss, roc_auc_score, classification_report

def main():
    DATASET_DIRECTORY ="../Data/"
    
    df = pd.concat([pd.read_csv(os.path.join(DATASET_DIRECTORY, f)) for f in ["Merged01.csv", "Merged02.csv", "Extra.csv"]],
        axis=0,
        ignore_index=True
    )
    
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




if __name__ == "__main__":
    main()