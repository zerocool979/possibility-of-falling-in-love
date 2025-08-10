import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
# import pickle # Menggunakan joblib, jadi pickle tidak lagi dibutuhkan
import joblib

def improve_and_save_model():
    print("Memuat dataset...")
    # Load the dataset
    data = pd.read_csv('Speed-Dating-Data.csv', encoding='ISO-8859-1')
    
    # Preprocessing
    print("Melakukan pra-pemrosesan data...")
    # Select relevant features based on the previous model and your app's form
    features = [
        'age', 'age_o', 'samerace', 'go_out', 'imprace', 'imprelig', 'int_corr',
        'attr1_1', 'sinc1_1', 'intel1_1', 'fun1_1', 'amb1_1', 'shar1_1',
        'pf_o_att', 'pf_o_sin', 'pf_o_int', 'pf_o_fun', 'pf_o_amb', 'pf_o_sha'
    ]
    target = 'match'
    
    # Filter out rows with too many missing values in key features
    data = data.dropna(subset=features + [target], how='any')
    
    X = data[features]
    y = data[target]
    
    # Impute missing values with the mean
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)
    
    print("Melatih model dan mencari hyperparameter terbaik...")
    # Define the model and parameter grid for GridSearchCV
    model = RandomForestClassifier(random_state=42)
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20],
        'min_samples_split': [2, 5]
    }
    
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_imputed, y)
    
    best_model = grid_search.best_estimator_
    
    print(f"Model terbaik ditemukan dengan parameter: {grid_search.best_params_}")
    print(f"Akurasi model terbaik: {grid_search.best_score_:.4f}")
    
    print("Menyimpan model dan imputer...")
    # Save the best model and the imputer using joblib
    joblib.dump(best_model, 'best_model.pkl')
    joblib.dump(imputer, 'imputer_improved.pkl')
    
    print("Model berhasil diperbarui dan disimpan.")
import secrets

def generate_secret_key(length=32):
    """
    Generates a strong, random string for use as a SECRET_KEY.

    Args:
        length (int): The length of the key to generate. Defaults to 32.

    Returns:
        str: The generated secret key.
    """
    return secrets.token_urlsafe(length)

if __name__ == '__main__':
    improve_and_save_model()
    print("membuat kunci......")
    secret_key = generate_secret_key()
    print(f"SECRET_KEY = '{secret_key}'")