from flask import Blueprint, jsonify, request

from database.conexion import conectar

routes = Blueprint('routes', __name__)


def generar_codigo_materia(cursor, numero_semestre):
    prefijo = f"INF{numero_semestre:02d}"

    cursor.execute("""
        SELECT codigo FROM materias
        WHERE codigo LIKE %s
        ORDER BY codigo DESC
        LIMIT 1
    """, (f"{prefijo}%",))

    resultado = cursor.fetchone()

    if resultado:
        ultimo_codigo = resultado[0]
        ultimo_consecutivo = int(ultimo_codigo[-2:])
        nuevo_consecutivo = ultimo_consecutivo + 1
    else:
        nuevo_consecutivo = 1

    return f"{prefijo}{nuevo_consecutivo:02d}"


#* Metodos GET
@routes.route('/horarios', methods=['GET'])
def obtener_horarios():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            s.numero AS semestre,
            m.codigo AS codigo_materia,
            m.nombre AS materia,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        ORDER BY
            s.numero,
            h.dia,
            h.hora_inicio
    """)

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:
        horarios.append({
            "id": fila[0],
            "semestre": fila[1],
            "codigo_materia": fila[2],
            "materia": fila[3],
            "profesor": fila[4],
            "jornada": fila[5],
            "dia": fila[6],
            "hora_inicio": str(fila[7]),
            "hora_fin": str(fila[8]),
            "salon": fila[9]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)

@routes.route('/horarios/<int:id>', methods=['GET'])
def obtener_horario(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            s.numero AS semestre,
            m.codigo AS codigo_materia,
            m.nombre AS materia,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE h.id = %s
    """, (id,))

    fila = cursor.fetchone()

    cursor.close()
    conexion.close()

    if fila is None:
        return jsonify({
            "mensaje": "Horario no encontrado"
        }), 404

    horario = {
        "id": fila[0],
        "semestre": fila[1],
        "codigo_materia": fila[2],
        "materia": fila[3],
        "profesor": fila[4],
        "jornada": fila[5],
        "dia": fila[6],
        "hora_inicio": str(fila[7]),
        "hora_fin": str(fila[8]),
        "salon": fila[9]
    }

    return jsonify(horario)

