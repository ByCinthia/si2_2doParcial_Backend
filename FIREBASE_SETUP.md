# 🔥 Configuración de Firebase para Notificaciones Push

## 📋 Requisitos Previos

- Cuenta de Firebase (https://console.firebase.google.com/)
- Proyecto de Firebase creado
- firebase-admin instalado en el backend (✅ ya instalado)

---

## 🚀 Pasos de Configuración

### 1️⃣ **Obtener Credenciales de Firebase**

1. Ve a la [Consola de Firebase](https://console.firebase.google.com/)
2. Selecciona tu proyecto (o crea uno nuevo)
3. Ve a **Configuración del Proyecto** (ícono de engranaje)
4. Pestaña **Cuentas de servicio**
5. Haz clic en **Generar nueva clave privada**
6. Se descargará un archivo JSON con las credenciales

### 2️⃣ **Guardar Credenciales en el Backend**

1. Renombra el archivo descargado a: `firebase-credentials.json`
2. Copia el archivo en la raíz del proyecto Django:
   ```
   backend/
   ├── firebase-credentials.json  ← Aquí
   ├── manage.py
   ├── requirements.txt
   └── ...
   ```

### 3️⃣ **Configurar .gitignore**

**⚠️ IMPORTANTE:** Nunca subas las credenciales a Git

Agrega al archivo `.gitignore`:

```
# Firebase credentials
firebase-credentials.json
```

---

## 📱 Configuración en el Cliente (Flutter/React Native)

### Para Flutter:

1. **Android:**

   - Descarga `google-services.json` desde Firebase Console
   - Colócalo en: `android/app/google-services.json`

2. **iOS:**

   - Descarga `GoogleService-Info.plist` desde Firebase Console
   - Colócalo en: `ios/Runner/GoogleService-Info.plist`

3. **Instalar paquete:**
   ```yaml
   dependencies:
     firebase_messaging: ^latest_version
   ```

### Para React Native:

1. Instalar Firebase:

   ```bash
   npm install @react-native-firebase/app
   npm install @react-native-firebase/messaging
   ```

2. Configurar archivos nativos (similar a Flutter)

---

## 🔑 Obtener FCM Token en el Cliente

### Flutter Example:

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

Future<String?> getFCMToken() async {
  final fcmToken = await FirebaseMessaging.instance.getToken();
  print("FCM Token: $fcmToken");
  return fcmToken;
}

// Enviar token al backend
Future<void> enviarTokenAlBackend(String fcmToken) async {
  await http.put(
    Uri.parse('http://tu-backend.com/api/usuarios/actualizar-fcm-token/'),
    headers: {'Authorization': 'Bearer $jwtToken'},
    body: json.encode({'fcmToken': fcmToken}),
  );
}
```

### React Native Example:

```javascript
import messaging from "@react-native-firebase/messaging";

async function getFCMToken() {
  const fcmToken = await messaging().getToken();
  console.log("FCM Token:", fcmToken);
  return fcmToken;
}

// Enviar token al backend
async function enviarTokenAlBackend(fcmToken) {
  await fetch("http://tu-backend.com/api/usuarios/actualizar-fcm-token/", {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${jwtToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ fcmToken }),
  });
}
```

---

## 📡 Endpoints Disponibles

### **1. Enviar Notificación (Admin)**

```http
POST /api/notificaciones/enviar/
Authorization: Bearer {token}
Content-Type: application/json

{
  "titulo": "Nueva promoción",
  "mensaje": "50% de descuento en todos los productos",
  "usuarios_ids": [1, 2, 3],  // Opcional, si no se envía va a todos
  "enviar_push": true          // Opcional, default: true
}
```

### **2. Ver Mis Notificaciones**

```http
GET /api/notificaciones/mis-notificaciones/
Authorization: Bearer {token}
```

### **3. Contar No Leídas**

```http
GET /api/notificaciones/no-leidas/
Authorization: Bearer {token}
```

### **4. Marcar como Leída**

```http
PUT /api/notificaciones/{id_user_noti}/marcar-leida/
Authorization: Bearer {token}
```

### **5. Marcar Todas como Leídas**

```http
PUT /api/notificaciones/marcar-todas-leidas/
Authorization: Bearer {token}
```

### **6. Eliminar Notificación**

```http
DELETE /api/notificaciones/{id_user_noti}/
Authorization: Bearer {token}
```

---

## 🧪 Testing

### Probar desde Python Shell:

```python
python manage.py shell

from notificaciones.services import NotificacionService

# Enviar notificación de prueba
NotificacionService.enviar_notificacion(
    titulo="Test",
    mensaje="Probando notificaciones push",
    usuarios_ids=[1],  # ID de usuario con fcmToken configurado
    enviar_push=True
)
```

### Probar desde Postman:

1. Obtener token JWT
2. Crear notificación con endpoint POST `/api/notificaciones/enviar/`
3. Verificar en la app móvil que llegue la notificación

---

## ⚠️ Troubleshooting

### Error: "Firebase app not initialized"

- Verifica que `firebase-credentials.json` esté en la raíz del proyecto
- Reinicia el servidor Django

### Error: "Invalid FCM token"

- El token del usuario expiró
- Pide al usuario regenerar el token en la app

### No llegan las notificaciones push

- Verifica que el usuario tenga `fcmToken` guardado en la BD
- Verifica que la app móvil tenga permisos de notificaciones
- Revisa los logs de Firebase Console

---

## 📚 Recursos Adicionales

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
- [Flutter Firebase Messaging](https://firebase.flutter.dev/docs/messaging/overview/)
