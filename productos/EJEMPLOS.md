# API de Productos e Inventario — Guía Completa para Frontend

**Base URL:** `http://localhost:8000/api/productos/`

---

## 🔐 Autenticación

Todos los endpoints POST/PATCH/DELETE requieren token JWT.

**Obtener token:**
```bash
POST /api/usuarios/login/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_password"
}
```

**Respuesta (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": { 
    "id": 1, 
    "username": "tu_usuario", 
    "rol": "Vendedor" 
  }
}
```

**Usar token en headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📦 1. LISTAR PRODUCTOS (CON VARIANTES Y STOCK)

**Endpoint:**
```
GET /
```

**Parámetros (opcional):**
- `search=nombre` — filtrar por nombre
- `categoria=id` — filtrar por categoría
- `active=true` — solo activos

**Ejemplo:**
```bash
GET /?search=remera&active=true
```

**Respuesta (200):**
```json
[
  {
    "id": 1,
    "name": "Remera Azul",
    "description": "Remera básica color azul, 100% algodón",
    "cost_price": "10.00",
    "price": "25.50",
    "categoria": {
      "id": 1,
      "nombre": "Remeras"
    },
    "images": [
      {
        "id": 1,
        "image_url": "https://res.cloudinary.com/.../remera-azul.jpg",
        "alt_text": "Remera azul frente",
        "is_main": true,
        "order": 0
      }
    ],
    "variants": [
      {
        "id": 1,
        "size": "M",
        "color": "Azul",
        "model_name": null,
        "price": null,
        "cost": null,
        "sale_price": "25.50",
        "cost_price": "10.00",
        "stock": 15,
        "is_available": true,
        "is_low_stock": false
      },
      {
        "id": 2,
        "size": "L",
        "color": "Azul",
        "model_name": null,
        "price": "27.50",
        "cost": null,
        "sale_price": "27.50",
        "cost_price": "10.00",
        "stock": 3,
        "is_available": true,
        "is_low_stock": true
      },
      {
        "id": 3,
        "size": "XL",
        "color": "Rojo",
        "model_name": null,
        "price": "30.00",
        "cost": "12.00",
        "sale_price": "30.00",
        "cost_price": "12.00",
        "stock": 0,
        "is_available": false,
        "is_low_stock": false
      }
    ],
    "active": true,
    "total_stock": 18,
    "is_available": true,
    "created_at": "2025-11-11T10:00:00Z"
  }
]
```

**Frontend debe mostrar:**
- ✅ Nombre, descripción, precio de venta (`price`)
- ✅ Primera imagen (`images[0].image_url`)
- ✅ Stock total (`total_stock`) — suma de todas las variantes
- ✅ Tallas disponibles — filtrar `variants` donde `is_available: true`
- ✅ Badge "Stock Bajo" si alguna variante tiene `is_low_stock: true`
- ✅ Badge "Agotado" si `is_available: false`

---

## 📄 2. DETALLE DE PRODUCTO

**Endpoint:**
```
GET /{id}/
```

**Ejemplo:**
```bash
GET /1/
```

**Respuesta (200):**
```json
{
  "id": 1,
  "name": "Remera Azul",
  "description": "Remera básica color azul, 100% algodón",
  "cost_price": "10.00",
  "price": "25.50",
  "categoria": {
    "id": 1,
    "nombre": "Remeras"
  },
  "images": [
    {
      "id": 1,
      "image_url": "https://res.cloudinary.com/.../remera-azul-front.jpg",
      "alt_text": "Frente",
      "is_main": true,
      "order": 0
    },
    {
      "id": 2,
      "image_url": "https://res.cloudinary.com/.../remera-azul-back.jpg",
      "alt_text": "Espalda",
      "is_main": false,
      "order": 1
    }
  ],
  "variants": [
    {
      "id": 1,
      "size": "M",
      "color": "Azul",
      "model_name": null,
      "price": null,
      "cost": null,
      "sale_price": "25.50",
      "cost_price": "10.00",
      "stock": 15,
      "is_available": true,
      "is_low_stock": false
    },
    {
      "id": 2,
      "size": "L",
      "color": "Azul",
      "model_name": null,
      "price": "27.50",
      "cost": null,
      "sale_price": "27.50",
      "cost_price": "10.00",
      "stock": 3,
      "is_available": true,
      "is_low_stock": true
    }
  ],
  "available_variants": [
    {
      "id": 1,
      "size": "M",
      "color": "Azul",
      "stock": 15,
      "sale_price": "25.50",
      "is_available": true,
      "is_low_stock": false
    },
    {
      "id": 2,
      "size": "L",
      "color": "Azul",
      "stock": 3,
      "sale_price": "27.50",
      "is_available": true,
      "is_low_stock": true
    }
  ],
  "active": true,
  "total_stock": 18,
  "is_available": true,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Frontend debe mostrar:**
- ✅ Galería de imágenes (todas)
- ✅ Información completa del producto
- ✅ **Selector de talla/color** — mostrar solo `available_variants` (con stock > 0)
  - Cada opción debe incluir: talla, color, stock disponible, precio
  - Deshabilitar tallas sin stock
- ✅ Precio dinámico según variante seleccionada (`sale_price`)
- ✅ Stock disponible de la variante seleccionada
- ✅ Botón "Agregar al carrito" (solo si `is_available: true`)

---

## ➕ 3. CREAR PRODUCTO CON VARIANTES E IMÁGENES

**Endpoint:**
```
POST /
```

**Headers:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: multipart/form-data
```

**Campos (form-data):**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `name` | string | ✓ | Nombre del producto |
| `description` | string | ✗ | Descripción |
| `cost_price` | decimal | ✓ | Precio de COSTO (lo que te cuesta) |
| `price` | decimal | ✓ | Precio de VENTA (precio al público) |
| `categoria` | integer | ✓ | ID de categoría |
| `active` | boolean | ✗ | Activo (default: true) |
| `variants` | JSON string | ✓ | Array de variantes (al menos 1) |
| `images` | file[] | ✗ | Imágenes (múltiples archivos) |

**Estructura de `variants` (JSON string):**
```json
[
  {
    "size": "M",
    "color": "Azul",
    "model_name": null,
    "stock": 15,
    "price": null,
    "cost": null
  },
  {
    "size": "L",
    "color": "Azul",
    "stock": 10,
    "price": 27.50,
    "cost": null
  },
  {
    "size": "XL",
    "color": "Rojo",
    "stock": 5,
    "price": 30.00,
    "cost": 12.00
  }
]
```

**Explicación de campos de variante:**
- `size` (string, opcional): Talla (XS, S, M, L, XL, XXL, etc.)
- `color` (string, opcional): Color de la prenda
- `model_name` (string, opcional): Nombre del modelo específico
- `stock` (integer, requerido): Stock inicial de esta variante (mínimo 0)
- `price` (decimal, opcional): Precio de VENTA específico para esta variante
  - Si es `null`, hereda `product.price`
  - **Útil para:** cobrar más por tallas grandes (ej: XL más caro que M)
- `cost` (decimal, opcional): Precio de COSTO específico para esta variante
  - Si es `null`, hereda `product.cost_price`
  - **Útil para:** algunas variantes cuestan más (ej: color especial requiere tela importada)

**⚠️ IMPORTANTE:** Cada variante representa un producto único en inventario con su propio stock.

**Ejemplo (JavaScript/FormData):**
```javascript
const formData = new FormData();
formData.append('name', 'Remera Básica');
formData.append('description', 'Remera 100% algodón');
formData.append('cost_price', '10.00');  // Precio de costo base
formData.append('price', '25.50');       // Precio de venta base
formData.append('categoria', '1');
formData.append('active', 'true');

// Variantes: cada una es un "producto" independiente en inventario
const variants = [
  {
    size: 'M',
    color: 'Azul',
    stock: 15
    // Hereda cost_price=10.00 y price=25.50 del producto
  },
  {
    size: 'L',
    color: 'Azul',
    stock: 10,
    price: 27.50  // Talla L cuesta más
    // Hereda cost_price=10.00 del producto
  },
  {
    size: 'XL',
    color: 'Rojo',
    stock: 5,
    price: 30.00,   // Precio de venta específico
    cost: 12.00     // Costo específico (tela especial)
  }
];
formData.append('variants', JSON.stringify(variants));

// Imágenes (múltiples)
fileInputs.forEach(file => formData.append('images', file));

// Enviar
fetch('/api/productos/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token },
  body: formData
})
.then(r => r.json())
.then(data => console.log('Producto creado:', data));
```

**Respuesta (201):**
```json
{
  "id": 1,
  "name": "Remera Básica",
  "description": "Remera 100% algodón",
  "cost_price": "10.00",
  "price": "25.50",
  "categoria": {
    "id": 1,
    "nombre": "Remeras"
  },
  "images": [
    {
      "id": 1,
      "image_url": "https://res.cloudinary.com/.../imagen1.jpg",
      "is_main": true,
      "order": 0
    }
  ],
  "variants": [
    {
      "id": 1,
      "size": "M",
      "color": "Azul",
      "price": null,
      "cost": null,
      "sale_price": "25.50",
      "cost_price": "10.00",
      "stock": 15,
      "is_available": true,
      "is_low_stock": false
    },
    {
      "id": 2,
      "size": "L",
      "color": "Azul",
      "price": "27.50",
      "cost": null,
      "sale_price": "27.50",
      "cost_price": "10.00",
      "stock": 10,
      "is_available": true,
      "is_low_stock": false
    },
    {
      "id": 3,
      "size": "XL",
      "color": "Rojo",
      "price": "30.00",
      "cost": "12.00",
      "sale_price": "30.00",
      "cost_price": "12.00",
      "stock": 5,
      "is_available": true,
      "is_low_stock": true
    }
  ],
  "total_stock": 30,
  "is_available": true,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

---

## 🔄 4. ACTUALIZAR PRODUCTO Y VARIANTES

**Endpoint:**
```
PATCH /{id}/
```

**Headers:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: multipart/form-data
```

**Ejemplo: Agregar nueva variante a producto existente**
```javascript
const formData = new FormData();

// Actualizar variantes (reemplaza todas las existentes)
const variants = [
  // Variantes existentes (mantener)
  { size: 'M', color: 'Azul', stock: 15 },
  { size: 'L', color: 'Azul', stock: 10, price: 27.50 },
  // Nueva variante
  { size: 'XL', color: 'Verde', stock: 8, price: 28.00 }
];
formData.append('variants', JSON.stringify(variants));

fetch('/api/productos/1/', {
  method: 'PATCH',
  headers: { 'Authorization': 'Bearer ' + token },
  body: formData
});
```

**⚠️ NOTA:** El endpoint UPDATE actual elimina todas las variantes antiguas y crea las nuevas. Si quieres añadir variantes sin eliminar las existentes, primero obtén las variantes actuales (GET /api/productos/{id}/), combínalas con las nuevas y envía el array completo.

---

## 📊 5. INVENTARIO COMPLETO (VISTA AGRUPADA POR PRODUCTO)

**Endpoint:**
```
GET /inventario/
```

**Headers:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Parámetros (opcional):**
- `categoria=id` — filtrar por categoría
- `search=texto` — buscar por nombre de producto, talla o color
- `low_stock=true` — solo variantes con stock bajo (< 5)
- `out_of_stock=true` — solo variantes sin stock

**Ejemplo:**
```bash
GET /inventario/?low_stock=true
```

**Respuesta (200):**
```json
{
  "count": 2,
  "results": [
    {
      "product_id": 1,
      "product_name": "Remera Básica",
      "categoria": {
        "id": 1,
        "nombre": "Remeras"
      },
      "total_stock": 30,
      "variants": [
        {
          "id": 1,
          "product_id": 1,
          "product_name": "Remera Básica",
          "categoria": {
            "id": 1,
            "nombre": "Remeras"
          },
          "size": "M",
          "color": "Azul",
          "model_name": null,
          "sale_price": "25.50",
          "cost_price": "10.00",
          "stock": 15,
          "is_available": true,
          "is_low_stock": false
        },
        {
          "id": 2,
          "product_id": 1,
          "product_name": "Remera Básica",
          "categoria": {
            "id": 1,
            "nombre": "Remeras"
          },
          "size": "L",
          "color": "Azul",
          "model_name": null,
          "sale_price": "27.50",
          "cost_price": "10.00",
          "stock": 3,
          "is_available": true,
          "is_low_stock": true
        },
        {
          "id": 3,
          "product_id": 1,
          "product_name": "Remera Básica",
          "categoria": {
            "id": 1,
            "nombre": "Remeras"
          },
          "size": "XL",
          "color": "Rojo",
          "model_name": null,
          "sale_price": "30.00",
          "cost_price": "12.00",
          "stock": 0,
          "is_available": false,
          "is_low_stock": false
        }
      ]
    },
    {
      "product_id": 2,
      "product_name": "Pantalón Negro",
      "categoria": {
        "id": 2,
        "nombre": "Pantalones"
      },
      "total_stock": 12,
      "variants": [
        {
          "id": 4,
          "product_id": 2,
          "product_name": "Pantalón Negro",
          "size": "32",
          "color": "Negro",
          "sale_price": "45.00",
          "cost_price": "20.00",
          "stock": 8,
          "is_available": true,
          "is_low_stock": false
        },
        {
          "id": 5,
          "product_id": 2,
          "product_name": "Pantalón Negro",
          "size": "34",
          "color": "Negro",
          "sale_price": "45.00",
          "cost_price": "20.00",
          "stock": 4,
          "is_available": true,
          "is_low_stock": true
        }
      ]
    }
  ]
}
```

**Frontend debe mostrar (tabla de inventario):**

| Producto | Categoría | Talla | Color | Costo | Venta | Stock | Estado | Acciones |
|----------|-----------|-------|-------|-------|-------|-------|--------|----------|
| Remera Básica | Remeras | M | Azul | $10.00 | $25.50 | 15 | ✅ Disponible | [Ajustar] |
| Remera Básica | Remeras | L | Azul | $10.00 | $27.50 | 3 | ⚠️ Stock Bajo | [Ajustar] |
| Remera Básica | Remeras | XL | Rojo | $12.00 | $30.00 | 0 | ❌ Agotado | [Reponer] |
| Pantalón Negro | Pantalones | 32 | Negro | $20.00 | $45.00 | 8 | ✅ Disponible | [Ajustar] |
| Pantalón Negro | Pantalones | 34 | Negro | $20.00 | $45.00 | 4 | ⚠️ Stock Bajo | [Ajustar] |

**Indicadores de estado:**
- ✅ **Disponible:** `is_available: true` y `is_low_stock: false`
- ⚠️ **Stock Bajo:** `is_low_stock: true` (stock < 5 pero > 0)
- ❌ **Agotado:** `is_available: false` (stock = 0)

**⚠️ NOTA IMPORTANTE:** Este endpoint muestra precios de costo. Solo debe ser accesible para usuarios administradores. Los clientes finales NO deben ver `cost_price`.

---

## 🔄 6. GESTIÓN DE STOCK DE VARIANTES

### 6.1. Actualizar stock (reemplazar valor)

**Endpoint:**
```
PATCH /variants/{variant_id}/update-stock/
```

**Headers:**
```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "stock": 20
}
```

**Respuesta (200):**
```json
{
  "message": "Stock actualizado correctamente",
  "variant": {
    "id": 1,
    "size": "M",
    "color": "Azul",
    "sale_price": "25.50",
    "cost_price": "10.00",
    "stock": 20,
    "is_available": true,
    "is_low_stock": false
  }
}
```

---

### 6.2. Incrementar stock (reposición)

**Body (JSON):**
```json
{
  "action": "increase",
  "quantity": 10
}
```

**Respuesta (200):**
```json
{
  "message": "Stock incrementado en 10",
  "variant": {
    "id": 1,
    "stock": 30,
    "is_available": true
  }
}
```

**Casos de uso:**
- ✅ Recibiste nueva mercadería
- ✅ Ajuste por conteo físico
- ✅ Devolución de cliente

---

### 6.3. Decrementar stock (venta manual o ajuste)

**Body (JSON):**
```json
{
  "action": "decrease",
  "quantity": 2
}
```

**Respuesta (200):**
```json
{
  "message": "Stock reducido en 2",
  "variant": {
    "id": 1,
    "stock": 28,
    "is_available": true
  }
}
```

**Error (stock insuficiente):**
```json
{
  "error": "Stock insuficiente. Disponible: 1, Solicitado: 2"
}
```

**Casos de uso:**
- ✅ Venta sin sistema (manual)
- ✅ Producto dañado
- ✅ Ajuste por inventario físico

---

## 🛒 7. FLUJO DE VENTA (INTEGRACIÓN CON VARIANTES)

### ⚠️ CRÍTICO: Usar `variant_id`, NO solo `product_id`

Cuando el cliente agrega un producto al carrito, el frontend **DEBE**:

1. ✅ Guardar el `variant_id` (ID de la variante específica)
2. ✅ Guardar el `sale_price` de esa variante
3. ✅ Validar que `is_available: true`
4. ✅ Respetar el stock disponible de esa variante

**Estructura del carrito (frontend):**
```json
{
  "items": [
    {
      "variant_id": 1,
      "product_id": 1,
      "product_name": "Remera Básica",
      "size": "M",
      "color": "Azul",
      "quantity": 2,
      "price": 25.50,
      "stock_available": 15
    },
    {
      "variant_id": 2,
      "product_id": 1,
      "product_name": "Remera Básica",
      "size": "L",
      "color": "Azul",
      "quantity": 1,
      "price": 27.50,
      "stock_available": 3
    }
  ],
  "total": 78.50
}
```

**Al confirmar la venta (POST /api/ventas/pedidos/):**
```json
{
  "items": [
    {
      "producto_id": 1,
      "variante_id": 1,
      "nombre": "Remera Básica - M - Azul",
      "cantidad": 2,
      "precio": 25.50
    },
    {
      "producto_id": 1,
      "variante_id": 2,
      "nombre": "Remera Básica - L - Azul",
      "cantidad": 1,
      "precio": 27.50
    }
  ],
  "total": 78.50,
  "metodo_pago": "efectivo"
}
```

**El backend automáticamente:**
1. ✅ Verifica que cada `variant_id` existe
2. ✅ Valida stock suficiente: `variant.stock >= cantidad`
3. ✅ Reduce stock: `variant.reduce_stock(cantidad)`
4. ✅ Crea registro en `InventoryMovement` (auditoría)
5. ✅ Actualiza `is_available` y `is_low_stock` automáticamente

**Ejemplo de validación en frontend antes de enviar:**
```javascript
function validateCart(cartItems) {
  for (const item of cartItems) {
    if (!item.variant_id) {
      alert('Error: falta variant_id en el carrito');
      return false;
    }
    if (item.quantity > item.stock_available) {
      alert(`Stock insuficiente para ${item.product_name} ${item.size}: disponible ${item.stock_available}, solicitado ${item.quantity}`);
      return false;
    }
    if (!item.is_available) {
      alert(`${item.product_name} ${item.size} no está disponible`);
      return false;
    }
  }
  return true;
}

