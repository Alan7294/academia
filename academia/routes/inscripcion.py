from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from config.conexionDB import get_conexion

router = APIRouter()

class Inscripcion(BaseModel):
    id_alumno: int
    id_clase: int
    fecha_inscripcion: Optional[str] = None 

@router.get("/")
async def listar_inscripciones(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_inscripcion, id_alumno, id_clase, fecha_inscripcion
        FROM inscripcion
        ORDER BY id_inscripcion
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            inscripciones = await cursor.fetchall()
            if not inscripciones:
                return {"mensaje": "No hay inscripciones registradas"}
            return inscripciones
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar inscripciones")

@router.get("/{id_inscripcion}")
async def obtener_inscripcion(id_inscripcion: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_inscripcion, id_alumno, id_clase, fecha_inscripcion
        FROM inscripcion
        WHERE id_inscripcion = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_inscripcion,))
            inscripcion = await cursor.fetchone()
            if not inscripcion:
                raise HTTPException(status_code=404, detail="Inscripción no encontrada")
            return inscripcion
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar inscripción")

@router.post("/")
async def insertar_inscripcion(inscripcion: Inscripcion, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO inscripcion(id_alumno, id_clase, fecha_inscripcion)
        VALUES (%s, %s, %s)
        RETURNING id_inscripcion
    """
    parametros = (
        inscripcion.id_alumno,
        inscripcion.id_clase,
        inscripcion.fecha_inscripcion
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Inscripción registrada exitosamente", "id_inscripcion": nuevo_id["id_inscripcion"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar la inscripción")

@router.put("/{id_inscripcion}")
async def actualizar_inscripcion(id_inscripcion: int, inscripcion: Inscripcion, conn=Depends(get_conexion)):
    consulta = """
        UPDATE inscripcion
        SET id_alumno = %s, id_clase = %s, fecha_inscripcion = %s
        WHERE id_inscripcion = %s
        RETURNING id_inscripcion
    """
    parametros = (
        inscripcion.id_alumno,
        inscripcion.id_clase,
        inscripcion.fecha_inscripcion,
        id_inscripcion
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Inscripción no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Inscripción actualizada correctamente", "id_inscripcion": actualizado["id_inscripcion"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la inscripción")

@router.delete("/{id_inscripcion}")
async def eliminar_inscripcion(id_inscripcion: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM inscripcion WHERE id_inscripcion = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_inscripcion,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Inscripción no encontrada")
            await conn.commit()
            return {"mensaje": "Inscripción eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la inscripción")
