import asyncio
import sys
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from config.conexionDB import get_conexion

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
router = APIRouter()

class Usuario(BaseModel):
    nombre: str
    contraseña: str
    id_tipo: int

@router.get("/")
async def listar_usuarios(conn=Depends(get_conexion)):
    consulta = "SELECT id_usuario, nombre, contraseña, id_tipo FROM usuario ORDER BY id_usuario"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            usuarios = await cursor.fetchall()
            if not usuarios:
                return {"mensaje": "No hay usuarios registrados"}
            return usuarios
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar usuarios")

@router.get("/{id_usuario}")
async def obtener_usuario(id_usuario: int, conn=Depends(get_conexion)):
    consulta = "SELECT id_usuario, nombre, contraseña, id_tipo FROM usuario WHERE id_usuario = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_usuario,))
            usuario = await cursor.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return usuario
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al consultar usuario: {e}")
        raise HTTPException(status_code=400, detail="Error al consultar usuario")

@router.post("/")
async def insertar_usuario(usuario: Usuario, conn=Depends(get_conexion)):
    consulta = "INSERT INTO usuario(nombre, contraseña, id_tipo) VALUES (%s, %s, %s) RETURNING id_usuario"
    parametros = (usuario.nombre, usuario.contraseña, usuario.id_tipo)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Usuario registrado exitosamente", "id_usuario": nuevo_id["id_usuario"]}
    except Exception as e:
        print(f"Error al insertar usuario: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el usuario")

@router.put("/{id_usuario}")
async def actualizar_usuario(id_usuario: int, usuario: Usuario, conn=Depends(get_conexion)):
    consulta = """
        UPDATE usuario
        SET nombre = %s,
            contraseña = %s,
            id_tipo = %s
        WHERE id_usuario = %s
        RETURNING id_usuario
    """
    parametros = (usuario.nombre, usuario.contraseña, usuario.id_tipo, id_usuario)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Usuario actualizado correctamente", "id_usuario": actualizado["id_usuario"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")

@router.delete("/{id_usuario}")
async def eliminar_usuario(id_usuario: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM usuario WHERE id_usuario = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_usuario,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            await conn.commit()
            return {"mensaje": "Usuario eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario")

app.include_router(router, prefix="/usuarios", tags=["Usuarios"])
