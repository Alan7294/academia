import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Materia(BaseModel):
    nombre: str
    descripcion: str 

@router.get("/")
async def listar_materias(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_materia, nombre, descripcion
        FROM materia
        ORDER BY id_materia
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            materias = await cursor.fetchall()

            if not materias:
                return {"mensaje": "No hay materias registradas"}

            return materias
    except Exception as e:
        print(f"Error al listar materias: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar materias")

@router.get("/{id_materia}")
async def obtener_materia(id_materia: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_materia, nombre, descripcion
        FROM materia
        WHERE id_materia = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_materia,))
            materia = await cursor.fetchone()

            if not materia:
                raise HTTPException(status_code=404, detail="Materia no encontrada")

            return materia
    except Exception as e:
        print(f"Error al consultar materia: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar materia")

@router.post("/")
async def insertar_materia(materia: Materia, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO materia(nombre, descripcion)
        VALUES (%s, %s)
        RETURNING id_materia
    """
    parametros = (materia.nombre, materia.descripcion)

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()

            return {
                "mensaje": "Materia registrada exitosamente",
                "id_materia": nuevo_id["id_materia"]
            }
    except Exception as e:
        print(f"Error al insertar materia: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar la materia")

@router.put("/{id_materia}")
async def actualizar_materia(id_materia: int, materia: Materia, conn=Depends(get_conexion)):
    consulta = """
        UPDATE materia
        SET nombre = %s,
            descripcion = %s
        WHERE id_materia = %s
        RETURNING id_materia
    """
    parametros = (materia.nombre, materia.descripcion, id_materia)

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Materia no encontrada")

            actualizado = await cursor.fetchone()
            await conn.commit()

            return {
                "mensaje": "Materia actualizada correctamente",
                "id_materia": actualizado["id_materia"]
            }
    except Exception as e:
        print(f"Error al actualizar materia: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la materia")

@router.delete("/{id_materia}")
async def eliminar_materia(id_materia: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM materia WHERE id_materia = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_materia,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Materia no encontrada")
            await conn.commit()
            return {"mensaje": "Materia eliminada correctamente"}
    except Exception as e:
        print(f"Error al eliminar materia: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar la materia")

app.include_router(router)
