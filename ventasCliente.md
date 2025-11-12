# API Ventas - Cliente

## VENTAS

### 1A. Crear Compra AL CONTADO (1 cuota)

**POST** `/api/ventas/`

**Headers:**

```
Authorization: Bearer {token}
```

**Body:**

```json
{
  "metodoPago": 1,
  "nrocuotas": 1,
  "detalles": [
    {
      "producto": 1,
      "cantidad": 2
    }
  ]
}
```

**Response 200:**

```json
{
  "mensaje": "Pago al contado - Checkout creado",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "session_id": "cs_test_a1b2c3d4e5f6g7h8i9j0",
  "total": 168.0,
  "subtotal": 168.0,
  "interes": 0.0,
  "nrocuotas": 1,
  "nota": "Complete el pago para confirmar su compra"
}
```

**Flujo:**

1. Backend genera Stripe Checkout Session
2. Cliente abre `checkout_url` y paga con tarjeta
3. Stripe envia webhook confirmando el pago
4. Backend crea la venta y decrementa stock
5. Compra completada

---

### 1B. Crear Compra CON CUOTAS (3, 6 o 12 cuotas)

**POST** `/api/ventas/`

**Headers:**

```
Authorization: Bearer {token}
```

**Body:**

```json
{
  "metodoPago": 1,
  "nrocuotas": 3,
  "detalles": [
    {
      "producto": 1,
      "cantidad": 2
    },
    {
      "producto": 3,
      "cantidad": 1
    }
  ]
}
```

**Response 201:**

```json
{
  "mensaje": "Venta con cuotas creada exitosamente",
  "venta": {
    "idVenta": 1,
    "usuario": 2,
    "metodoPago": 1,
    "nombre_metodo_pago": "Tarjeta",
    "subtotal": "168.00",
    "interes": "0.19",
    "total": "175.98",
    "nrocuotas": 3,
    "fecha_venta": "2025-11-12T05:28:54Z",
    "fecha_modificacion": "2025-11-12T05:28:54Z",
    "detalles": [
      {
        "idDetalleVenta": 1,
        "producto": 1,
        "producto_detalle": {
          "idProducto": 1,
          "nombre": "Polera Roja M",
          "precio": "45.00",
          "stock": 28
        },
        "nombre_producto": "Polera Roja M",
        "cantidad": 2,
        "precio": "45.00",
        "subtotal": "90.00",
        "fecha_creacion": "2025-11-12T05:28:54Z"
      },
      {
        "idDetalleVenta": 2,
        "producto": 3,
        "producto_detalle": {
          "idProducto": 3,
          "nombre": "Camisa Azul",
          "precio": "78.00",
          "stock": 44
        },
        "nombre_producto": "Camisa Azul",
        "cantidad": 1,
        "precio": "78.00",
        "subtotal": "78.00",
        "fecha_creacion": "2025-11-12T05:28:54Z"
      }
    ],
    "cuotas": [
      {
        "idCuota": 1,
        "numero_cuota": 1,
        "monto": "58.66",
        "pagada": false,
        "fecha_vencimiento": "2025-12-12",
        "fecha_pago": null,
        "esta_vencida": false,
        "stripe_payment_intent_id": null,
        "stripe_checkout_session_id": null,
        "fecha_creacion": "2025-11-12T05:28:54Z"
      },
      {
        "idCuota": 2,
        "numero_cuota": 2,
        "monto": "58.66",
        "pagada": false,
        "fecha_vencimiento": "2026-01-12",
        "fecha_pago": null,
        "esta_vencida": false,
        "stripe_payment_intent_id": null,
        "stripe_checkout_session_id": null,
        "fecha_creacion": "2025-11-12T05:28:54Z"
      },
      {
        "idCuota": 3,
        "numero_cuota": 3,
        "monto": "58.66",
        "pagada": false,
        "fecha_vencimiento": "2026-02-12",
        "fecha_pago": null,
        "esta_vencida": false,
        "stripe_payment_intent_id": null,
        "stripe_checkout_session_id": null,
        "fecha_creacion": "2025-11-12T05:28:54Z"
      }
    ],
    "cantidad_productos": 2
  },
  "productos_comprados": 2,
  "cuotas_generadas": 3,
  "monto_por_cuota": 58.66,
  "nota": "Ahora puede pagar cada cuota individualmente usando los endpoints de pago"
}
```

**Flujo:**