// Antes de confirmar pedido
if (validateCart(cartItems)) {
  fetch('/api/ventas/pedidos/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });
}
```

---

## 📈 8. REPORTES DE INVENTARIO

### 8.1. Variantes con stock bajo

**Endpoint:**
```
GET /variants/low-stock/
```

**Headers:**
```
Authorization: Bearer <ACCESS_TOKEN>
```

**Respuesta (200):**
```json
[
  {
    "id": 2,
    "product_id": 1,
    "product_name": "Remera Básica",
    "size": "L",
    "color": "Azul",
    "stock": 3,
    "is_available": true,
    "is_low_stock": true
  },
  {
    "id": 5,
    "product_id": 2,
    "product_name": "Pantalón Negro",
    "size": "34",
    "color": "Negro",
    "stock": 4,
    "is_available": true,
    "is_low_stock": true
  }
]
```

**Frontend debe mostrar:**
- ⚠️ Alerta/notificación de productos a reponer
- 📋 Lista de variantes con badge "Stock Bajo"
- 🔔 Opción de generar orden de compra

---

### 8.2. Variantes agotadas

**Endpoint:**
```
GET /variants/out-of-stock/
```

**Respuesta (200):**
```json
[
  {
    "id": 3,
    "product_id": 1,
    "product_name": "Remera Básica",
    "size": "XL",
    "color": "Rojo",
    "stock": 0,
    "is_available": false
  }
]
```

**Frontend debe mostrar:**
- ❌ Badge "Agotado" en catálogo
- 🚫 Deshabilitar opción de compra
- 📧 Opción "Notificarme cuando esté disponible"

---

## 🎯 CAMPOS CLAVE PARA EL FRONTEND

### Producto:
| Campo | Tipo | Descripción | Uso en Frontend | Visible para Cliente |
|-------|------|-------------|-----------------|----------------------|
| `id` | integer | ID único del producto | Identificación | ✅ |
| `name` | string | Nombre del producto | Mostrar en catálogo | ✅ |
| `description` | string | Descripción | Detalle del producto | ✅ |
| `cost_price` | decimal | Precio de COSTO | **Solo admin** | ❌ |
| `price` | decimal | Precio de VENTA base | Precio por defecto | ✅ |
| `categoria` | object | Categoría del producto | Filtros y navegación | ✅ |
| `images` | array | Imágenes del producto | Galería | ✅ |
| `variants` | array | Todas las variantes | Selector de talla/color | ✅ |
| `available_variants` | array | Solo variantes con stock | Opciones del selector | ✅ |
| `total_stock` | integer | Stock total (suma) | Indicador general | ✅ |
| `is_available` | boolean | Producto disponible | Habilitar/deshabilitar compra | ✅ |
| `active` | boolean | Producto activo | Mostrar/ocultar en catálogo | ✅ |

### Variante:
| Campo | Tipo | Descripción | Uso en Frontend | Visible para Cliente |
|-------|------|-------------|-----------------|----------------------|
| `id` | integer | ID único de la variante | **CRÍTICO: USAR PARA VENTAS** | ❌ (interno) |
| `size` | string | Talla (M, L, XL, etc.) | Mostrar en selector | ✅ |
| `color` | string | Color | Mostrar en selector | ✅ |
| `model_name` | string | Nombre del modelo | Opcional | ✅ |
| `price` | decimal | Precio específico o null | Interno | ❌ |
| `cost` | decimal | Costo específico o null | **Solo admin** | ❌ |
| `sale_price` | decimal | Precio de venta efectivo | **USAR ESTE PRECIO** | ✅ |
| `cost_price` | decimal | Costo efectivo | **Solo admin/inventario** | ❌ |
| `stock` | integer | Stock disponible | Mostrar y validar | ✅ |
| `is_available` | boolean | Variante disponible | Habilitar opción | ✅ |
| `is_low_stock` | boolean | Stock bajo (< 5) | Badge "Pocas unidades" | ✅ |

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

| Error | Causa | Solución |
|-------|-------|----------|
| 400 - `"variants": ["Debe incluir al menos una variante"]` | No se envió campo `variants` | Enviar `variants` como JSON string en form-data |
| 400 - `"variants": ["JSON de variantes inválido"]` | JSON malformado | Validar JSON: `JSON.stringify(variants)` |
| 400 - `"categoria": ["Categoría ... no existe"]` | ID de categoría inválido | Listar categorías antes y validar ID |
| 400 - `"Stock insuficiente. Disponible: X, Solicitado: Y"` | Intentar vender más de lo disponible | Validar `stock` antes de agregar al carrito |
| 400 - `"variante_id": ["This field is required"]` | No se envió `variante_id` en venta | Asegurar que cada item tenga `variante_id` |
| 404 - `"ProductVariant matching query does not exist"` | `variant_id` inválido | Verificar que la variante existe antes de vender |

---

## 🎯 CHECKLIST PARA FRONTEND

### Al listar productos (catálogo):
- ✅ Mostrar `total_stock` para indicar disponibilidad general
- ✅ Filtrar solo `available_variants` para mostrar tallas disponibles
- ✅ Badge "Stock Bajo" si alguna variante tiene `is_low_stock: true`
- ✅ Badge "Agotado" si `is_available: false`
- ✅ Deshabilitar botón "Agregar al carrito" si no hay stock

### Al mostrar detalle de producto:
- ✅ Selector de talla/color con solo `available_variants`
- ✅ Mostrar `sale_price` de la variante seleccionada (puede variar)
- ✅ Mostrar `stock` de la variante seleccionada
- ✅ Validar cantidad <= stock disponible
- ✅ Actualizar precio al cambiar de variante

### Al crear carrito:
- ✅ Guardar `variant_id` (NO solo `product_id`)
- ✅ Guardar `sale_price` de la variante
- ✅ Validar `is_available: true` antes de agregar
- ✅ Validar cantidad <= stock
- ✅ Mostrar: "Producto - Talla - Color"

### Al confirmar venta:
- ✅ Enviar `variante_id` en cada item
- ✅ Enviar `precio` de la variante (el `sale_price` mostrado)
- ✅ Backend automáticamente reduce stock
- ✅ Manejar error de stock insuficiente

### En panel de inventario (admin):
- ✅ Mostrar todas las variantes agrupadas por producto
- ✅ Mostrar `cost_price` y `sale_price`
- ✅ Resaltar variantes con `is_low_stock: true`
- ✅ Permitir ajustar stock (incrementar/decrementar/reemplazar)
- ✅ Filtros: categoría, búsqueda, stock bajo, agotados
- ✅ Exportar reportes de inventario

---

## 📋 EJEMPLO COMPLETO DE FLUJO

### 1. Cliente ve catálogo
```javascript
fetch('/api/productos/?active=true')
  .then(r => r.json())
  .then(products => {
    products.forEach(p => {
      console.log(`${p.name} - Stock total: ${p.total_stock}`);
      
      // Mostrar tallas disponibles
      const sizes = p.available_variants.map(v => v.size).join(', ');
      console.log(`Tallas disponibles: ${sizes}`);
      
      // Verificar si hay stock bajo
      const hasLowStock = p.variants.some(v => v.is_low_stock);
      if (hasLowStock) {
        console.log('⚠️ Algunas tallas con pocas unidades');
      }
    });
  });
```

---

### 2. Cliente selecciona producto y talla
```javascript
// Usuario selecciona talla "L" y color "Azul"
const selectedVariant = product.variants.find(
  v => v.size === 'L' && v.color === 'Azul'
);

if (selectedVariant && selectedVariant.is_available) {
  // Mostrar información de la variante seleccionada
  document.getElementById('price').textContent = `$${selectedVariant.sale_price}`;
  document.getElementById('stock').textContent = `Stock: ${selectedVariant.stock} unidades`;
  
  if (selectedVariant.is_low_stock) {
    document.getElementById('stock-warning').textContent = '⚠️ Pocas unidades disponibles';
  }
  
  // Agregar al carrito
  addToCart({
    variant_id: selectedVariant.id,
    product_id: product.id,
    product_name: product.name,
    size: selectedVariant.size,
    color: selectedVariant.color,
    quantity: 1,
    price: parseFloat(selectedVariant.sale_price),
    stock_available: selectedVariant.stock
  });
} else {
  alert('Esta combinación de talla/color no está disponible');
}
```

---

### 3. Cliente confirma compra
```javascript
// Validar carrito antes de enviar
function validateAndSubmitOrder(cartItems) {
  // Validar cada item
  for (const item of cartItems) {
    if (!item.variant_id) {
      alert('Error en el carrito: falta información de variante');
      return;
    }
    if (item.quantity > item.stock_available) {
      alert(`Stock insuficiente para ${item.product_name} ${item.size}`);
      return;
    }
  }
  
  // Crear orden
  const orderData = {
    items: cartItems.map(item => ({
      producto_id: item.product_id,
      variante_id: item.variant_id,  // CRÍTICO
      nombre: `${item.product_name} - ${item.size} - ${item.color}`,
      cantidad: item.quantity,
      precio: item.price
    })),
    total: cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0),
    metodo_pago: 'efectivo'
  };
  
  fetch('/api/ventas/pedidos/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  })
  .then(r => {
    if (!r.ok) throw new Error('Error al crear pedido');
    return r.json();
  })
  .then(pedido => {
    console.log('✅ Pedido creado:', pedido.id);
    // Backend automáticamente redujo stock de cada variante
    alert('¡Compra realizada con éxito!');
    clearCart();
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error al procesar la compra. Por favor intenta nuevamente.');
  });
}

// Ejecutar
validateAndSubmitOrder(cartItems);
```

---

### 4. Admin revisa inventario
```javascript
fetch('/api/productos/inventario/?low_stock=true', {
  headers: { 'Authorization': 'Bearer ' + adminToken }
})
.then(r => r.json())
.then(data => {
  console.log(`📊 Productos con stock bajo: ${data.count}`);
  
  data.results.forEach(product => {
    console.log(`\n📦 ${product.product_name} (Stock total: ${product.total_stock})`);
    
    product.variants.forEach(v => {
      if (v.is_low_stock) {
        console.log(`   ⚠️ ${v.size} ${v.color}: ${v.stock} unidades - ¡REPONER!`);
      } else if (!v.is_available) {
        console.log(`   ❌ ${v.size} ${v.color}: AGOTADO`);
      } else {
        console.log(`   ✅ ${v.size} ${v.color}: ${v.stock} unidades`);
      }
    });
  });
});
```

---

### 5. Admin ajusta stock
```javascript
// Aumentar stock (recibió mercadería)
function increaseStock(variantId, quantity) {
  fetch(`/api/productos/variants/${variantId}/update-stock/`, {
    method: 'PATCH',
    headers: {
      'Authorization': 'Bearer ' + adminToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'increase',
      quantity: quantity
    })
  })
  .then(r => r.json())
  .then(data => {
    console.log(`✅ ${data.message}`);
    console.log(`Nuevo stock: ${data.variant.stock}`);
  });
}

// Ejemplo: recibió 20 unidades de remera M azul
increaseStock(1, 20);
```

---

## 📞 SOPORTE

Si algo no funciona:
1. ✅ Verificar token JWT válido y no expirado
2. ✅ Verificar estructura de datos (especialmente `variants` y `variante_id`)
3. ✅ Revisar logs del backend (`python manage.py runserver`)
4. ✅ Comprobar migraciones aplicadas (`python manage.py migrate`)
5. ✅ Verificar que Cloudinary esté configurado para imágenes

**Logs útiles:**
```bash
# Backend logs
python manage.py runserver

# Ver última migración
python manage.py showmigrations productos

# Shell para debug
python manage.py shell
>>> from productos.models import Product, ProductVariant
>>> Product.objects.all()
>>> ProductVariant.objects.filter(stock__lt=5)
```

---

**Última actualización:** 11 de noviembre de 2025  
**Versión:** 2.0 - Sistema de variantes con stock independiente