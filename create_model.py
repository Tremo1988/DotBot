import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input

# Parametri del modello
timesteps = 48
features = 5

# Costruzione del modello
model = Sequential()
model.add(Input(shape=(timesteps, features)))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))  # Previsione del prezzo successivo

# Compilazione
model.compile(optimizer='adam', loss='mean_squared_error')

# Dummy training per inizializzare i pesi
X_dummy = np.random.rand(100, timesteps, features)
y_dummy = np.random.rand(100)
model.fit(X_dummy, y_dummy, epochs=1, batch_size=32)

# Salvataggio del modello
model.save("lstm_model.h5")

print("✅ Modello salvato come lstm_model.h5 compatibile con TensorFlow 2.13.0")