1. Backend crea la venta inmediatamente
2. Backend genera las cuotas (todas con pagada=false)
3. Stock se decrementa inmediatamente
4. Cliente paga cada cuota individualmente usando:
   - POST /api/ventas/cuotas/{id}/generar-link-pago/ (Web)
   - POST /api/ventas/cuotas/{id}/crear-payment-intent/ (Flutter)

**Response 400 (Stock insuficiente):**

```json
{
  "error": "Stock insuficiente para Polera Roja M. Disponible: 5"
}
```

---

### 2. Listar Mis Ventas

**GET** `/api/ventas/mis-ventas/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
[
  {
    "idVenta": 1,
    "usuario": 2,
    "metodoPago": 1,
    "nombre_metodo_pago": "Tarjeta",
    "subtotal": "168.00",
    "interes": "0.00",
    "total": "168.00",
    "nrocuotas": 1,
    "stripe_payment_intent_id": null,
      "stripe_checkout_session_id": null,
      "fecha_venta": "2025-11-12T10:30:00Z",
      "fecha_modificacion": "2025-11-12T10:30:00Z",
      "detalles": [],
      "cuotas": [],
      "cantidad_productos": 2
    }
  ]
}
```

---

### 3. Detalle de Venta

**GET** `/api/ventas/{id}/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
{
  "idVenta": 1,
  "usuario": 2,
  "metodoPago": 1,
  "nombre_metodo_pago": "Tarjeta",
  "subtotal": "168.00",
  "interes": "0.19",
  "total": "175.98",
  "nrocuotas": 3,
  "stripe_payment_intent_id": null,
  "stripe_checkout_session_id": null,
  "fecha_venta": "2025-11-12T10:30:00Z",
  "fecha_modificacion": "2025-11-12T10:30:00Z",
  "detalles": [
    {
      "idDetalleVenta": 1,
      "producto": 1,
      "producto_detalle": {
        "idProducto": 1,
        "nombre": "Polera Roja M",
        "precio": "45.00",
        "stock": 28
      },
      "nombre_producto": "Polera Roja M",
      "cantidad": 2,
      "precio": "45.00",
      "subtotal": "90.00",
      "fecha_creacion": "2025-11-12T10:30:00Z"
    },
    {
      "idDetalleVenta": 2,
      "producto": 3,
      "producto_detalle": {
        "idProducto": 3,
        "nombre": "Camisa Azul",
        "precio": "78.00",
        "stock": 44
      },
      "nombre_producto": "Camisa Azul",
      "cantidad": 1,
      "precio": "78.00",
      "subtotal": "78.00",
      "fecha_creacion": "2025-11-12T10:30:00Z"
    }
  ],
  "cuotas": [
    {
      "idCuota": 1,
      "numero_cuota": 1,
      "monto": "58.66",
      "pagada": false,
      "fecha_vencimiento": "2025-12-12",
      "fecha_pago": null,
      "esta_vencida": false,
      "stripe_payment_intent_id": null,
      "stripe_checkout_session_id": null,
      "fecha_creacion": "2025-11-12T10:30:00Z"
    },
    {
      "idCuota": 2,
      "numero_cuota": 2,
      "monto": "58.66",
      "pagada": false,
      "fecha_vencimiento": "2026-01-12",
      "fecha_pago": null,
      "esta_vencida": false,
      "stripe_payment_intent_id": null,
      "stripe_checkout_session_id": null,
      "fecha_creacion": "2025-11-12T10:30:00Z"
    },
    {
      "idCuota": 3,
      "numero_cuota": 3,
      "monto": "58.66",
      "pagada": false,
      "fecha_vencimiento": "2026-02-12",
      "fecha_pago": null,
      "esta_vencida": false,
      "stripe_payment_intent_id": null,
      "stripe_checkout_session_id": null,
      "fecha_creacion": "2025-11-12T10:30:00Z"
    }
  ],
  "cantidad_productos": 2
}
```

---

### 4. Listar Cuotas de Venta

**GET** `/api/ventas/{id_venta}/cuotas/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
[
  {
    "idCuota": 1,
    "numero_cuota": 1,
    "monto": "58.66",
    "pagada": false,
    "fecha_vencimiento": "2025-12-12",
    "fecha_pago": null,
    "esta_vencida": false,
    "stripe_payment_intent_id": null,
    "stripe_checkout_session_id": null,
    "fecha_creacion": "2025-11-12T10:30:00Z"
  },
  {
    "idCuota": 2,
    "numero_cuota": 2,
    "monto": "58.66",
    "pagada": false,
    "fecha_vencimiento": "2026-01-12",
    "fecha_pago": null,
    "esta_vencida": false,
    "stripe_payment_intent_id": null,
    "stripe_checkout_session_id": null,
    "fecha_creacion": "2025-11-12T10:30:00Z"
  }
]
```

