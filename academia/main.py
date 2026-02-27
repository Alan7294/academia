from fastapi import FastAPI
from routes import alumno
from routes import docente
from routes import curso
from routes import clase
from routes import inscripcion
from routes import nota
from routes import tipo
from routes import administrador

app = FastAPI()

app.include_router(alumno.router, prefix="/alumno", tags=["Alumno"])
app.include_router(docente.router, prefix="/docente", tags=["Docente"])
app.include_router(curso.router, prefix="/curso", tags=["Curso"])
app.include_router(clase.router, prefix="/clase", tags=["Clase"])
app.include_router(inscripcion.router, prefix="/inscripcion", tags=["Inscripcion"])
app.include_router(nota.router, prefix="/nota", tags=["Nota"])
app.include_router(tipo.router, prefix="/tipo", tags=["Tipo_Usuario"])
app.include_router(administrador.router, prefix="/administrador", tags=["Administrador"])