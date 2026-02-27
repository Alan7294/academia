from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Administrador(BaseModel):
    nombre: str
    correo: str
    id_tipo: int   

@router.get("/")
async def listar_administradores(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_admin, nombre, correo, id_tipo
        FROM administrador
        ORDER BY id_admin
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            administradores = await cursor.fetchall()
            if not administradores:
                return {"mensaje": "No hay administradores registrados"}
            return administradores
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar administradores")

@router.get("/{id_admin}")
async def obtener_administrador(id_admin: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_admin, nombre, correo, id_tipo
        FROM administrador
        WHERE id_admin = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_admin,))
            admin = await cursor.fetchone()
            if not admin:
                raise HTTPException(status_code=404, detail="Administrador no encontrado")
            return admin
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar administrador")

@router.post("/")
async def insertar_administrador(admin: Administrador, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO administrador(nombre, correo, id_tipo)
        VALUES (%s, %s, %s)
        RETURNING id_admin
    """
    parametros = (
        admin.nombre,
        admin.correo,
        admin.id_tipo
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Administrador registrado exitosamente", "id_admin": nuevo_id["id_admin"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar el administrador")

@router.put("/{id_admin}")
async def actualizar_administrador(id_admin: int, admin: Administrador, conn=Depends(get_conexion)):
    consulta = """
        UPDATE administrador
        SET nombre = %s, correo = %s, id_tipo = %s
        WHERE id_admin = %s
        RETURNING id_admin
    """
    parametros = (
        admin.nombre,
        admin.correo,
        admin.id_tipo,
        id_admin
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Administrador no encontrado")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Administrador actualizado correctamente", "id_admin": actualizado["id_admin"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el administrador")

@router.delete("/{id_admin}")
async def eliminar_administrador(id_admin: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM administrador WHERE id_admin = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_admin,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Administrador no encontrado")
            await conn.commit()
            return {"mensaje": "Administrador eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el administrador")
