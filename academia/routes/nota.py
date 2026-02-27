from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Nota(BaseModel):
    id_inscripcion: int
    id_docente: int
    nota: float 

@router.get("/")
async def listar_notas(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_nota, id_inscripcion, id_docente, nota, fecha_registro
        FROM notas
        ORDER BY id_nota
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            notas = await cursor.fetchall()
            if not notas:
                return {"mensaje": "No hay notas registradas"}
            return notas
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar notas")

@router.get("/{id_nota}")
async def obtener_nota(id_nota: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_nota, id_inscripcion, id_docente, nota, fecha_registro
        FROM notas
        WHERE id_nota = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_nota,))
            nota = await cursor.fetchone()
            if not nota:
                raise HTTPException(status_code=404, detail="Nota no encontrada")
            return nota
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar nota")

@router.post("/")
async def insertar_nota(nota: Nota, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO notas(id_inscripcion, id_docente, nota)
        VALUES (%s, %s, %s)
        RETURNING id_nota
    """
    parametros = (
        nota.id_inscripcion,
        nota.id_docente,
        nota.nota
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Nota registrada exitosamente", "id_nota": nuevo_id["id_nota"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar la nota")

@router.put("/{id_nota}")
async def actualizar_nota(id_nota: int, nota: Nota, conn=Depends(get_conexion)):
    consulta = """
        UPDATE notas
        SET id_inscripcion = %s, id_docente = %s, nota = %s
        WHERE id_nota = %s
        RETURNING id_nota
    """
    parametros = (
        nota.id_inscripcion,
        nota.id_docente,
        nota.nota,
        id_nota
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Nota no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Nota actualizada correctamente", "id_nota": actualizado["id_nota"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la nota")

@router.delete("/{id_nota}")
async def eliminar_nota(id_nota: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM notas WHERE id_nota = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_nota,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Nota no encontrada")
            await conn.commit()
            return {"mensaje": "Nota eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la nota")