@routes.route('/horarios/semestre/<nombre>', methods=['GET'])
def obtener_horarios_semestre(nombre):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            s.numero AS semestre,
            m.codigo AS codigo_materia,
            m.nombre AS materia,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE s.periodo_academico = %s
        ORDER BY
            h.dia,
            h.hora_inicio
    """, (nombre,))

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:
        horarios.append({
            "id": fila[0],
            "semestre": fila[1],
            "codigo_materia": fila[2],
            "materia": fila[3],
            "profesor": fila[4],
            "jornada": fila[5],
            "dia": fila[6],
            "hora_inicio": str(fila[7]),
            "hora_fin": str(fila[8]),
            "salon": fila[9]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)

@routes.route('/horarios/semestre/<nombre>/dia/<dia>', methods=['GET'])
def obtener_horarios_dia(nombre, dia):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            s.numero AS semestre,
            m.codigo AS codigo_materia,
            m.nombre AS materia,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE s.periodo_academico = %s
        AND h.dia = %s
        ORDER BY h.hora_inicio
    """, (nombre, dia))

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:
        horarios.append({
            "id": fila[0],
            "semestre": fila[1],
            "codigo_materia": fila[2],
            "materia": fila[3],
            "profesor": fila[4],
            "jornada": fila[5],
            "dia": fila[6],
            "hora_inicio": str(fila[7]),
            "hora_fin": str(fila[8]),
            "salon": fila[9]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)

@routes.route('/materias', methods=['GET'])
def obtener_materias():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, codigo, nombre
        FROM materias
        ORDER BY nombre
    """)

    datos = cursor.fetchall()

    materias = []

    for fila in datos:
        materias.append({
            "id": fila[0],
            "codigo": fila[1],
            "nombre": fila[2]
        })

    cursor.close()
    conexion.close()

    return jsonify(materias)

#todo Metodos POST

@routes.route('/horarios', methods=['POST'])
def crear_horario():

    datos = request.get_json()

    campos_requeridos = ['usuario_id', 'numero_semestre', 'periodo_academico', 'nombre_materia', 'profesor', 'dia', 'hora_inicio', 'hora_fin']
    faltantes = [campo for campo in campos_requeridos if campo not in datos or datos.get(campo) in (None, '')]

    if faltantes:
        return jsonify({"mensaje": f"Faltan campos obligatorios: {', '.join(faltantes)}"}), 400

    usuario_id = datos.get('usuario_id')
    numero_semestre = datos.get('numero_semestre')
    periodo_academico = datos.get('periodo_academico')
    nombre_materia = datos.get('nombre_materia').strip()
    profesor = datos.get('profesor')
    jornada = datos.get('jornada')
    dia = datos.get('dia')
    hora_inicio = datos.get('hora_inicio')
    hora_fin = datos.get('hora_fin')
    salon = datos.get('salon')

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        # 0. Verificar que el usuario exista
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conexion.close()
            return jsonify({"mensaje": "El usuario indicado no existe"}), 404

        # 1. Buscar o crear el semestre (numero + periodo)
        cursor.execute("""
            SELECT id FROM semestres
            WHERE numero = %s AND periodo_academico = %s
        """, (numero_semestre, periodo_academico))
        resultado = cursor.fetchone()

        if resultado:
            semestre_id = resultado[0]
        else:
            cursor.execute("""
                INSERT INTO semestres (numero, periodo_academico)
                VALUES (%s, %s)
                RETURNING id
            """, (numero_semestre, periodo_academico))
            semestre_id = cursor.fetchone()[0]

        # 2. Buscar o crear la materia por nombre
        cursor.execute("SELECT id, codigo FROM materias WHERE UPPER(nombre) = UPPER(%s)", (nombre_materia,))
        resultado = cursor.fetchone()

        if resultado:
            materia_id, codigo_materia = resultado
        else:
            codigo_materia = generar_codigo_materia(cursor, numero_semestre)
            cursor.execute("""
                INSERT INTO materias (codigo, nombre)
                VALUES (%s, %s)
                RETURNING id
            """, (codigo_materia, nombre_materia))
            materia_id = cursor.fetchone()[0]

        # 3. Insertar el horario (ahora con usuario_id)
        cursor.execute("""
            INSERT INTO horarios
                (usuario_id, semestre_id, materia_id, profesor, jornada, dia, hora_inicio, hora_fin, salon)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (usuario_id, semestre_id, materia_id, profesor, jornada, dia, hora_inicio, hora_fin, salon))

        nuevo_id = cursor.fetchone()[0]
        conexion.commit()

    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": f"Error al crear el horario: {str(e)}"}), 500

    cursor.close()
    conexion.close()

    return jsonify({
        "id": nuevo_id,
        "usuario_id": usuario_id,
        "numero_semestre": numero_semestre,
        "periodo_academico": periodo_academico,
        "materia_id": materia_id,
        "codigo_materia": codigo_materia,
        "nombre_materia": nombre_materia,
        "profesor": profesor,
        "jornada": jornada,
        "dia": dia,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "salon": salon
    }), 201

#? Metodo PUT

