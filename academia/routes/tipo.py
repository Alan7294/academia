import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class TipoUsuario(BaseModel):
    nombre_tipo: str

@router.get("/")
async def listar_tipos(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_tipo, nombre_tipo
        FROM tipo_usuario
        ORDER BY id_tipo
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            tipos = await cursor.fetchall()
            if not tipos:
                return {"mensaje": "No hay tipos de usuario registrados"}
            return tipos
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar tipos de usuario")

@router.get("/{id_tipo}")
async def obtener_tipo(id_tipo: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_tipo, nombre_tipo
        FROM tipo_usuario
        WHERE id_tipo = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_tipo,))
            tipo = await cursor.fetchone()
            if not tipo:
                raise HTTPException(status_code=404, detail="Tipo de usuario no encontrado")
            return tipo
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar tipo de usuario")
