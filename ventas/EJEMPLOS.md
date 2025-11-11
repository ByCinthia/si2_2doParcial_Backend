# API de Ventas — Guía Completa con Análisis de Rentabilidad

## 📊 Reportes con Rentabilidad

**Endpoint:** `GET /api/ventas/reportes/?periodo=mes`

**Respuesta (200):**
```json
{
  "periodo": {
    "tipo": "mes",
    "fecha_inicio": "2025-11-01",
    "fecha_fin": "2025-11-30"
  },
  "metricas": {
    "total_ingresos": 2543.50,
    "total_costos": 1200.00,
    "total_ganancia": 1343.50,
    "margen_promedio": 111.96,
    "total_ventas": 28,
    "promedio_venta": 90.84
  },
  "ventas_por_dia": [...],
  "productos_rentables": [
    {
      "producto_id": 1,
      "nombre": "Remera Azul",
      "cantidad_vendida": 15,
      "ingresos": 382.50,
      "costos": 150.00,
      "ganancia": 232.50,
      "margen_porcentaje": 155.0
    },
    {
      "producto_id": 2,
      "nombre": "Pantalón Negro",
      "cantidad_vendida": 8,
      "ingresos": 360.00,
      "costos": 160.00,
      "ganancia": 200.00,
      "margen_porcentaje": 125.0
    }
  ]
}
```

## 💡 Frontend debe mostrar:

### En dashboard de ventas:
- ✅ **Ingresos totales** (lo que cobras)
- ✅ **Costos totales** (lo que te cuestan los productos)
- ✅ **Ganancia neta** (ingresos - costos)
- ✅ **Margen promedio** (%)
- ✅ **Productos más rentables** (ordenados por ganancia)

### En inventario:
- ✅ **Solo precios y stock**
- ❌ **NO mostrar ganancias** (eso es del módulo de ventas)

---

# Ejemplos de uso — app `ventas`

Base URL: `http://localhost:8000/api/ventas/` (requiere autenticación Bearer token)

## 1. Pedidos (Orders) - Gestión básica

### Listar pedidos (GET)
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/ventas/pedidos/
```

**Respuesta (200):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "idPedido": 1,
      "total": "91.00",
      "metodo_pago": "tarjeta",
      "estado": "CREADO",
      "fecha_creacion": "2025-11-11T10:30:00Z",
      "items_count": 2
    },
    {
      "idPedido": 2,
      "total": "50.00",
      "metodo_pago": "efectivo",
      "estado": "PAGADO",
      "fecha_creacion": "2025-11-10T15:45:00Z",
      "items_count": 1
    }
  ]
}
```

### Crear pedido (POST)
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "items":[
      {"producto_id": 12, "nombre":"Remera Azul", "cantidad":2, "precio":25.50},
      {"producto_id": 15, "nombre":"Pantalón Negro", "cantidad":1, "precio":40.00}
    ],
    "total": 91.00,
    "metodo_pago": "tarjeta",
    "datos_cliente": {
      "nombre": "Ana Perez",
      "direccion": "Calle Falsa 123",
      "telefono": "99999999"
    },
    "recoger_hasta": null
  }' \
  http://localhost:8000/api/ventas/pedidos/
```

**Respuesta (201):**
```json
{
  "idPedido": 5
}
```

### Detalle de pedido (GET)
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/ventas/pedidos/5/
```

**Respuesta (200):**
```json
{
  "idPedido": 5,
  "total": "91.00",
  "metodo_pago": "tarjeta",
  "estado": "CREADO",
  "datos_cliente": {
    "nombre": "Ana Perez",
    "direccion": "Calle Falsa 123",
    "telefono": "99999999"
  },
  "recoger_hasta": null,
  "fecha_creacion": "2025-11-11T10:30:00Z",
  "items": [
    {
      "idItem": 8,
      "producto_id": 12,
      "nombre": "Remera Azul",
      "cantidad": 2,
      "precio": "25.50",
      "subtotal": "51.00"
    },
    {
      "idItem": 9,
      "producto_id": 15,
      "nombre": "Pantalón Negro",
      "cantidad": 1,
      "precio": "40.00",
      "subtotal": "40.00"
    }
  ]
}
```

### Confirmar pedido → crear venta (POST)
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "pago": {
      "id_transaccion": "abc123",
      "metodo": "tarjeta"
    }
  }' \
  http://localhost:8000/api/ventas/pedidos/5/confirmar/
