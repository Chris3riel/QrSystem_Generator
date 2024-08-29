from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles

from typing import List
from datetime import datetime
import qrcode
import io
import datetime as dt
import subprocess
import os
import json


DATABASE_URL = "postgresql://chris:admin@localhost/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Configuración de CORS
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5500",  
    "http://192.168.1.31",   
    "http://0.0.0.0:8000", 
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)  


templates = Jinja2Templates(directory="templates")

class MyTable(Base):
    __tablename__ = "mytable"
    id = Column(Integer, primary_key=True, index=True)
    noSerie = Column(Integer, index=True)
    fecha = Column(Date, index=True)
    sap = Column(Integer, index=True)
    prev = Column(Boolean, index=True)
    amp = Column(String, index=True)
    capacidad = Column(String, index=True)
    rpm = Column(String, index=True)
    corr = Column(String, index=True)
    voltaje = Column(String, index=True)
    frame = Column(String, index=True)
    tels = Column(String, index=True)
    direccion = Column(String, index=True)
    empresa = Column(String, index=True)
    descripcion = Column(String, index=True)

class MyTableCreate(BaseModel):
    noSerie: int
    fecha: str
    sap: int
    prev: bool
    amp: str
    capacidad: str
    rpm: str
    corr: str
    voltaje: str
    frame: str
    tels: str
    direccion: str
    empresa: str
    descripcion: str

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
async def name(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "name": "Cammer Corporativo Industrial"})

@app.get("/all", response_model=List[MyTableCreate])
def read_all_data(db: Session = Depends(get_db)):
    # Subquery para obtener la fecha más reciente para cada noSerie
    subquery = (
        db.query(
            MyTable.noSerie,
            func.max(MyTable.fecha).label('max_fecha')
        )
        .group_by(MyTable.noSerie)
        .subquery()
    )

    # Obtener los registros con la fecha más reciente por noSerie
    items = db.query(MyTable)\
        .join(subquery, (MyTable.noSerie == subquery.c.noSerie) & (MyTable.fecha == subquery.c.max_fecha))\
        .all()

    # Formatear la fecha antes de devolver los registros
    for item in items:
        item.fecha = item.fecha.strftime("%d/%m/%Y")

    return items


@app.get("/data/{item_noSerie}")
def read_data(item_noSerie: int, db: Session = Depends(get_db)):
    item = db.query(MyTable).filter(MyTable.noSerie == item_noSerie).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/data_card/{item_noSerie}", response_class=HTMLResponse)
def read_data_card(item_noSerie: int, db: Session = Depends(get_db)):
    # Almacenar la fecha actual
    fecha_actual = dt.datetime.now().date()

    # Buscar el registro con la fecha más reciente o la más cercana a la fecha actual para el número de serie dado
    item = db.query(MyTable)\
        .filter(MyTable.noSerie == item_noSerie)\
        .order_by(
            MyTable.fecha.desc(),  # Primero ordena por la fecha más reciente
            func.abs(func.extract('epoch', func.age(MyTable.fecha, fecha_actual)))  # Luego por la fecha más cercana a la actual
        ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return templates.TemplateResponse("card.html", {"request": {}, "item": item})


@app.get("/qrcode/{item_noSerie}")
def get_qrcode(item_noSerie: int):
    url = f"http://0.0.0.0:8000/data_card/{item_noSerie}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")   
    
@app.post("/carga")
async def create_etiqueta(data: MyTableCreate, db: Session = Depends(get_db)):
    try:
        # Convertir la fecha en formato DD/MM/YYYY a objeto date
        fecha_dt = datetime.strptime(data.fecha, "%d/%m/%Y").date()

        # Crear objeto MyTable
        carga = MyTable(
            noSerie=data.noSerie,
            fecha=fecha_dt,
            sap=data.sap,
            prev=data.prev,
            amp=data.amp,
            capacidad=data.capacidad,
            rpm=data.rpm,
            corr=data.corr,
            voltaje=data.voltaje,
            frame=data.frame,
            tels=data.tels,
            direccion=data.direccion,
            empresa=data.empresa,
            descripcion=data.descripcion
        )

        # Añadir a la base de datos
        db.add(carga)
        db.commit()
        db.refresh(carga)

        # Devolver el objeto creado como JSON
        return carga
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/upload")
async def show_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/view", response_class=HTMLResponse)
def view_data(request: Request):
    return templates.TemplateResponse("view.html", {"request": request})

@app.get("/update/{noSerie}")
def update_form(noSerie: str, request: Request, db: Session = Depends(get_db)):
    # Obtener el registro más reciente para el número de serie
    item = (
        db.query(MyTable)
        .filter(MyTable.noSerie == noSerie)
        .order_by(MyTable.fecha.desc())
        .first()
    )
    
    if item:
        # Convertir la fecha a una cadena en formato DD/MM/YYYY
        fecha_str = item.fecha.strftime("%d/%m/%Y")
        
        # Convertir la cadena de fecha de nuevo a un objeto date
        fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y").date()
        
        # Actualizar el objeto item con la fecha convertida
        item.fecha = fecha_dt
    
    return templates.TemplateResponse("update_form.html", {"request": request, "item": item})


@app.get("/historico/{item_noSerie}")
def historial_form( item_noSerie: int, db: Session = Depends(get_db)):

    items = db.query(MyTable).filter(MyTable.noSerie == item_noSerie).all()
    
    return items

@app.get("/run_qr_code_detector")
async def run_qr_code_detector():
    try:
        # Ejecutar el script de OpenCV en segundo plano
        process = subprocess.Popen(["python", "qr_detector.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Devolver una respuesta rápida
        return {"message": "El script de detección de códigos QR se está ejecutando."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
