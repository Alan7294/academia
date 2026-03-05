from fastapi import FastAPI
from routes import alumno
from routes import docente
from routes import clase
from routes import inscripcion
from routes import nota
from routes import tipo
from routes import administrador
from routes import materia
from routes import carrera
from routes import especialidad
from routes import usuario
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(alumno.router, prefix="/alumno", tags=["Alumno"])
app.include_router(docente.router, prefix="/docente", tags=["Docente"])
app.include_router(materia.router, prefix="/materia", tags=["Materia"])
app.include_router(clase.router, prefix="/clase", tags=["Clase"])
app.include_router(inscripcion.router, prefix="/inscripcion", tags=["Inscripcion"])
app.include_router(nota.router, prefix="/nota", tags=["Nota"])
app.include_router(tipo.router, prefix="/tipo", tags=["Tipo_Usuario"])
app.include_router(administrador.router, prefix="/administrador", tags=["Administrador"])
app.include_router(carrera.router, prefix="/carrera", tags=["Carrera"])
app.include_router(especialidad.router, prefix="/especialidad", tags=["Especialidad"])
app.include_router(usuario.router, prefix="/usuario", tags=["Usuario"])
print("hola mundo")
