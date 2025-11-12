# Configuración del Webhook de Stripe

## 🎯 Objetivo

El webhook permite que Stripe notifique automáticamente a tu backend cuando un pago se completa exitosamente, ya sea desde Flutter (Payment Intent) o desde Web (Hosted Checkout).

---

## 🔧 Configuración en Stripe Dashboard

### **1. Acceder al Dashboard de Stripe**

- Ir a: https://dashboard.stripe.com/webhooks
- Iniciar sesión con tu cuenta

### **2. Agregar Endpoint**

1. Click en **"Add endpoint"** o **"Agregar punto de conexión"**
2. En **"Endpoint URL"** ingresar:

   ```
   https://tudominio.com/api/ventas/webhook/stripe/
   ```

   **Ejemplos:**

   - Desarrollo local (ngrok): `https://abc123.ngrok.io/api/ventas/webhook/stripe/`
   - Producción: `https://tuapp.onrender.com/api/ventas/webhook/stripe/`

### **3. Seleccionar Eventos**

Marcar los siguientes eventos:

✅ **payment_intent.succeeded** (Para pagos desde Flutter)
✅ **checkout.session.completed** (Para pagos desde Web)
✅ **payment_intent.payment_failed** (Opcional: para detectar pagos fallidos)

### **4. Guardar Endpoint**

1. Click en **"Add endpoint"**
2. Copiar el **"Signing secret"** que aparece (empieza con `whsec_...`)

### **5. Actualizar .env**

Agregar el signing secret a tu archivo `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

---

## 🧪 Probar el Webhook (Desarrollo Local)

### **Opción 1: Usar Stripe CLI (Recomendado)**

1. **Instalar Stripe CLI:**

   - Windows: `scoop install stripe`
   - Mac: `brew install stripe/stripe-cli/stripe`
   - Linux: [Descargar](https://github.com/stripe/stripe-cli/releases/latest)

2. **Login en Stripe CLI:**

   ```bash
   stripe login
   ```

3. **Reenviar eventos a tu local:**

   ```bash
   stripe listen --forward-to localhost:8000/api/ventas/webhook/stripe/
   ```

4. **Copiar el webhook secret que aparece** y agregarlo a `.env`:

   ```env
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
   ```

5. **En otra terminal, ejecutar tu servidor Django:**

   ```bash
   python manage.py runserver
   ```

6. **Simular un pago exitoso:**
   ```bash
   stripe trigger payment_intent.succeeded
   ```

### **Opción 2: Usar ngrok**

1. **Instalar ngrok:**

   - Descargar desde: https://ngrok.com/download

2. **Exponer tu servidor local:**

   ```bash
   ngrok http 8000
   ```

3. **Copiar la URL HTTPS** que proporciona ngrok (ej: `https://abc123.ngrok.io`)

4. **Configurar en Stripe Dashboard:**
   - URL: `https://abc123.ngrok.io/api/ventas/webhook/stripe/`

---

## 📊 Flujo de Funcionamiento

### **Pago desde Flutter (Payment Intent):**

```
1. Usuario paga en Flutter con flutter_stripe
2. Stripe procesa el pago
3. Stripe envía evento: payment_intent.succeeded
4. Tu webhook recibe el evento
5. Marca la cuota como pagada automáticamente
```

### **Pago desde Web (Hosted Checkout):**

```
1. Usuario hace click en link de pago
2. Paga en página de Stripe
3. Stripe envía evento: checkout.session.completed
4. Tu webhook recibe el evento
5. Marca la cuota como pagada automáticamente
```

---

## 🔍 Verificar que Funciona

### **1. Ver logs en tiempo real:**

```bash
# En terminal donde corre Django, verás:
✅ Cuota 123 pagada exitosamente (Payment Intent)
# o
✅ Cuota 123 pagada exitosamente (Checkout Session)
```

### **2. Verificar en Stripe Dashboard:**

- Ir a: https://dashboard.stripe.com/webhooks
- Click en tu endpoint
- Ver la sección **"Recent deliveries"**
- Debe aparecer status **200** (exitoso)

### **3. Verificar en tu base de datos:**

```python
from ventas.models import Cuota
cuota = Cuota.objects.get(idCuota=123)
print(cuota.pagada)  # Debe ser True
print(cuota.fecha_pago)  # Debe tener fecha
```

---

## ⚠️ Problemas Comunes

### **Error 400 - Invalid signature**

- **Causa:** El `STRIPE_WEBHOOK_SECRET` no coincide
- **Solución:** Copiar el signing secret correcto desde Stripe Dashboard

### **Error 404 - Not Found**

- **Causa:** La URL del webhook es incorrecta
- **Solución:** Verificar que la URL sea exactamente: `/api/ventas/webhook/stripe/`

### **No se marca la cuota como pagada**

- **Causa:** El metadata no se envió correctamente
- **Solución:** Verificar que en `crear_payment_intent_cuota()` y `generar_link_pago_cuota()` se esté enviando `cuota_id` en metadata

---

## 🔒 Seguridad

### **El webhook verifica:**

1. ✅ Firma de Stripe (previene requests falsas)
2. ✅ Metadata con `cuota_id` (identifica qué cuota pagar)
3. ✅ Estado de la cuota (evita pagos duplicados)

### **No requiere autenticación JWT:**

- El webhook usa `@csrf_exempt` porque Stripe envía las requests
- La seguridad está garantizada por la firma (`STRIPE_WEBHOOK_SECRET`)

---

## 📝 Testing Manual

### **Test 1: Payment Intent (Flutter)**

```bash
curl -X POST http://localhost:8000/api/ventas/cuotas/1/crear-payment-intent/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json"
```

Luego simular el pago con Stripe CLI:

```bash
stripe trigger payment_intent.succeeded
```

### **Test 2: Checkout Session (Web)**

```bash
curl -X POST http://localhost:8000/api/ventas/cuotas/1/generar-link-pago/ \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json"
```

Abrir el link generado y completar el pago de prueba con:

- Tarjeta: `4242 4242 4242 4242`
- Fecha: Cualquier fecha futura
- CVC: Cualquier 3 dígitos

---

## 🚀 Producción

1. **Cambiar a claves de producción en `.env`:**

   ```env
   STRIPE_PUBLIC_KEY=pk_live_xxxxx
   STRIPE_SECRET_KEY=sk_live_xxxxx
   ```

2. **Configurar webhook en modo live:**

   - Ir a: https://dashboard.stripe.com/webhooks
   - Cambiar a modo **"Live"** (no "Test")
   - Agregar endpoint de producción

3. **Actualizar FRONTEND_URL en `.env`:**
   ```env
   FRONTEND_URL=https://tuapp.com
   ```

---

## 📚 Eventos Adicionales (Opcional)

Si quieres manejar más casos, puedes agregar:

```python
# En stripe_webhook()

elif event_type == 'payment_intent.processing':
    # Pago en proceso
    pass

elif event_type == 'payment_intent.canceled':
    # Pago cancelado
    pass

elif event_type == 'charge.refunded':
    # Reembolso
    pass
```

---

## ✅ Checklist Final

- [ ] Webhook configurado en Stripe Dashboard
- [ ] `STRIPE_WEBHOOK_SECRET` agregado a `.env`
- [ ] Probado con Stripe CLI o ngrok
- [ ] Verificado que las cuotas se marcan como pagadas
- [ ] Logs funcionando correctamente
- [ ] Listo para producción

---

**¡Tu webhook está listo para recibir pagos automáticamente desde Flutter y Web!** 🎉
