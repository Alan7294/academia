from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Clase(BaseModel):
    id_curso: int
    id_docente: int
    periodo: str  

@router.get("/")
async def listar_clases(conn=Depends(get_conexion)):
    print("Listando clases")
    consulta = """
        SELECT id_clase, id_curso, id_docente, periodo
        FROM clase
        ORDER BY id_clase
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            clases = await cursor.fetchall()
            if not clases:
                return {"mensaje": "No hay clases registradas"}
            return clases
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar clases")

@router.get("/{id_clase}")
async def obtener_clase(id_clase: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_clase, id_curso, id_docente, periodo
        FROM clase
        WHERE id_clase = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_clase,))
            clase = await cursor.fetchone()
            if not clase:
                raise HTTPException(status_code=404, detail="Clase no encontrada")
            return clase
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar clase")

@router.post("/")
async def insertar_clase(clase: Clase, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO clase(id_curso, id_docente, periodo)
        VALUES (%s, %s, %s)
        RETURNING id_clase
    """
    parametros = (
        clase.id_curso,
        clase.id_docente,
        clase.periodo
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Clase registrada exitosamente", "id_clase": nuevo_id["id_clase"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar la clase")

@router.put("/{id_clase}")
async def actualizar_clase(id_clase: int, clase: Clase, conn=Depends(get_conexion)):
    consulta = """
        UPDATE clase
        SET id_curso = %s, id_docente = %s, periodo = %s
        WHERE id_clase = %s
        RETURNING id_clase
    """
    parametros = (
        clase.id_curso,
        clase.id_docente,
        clase.periodo,
        id_clase
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Clase no encontrada")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Clase actualizada correctamente", "id_clase": actualizado["id_clase"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la clase")

@router.delete("/{id_clase}")
async def eliminar_clase(id_clase: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM clase WHERE id_clase = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_clase,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Clase no encontrada")
            await conn.commit()
            return {"mensaje": "Clase eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la clase")
