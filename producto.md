# 📦 API Productos

## Modelo

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP",
  "precio": 5000.0,
  "stock": 10,
  "imagen": "https://res.cloudinary.com/.../imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos",
    "fecha_creacion": "2025-11-11T10:00:00Z",
    "fecha_modificacion": "2025-11-11T10:00:00Z"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:00:00Z"
}
```

---

## `GET /api/productos/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": 5000.0,
    "stock": 10,
    "imagen": "https://res.cloudinary.com/.../imagen.jpg",
    "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica",
      "descripcion": "Productos electrónicos"
    },
    "fecha_creacion": "2025-11-11T15:00:00Z",
    "fecha_modificacion": "2025-11-11T15:00:00Z"
  }
]
```

---

## `POST /api/productos/`

**Auth:** ✅ Required  
**Content-Type:** `application/json` o `multipart/form-data`

**Request:**

```
Content-Type: multipart/form-data

nombre: Laptop HP
precio: 5000
stock: 10
idCategoria: 1
imagen: [archivo]
```

**Response 201:**

```json
{
  "idProducto": 2,
  "nombre": "Laptop HP",
  "precio": 5000.0,
  "stock": 10,
  "imagen": "https://res.cloudinary.com/.../imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:00:00Z"
}
```

**Error 400:**

```json
{
  "idCategoria": ["La categoría no existe"]
}
```

---

## `GET /api/productos/{id}/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP",
  "precio": 5000.0,
  "stock": 10,
  "imagen": "https://res.cloudinary.com/.../imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:00:00Z"
}
```

**Error 404:**

```json
{
  "error": "Producto no encontrado"
}
```

---

## `PUT /api/productos/{id}/`

**Auth:** ✅ Required  
**Content-Type:** `application/json` o `multipart/form-data`

**Request (JSON):**

```json
{
  "nombre": "Laptop HP Pavilion",
  "precio": 5500.0,
  "stock": 15,
  "idCategoria": 1
}
```

**Request (FormData con imagen):**

```
nombre: Laptop HP Pavilion
precio: 5500
stock: 15
idCategoria: 1
imagen: [nuevo archivo]
```

**Response 200:**

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP Pavilion",
  "precio": 5500.0,
  "stock": 15,
  "imagen": "https://res.cloudinary.com/.../nueva-imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../nueva-imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:30:00Z"
}
```

---

## `PATCH /api/productos/{id}/`

**Auth:** ✅ Required  
**Content-Type:** `application/json` o `multipart/form-data`

**Request (solo campos a actualizar):**

```json
{
  "precio": 4800.0,
  "stock": 20
}
```

**Request (actualizar solo imagen):**

```
Content-Type: multipart/form-data

imagen: [nuevo archivo]
```

**Response 200:**

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP",
  "precio": 4800.0,
  "stock": 20,
  "imagen": "https://res.cloudinary.com/.../nueva-imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../nueva-imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:35:00Z"
}
```

---

## `DELETE /api/productos/{id}/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
{
  "mensaje": "Producto 'Laptop HP' eliminado correctamente"
}
```

**Error 404:**

```json
{
  "error": "Producto no encontrado"
}
```

---

## `GET /api/productos/buscar/?q={query}`

**Auth:** ✅ Required

**Request:** No body (query param: `q`)

**Ejemplo:** `GET /api/productos/buscar/?q=laptop`

**Response 200:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": 5000.0,
    "stock": 10,
    "imagen": "https://res.cloudinary.com/.../imagen.jpg",
    "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica"
    },
    "fecha_creacion": "2025-11-11T15:00:00Z",
    "fecha_modificacion": "2025-11-11T15:00:00Z"
  }
]
```

**Error 400:**

```json
{
  "error": "Debe proporcionar un término de búsqueda (q)"
}
```

---

## `GET /api/productos/categoria/{id_categoria}/`

**Auth:** ✅ Required

**Request:** No body

**Ejemplo:** `GET /api/productos/categoria/1/`

**Response 200:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": 5000.0,
    "stock": 10,
    "imagen": "https://res.cloudinary.com/.../imagen.jpg",
    "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica"
    },
    "fecha_creacion": "2025-11-11T15:00:00Z",
    "fecha_modificacion": "2025-11-11T15:00:00Z"
  }
]
```

**Error 404:**

```json
{
  "error": "Categoría no encontrada"
}
```

---

## `PATCH /api/productos/{id}/stock/`

**Auth:** ✅ Required

**Request:**

```json
{
  "cantidad": 10
}
```

**Nota:** `cantidad` puede ser positiva (incrementar) o negativa (decrementar)

**Response 200:**

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP",
  "precio": 5000.0,
  "stock": 20,
  "imagen": "https://res.cloudinary.com/.../imagen.jpg",
  "imagen_url": "https://res.cloudinary.com/.../imagen.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica"
  },
  "fecha_creacion": "2025-11-11T15:00:00Z",
  "fecha_modificacion": "2025-11-11T15:40:00Z"
}
```

**Error 400 (stock negativo):**

```json
{
  "error": "El stock no puede ser negativo"
}
```

**Error 400 (cantidad inválida):**

```json
{
  "error": "La cantidad debe ser un número entero"
}
```

**Error 400 (falta cantidad):**

```json
{
  "error": "Debe proporcionar la cantidad"
}
```

**Error 404:**

```json
{
  "error": "Producto no encontrado"
}
```

---

## Notas

- Todos los endpoints requieren autenticación JWT
- Campo `imagen` es opcional (puede ser null)
- Imagen se sube a Cloudinary automáticamente
- `idCategoria` debe ser una categoría existente
- Búsqueda por nombre es case-insensitive
- Stock se actualiza sumando/restando la cantidad proporcionada
- Stock no puede ser negativo
