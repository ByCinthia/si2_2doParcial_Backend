# 📁 API Categorías

## Modelo

```json
{
  "idCategoria": 1,
  "nombre": "Electrónica",
  "descripcion": "Productos electrónicos",
  "fecha_creacion": "2025-11-11T10:00:00Z",
  "fecha_modificacion": "2025-11-11T10:00:00Z"
}
```

---

## `GET /api/productos/categorias/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
[
  {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos",
    "fecha_creacion": "2025-11-11T10:00:00Z",
    "fecha_modificacion": "2025-11-11T10:00:00Z"
  }
]
```

---

## `POST /api/productos/categorias/`

**Auth:** ✅ Required

**Request:**

```json
{
  "nombre": "Ropa",
  "descripcion": "Prendas de vestir"
}
```

**Response 201:**

```json
{
  "idCategoria": 2,
  "nombre": "Ropa",
  "descripcion": "Prendas de vestir",
  "fecha_creacion": "2025-11-11T10:05:00Z",
  "fecha_modificacion": "2025-11-11T10:05:00Z"
}
```

**Error 400:**

```json
{
  "nombre": ["Ya existe una categoría con este nombre"]
}
```

---

## `GET /api/productos/categorias/{id}/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
{
  "idCategoria": 1,
  "nombre": "Electrónica",
  "descripcion": "Productos electrónicos",
  "fecha_creacion": "2025-11-11T10:00:00Z",
  "fecha_modificacion": "2025-11-11T10:00:00Z"
}
```

**Error 404:**

```json
{
  "error": "Categoría no encontrada"
}
```

---

## `PUT /api/productos/categorias/{id}/`

**Auth:** ✅ Required

**Request:**

```json
{
  "nombre": "Electrónica Avanzada",
  "descripcion": "Productos electrónicos de alta gama"
}
```

**Response 200:**

```json
{
  "idCategoria": 1,
  "nombre": "Electrónica Avanzada",
  "descripcion": "Productos electrónicos de alta gama",
  "fecha_creacion": "2025-11-11T10:00:00Z",
  "fecha_modificacion": "2025-11-11T10:10:00Z"
}
```

---

## `PATCH /api/productos/categorias/{id}/`

**Auth:** ✅ Required

**Request (solo campos a actualizar):**

```json
{
  "descripcion": "Nueva descripción"
}
```

**Response 200:**

```json
{
  "idCategoria": 1,
  "nombre": "Electrónica",
  "descripcion": "Nueva descripción",
  "fecha_creacion": "2025-11-11T10:00:00Z",
  "fecha_modificacion": "2025-11-11T10:12:00Z"
}
```

---

## `DELETE /api/productos/categorias/{id}/`

**Auth:** ✅ Required

**Request:** No body

**Response 200:**

```json
{
  "mensaje": "Categoría eliminada correctamente"
}
```

**Error 400 (tiene productos):**

```json
{
  "error": "No se puede eliminar la categoría porque tiene productos asociados"
}
```

**Error 404:**

```json
{
  "error": "Categoría no encontrada"
}
```

---

## `GET /api/productos/categorias/buscar/?nombre={nombre}`

**Auth:** ✅ Required

**Request:** No body (query param: `nombre`)

**Response 200:**

```json
{
  "idCategoria": 1,
  "nombre": "Electrónica",
  "descripcion": "Productos electrónicos",
  "fecha_creacion": "2025-11-11T10:00:00Z",
  "fecha_modificacion": "2025-11-11T10:00:00Z"
}
```

**Error 400:**

```json
{
  "error": "Debe proporcionar un nombre"
}
```

**Error 404:**

```json
{
  "error": "Categoría no encontrada"
}
```

---

## Notas

- Todos los endpoints requieren autenticación JWT
- `nombre` es único (no puede haber dos categorías con el mismo nombre)
- No se puede eliminar una categoría con productos asociados
- Búsqueda por nombre es case-insensitive
