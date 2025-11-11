# 📦 Módulo de Compras - API REST

## 📋 Descripción

El módulo de **Compras** permite gestionar las compras de productos a proveedores, incluyendo:

- Registro de proveedores
- Creación de compras con múltiples productos (DetalleCompra)
- **Actualización automática del stock** de productos al registrar una compra
- Subida de comprobantes/imágenes de las compras
- Estadísticas de compras

---

## 🗂️ Modelos

### **Proveedor**

```python
{
  "idProveedor": 1,
  "nombre": "Distribuidora ABC",
  "telefono": "12345678",
  "email": "contacto@abc.com",
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_modificacion": "2025-01-15T10:30:00Z"
}
```

### **Compra**

```python
{
  "idCompra": 1,
  "proveedor": 1,
  "proveedor_detalle": {...},
  "nombre_proveedor": "Distribuidora ABC",
  "total": 1500.00,
  "imagen": "https://res.cloudinary.com/...",  # Comprobante (opcional)
  "fecha_compra": "2025-01-15T10:30:00Z",
  "detalles": [...],
  "cantidad_productos": 3
}
```

### **DetalleCompra**

```python
{
  "idDetalleCompra": 1,
  "producto": 5,
  "producto_detalle": {...},
  "nombre_producto": "Laptop HP",
  "cantidad": 10,
  "precio": 500.00,
  "subtotal": 5000.00,
  "fecha_creacion": "2025-01-15T10:30:00Z"
}
```

---

## 🔗 Endpoints

### **PROVEEDORES**

#### 1. Listar Proveedores

```http
GET /api/compras/proveedores/
Authorization: Bearer {token}
```

**Respuesta:**

```json
[
  {
    "idProveedor": 1,
    "nombre": "Distribuidora ABC",
    "telefono": "12345678",
    "email": "contacto@abc.com",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_modificacion": "2025-01-15T10:30:00Z"
  }
]
```

#### 2. Crear Proveedor

```http
POST /api/compras/proveedores/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Distribuidora XYZ",
  "telefono": "87654321",
  "email": "ventas@xyz.com"
}
```

#### 3. Obtener Proveedor

```http
GET /api/compras/proveedores/{id_proveedor}/
Authorization: Bearer {token}
```

#### 4. Actualizar Proveedor

```http
PUT /api/compras/proveedores/{id_proveedor}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nombre": "Distribuidora XYZ S.A.",
  "telefono": "11112222"
}
```

#### 5. Eliminar Proveedor

```http
DELETE /api/compras/proveedores/{id_proveedor}/
Authorization: Bearer {token}
```

**Nota:** No se puede eliminar un proveedor con compras asociadas.

#### 6. Buscar Proveedores

```http
GET /api/compras/proveedores/buscar/?q=ABC
Authorization: Bearer {token}
```

---

### **COMPRAS**

#### 1. Listar Compras

```http
GET /api/compras/
Authorization: Bearer {token}
```

**Respuesta:**

```json
[
  {
    "idCompra": 1,
    "proveedor": 1,
    "proveedor_detalle": {
      "idProveedor": 1,
      "nombre": "Distribuidora ABC"
    },
    "nombre_proveedor": "Distribuidora ABC",
    "total": 1500.0,
    "imagen": "https://res.cloudinary.com/...",
    "fecha_compra": "2025-01-15T10:30:00Z",
    "detalles": [
      {
        "idDetalleCompra": 1,
        "producto": 5,
        "nombre_producto": "Laptop HP",
        "cantidad": 10,
        "precio": 500.0,
        "subtotal": 5000.0
      }
    ],
    "cantidad_productos": 1
  }
]
```

#### 2. Crear Compra (⭐ Actualiza Stock Automáticamente)

```http
POST /api/compras/
Authorization: Bearer {token}
Content-Type: application/json

{
  "proveedor": 1,
  "detalles": [
    {
      "producto": 5,
      "cantidad": 10,
      "precio": 500.00
    },
    {
      "producto": 8,
      "cantidad": 5,
      "precio": 200.00
    }
  ],
  "imagen": <archivo opcional>
}
```

**⚠️ IMPORTANTE:** Al crear una compra:

- Se crea el registro de la compra
- Se crean los detalles de compra
- **Se actualiza automáticamente el stock de cada producto** (suma la cantidad comprada)
- Se calcula el total automáticamente
- Se puede subir una imagen/comprobante (opcional)

**Respuesta:**

```json
{
  "mensaje": "Compra registrada correctamente",
  "compra": {
    "idCompra": 1,
    "proveedor": 1,
    "total": 6000.00,
    "detalles": [...]
  },
  "productos_actualizados": 2
}
```

#### 3. Obtener Compra por ID

```http
GET /api/compras/{id_compra}/
Authorization: Bearer {token}
```

#### 4. Eliminar Compra

```http
DELETE /api/compras/{id_compra}/
Authorization: Bearer {token}
```

**⚠️ NOTA:** Eliminar una compra NO revierte el stock. Si necesitas revertir el stock, debes implementar esa lógica.

#### 5. Actualizar Imagen/Comprobante

```http
PUT /api/compras/{id_compra}/imagen/
Authorization: Bearer {token}
Content-Type: multipart/form-data

imagen: <archivo>
```

**Respuesta:**

