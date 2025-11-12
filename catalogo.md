# API Catálogo - Documentación Técnica

Base URL: `/api/catalogo`

---

## 1. GET /api/catalogo/productos/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Lista todos los productos con stock disponible.

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": "850.00",
    "stock": 15,
    "imagen": "producto/laptop_hp_abc123.jpg",
    "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/laptop.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica",
      "descripcion": "Productos electrónicos"
    },
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_modificacion": "2025-01-15T10:30:00Z"
  },
  {
    "idProducto": 2,
    "nombre": "Mouse Logitech",
    "precio": "25.00",
    "stock": 50,
    "imagen": null,
    "imagen_url": null,
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-01-20T14:20:00Z",
    "fecha_modificacion": "2025-01-20T14:20:00Z"
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

## 2. GET /api/catalogo/productos/?categoria={id}

**Autenticación:** No requerida (AllowAny)

**Descripción:** Filtra productos por categoría.

**Query Parameters:**

- `categoria` (integer): ID de la categoría

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProducto": 1,
    "nombre": "Laptop HP",
    "precio": "850.00",
    "stock": 15,
    "imagen": "producto/laptop_hp_abc123.jpg",
    "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/laptop.jpg",
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica",
      "descripcion": "Productos electrónicos"
    },
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_modificacion": "2025-01-15T10:30:00Z"
  }
]
```

**Response 400:**

```json
{
  "error": "ID de categoría inválido"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 3. GET /api/catalogo/productos/{id_producto}/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Obtiene detalles de un producto específico con stock disponible.

**Path Parameters:**

- `id_producto` (integer): ID del producto

**Request Body:** Ninguno

**Response 200:**

```json
{
  "idProducto": 1,
  "nombre": "Laptop HP",
  "precio": "850.00",
  "stock": 15,
  "imagen": "producto/laptop_hp_abc123.jpg",
  "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/laptop.jpg",
  "categoria": {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_modificacion": "2025-01-15T10:30:00Z"
}
```

**Response 404:**

```json
{
  "error": "Producto no encontrado o sin stock"
}
```

**Response 500:**

```json
{
  "error": "Error interno del servidor"
}
```

---

## 4. GET /api/catalogo/categorias/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Lista categorías que tienen productos con stock disponible.

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idCategoria": 1,
    "nombre": "Electrónica",
    "descripcion": "Productos electrónicos"
  },
  {
    "idCategoria": 2,
    "nombre": "Accesorios",
    "descripcion": "Accesorios de computación"
  },
  {
    "idCategoria": 3,
    "nombre": "Oficina",
    "descripcion": "Artículos de oficina"
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

## 5. GET /api/catalogo/productos/destacados/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Retorna los 10 productos con mayor stock (más populares).

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProducto": 5,
    "nombre": "Teclado Mecánico",
    "precio": "120.00",
    "stock": 100,
    "imagen": "producto/teclado_mecanico_xyz789.jpg",
    "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/teclado.jpg",
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-01-10T09:00:00Z",
    "fecha_modificacion": "2025-01-10T09:00:00Z"
  },
  {
    "idProducto": 3,
    "nombre": "Monitor Samsung 24",
    "precio": "200.00",
    "stock": 80,
    "imagen": null,
    "imagen_url": null,
    "categoria": {
      "idCategoria": 1,
      "nombre": "Electrónica",
      "descripcion": "Productos electrónicos"
    },
    "fecha_creacion": "2025-01-12T11:15:00Z",
    "fecha_modificacion": "2025-01-12T11:15:00Z"
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

## 6. GET /api/catalogo/productos/nuevos/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Retorna los 10 productos más recientes ordenados por fecha de creación.

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProducto": 10,
    "nombre": "Webcam Logitech HD",
    "precio": "65.00",
    "stock": 30,
    "imagen": "producto/webcam_logitech_def456.jpg",
    "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/webcam.jpg",
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-02-01T16:45:00Z",
    "fecha_modificacion": "2025-02-01T16:45:00Z"
  },
  {
    "idProducto": 9,
    "nombre": "Auriculares Bluetooth",
    "precio": "80.00",
    "stock": 25,
    "imagen": null,
    "imagen_url": null,
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-01-28T13:30:00Z",
    "fecha_modificacion": "2025-01-28T13:30:00Z"
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

## 7. GET /api/catalogo/productos/mas-vendidos/

**Autenticación:** No requerida (AllowAny)

**Descripción:** Retorna los 10 productos más vendidos (con stock bajo <= 20).

**Request Body:** Ninguno

**Response 200:**

```json
[
  {
    "idProducto": 7,
    "nombre": "Cable HDMI 2m",
    "precio": "15.00",
    "stock": 5,
    "imagen": null,
    "imagen_url": null,
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-01-05T08:20:00Z",
    "fecha_modificacion": "2025-01-05T08:20:00Z"
  },
  {
    "idProducto": 12,
    "nombre": "Mousepad Gaming",
    "precio": "30.00",
    "stock": 8,
    "imagen": "producto/mousepad_gaming_ghi123.jpg",
    "imagen_url": "https://res.cloudinary.com/demo/image/upload/v1234/mousepad.jpg",
    "categoria": {
      "idCategoria": 2,
      "nombre": "Accesorios",
      "descripcion": "Accesorios de computación"
    },
    "fecha_creacion": "2025-01-18T15:00:00Z",
    "fecha_modificacion": "2025-01-18T15:00:00Z"
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

## Notas Técnicas

- Todos los endpoints son públicos (no requieren autenticación)
- Solo se muestran productos con `stock > 0`
- Las categorías solo aparecen si tienen productos con stock disponible
- Productos destacados: ordenados por mayor stock (top 10)
- Productos nuevos: ordenados por fecha_creacion descendente (últimos 10)
- Productos más vendidos: stock <= 20, ordenados por menor stock (top 10)
- Las imágenes se gestionan con Cloudinary:
  - `imagen`: ruta relativa en Cloudinary
  - `imagen_url`: URL completa de la imagen (puede ser null si no tiene imagen)