```

**Respuesta (201):**
```json
{
  "venta_id": 2
}
```

**Nota:** Esta operación crea una Venta, reduce stock de productos y cambia estado del pedido a PAGADO.

---

## 2. Reportes y Analytics

### Métricas por período (GET)
```bash
# Reporte del mes actual
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/ventas/reportes/?periodo=mes"

# Reporte personalizado
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/ventas/reportes/?periodo=año&fecha_inicio=2024-01-01&fecha_fin=2024-12-31"

# Otros períodos: dia, semana, trimestre, año
```

**Parámetros:**
- `periodo` (opcional): dia | semana | mes | trimestre | año (default: mes)
- `fecha_inicio` (opcional): YYYY-MM-DD
- `fecha_fin` (opcional): YYYY-MM-DD

**Respuesta (200):**
```json
{
  "periodo": {
    "tipo": "mes",
    "fecha_inicio": "2025-10-11",
    "fecha_fin": "2025-11-11"
  },
  "metricas": {
    "total_ingresos": 2543.50,
    "total_ventas": 28,
    "promedio_venta": 90.84
  },
  "ventas_por_dia": [
    {
      "dia": "2025-11-01",
      "total_dia": 245.00,
      "cantidad_dia": 3
    },
    {
      "dia": "2025-11-02",
      "total_dia": 180.50,
      "cantidad_dia": 2
    }
  ],
  "productos_top": [
    {
      "nombre": "Remera Azul",
      "total_vendido": 15,
      "ingresos": 382.50
    },
    {
      "nombre": "Pantalón Negro",
      "total_vendido": 8,
      "ingresos": 320.00
    }
  ]
}
```

### Comparación entre períodos (GET)
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/ventas/comparacion/?periodo_actual_inicio=2025-11-01&periodo_actual_fin=2025-11-30&periodo_anterior_inicio=2025-10-01&periodo_anterior_fin=2025-10-31"
```

**Parámetros (todos requeridos):**
- `periodo_actual_inicio`: YYYY-MM-DD
- `periodo_actual_fin`: YYYY-MM-DD  
- `periodo_anterior_inicio`: YYYY-MM-DD
- `periodo_anterior_fin`: YYYY-MM-DD

**Respuesta (200):**
```json
{
  "periodo_actual": {
    "ingresos": 2543.50,
    "ventas": 28
  },
  "periodo_anterior": {
    "ingresos": 2100.00,
    "ventas": 25
  },
  "crecimiento": {
    "ingresos_porcentaje": 21.12,
    "ventas_porcentaje": 12.0
  }
}
```

---

## 3. Estados y métodos de pago

### Estados de pedido
- `CREADO` — Recién creado
- `PAGADO` — Confirmado/pagado (post-confirmar)
- `CANCELADO` — Cancelado por usuario/admin
- `COMPLETADO` — Entregado al cliente

### Métodos de pago disponibles
- `tarjeta` — Pago con tarjeta
- `efectivo` — Pago en efectivo
- `recoger` — Pagar al recoger

### Estados de venta
- `CREADA` — Venta registrada
- `ANULADA` — Venta anulada/devuelta
- `FINALIZADA` — Venta completada

---

## 4. Permisos y autorización

- **Staff/Admin:** Ve todos los pedidos y puede confirmar cualquier pedido
- **Cliente regular:** Solo ve sus propios pedidos
- **Roles especiales:** SuperAdmin, Trabajador, Vendedor tienen acceso completo

---

## 5. Relación con imágenes

Las imágenes se gestionan en la app `productos`. Para mostrar imágenes en recibos/confirmaciones:

```bash
# Subir imagen de producto
curl -X POST -F "product=12" -F "image=@foto.jpg" \
  -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/productos/images/upload/
```

Ver: `productos/EJEMPLOS_IMAGENES.md` para detalles completos.

---

## 6. Ejemplos frontend (JavaScript)

```javascript
// Obtener reportes
async function getReportes(periodo = 'mes') {
  const response = await fetch(`/api/ventas/reportes/?periodo=${periodo}`, {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  return response.json();
}

// Crear pedido
async function crearPedido(pedidoData) {
  const response = await fetch('/api/ventas/pedidos/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(pedidoData)
  });
  return response.json();
}

// Confirmar pedido
async function confirmarPedido(idPedido, pagoInfo) {
  const response = await fetch(`/api/ventas/pedidos/${idPedido}/confirmar/`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ pago: pagoInfo })
  });
  return response.json();
}
```

---

**Nota final:** Todos los endpoints requieren autenticación. Obtén el token desde `/api/token/` primero.