```json
{
  "mensaje": "Comprobante actualizado correctamente",
  "compra": {
    "idCompra": 1,
    "imagen": "https://res.cloudinary.com/..."
  }
}
```

#### 6. Listar Compras por Proveedor

```http
GET /api/compras/proveedor/{id_proveedor}/
Authorization: Bearer {token}
```

#### 7. Estadísticas de Compras

```http
GET /api/compras/estadisticas/
Authorization: Bearer {token}
```

**Respuesta:**

```json
{
  "total_compras": 25,
  "monto_total": 50000.0,
  "promedio_por_compra": 2000.0,
  "proveedor_top": {
    "proveedor__nombre": "Distribuidora ABC",
    "cantidad": 15,
    "total_gastado": 30000.0
  }
}
```

---

## 🔄 Flujo de Compra (con actualización de stock)

### Ejemplo Completo:

**1. Estado inicial del producto:**

```json
{
  "idProducto": 5,
  "nombre": "Laptop HP",
  "stock": 3, // <- Stock actual
  "precio": 5000.0
}
```

**2. Crear compra:**

```http
POST /api/compras/
{
  "proveedor": 1,
  "detalles": [
    {
      "producto": 5,
      "cantidad": 10,  // <- Compramos 10 unidades
      "precio": 4500.00
    }
  ]
}
```

**3. Resultado (automático):**

- ✅ Se crea la compra con `total = 45000.00`
- ✅ Se crea el detalle con `subtotal = 45000.00`
- ✅ **El stock del producto se actualiza a: 3 + 10 = 13**

**4. Verificar producto actualizado:**

```json
{
  "idProducto": 5,
  "nombre": "Laptop HP",
  "stock": 13, // <- ✅ Stock actualizado
  "precio": 5000.0
}
```

---

## 🧪 Testing con Postman

### 1. Crear Proveedor

```
POST http://localhost:8000/api/compras/proveedores/
Headers:
  Authorization: Bearer {tu_token_jwt}
  Content-Type: application/json

Body:
{
  "nombre": "Proveedor Test",
  "telefono": "12345678",
  "email": "test@proveedor.com"
}
```

### 2. Crear Compra (con stock update)

```
POST http://localhost:8000/api/compras/
Headers:
  Authorization: Bearer {tu_token_jwt}
  Content-Type: application/json

Body:
{
  "proveedor": 1,
  "detalles": [
    {
      "producto": 1,
      "cantidad": 50,
      "precio": 100.00
    }
  ]
}
```

### 3. Subir Comprobante

```
PUT http://localhost:8000/api/compras/1/imagen/
Headers:
  Authorization: Bearer {tu_token_jwt}
  Content-Type: multipart/form-data

Body (form-data):
  imagen: [seleccionar archivo]
```

---

## 📊 Diagrama de Flujo

```
1. Usuario crea compra
   ↓
2. Backend valida datos (proveedor existe, productos existen)
   ↓
3. Se inicia transacción (@transaction.atomic)
   ↓
4. Se crea registro de Compra
   ↓
5. Para cada detalle:
   - Se crea DetalleCompra
   - Se calcula subtotal
   - **SE ACTUALIZA STOCK: producto.stock += cantidad**
   - Se acumula total
   ↓
6. Se actualiza total de la compra
   ↓
7. Se guarda imagen si existe
   ↓
8. Se confirma transacción (commit)
   ↓
9. Se retorna compra creada con detalles
```

---

## ⚠️ Consideraciones Importantes

### **Actualización de Stock:**

- ✅ El stock se actualiza **automáticamente** al crear una compra
- ⚠️ Al **eliminar** una compra, el stock **NO se revierte** automáticamente
- 💡 Si necesitas revertir stock, debes:
  1. Obtener los detalles de la compra
  2. Restar las cantidades del stock
  3. Eliminar la compra

### **Transacciones:**

- Se usa `@transaction.atomic` para garantizar consistencia
- Si falla algún paso, **toda la operación se revierte**
- No se crean registros inconsistentes

### **Validaciones:**

- Cantidad y precio deben ser > 0
- El proveedor debe existir
- Los productos deben existir
- Al menos un detalle es requerido

### **Eliminación de Proveedores:**

- No se puede eliminar un proveedor con compras asociadas
- Se retorna error 400 con mensaje descriptivo

---

## 🔐 Permisos

Todos los endpoints requieren:

- ✅ **Autenticación JWT** (`IsAuthenticated`)
- 📝 Header: `Authorization: Bearer {token}`

---

## 📝 Migraciones

```bash
# Crear migraciones
python manage.py makemigrations compras

# Aplicar migraciones
python manage.py migrate compras
```

---

## 🚀 Deploy

El módulo está listo para Render:

- ✅ Serializers creados
- ✅ Services con lógica de negocio
- ✅ Views con autenticación
- ✅ URLs configuradas
- ✅ Admin panel configurado
- ✅ Actualización de stock implementada
- ✅ Soporte para Cloudinary (imágenes)

---

## 📚 Resumen de Archivos

```
compras/
├── models.py              # Proveedor, Compra, DetalleCompra
├── serializers.py         # Serializers para validación
├── services/
│   ├── service_proveedor.py  # Lógica de proveedores
│   └── service_compra.py     # Lógica de compras + stock update
├── views.py               # APIViews con autenticación
├── urls.py                # Rutas del módulo
├── admin.py               # Configuración del admin
└── migrations/            # Migraciones de BD
```
