from flask import Flask, render_template, request, redirect, url_for, session, flash
from GestorTareas import GestorTareas
from bson import ObjectId

app = Flask(__name__)
app.secret_key = '12345678'

gestor = GestorTareas()

gestor.crear_usuario("trevi", "trevi@gmail.com", "1234")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        clave = request.form.get('clave')
        
        if not nombre or not correo or not clave:
            flash('Todos los campos son obligatorios')
            return redirect(url_for('registro'))
        
        if gestor.usuarios.find_one({"correo": correo}):
            flash('El correo ya está registrado')
            return redirect(url_for('registro'))
        
        gestor.usuarios.insert_one({
            "nombre": nombre,
            "correo": correo,
            "clave": clave
        })
        
        flash('Registro exitoso. Ahora puedes iniciar sesión')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        clave = request.form.get('clave')
        
        if not correo or not clave:
            flash('Correo y contraseña son obligatorios')
            return redirect(url_for('login'))
        
        # Buscar por "correo" (el campo que tienes en MongoDB)
        usuario = gestor.usuarios.find_one({"correo": correo})
        
        if usuario and usuario['clave'] == clave:
            session['usuario_id'] = str(usuario['_id'])
            session['usuario_nombre'] = usuario['nombre']
            flash('Bienvenido')
            return redirect(url_for('tareas'))
        else:
            flash('Correo o contraseña incorrectos')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/tareas')
def tareas():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión primero')
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    lista_tareas = gestor.obtener_tareas_usuario(usuario_id)
    
    return render_template('tareas.html', tareas=lista_tareas)

@app.route('/agregar_tarea', methods=['POST'])
def agregar_tarea():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion', '')
    
    if not titulo:
        flash('El título es obligatorio')
        return redirect(url_for('tareas'))
    
    usuario_id = session['usuario_id']
    gestor.crear_tarea(usuario_id, titulo, descripcion)
    flash('Tarea agregada')
    return redirect(url_for('tareas'))

@app.route('/completar_tarea/<tarea_id>')
def completar_tarea(tarea_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    
    gestor.tareas.update_one(
        {"_id": ObjectId(tarea_id), "usuario_id": ObjectId(usuario_id)},
        {"$set": {"completada": True, "estado": "completada"}}
    )
    flash('¡Tarea completada!')
    return redirect(url_for('tareas'))

@app.route('/editar_tarea/<tarea_id>', methods=['POST'])
def editar_tarea(tarea_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    
    gestor.tareas.update_one(
        {"_id": ObjectId(tarea_id), "usuario_id": ObjectId(usuario_id)},
        {"$set": {"titulo": titulo, "descripcion": descripcion}}
    )
    flash('Tarea actualizada')
    return redirect(url_for('tareas'))

@app.route('/eliminar_tarea/<tarea_id>')
def eliminar_tarea(tarea_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    
    gestor.tareas.delete_one({"_id": ObjectId(tarea_id), "usuario_id": ObjectId(usuario_id)})
    flash('Tarea eliminada')
    return redirect(url_for('tareas'))

@app.route('/salir')
def salir():
    session.clear()
    flash('Sesión cerrada')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)