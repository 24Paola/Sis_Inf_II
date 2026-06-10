from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SECRET_KEY'] = 'clave-secreta-legacy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    proveedor = db.Column(db.String(100), nullable=False)


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, nullable=False)
    producto_nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    cliente = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    productos = Producto.query.all()
    ventas = Venta.query.all()
    total_productos = len(productos)
    total_ventas = len(ventas)
    return render_template('index.html', productos=productos, ventas=ventas,
                           total_productos=total_productos, total_ventas=total_ventas)


@app.route('/productos')
def listar_productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        producto = Producto(
            nombre=request.form['nombre'],
            categoria=request.form['categoria'],
            precio=float(request.form['precio']),
            stock=int(request.form['stock']),
            proveedor=request.form['proveedor']
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado')
        return redirect(url_for('listar_productos'))
    return render_template('producto_form.html')


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.categoria = request.form['categoria']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        producto.proveedor = request.form['proveedor']
        db.session.commit()
        flash('Producto actualizado')
        return redirect(url_for('listar_productos'))
    return render_template('producto_form.html', producto=producto)


@app.route('/productos/eliminar/<int:id>')
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado')
    return redirect(url_for('listar_productos'))


@app.route('/ventas')
def listar_ventas():
    ventas = Venta.query.all()
    return render_template('ventas.html', ventas=ventas)


@app.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    productos = Producto.query.all()
    if request.method == 'POST':
        producto = Producto.query.get(int(request.form['producto_id']))
        cantidad = int(request.form['cantidad'])
        total_venta = cantidad * producto.precio
        venta = Venta(
            producto_id=producto.id,
            producto_nombre=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            total=total_venta,
            fecha=request.form['fecha'],
            cliente=request.form['cliente']
        )
        db.session.add(venta)
        db.session.commit()
        flash('Venta registrada')
        return redirect(url_for('listar_ventas'))
    return render_template('venta_form.html', productos=productos)


if __name__ == '__main__':
    app.run(debug=True)
