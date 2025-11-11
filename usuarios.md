# 👥 API de Usuarios - Documentación de Endpoints

## 📋 Índice

- [Gestión de Usuarios](#gestión-de-usuarios)
  - [Listar Usuarios](#1-listar-usuarios)
  - [Crear Usuario](#2-crear-usuario)
  - [Obtener Usuario](#3-obtener-usuario)
  - [Actualizar Usuario Completo](#4-actualizar-usuario-completo)
  - [Actualizar Usuario Parcial](#5-actualizar-usuario-parcial)
  - [Desactivar Usuario](#6-desactivar-usuario)
  - [Eliminar Usuario Permanente](#7-eliminar-usuario-permanente)
  - [Cambiar Contraseña](#8-cambiar-contraseña)
  - [Buscar Usuarios](#9-buscar-usuarios)

---

## Gestión de Usuarios

### 1️⃣ Listar Usuarios

**Endpoint:** `GET /api/usuarios/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
GET http://localhost:8000/api/usuarios/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
[
  {
    "idUsuario": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "12345678",
    "direccion": "Av. Principal 123",
    "ci": "1234567",
    "fcmToken": "eXXXXXXXXXXXXXXXXXXXXXXXX",
    "activo": true,
    "rol": 2,
    "rol_detalle": {
      "idRol": 2,
      "nombre": "Cliente",
      "descripcion": "Usuario cliente"
    },
    "nombre_rol": "Cliente",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_modificacion": "2025-01-15T10:30:00Z"
  },
  {
    "idUsuario": 2,
    "nombre": "María López",
    "email": "maria@example.com",
    "telefono": "87654321",
    "direccion": "Calle Secundaria 456",
    "ci": "7654321",
    "fcmToken": null,
    "activo": true,
    "rol": 1,
    "rol_detalle": {
      "idRol": 1,
      "nombre": "Administrador",
      "descripcion": "Usuario administrador"
    },
    "nombre_rol": "Administrador",
    "fecha_creacion": "2025-01-10T08:20:00Z",
    "fecha_modificacion": "2025-01-10T08:20:00Z"
  }
]
```

---

### 2️⃣ Crear Usuario

**Endpoint:** `POST /api/usuarios/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido

**Request:**

```http
POST http://localhost:8000/api/usuarios/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body:**

```json
{
  "nombre": "Pedro García",
  "email": "pedro@example.com",
  "password": "password123",
  "telefono": "11112222",
  "direccion": "Zona Norte 789",
  "ci": "9876543",
  "rol": 2
}
```

**Campos:**

- `nombre` (string, requerido): Nombre completo del usuario
- `email` (string, requerido): Email único
- `password` (string, requerido): Contraseña (se hashea automáticamente)
- `telefono` (string, opcional): Teléfono del usuario
- `direccion` (string, opcional): Dirección física
- `ci` (string, opcional): Cédula de identidad
- `rol` (integer, requerido): ID del rol (1=Admin, 2=Cliente, etc.)
- `fcmToken` (string, opcional): Token de Firebase para notificaciones push

**Respuesta (201 Created):**

```json
{
  "idUsuario": 3,
  "nombre": "Pedro García",
  "email": "pedro@example.com",
  "telefono": "11112222",
  "direccion": "Zona Norte 789",
  "ci": "9876543",
  "fcmToken": null,
  "activo": true,
  "rol": 2,
  "rol_detalle": {
    "idRol": 2,
    "nombre": "Cliente",
    "descripcion": "Usuario cliente"
  },
  "nombre_rol": "Cliente",
  "fecha_creacion": "2025-11-11T14:25:00Z",
  "fecha_modificacion": "2025-11-11T14:25:00Z"
}
```

**Respuesta Error (400 Bad Request):**

```json
{
  "email": ["Ya existe un usuario con este email."],
  "password": ["Este campo es requerido."]
}
```

---

### 3️⃣ Obtener Usuario

**Endpoint:** `GET /api/usuarios/{id}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
GET http://localhost:8000/api/usuarios/1/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
{
  "idUsuario": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "12345678",
  "direccion": "Av. Principal 123",
  "ci": "1234567",
  "fcmToken": "eXXXXXXXXXXXXXXXXXXXXXXXX",
  "activo": true,
  "rol": 2,
  "rol_detalle": {
    "idRol": 2,
    "nombre": "Cliente",
    "descripcion": "Usuario cliente"
  },
  "nombre_rol": "Cliente",
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_modificacion": "2025-01-15T10:30:00Z"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Usuario no encontrado"
}
```

---

### 4️⃣ Actualizar Usuario Completo

**Endpoint:** `PUT /api/usuarios/{id}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido (todos los campos excepto password y fcmToken)

**Request:**

```http
PUT http://localhost:8000/api/usuarios/1/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body:**

```json
{
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.nuevo@example.com",
  "telefono": "99998888",
  "direccion": "Nueva Dirección 999",
  "ci": "1234567",
  "rol": 2
}
```

**Nota:** PUT requiere todos los campos (nombre, email, telefono, direccion, ci, rol). Si quieres actualizar solo algunos campos, usa PATCH.

**Respuesta (200 OK):**

```json
{
  "idUsuario": 1,
  "nombre": "Juan Pérez Actualizado",
  "email": "juan.nuevo@example.com",
  "telefono": "99998888",
  "direccion": "Nueva Dirección 999",
  "ci": "1234567",
  "fcmToken": "eXXXXXXXXXXXXXXXXXXXXXXXX",
  "activo": true,
  "rol": 2,
  "rol_detalle": {
    "idRol": 2,
    "nombre": "Cliente",
    "descripcion": "Usuario cliente"
  },
  "nombre_rol": "Cliente",
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_modificacion": "2025-11-11T14:30:00Z"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Usuario no encontrado"
}
```

---

### 5️⃣ Actualizar Usuario Parcial

**Endpoint:** `PATCH /api/usuarios/{id}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido (solo los campos que quieres actualizar)

**Request:**

```http
PATCH http://localhost:8000/api/usuarios/1/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body Ejemplo 1 (actualizar teléfono y dirección):**

```json
{
  "telefono": "77776666",
  "direccion": "Nueva Dirección Parcial"
}
```

**Body Ejemplo 2 (actualizar solo nombre):**

```json
{
  "nombre": "Juan Carlos Pérez"
}
```

**Body Ejemplo 3 (actualizar email):**

```json
{
  "email": "nuevo.email@example.com"
}
```

**Respuesta (200 OK):**

```json
{
  "idUsuario": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "77776666",
  "direccion": "Nueva Dirección Parcial",
  "ci": "1234567",
  "fcmToken": "eXXXXXXXXXXXXXXXXXXXXXXXX",
  "activo": true,
  "rol": 2,
  "rol_detalle": {
    "idRol": 2,
    "nombre": "Cliente",
    "descripcion": "Usuario cliente"
  },
  "nombre_rol": "Cliente",
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_modificacion": "2025-11-11T14:35:00Z"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Usuario no encontrado"
}
```

---

### 6️⃣ Desactivar Usuario (Soft Delete)

**Endpoint:** `DELETE /api/usuarios/{id}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
DELETE http://localhost:8000/api/usuarios/1/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
{
  "mensaje": "Usuario desactivado correctamente"
}
```

**Nota:** ⚠️ Este endpoint NO elimina el usuario de la base de datos, solo marca `activo = false`. El usuario sigue existiendo pero no puede hacer login ni aparecer en listados (si se filtra por activo).

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Usuario no encontrado"
}
```

---

### 7️⃣ Eliminar Usuario Permanente

**Endpoint:** `DELETE /api/usuarios/{id}/permanente/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
DELETE http://localhost:8000/api/usuarios/1/permanente/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
{
  "mensaje": "Usuario eliminado permanentemente"
}
```

**Nota:** ⚠️⚠️⚠️ **¡PELIGRO!** Este endpoint **SÍ elimina permanentemente** el usuario de la base de datos. No se puede recuperar. Usar con extrema precaución.

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Usuario no encontrado"
}
```

---

### 8️⃣ Cambiar Contraseña

**Endpoint:** `POST /api/usuarios/cambiar-password/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido

**Request:**

```http
POST http://localhost:8000/api/usuarios/cambiar-password/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body:**

```json
{
  "password_actual": "password123",
  "password_nueva": "nuevaPassword456"
}
```

**Campos:**

- `password_actual` (string, requerido): Contraseña actual del usuario autenticado
- `password_nueva` (string, requerido): Nueva contraseña (mínimo 6 caracteres recomendado)

**Respuesta (200 OK):**

```json
{
  "mensaje": "Contraseña actualizada correctamente"
}
```

**Respuesta Error (400 Bad Request):**

```json
{
  "error": "La contraseña actual es incorrecta"
}
```

**Respuesta Error (401 Unauthorized):**

```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

**Nota:** Este endpoint cambia la contraseña del usuario autenticado (el que envía el token JWT). No se puede cambiar la contraseña de otro usuario.

---

### 9️⃣ Buscar Usuarios

**Endpoint:** `GET /api/usuarios/buscar/?q={query}`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Query Params:**

- `q` (string, requerido): Término de búsqueda

**Request:**

```http
GET http://localhost:8000/api/usuarios/buscar/?q=juan
Authorization: Bearer {tu_token_jwt}
```

**Ejemplos de búsqueda:**

```http
# Buscar por nombre
GET /api/usuarios/buscar/?q=juan

# Buscar por email
GET /api/usuarios/buscar/?q=@example.com

# Buscar por teléfono
GET /api/usuarios/buscar/?q=1234

# Buscar por CI
GET /api/usuarios/buscar/?q=7654321
```

**Respuesta (200 OK):**

```json
[
  {
    "idUsuario": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "telefono": "12345678",
    "direccion": "Av. Principal 123",
    "ci": "1234567",
    "fcmToken": "eXXXXXXXXXXXXXXXXXXXXXXXX",
    "activo": true,
    "rol": 2,
    "rol_detalle": {
      "idRol": 2,
      "nombre": "Cliente",
      "descripcion": "Usuario cliente"
    },
    "nombre_rol": "Cliente",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_modificacion": "2025-01-15T10:30:00Z"
  }
]
```

**Respuesta Error (400 Bad Request):**

```json
{
  "error": "Parámetro 'q' requerido"
}
```

**Respuesta (sin resultados):**

```json
[]
```

**Nota:** La búsqueda es case-insensitive y busca coincidencias parciales en los campos: nombre, email, teléfono y CI.

---

## 📊 Tabla Resumen de Endpoints

| Endpoint                          | Método | Body             | Autenticación | Descripción                     |
| --------------------------------- | ------ | ---------------- | ------------- | ------------------------------- |
| `/api/usuarios/`                  | GET    | ❌ No            | ✅ Sí         | Lista todos los usuarios        |
| `/api/usuarios/`                  | POST   | ✅ Sí            | ✅ Sí         | Crea un nuevo usuario           |
| `/api/usuarios/{id}/`             | GET    | ❌ No            | ✅ Sí         | Obtiene un usuario por ID       |
| `/api/usuarios/{id}/`             | PUT    | ✅ Sí (completo) | ✅ Sí         | Actualiza todos los campos      |
| `/api/usuarios/{id}/`             | PATCH  | ✅ Sí (parcial)  | ✅ Sí         | Actualiza campos específicos    |
| `/api/usuarios/{id}/`             | DELETE | ❌ No            | ✅ Sí         | Desactiva usuario (soft delete) |
| `/api/usuarios/{id}/permanente/`  | DELETE | ❌ No            | ✅ Sí         | Elimina permanentemente         |
| `/api/usuarios/cambiar-password/` | POST   | ✅ Sí            | ✅ Sí         | Cambia contraseña               |
| `/api/usuarios/buscar/?q=`        | GET    | ❌ No            | ✅ Sí         | Busca usuarios                  |

---

## 🧪 Ejemplos con cURL

### Listar Usuarios

```bash
curl -X GET "http://localhost:8000/api/usuarios/" \
  -H "Authorization: Bearer {tu_token_jwt}"
```

### Crear Usuario

```bash
curl -X POST "http://localhost:8000/api/usuarios/" \
  -H "Authorization: Bearer {tu_token_jwt}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pedro García",
    "email": "pedro@example.com",
    "password": "password123",
    "telefono": "11112222",
    "direccion": "Zona Norte 789",
    "ci": "9876543",
    "rol": 2
  }'
```

### Actualizar Parcial (PATCH)

```bash
curl -X PATCH "http://localhost:8000/api/usuarios/1/" \
  -H "Authorization: Bearer {tu_token_jwt}" \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "77776666"
  }'
```

### Cambiar Contraseña

```bash
curl -X POST "http://localhost:8000/api/usuarios/cambiar-password/" \
  -H "Authorization: Bearer {tu_token_jwt}" \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "password123",
    "password_nueva": "nuevaPassword456"
  }'
```

### Buscar Usuarios

```bash
curl -X GET "http://localhost:8000/api/usuarios/buscar/?q=juan" \
  -H "Authorization: Bearer {tu_token_jwt}"
```

---

## 🔐 Notas de Seguridad

1. **Autenticación Requerida:** Todos estos endpoints requieren un token JWT válido en el header `Authorization: Bearer {token}`

2. **Contraseñas:** Las contraseñas se hashean automáticamente con `make_password()` antes de guardar en la base de datos

3. **Soft Delete vs Hard Delete:**

   - `DELETE /api/usuarios/{id}/` → Soft delete (solo marca `activo = false`)
   - `DELETE /api/usuarios/{id}/permanente/` → Hard delete (elimina el registro)

4. **Cambio de Contraseña:** Solo el usuario autenticado puede cambiar su propia contraseña

5. **Email Único:** No se pueden crear dos usuarios con el mismo email

---

## 🚀 Ejemplos con JavaScript/Fetch

### Crear Usuario

```javascript
const response = await fetch("http://localhost:8000/api/usuarios/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    nombre: "Pedro García",
    email: "pedro@example.com",
    password: "password123",
    telefono: "11112222",
    direccion: "Zona Norte 789",
    ci: "9876543",
    rol: 2,
  }),
});

const data = await response.json();
console.log(data);
```

### Actualizar Parcial con Axios

```javascript
const response = await axios.patch(
  "http://localhost:8000/api/usuarios/1/",
  {
    telefono: "77776666",
  },
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

console.log(response.data);
```

### Buscar Usuarios

```javascript
const query = "juan";
const response = await fetch(
  `http://localhost:8000/api/usuarios/buscar/?q=${encodeURIComponent(query)}`,
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

const usuarios = await response.json();
console.log(usuarios);
```
