from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from config.conexionDB import get_conexion

router = APIRouter()

class Curso(BaseModel):
    nombre: str
    descripcion: str
    creditos: int 

@router.get("/")
async def listar_cursos(conn=Depends(get_conexion)):
    consulta = """
        SELECT id_curso, nombre, descripcion, creditos
        FROM curso
        ORDER BY id_curso
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            cursos = await cursor.fetchall()
            if not cursos:
                return {"mensaje": "No hay cursos registrados"}
            return cursos
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar cursos")

@router.get("/{id_curso}")
async def obtener_curso(id_curso: int, conn=Depends(get_conexion)):
    consulta = """
        SELECT id_curso, nombre, descripcion, creditos
        FROM curso
        WHERE id_curso = %s
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_curso,))
            curso = await cursor.fetchone()
            if not curso:
                raise HTTPException(status_code=404, detail="Curso no encontrado")
            return curso
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al consultar curso")

@router.post("/")
async def insertar_curso(curso: Curso, conn=Depends(get_conexion)):
    consulta = """
        INSERT INTO curso(nombre, descripcion, creditos)
        VALUES (%s, %s, %s)
        RETURNING id_curso
    """
    parametros = (
        curso.nombre,
        curso.descripcion,
        curso.creditos
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            nuevo_id = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Curso registrado exitosamente", "id_curso": nuevo_id["id_curso"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo registrar el curso")

@router.put("/{id_curso}")
async def actualizar_curso(id_curso: int, curso: Curso, conn=Depends(get_conexion)):
    consulta = """
        UPDATE curso
        SET nombre = %s, descripcion = %s, creditos = %s
        WHERE id_curso = %s
        RETURNING id_curso
    """
    parametros = (
        curso.nombre,
        curso.descripcion,
        curso.creditos,
        id_curso
    )
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Curso no encontrado")
            actualizado = await cursor.fetchone()
            await conn.commit()
            return {"mensaje": "Curso actualizado correctamente", "id_curso": actualizado["id_curso"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el curso")

@router.delete("/{id_curso}")
async def eliminar_curso(id_curso: int, conn=Depends(get_conexion)):
    consulta = "DELETE FROM curso WHERE id_curso = %s"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (id_curso,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Curso no encontrado")
            await conn.commit()
            return {"mensaje": "Curso eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el curso")
