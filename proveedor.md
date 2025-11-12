# API Proveedores - Documentación Técnica

Base URL: `/api/compras/proveedores`

---

## 1. GET /api/compras/proveedores/

**Autenticación:** Requerida (IsAuthenticated)

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProveedor": 1,
    "nombre": "Proveedor Tech S.A.",
    "telefono": "555-1234",
    "email": "contacto@proveedortech.com",
    "fecha_creacion": "2025-01-10T08:30:00Z",
    "fecha_modificacion": "2025-01-10T08:30:00Z"
  },
  {
    "idProveedor": 2,
    "nombre": "Distribuidora Global",
    "telefono": "555-5678",
    "email": "ventas@distglobal.com",
    "fecha_creacion": "2025-01-15T14:20:00Z",
    "fecha_modificacion": "2025-01-15T14:20:00Z"
  }
]
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 2. POST /api/compras/proveedores/

**Autenticación:** Requerida (IsAuthenticated)

**Request Body:**

```json
{
  "nombre": "Proveedor Tech S.A.",
  "telefono": "555-1234",
  "email": "contacto@proveedortech.com"
}
```

**Response 201:**

```json
{
  "idProveedor": 1,
  "nombre": "Proveedor Tech S.A.",
  "telefono": "555-1234",
  "email": "contacto@proveedortech.com",
  "fecha_creacion": "2025-01-10T08:30:00Z",
  "fecha_modificacion": "2025-01-10T08:30:00Z"
}
```

**Response 400:**

```json
{
  "nombre": ["Este campo es requerido."]
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 3. GET /api/compras/proveedores/buscar/?q={query}

**Autenticación:** Requerida (IsAuthenticated)

**Query Parameters:**

- `q` (string, requerido): Texto a buscar en nombre o email

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProveedor": 1,
    "nombre": "Proveedor Tech S.A.",
    "telefono": "555-1234",
    "email": "contacto@proveedortech.com",
    "fecha_creacion": "2025-01-10T08:30:00Z",
    "fecha_modificacion": "2025-01-10T08:30:00Z"
  }
]
```

**Response 400:**

```json
{
  "error": "Parámetro 'q' requerido"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 4. GET /api/compras/proveedores/{id}/

**Autenticación:** Requerida (IsAuthenticated)

**Path Parameters:**

- `id` (integer): ID del proveedor

**Request Body:** Ninguno

**Response 200:**

```json
{
  "idProveedor": 1,
  "nombre": "Proveedor Tech S.A.",
  "telefono": "555-1234",
  "email": "contacto@proveedortech.com",
  "fecha_creacion": "2025-01-10T08:30:00Z",
  "fecha_modificacion": "2025-01-10T08:30:00Z"
}
```

**Response 404:**

```json
{
  "error": "Proveedor no encontrado"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 5. PUT /api/compras/proveedores/{id}/

**Autenticación:** Requerida (IsAuthenticated)

**Path Parameters:**

- `id` (integer): ID del proveedor

**Request Body:**

```json
{
  "nombre": "Proveedor Tech S.A. Actualizado",
  "telefono": "555-9999",
  "email": "nuevo@proveedortech.com"
}
```

**Response 200:**

```json
{
  "idProveedor": 1,
  "nombre": "Proveedor Tech S.A. Actualizado",
  "telefono": "555-9999",
  "email": "nuevo@proveedortech.com",
  "fecha_creacion": "2025-01-10T08:30:00Z",
  "fecha_modificacion": "2025-02-05T10:15:00Z"
}
```

**Response 400:**

```json
{
  "email": ["Ingrese una dirección de correo electrónico válida."]
}
```

**Response 404:**

```json
{
  "error": "Proveedor no encontrado"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 6. PATCH /api/compras/proveedores/{id}/

**Autenticación:** Requerida (IsAuthenticated)

**Path Parameters:**

- `id` (integer): ID del proveedor

**Request Body (actualización parcial):**

```json
{
  "telefono": "555-8888"
}
```

**Response 200:**

```json
{
  "idProveedor": 1,
  "nombre": "Proveedor Tech S.A.",
  "telefono": "555-8888",
  "email": "contacto@proveedortech.com",
  "fecha_creacion": "2025-01-10T08:30:00Z",
  "fecha_modificacion": "2025-02-05T11:20:00Z"
}
```

**Response 400:**

```json
{
  "email": ["Ingrese una dirección de correo electrónico válida."]
}
```

**Response 404:**

```json
{
  "error": "Proveedor no encontrado"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 7. DELETE /api/compras/proveedores/{id}/

**Autenticación:** Requerida (IsAuthenticated)

**Path Parameters:**

- `id` (integer): ID del proveedor

**Request Body:** Ninguno

**Response 200:**

```json
{
  "mensaje": "Proveedor eliminado correctamente"
}
```

**Response 400:**

```json
{
  "error": "No se puede eliminar el proveedor porque tiene compras asociadas"
}
```

**Response 404:**

```json
{
  "error": "Proveedor no encontrado"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## Notas Técnicas

- Todos los endpoints requieren autenticación JWT
- Campos del modelo Proveedor:
  - `idProveedor`: Primary key (auto-generado)
  - `nombre`: string (requerido, max 200 caracteres)
  - `telefono`: string (opcional, max 20 caracteres)
  - `email`: email (opcional, max 255 caracteres)
  - `fecha_creacion`: datetime (auto-generado)
  - `fecha_modificacion`: datetime (auto-actualizado)
- No se puede eliminar un proveedor si tiene compras asociadas (PROTECT constraint)
- La búsqueda es case-insensitive y busca coincidencias parciales en nombre y email
