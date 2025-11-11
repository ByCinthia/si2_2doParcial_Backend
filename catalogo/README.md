# Módulo de Catálogo

Este módulo proporciona endpoints **públicos** (sin autenticación) para que los clientes puedan ver los productos disponibles en la tienda.

## Características

- ✅ **Sin autenticación requerida** - Acceso público
- ✅ **Solo lectura** - No se pueden modificar productos
- ✅ **Solo productos con stock** - Muestra solo productos disponibles
- ✅ **Filtros inteligentes** - Por categoría, destacados, nuevos, más vendidos

## Endpoints Disponibles

### 1. Listar Todos los Productos

```http
GET /api/catalogo/productos/
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

---

### 2. Filtrar Productos por Categoría

```http
GET /api/catalogo/productos/?categoria=1
```

**Parámetros:**

- `categoria` (int): ID de la categoría para filtrar

**Ejemplo:**

```
GET /api/catalogo/productos/?categoria=1
```

---

### 3. Obtener Detalles de un Producto

```http
GET /api/catalogo/productos/{id}/
```

**Ejemplo:**

```
GET /api/catalogo/productos/5/
```

**Respuesta:**

```json
{
  "idProducto": 5,
  "nombre": "Mouse Logitech",
  "precio": 25.99,
  "stock": 50,
  "imagen": "...",
  "imagen_url": "https://res.cloudinary.com/.../mouse.jpg",
  "categoria": {
    "idCategoria": 2,
    "nombre": "Accesorios",
    "descripcion": "Accesorios de computadora"
  },
  "fecha_creacion": "2025-11-05T10:00:00Z",
  "fecha_modificacion": "2025-11-05T10:00:00Z"
}
```

---

### 4. Listar Categorías

```http
GET /api/catalogo/categorias/
```

**Descripción:** Lista todas las categorías que tienen productos con stock disponible.

**Respuesta:**

```json
[
  {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos",
    "fecha_creacion": "2025-11-05T10:00:00Z",
    "fecha_modificacion": "2025-11-05T10:00:00Z"
  },
  {
    "idCategoria": 2,
    "nombre": "Accesorios",
    "descripcion": "Accesorios de computadora",
    "fecha_creacion": "2025-11-05T10:00:00Z",
    "fecha_modificacion": "2025-11-05T10:00:00Z"
  }
]
```

---

### 5. Productos Destacados

```http
GET /api/catalogo/productos/destacados/
```

**Descripción:** Retorna los 10 productos con mayor stock (asumiendo que son los más populares).

**Criterio:** Productos ordenados por stock descendente.

---

### 6. Productos Nuevos

```http
GET /api/catalogo/productos/nuevos/
```

**Descripción:** Retorna los 10 productos más recientes.

**Criterio:** Productos ordenados por fecha de creación descendente.

---

### 7. Productos Más Vendidos

```http
GET /api/catalogo/productos/mas-vendidos/
```

**Descripción:** Retorna los productos más vendidos (con stock bajo pero disponible).

**Criterio:** Productos con stock entre 1 y 20 unidades, ordenados por menor stock.

---

## Lógica de Negocio

### Filtros Aplicados Automáticamente

1. **Solo productos con stock**: Todos los endpoints filtran `stock > 0`
2. **Categorías activas**: Solo muestra categorías que tienen productos disponibles
3. **Límite de resultados**: Los endpoints de destacados, nuevos y más vendidos retornan máximo 10 productos

### Criterios de Clasificación

| Endpoint     | Criterio          | Ordenamiento          | Límite |
| ------------ | ----------------- | --------------------- | ------ |
| Destacados   | Mayor stock       | `stock` DESC          | 10     |
| Nuevos       | Fecha reciente    | `fecha_creacion` DESC | 10     |
| Más vendidos | Stock bajo (1-20) | `stock` ASC           | 10     |

---

## Diferencias con el Módulo de Productos

| Característica | Productos      | Catálogo             |
| -------------- | -------------- | -------------------- |
| Autenticación  | ✅ Requerida   | ❌ Pública           |
| Operaciones    | CRUD completo  | Solo lectura         |
| Filtros        | Solo stock     | Stock > 0 automático |
| Propósito      | Administración | Clientes/Frontend    |

---

## Casos de Uso

### Frontend de Tienda

```javascript
// Obtener productos para la página principal
fetch("/api/catalogo/productos/destacados/")
  .then((res) => res.json())
  .then((productos) => mostrarDestacados(productos));

// Filtrar por categoría
fetch("/api/catalogo/productos/?categoria=1")
  .then((res) => res.json())
  .then((productos) => mostrarProductos(productos));

// Ver detalles de producto
fetch("/api/catalogo/productos/5/")
  .then((res) => res.json())
  .then((producto) => mostrarDetalles(producto));
```

---

## Estructura del Código

```
catalogo/
├── service_catalogo.py    # Lógica de negocio
├── views.py               # APIViews públicas
├── urls.py                # Rutas del catálogo
└── README.md              # Esta documentación
```

---

## Notas Importantes

⚠️ **Sin autenticación**: Todos los endpoints son públicos (permission_classes = [AllowAny])

⚠️ **Solo lectura**: No hay métodos POST, PUT, PATCH o DELETE

⚠️ **Optimizado para clientes**: Consultas optimizadas con `select_related('categoria')`

✅ **Reutiliza serializers**: Usa los mismos serializers del módulo de productos