@routes.route('/horarios/<int:id>', methods=['PUT'])
def actualizar_horario(id):

    datos = request.get_json()

    campos_requeridos = ['usuario_id', 'numero_semestre', 'periodo_academico', 'nombre_materia', 'profesor', 'dia', 'hora_inicio', 'hora_fin']
    faltantes = [campo for campo in campos_requeridos if campo not in datos or datos.get(campo) in (None, '')]

    if faltantes:
        return jsonify({"mensaje": f"Faltan campos obligatorios: {', '.join(faltantes)}"}), 400

    usuario_id = datos.get('usuario_id')
    numero_semestre = datos.get('numero_semestre')
    periodo_academico = datos.get('periodo_academico')
    nombre_materia = datos.get('nombre_materia').strip()
    profesor = datos.get('profesor')
    jornada = datos.get('jornada')
    dia = datos.get('dia')
    hora_inicio = datos.get('hora_inicio')
    hora_fin = datos.get('hora_fin')
    salon = datos.get('salon')

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        # 0. Verificar que el horario exista
        cursor.execute("SELECT id FROM horarios WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            cursor.close()
            conexion.close()
            return jsonify({"mensaje": "Horario no encontrado"}), 404

        # 0.1 Verificar que el usuario exista
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conexion.close()
            return jsonify({"mensaje": "El usuario indicado no existe"}), 404

        # 1. Buscar o crear el semestre (numero + periodo)
        cursor.execute("""
            SELECT id FROM semestres
            WHERE numero = %s AND periodo_academico = %s
        """, (numero_semestre, periodo_academico))
        resultado = cursor.fetchone()

        if resultado:
            semestre_id = resultado[0]
        else:
            cursor.execute("""
                INSERT INTO semestres (numero, periodo_academico)
                VALUES (%s, %s)
                RETURNING id
            """, (numero_semestre, periodo_academico))
            semestre_id = cursor.fetchone()[0]

        # 2. Buscar o crear la materia por nombre
        cursor.execute("SELECT id, codigo FROM materias WHERE UPPER(nombre) = UPPER(%s)", (nombre_materia,))
        resultado = cursor.fetchone()

        if resultado:
            materia_id, codigo_materia = resultado
        else:
            codigo_materia = generar_codigo_materia(cursor, numero_semestre)
            cursor.execute("""
                INSERT INTO materias (codigo, nombre)
                VALUES (%s, %s)
                RETURNING id
            """, (codigo_materia, nombre_materia))
            materia_id = cursor.fetchone()[0]

        # 3. Actualizar el horario (ahora con usuario_id)
        cursor.execute("""
            UPDATE horarios
            SET usuario_id = %s,
                semestre_id = %s,
                materia_id = %s,
                profesor = %s,
                jornada = %s,
                dia = %s,
                hora_inicio = %s,
                hora_fin = %s,
                salon = %s
            WHERE id = %s
        """, (usuario_id, semestre_id, materia_id, profesor, jornada, dia, hora_inicio, hora_fin, salon, id))

        conexion.commit()

    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": f"Error al actualizar el horario: {str(e)}"}), 500

    cursor.close()
    conexion.close()

    return jsonify({
        "id": id,
        "usuario_id": usuario_id,
        "numero_semestre": numero_semestre,
        "periodo_academico": periodo_academico,
        "materia_id": materia_id,
        "codigo_materia": codigo_materia,
        "nombre_materia": nombre_materia,
        "profesor": profesor,
        "jornada": jornada,
        "dia": dia,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "salon": salon
    }), 200

#! Metodo DELETE

@routes.route('/horarios/<int:id>', methods=['DELETE'])
def eliminar_horario(id):

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id FROM horarios WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            cursor.close()
            conexion.close()
            return jsonify({"mensaje": "Horario no encontrado"}), 404

        cursor.execute("DELETE FROM horarios WHERE id = %s", (id,))
        conexion.commit()

    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": f"Error al eliminar el horario: {str(e)}"}), 500

    cursor.close()
    conexion.close()

    return jsonify({"mensaje": f"Horario con id {id} eliminado correctamente"}), 200

#TODO: Usuarios

@routes.route('/usuarios', methods=['GET'])
def obtener_usuarios():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            correo
        FROM usuarios
        ORDER BY nombre
    """)

    datos = cursor.fetchall()

    usuarios = []

    for fila in datos:
        usuarios.append({
            "id": fila[0],
            "nombre": fila[1],
            "correo": fila[2]
        })

    cursor.close()
    conexion.close()

    return jsonify(usuarios)

@routes.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id,
            nombre,
            correo
        FROM usuarios
        WHERE id = %s
    """, (id,))

    fila = cursor.fetchone()

    cursor.close()
    conexion.close()

    if fila is None:
        return jsonify({
            "mensaje": "Usuario no encontrado"
        }), 404

    return jsonify({
        "id": fila[0],
        "nombre": fila[1],
        "correo": fila[2]
    })

