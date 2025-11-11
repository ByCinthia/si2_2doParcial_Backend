# Módulo de Productos

Este módulo maneja la gestión de productos y categorías en el sistema.

## Modelos

### Categoria

- `idCategoria` (AutoField, PK): ID único de la categoría
- `nombre` (CharField): Nombre de la categoría (único)
- `descripcion` (CharField): Descripción opcional de la categoría
- `fecha_creacion` (DateTimeField): Fecha de creación automática
- `fecha_modificacion` (DateTimeField): Fecha de última modificación automática

### Producto

- `idProducto` (AutoField, PK): ID único del producto
- `nombre` (CharField): Nombre del producto
- `precio` (FloatField): Precio del producto
- `stock` (IntegerField): Cantidad en stock
- `imagen` (CloudinaryField): Imagen del producto en Cloudinary
- `categoria` (ForeignKey): Relación con Categoria
- `fecha_creacion` (DateTimeField): Fecha de creación automática
- `fecha_modificacion` (DateTimeField): Fecha de última modificación automática

## Endpoints

### Categorías

#### Listar todas las categorías

```http
GET /api/productos/categorias/
Authorization: Bearer {token}
```

#### Crear una categoría

```http
POST /api/productos/categorias/
Authorization: Bearer {token}
Content-Type: application/json

{
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
}
```

#### Obtener una categoría

```http
GET /api/productos/categorias/{id}/
Authorization: Bearer {token}
```

#### Actualizar una categoría

```http
PUT /api/productos/categorias/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "nombre": "Electrónica Actualizada",
    "descripcion": "Nueva descripción"
}
```

#### Actualizar parcialmente una categoría

```http
PATCH /api/productos/categorias/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "descripcion": "Solo actualizar descripción"
}
```

#### Eliminar una categoría

```http
DELETE /api/productos/categorias/{id}/
Authorization: Bearer {token}
```

#### Buscar categoría por nombre

```http
GET /api/productos/categorias/buscar/?nombre=Electrónica
Authorization: Bearer {token}
```

### Productos

#### Listar todos los productos

```http
GET /api/productos/
Authorization: Bearer {token}
```

**Respuesta:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": 1500.0,
    "stock": 10,
    "imagen": "...",
    "imagen_url": "https://res.cloudinary.com/.../image.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica",
      "descripcion": "Productos electrónicos",
      "fecha_creacion": "2025-11-05T10:00:00Z",
      "fecha_modificacion": "2025-11-05T10:00:00Z"
    },
    "fecha_creacion": "2025-11-05T10:00:00Z",
    "fecha_modificacion": "2025-11-05T10:00:00Z"
  }
]
```

#### Crear un producto

```http
POST /api/productos/
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
    "nombre": "Laptop Dell",
    "precio": 1200.50,
    "stock": 5,
    "idCategoria": 1,
    "imagen": <archivo>
}
```

#### Obtener un producto

```http
GET /api/productos/{id}/
Authorization: Bearer {token}
```

#### Actualizar un producto

```http
PUT /api/productos/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "nombre": "Laptop Dell Actualizada",
    "precio": 1300.00,
    "stock": 8,
    "idCategoria": 1
}
```

#### Actualizar parcialmente un producto

```http
PATCH /api/productos/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "precio": 1250.00
}
```

#### Eliminar un producto

```http
DELETE /api/productos/{id}/
Authorization: Bearer {token}
```

#### Buscar productos

```http
GET /api/productos/buscar/?q=laptop
Authorization: Bearer {token}
```

#### Listar productos por categoría

```http
GET /api/productos/categoria/{id_categoria}/
Authorization: Bearer {token}
```

#### Actualizar stock de un producto

```http
PATCH /api/productos/{id}/stock/
Authorization: Bearer {token}
Content-Type: application/json

{
    "cantidad": 5  // Puede ser positivo (aumentar) o negativo (disminuir)
}
```

## Características

- **Validaciones**:

  - No se puede eliminar una categoría con productos asociados
  - El stock no puede ser negativo
  - Las imágenes se almacenan en Cloudinary

- **Relaciones**:

  - Un producto pertenece a una categoría
  - Una categoría puede tener múltiples productos

- **Seguridad**:
  - Todos los endpoints requieren autenticación JWT
  - Manejo de errores con try-catch en todos los servicios

## Estructura del código

```
productos/
├── models.py           # Modelos Categoria y Producto
├── serializers.py      # Serializers para validación y transformación
├── views.py           # APIViews para endpoints
├── urls.py            # Configuración de rutas
├── admin.py           # Configuración del admin de Django
└── services/
    ├── services_categoria.py  # Lógica de negocio de categorías
    └── sevices_producto.py    # Lógica de negocio de productos
```
