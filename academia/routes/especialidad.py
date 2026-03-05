import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Especialidad(BaseModel):
    nombre_especialidad: str

@router.get("/")
async def listar_especialidades(conn=Depends(get_conexion)):
    consulta = "SELECT id_especialidad, nombre_especialidad FROM especialidad ORDER BY id_especialidad"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            especialidades = await cursor.fetchall()
            if not especialidades:
                return {"mensaje": "No hay especialidades registradas"}
            return especialidades
    except Exception as e:
        print(f"Error al listar especialidades: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar especialidades")

@router.get("/{id_especialidad}")
async def obtener_especialidad(id_especialidad: int, conn=Depends(get_conexion)):
    consulta = "SELECT id_especialidad, nombre_especialidad FROM especialidad WHERE id_especialidad = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_especialidad,))
            especialidad = await cursor.fetchone()
            if not especialidad:
                raise HTTPException(status_code=404, detail="Especialidad no encontrada")
            return especialidad
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al consultar especialidad: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar especialidad")

@router.post("/")
async def insertar_especialidad(especialidad: Especialidad, conn=Depends(get_conexion)):
    consulta = "INSERT INTO especialidad(nombre_especialidad) VALUES (%s) RETURNING id_especialidad"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (especialidad.nombre_especialidad,))
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Especialidad registrada exitosamente", "id_especialidad": nuevo_id["id_especialidad"]}
    except Exception as e:
        print(f"Error al insertar especialidad: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar la especialidad")

@router.put("/{id_especialidad}")
async def actualizar_especialidad(id_especialidad: int, especialidad: Especialidad, conn=Depends(get_conexion)):
    consulta = "UPDATE especialidad SET nombre_especialidad = %s WHERE id_especialidad = %s RETURNING id_especialidad"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (especialidad.nombre_especialidad, id_especialidad))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Especialidad no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Especialidad actualizada correctamente", "id_especialidad": actualizado["id_especialidad"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar especialidad: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la especialidad")

@router.delete("/{id_especialidad}")
async def eliminar_especialidad(id_especialidad: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM especialidad WHERE id_especialidad = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_especialidad,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Especialidad no encontrada")
            await conn.commit()
            return {"mensaje": "Especialidad eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar especialidad: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar la especialidad")

app.include_router(router, prefix="/especialidades", tags=["Especialidades"])