---

## CUOTAS

### 5. Listar Mis Cuotas

**GET** `/api/ventas/mis-cuotas/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
[
  {
    "idCuota": 1,
    "numero_cuota": 1,
    "monto": "58.66",
    "pagada": false,
    "fecha_vencimiento": "2025-12-12",
    "fecha_pago": null,
    "esta_vencida": false,
    "stripe_payment_intent_id": null,
    "stripe_checkout_session_id": null,
    "fecha_creacion": "2025-11-12T10:30:00Z"
  }
]
```

---

### 6. Listar Mis Cuotas Pendientes

**GET** `/api/ventas/mis-cuotas/pendientes/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
[
  {
    "idCuota": 1,
    "numero_cuota": 1,
    "monto": "58.66",
    "pagada": false,
    "fecha_vencimiento": "2025-12-12",
    "fecha_pago": null,
    "esta_vencida": false,
    "stripe_payment_intent_id": null,
    "stripe_checkout_session_id": null,
    "fecha_creacion": "2025-11-12T10:30:00Z"
  }
]
```

---

### 7. Detalle de Cuota

**GET** `/api/ventas/cuotas/{id}/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
{
  "idCuota": 1,
  "numero_cuota": 1,
  "monto": "58.66",
  "pagada": false,
  "fecha_vencimiento": "2025-12-12",
  "fecha_pago": null,
  "esta_vencida": false,
  "stripe_payment_intent_id": null,
  "stripe_checkout_session_id": null,
  "fecha_creacion": "2025-11-12T10:30:00Z"
}
```

---

## PAGOS STRIPE

### 8. Generar Link de Pago (Web)

**POST** `/api/ventas/cuotas/{id}/generar-link-pago/`

**Headers:**

```
Authorization: Bearer {token}
```

**Response 200:**

```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "session_id": "cs_test_a1b2c3d4e5f6g7h8i9j0",
  "cuota_id": 1,
  "monto": 58.66
}
```

**Response 400 (Cuota ya pagada):**

```json
{
  "error": "Cuota ya pagada"
}
```

**Response 403 (No autorizado):**

```json
{
  "error": "No autorizado"
}
```

**Response 404:**

```json
{
  "error": "Cuota no encontrada"
}
```

---

## Notas Tecnicas

### Tasas de Interes

- 1 cuota: 0% (pago al contado)
- 3 cuotas: 19% anual
- 6 cuotas: 15% anual
- 12 cuotas: 12% anual

### Calculo de Cuotas

- El interes se distribuye equitativamente entre todas las cuotas
- Las cuotas vencen mensualmente desde la fecha de la venta
- Primera cuota vence 30 dias despues de la venta

### Stock

**Pago al contado (1 cuota):**

- Al crear compra se valida stock pero NO se decrementa
- Stock se decrementa SOLO cuando Stripe confirma el pago via webhook
- Si pago falla o se cancela, stock NO se afecta

**Pago con cuotas (3, 6 o 12):**

- Al crear venta se valida stock Y se decrementa inmediatamente
- La venta queda registrada aunque las cuotas no esten pagadas
- Si no hay stock suficiente, se rechaza con error 400

### Flujo de Compra AL CONTADO (1 cuota)

1. POST /api/ventas/ con nrocuotas=1
2. Backend valida stock y genera Stripe Checkout
3. Backend retorna checkout_url
4. Cliente paga en Stripe
5. Webhook confirma pago
6. Backend crea venta y decrementa stock
7. Compra completada

### Flujo de Compra CON CUOTAS (3, 6 o 12)

1. POST /api/ventas/ con nrocuotas=3/6/12
2. Backend valida stock y crea venta inmediatamente
3. Backend decrementa stock
4. Backend genera cuotas (todas pendientes de pago)
5. Cliente paga cada cuota individualmente:
   - GET /api/ventas/mis-cuotas/pendientes/
   - POST /api/ventas/cuotas/{id}/generar-link-pago/
   - Cliente paga en Stripe
   - Webhook marca cuota como pagada

### Pagos con Stripe

- **Pago al contado:** Stripe Checkout generado automaticamente
- **Cuotas individuales:** Usar `generar-link-pago` o `crear-payment-intent`
- Los pagos se confirman automaticamente via webhook
- Al confirmar pago de cuota, se marca como pagada y se actualiza fecha_pago
