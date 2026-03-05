import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Carrera(BaseModel):
    nombre_carrera: str

@router.get("/")
async def listar_carreras(conn=Depends(get_conexion)):
    consulta = "SELECT id_carrera, nombre_carrera FROM carrera ORDER BY id_carrera"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            carreras = await cursor.fetchall()
            if not carreras:
                return {"mensaje": "No hay carreras registradas"}
            return carreras
    except Exception as e:
        print(f"Error al listar carreras: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar carreras")

@router.get("/{id_carrera}")
async def obtener_carrera(id_carrera: int, conn=Depends(get_conexion)):
    consulta = "SELECT id_carrera, nombre_carrera FROM carrera WHERE id_carrera = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_carrera,))
            carrera = await cursor.fetchone()
            if not carrera:
                raise HTTPException(status_code=404, detail="Carrera no encontrada")
            return carrera
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al consultar carrera: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar carrera")

@router.post("/")
async def insertar_carrera(carrera: Carrera, conn=Depends(get_conexion)):
    consulta = "INSERT INTO carrera(nombre_carrera) VALUES (%s) RETURNING id_carrera"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (carrera.nombre_carrera,))
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Carrera registrada exitosamente", "id_carrera": nuevo_id["id_carrera"]}
    except Exception as e:
        print(f"Error al insertar carrera: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar la carrera")

@router.put("/{id_carrera}")
async def actualizar_carrera(id_carrera: int, carrera: Carrera, conn=Depends(get_conexion)):
    consulta = "UPDATE carrera SET nombre_carrera = %s WHERE id_carrera = %s RETURNING id_carrera"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (carrera.nombre_carrera, id_carrera))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Carrera no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Carrera actualizada correctamente", "id_carrera": actualizado["id_carrera"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar carrera: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la carrera")

@router.delete("/{id_carrera}")
async def eliminar_carrera(id_carrera: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM carrera WHERE id_carrera = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_carrera,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Carrera no encontrada")
            await conn.commit()
            return {"mensaje": "Carrera eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar carrera: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar la carrera")

app.include_router(router, prefix="/carreras", tags=["Carreras"])
