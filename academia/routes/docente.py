import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Docente(BaseModel):
    nombre: str
    apellido_pat: str
    apellido_mat: str
    ci: str
    correo: str
    especialidad: str

@router.get("/")
async def listar_docentes(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_docente, nombre, apellido_pat, apellido_mat, ci,
               correo, especialidad
        FROM docente
        ORDER BY id_docente
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            docentes = await cursor.fetchall()
            if not docentes:
                return {"mensaje": "No hay docentes registrados"}
            return docentes
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar docentes")

@router.get("/{id_docente}")
async def obtener_docente(id_docente: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_docente, nombre, apellido_pat, apellido_mat, ci,
               correo, especialidad
        FROM docente
        WHERE id_docente = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_docente,))
            docente = await cursor.fetchone()
            if not docente:
                raise HTTPException(status_code=404, detail="Docente no encontrado")
            return docente
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar docente")

@router.post("/")
async def insertar_docente(docente: Docente, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO docente(nombre, apellido_pat, apellido_mat, ci, correo, especialidad)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_docente
    """
    parametros = (
        docente.nombre,
        docente.apellido_pat,
        docente.apellido_mat,
        docente.ci,
        docente.correo,
        docente.especialidad
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Docente registrado exitosamente", "id_docente": nuevo_id["id_docente"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar el docente")

@router.put("/{id_docente}")
async def actualizar_docente(id_docente: int, docente: Docente, conn=Depends(get_conexion)):
    consulta = """
        UPDATE docente
        SET nombre = %s, apellido_pat = %s, apellido_mat = %s,
            ci = %s, correo = %s, especialidad = %s
        WHERE id_docente = %s
        RETURNING id_docente
    """
    parametros = (
        docente.nombre,
        docente.apellido_pat,
        docente.apellido_mat,
        docente.ci,
        docente.correo,
        docente.especialidad,
        id_docente
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Docente no encontrado")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Docente actualizado correctamente", "id_docente": actualizado["id_docente"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el docente")

@router.delete("/{id_docente}")
async def eliminar_docente(id_docente: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM docente WHERE id_docente = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_docente,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Docente no encontrado")
            await conn.commit()
            return {"mensaje": "Docente eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el docente")
