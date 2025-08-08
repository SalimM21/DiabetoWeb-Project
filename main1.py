from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

model = joblib.load(r'C:\Users\hp\Desktop\projet\model.pkl')

if hasattr(model, 'feature_namesin'):
    feature_names = list(model.feature_namesin)
else:
    raise ValueError("Impossible de retrouver les noms de colonnes d'entraînement automatiquement.")

app = FastAPI()

class FeaturesInput(BaseModel):
    features: dict

@app.post("/predict")
async def predict(data: FeaturesInput):
    try:
        features = data.features

        input_data = {col: 0 for col in feature_names}

        for key in features:
            if key in input_data:
                input_data[key] = features[key]

        city = features.get("city_name")
        if city:
            citycol = f"city{city}"
            if city_col in input_data:
                input_data[city_col] = 1

        X_input = pd.DataFrame([input_data], columns=feature_names)

        prediction = model.predict(X_input)[0]
        prediction_mad = prediction * 1_000_000

        return {"prediction_mad": round(prediction_mad, 2)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Person(BaseModel):
    nom:str
    prenom:str
    age:int
    
@app.get('/hello',description='this is get method')
async def hello():
    return {'message':'hello guys'}

@app.post('/ajoute',description='this post method')
async def post(person:Person):
    return {'message':f"votre nom est {person.nom} {person.prenom} , votre age est {person.age}"}

@app.put('/modify')
async def modify(person:Person):
    return {'message':f" pesron est {person.nom} {person.prenom} , votre age est {person.age} est modifie"}

@app.delete('/delete',deprecated=True)
async def deleteee(person:Person):
    return {'message':f" pesron  {person.nom} {person.prenom} est supprimer"}