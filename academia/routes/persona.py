import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Persona(BaseModel):
    nombre: str
    apellido_pat: str
    apellido_mat: str | None = None
    ci: int
    correo: str
    fecha_nacimiento: str | None = None   # opcional

@router.get("/")
async def listar_personas(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_persona, nombre, apellido_pat, apellido_mat, ci,
               correo, fecha_nacimiento
        FROM persona
        ORDER BY id_persona
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            personas = await cursor.fetchall()
            if not personas:
                return {"mensaje": "No hay personas registradas"}
            return personas
    except Exception as e:
        print(f"Error al listar personas: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar personas")

@router.get("/{id_persona}")
async def obtener_persona(id_persona: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_persona, nombre, apellido_pat, apellido_mat, ci,
               correo, fecha_nacimiento
        FROM persona
        WHERE id_persona = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_persona,))
            persona = await cursor.fetchone()
            if not persona:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            return persona
    except Exception as e:
        print(f"Error al consultar persona: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar persona")

@router.post("/")
async def insertar_persona(persona: Persona, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO persona(nombre, apellido_pat, apellido_mat, ci, correo, fecha_nacimiento)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_persona
    """
    parametros = (
        persona.nombre,
        persona.apellido_pat,
        persona.apellido_mat,
        persona.ci,
        persona.correo,
        persona.fecha_nacimiento
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Persona registrada exitosamente", "id_persona": nuevo_id["id_persona"]}
    except Exception as e:
        print(f"Error al insertar persona: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar la persona")

@router.put("/{id_persona}")
async def actualizar_persona(id_persona: int, persona: Persona, conn=Depends(get_conexion)):
    consulta = """
        UPDATE persona
        SET nombre = %s,
            apellido_pat = %s,
            apellido_mat = %s,
            ci = %s,
            correo = %s,
            fecha_nacimiento = %s
        WHERE id_persona = %s
        RETURNING id_persona
    """
    parametros = (
        persona.nombre,
        persona.apellido_pat,
        persona.apellido_mat,
        persona.ci,
        persona.correo,
        persona.fecha_nacimiento,
        id_persona
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Persona actualizada correctamente", "id_persona": actualizado["id_persona"]}
    except Exception as e:
        print(f"Error al actualizar persona: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la persona")

@router.delete("/{id_persona}")
async def eliminar_persona(id_persona: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM persona WHERE id_persona = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_persona,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
            await conn.commit()
            return {"mensaje": "Persona eliminada correctamente"}
    except Exception as e:
        print(f"Error al eliminar persona: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar la persona")

app.include_router(router)
