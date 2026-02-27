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

class Alumno(BaseModel):
    nombre: str
    apellido_pat: str
    apellido_mat: Optional[str] = None
    ci: str
    correo: str
    fecha_nacimiento: Optional[str] = None
    carrera: Optional[str] = None

@router.get("/")
async def listar_alumnos(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_alumno, nombre, apellido_pat, apellido_mat, ci,
               correo, fecha_nacimiento, carrera
        FROM alumno
        ORDER BY id_alumno
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            alumnos = await cursor.fetchall()

            if not alumnos:
                return {"mensaje": "No hay alumnos registrados"}

            return alumnos

    except Exception as e:
        print(f"Error al listar alumnos: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar alumnos")

@router.get("/{id_alumno}")
async def obtener_alumno(id_alumno: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_alumno, nombre, apellido_pat, apellido_mat, ci,
               correo, fecha_nacimiento, carrera
        FROM alumno
        WHERE id_alumno = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_alumno,))
            alumno = await cursor.fetchone()

            if not alumno:
                raise HTTPException(status_code=404, detail="Alumno no encontrado")

            return alumno

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al consultar alumno: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar alumno")

@router.post("/")
async def insertar_alumno(alumno: Alumno, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO alumno(
            nombre, apellido_pat, apellido_mat, ci,
            correo, fecha_nacimiento, carrera
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_alumno
    """

    parametros = (
        alumno.nombre,
        alumno.apellido_pat,
        alumno.apellido_mat,
        alumno.ci,
        alumno.correo,
        alumno.fecha_nacimiento,
        alumno.carrera
    )

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()

            return {
                "mensaje": "Alumno registrado exitosamente",
                "id_alumno": nuevo_id["id_alumno"]
            }

    except Exception as e:
        print(f"Error al insertar alumno: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el alumno")

@router.put("/{id_alumno}")
async def actualizar_alumno(id_alumno: int, alumno: Alumno, conn=Depends(get_conexion)):
    consulta = """
        UPDATE alumno
        SET nombre = %s,
            apellido_pat = %s,
            apellido_mat = %s,
            ci = %s,
            correo = %s,
            fecha_nacimiento = %s,
            carrera = %s
        WHERE id_alumno = %s
        RETURNING id_alumno
    """

    parametros = (
        alumno.nombre,
        alumno.apellido_pat,
        alumno.apellido_mat,
        alumno.ci,
        alumno.correo,
        alumno.fecha_nacimiento,
        alumno.carrera,
        id_alumno
    )

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Alumno no encontrado")

            actualizado = await cursor.fetchone()
            await conn.commit()

            return {
                "mensaje": "Alumno actualizado correctamente",
                "id_alumno": actualizado["id_alumno"]
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar alumno: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el alumno")

@router.delete("/{id_alumno}")
async def eliminar_alumno(id_alumno: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM alumno WHERE id_alumno = %s"

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_alumno,))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Alumno no encontrado")

            await conn.commit()
            return {"mensaje": "Alumno eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar alumno: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar el alumno")

app.include_router(router)