@routes.route('/usuarios', methods=['POST'])
def crear_usuario():

    data = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO usuarios
        (
            nombre,
            correo
        )
        VALUES
        (
            %s,
            %s
        )
    """, (
        data['nombre'],
        data['correo']
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Usuario creado correctamente"
    }), 201

@routes.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):

    data = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET
            nombre = %s,
            correo = %s
        WHERE id = %s
    """, (
        data['nombre'],
        data['correo'],
        id
    ))

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Usuario actualizado correctamente"
    })

@routes.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM usuarios
        WHERE id = %s
    """, (id,))

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Usuario eliminado correctamente"
    })

@routes.route('/usuarios/<int:id>/horarios', methods=['GET'])
def obtener_horarios_usuario(id):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            u.nombre,
            s.numero,
            s.periodo_academico,
            m.codigo,
            m.nombre,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon,
            u.id
        FROM horarios h
        INNER JOIN usuarios u
            ON h.usuario_id = u.id
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE u.id = %s
        ORDER BY
            s.numero,
            h.dia,
            h.hora_inicio
    """, (id,))

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:

        horarios.append({
            "id": fila[0],
            "usuario": fila[1],
            "semestre": fila[2],
            "periodo": fila[3],
            "codigo_materia": fila[4],
            "materia": fila[5],
            "profesor": fila[6],
            "jornada": fila[7],
            "dia": fila[8],
            "hora_inicio": str(fila[9]),
            "hora_fin": str(fila[10]),
            "salon": fila[11],
            "id_usuario": fila[12]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)

@routes.route('/usuarios/<int:id>/horarios/semestre/<periodo>', methods=['GET'])
def obtener_horarios_usuario_semestre(id, periodo):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            h.id,
            m.codigo,
            m.nombre,
            h.profesor,
            h.jornada,
            h.dia,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE h.usuario_id = %s
        AND s.periodo_academico = %s
        ORDER BY
            h.dia,
            h.hora_inicio
    """, (id, periodo))

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:

        horarios.append({
            "id": fila[0],
            "codigo_materia": fila[1],
            "materia": fila[2],
            "profesor": fila[3],
            "jornada": fila[4],
            "dia": fila[5],
            "hora_inicio": str(fila[6]),
            "hora_fin": str(fila[7]),
            "salon": fila[8]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)

@routes.route('/usuarios/<int:id>/horarios/semestre/<periodo>/dia/<dia>', methods=['GET'])
def obtener_horarios_usuario_dia(id, periodo, dia):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            m.codigo,
            m.nombre,
            h.profesor,
            h.jornada,
            h.hora_inicio,
            h.hora_fin,
            h.salon
        FROM horarios h
        INNER JOIN semestres s
            ON h.semestre_id = s.id
        INNER JOIN materias m
            ON h.materia_id = m.id
        WHERE h.usuario_id = %s
        AND s.periodo_academico = %s
        AND h.dia = %s
        ORDER BY h.hora_inicio
    """, (id, periodo, dia))

    datos = cursor.fetchall()

    horarios = []

    for fila in datos:

        horarios.append({
            "codigo_materia": fila[0],
            "materia": fila[1],
            "profesor": fila[2],
            "jornada": fila[3],
            "hora_inicio": str(fila[4]),
            "hora_fin": str(fila[5]),
            "salon": fila[6]
        })

    cursor.close()
    conexion.close()

    return jsonify(horarios)