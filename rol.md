# 🎭 API de Roles - Documentación de Endpoints

## 📋 Índice

- [Listar Roles](#1-listar-roles)
- [Crear Rol](#2-crear-rol)
- [Obtener Rol](#3-obtener-rol)
- [Actualizar Rol Completo](#4-actualizar-rol-completo)
- [Actualizar Rol Parcial](#5-actualizar-rol-parcial)
- [Eliminar Rol](#6-eliminar-rol)
- [Buscar Rol por Nombre](#7-buscar-rol-por-nombre)

---

## Estructura del Modelo Rol

```python
{
  "idRol": 1,
  "nombre": "Administrador",
  "descripcion": "Usuario con permisos completos"
}
```

**Campos:**

- `idRol` (integer, auto): ID único del rol (generado automáticamente)
- `nombre` (string, requerido, único): Nombre del rol (máx 100 caracteres)
- `descripcion` (string, opcional): Descripción del rol (máx 255 caracteres)

---

## 1️⃣ Listar Roles

**Endpoint:** `GET /api/usuarios/roles/`

**Autenticación:** ❌ No requerida (AllowAny)

**Body:** ❌ No requiere

**Request:**

```http
GET http://localhost:8000/api/usuarios/roles/
```

**Respuesta (200 OK):**

```json
[
  {
    "idRol": 1,
    "nombre": "Administrador",
    "descripcion": "Usuario con permisos completos"
  },
  {
    "idRol": 2,
    "nombre": "Cliente",
    "descripcion": "Usuario cliente del sistema"
  },
  {
    "idRol": 3,
    "nombre": "Vendedor",
    "descripcion": "Personal de ventas"
  }
]
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al listar roles: [mensaje de error]"
}
```

**Notas:**

- Este endpoint NO requiere autenticación
- Retorna todos los roles ordenados por nombre
- Si no hay roles, retorna un array vacío `[]`

---

## 2️⃣ Crear Rol

**Endpoint:** `POST /api/usuarios/roles/`

**Autenticación:** ❌ No requerida (AllowAny)

**Body:** ✅ Requerido

**Request:**

```http
POST http://localhost:8000/api/usuarios/roles/
Content-Type: application/json
```

**Body:**

```json
{
  "nombre": "Gerente",
  "descripcion": "Usuario gerente con permisos administrativos"
}
```

**Campos:**

- `nombre` (string, requerido): Nombre único del rol (máx 100 caracteres)
- `descripcion` (string, opcional): Descripción del rol (máx 255 caracteres)

**Body Mínimo (solo con campos requeridos):**

```json
{
  "nombre": "Supervisor"
}
```

**Respuesta (201 Created):**

```json
{
  "idRol": 4,
  "nombre": "Gerente",
  "descripcion": "Usuario gerente con permisos administrativos"
}
```

**Respuesta Error (400 Bad Request) - Nombre duplicado:**

```json
{
  "error": "Ya existe un rol con ese nombre"
}
```

**Respuesta Error (400 Bad Request) - Validación:**

```json
{
  "nombre": ["Este campo es requerido."]
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al crear rol: [mensaje de error]"
}
```

**Notas:**

- El nombre del rol debe ser único en el sistema
- La descripción es opcional
- El `idRol` se genera automáticamente

---

## 3️⃣ Obtener Rol

**Endpoint:** `GET /api/usuarios/roles/{id_rol}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
GET http://localhost:8000/api/usuarios/roles/1/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
{
  "idRol": 1,
  "nombre": "Administrador",
  "descripcion": "Usuario con permisos completos"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Rol no encontrado"
}
```

**Respuesta Error (401 Unauthorized):**

```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al obtener rol: [mensaje de error]"
}
```

**Notas:**

- Requiere token JWT válido
- El ID del rol debe existir en la base de datos

---

## 4️⃣ Actualizar Rol Completo (PUT)

**Endpoint:** `PUT /api/usuarios/roles/{id_rol}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido

**Request:**

```http
PUT http://localhost:8000/api/usuarios/roles/1/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body:**

```json
{
  "nombre": "Administrador General",
  "descripcion": "Usuario administrador con acceso total al sistema"
}
```

**Campos:**

- `nombre` (string, requerido): Nuevo nombre del rol (máx 100 caracteres)
- `descripcion` (string, opcional): Nueva descripción del rol (máx 255 caracteres)

**Respuesta (200 OK):**

```json
{
  "idRol": 1,
  "nombre": "Administrador General",
  "descripcion": "Usuario administrador con acceso total al sistema"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Rol no encontrado"
}
```

**Respuesta Error (400 Bad Request) - Nombre duplicado:**

```json
{
  "error": "Ya existe un rol con ese nombre"
}
```

**Respuesta Error (400 Bad Request) - Validación:**

```json
{
  "nombre": ["Este campo es requerido."]
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al actualizar rol: [mensaje de error]"
}
```

**Notas:**

- PUT requiere enviar todos los campos (nombre y opcionalmente descripcion)
- El nombre actualizado debe ser único
- No se puede cambiar el `idRol`

---

## 5️⃣ Actualizar Rol Parcial (PATCH)

**Endpoint:** `PATCH /api/usuarios/roles/{id_rol}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ✅ Requerido (solo campos a actualizar)

**Request:**

```http
PATCH http://localhost:8000/api/usuarios/roles/1/
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
```

**Body Ejemplo 1 (actualizar solo nombre):**

```json
{
  "nombre": "Super Admin"
}
```

**Body Ejemplo 2 (actualizar solo descripción):**

```json
{
  "descripcion": "Descripción actualizada del rol"
}
```

**Body Ejemplo 3 (actualizar ambos campos):**

```json
{
  "nombre": "Admin Principal",
  "descripcion": "Administrador principal del sistema"
}
```

**Respuesta (200 OK):**

```json
{
  "idRol": 1,
  "nombre": "Super Admin",
  "descripcion": "Usuario con permisos completos"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Rol no encontrado"
}
```

**Respuesta Error (400 Bad Request) - Nombre duplicado:**

```json
{
  "error": "Ya existe un rol con ese nombre"
}
```

**Respuesta Error (400 Bad Request) - Validación:**

```json
{
  "nombre": ["Este campo no puede estar en blanco."]
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al actualizar rol: [mensaje de error]"
}
```

**Notas:**

- PATCH permite actualizar solo los campos que envíes
- El nombre (si se envía) debe ser único
- Más flexible que PUT

---

## 6️⃣ Eliminar Rol

**Endpoint:** `DELETE /api/usuarios/roles/{id_rol}/`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Request:**

```http
DELETE http://localhost:8000/api/usuarios/roles/3/
Authorization: Bearer {tu_token_jwt}
```

**Respuesta (200 OK):**

```json
{
  "mensaje": "Rol eliminado exitosamente"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Rol no encontrado"
}
```

**Respuesta Error (400 Bad Request) - Tiene usuarios asociados:**

```json
{
  "error": "No se puede eliminar el rol porque tiene usuarios asociados"
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al eliminar rol: [mensaje de error]"
}
```

**Notas:**

- ⚠️ Este es un **hard delete** (eliminación permanente)
- **NO se puede eliminar un rol si tiene usuarios asociados**
- Primero debes reasignar o eliminar los usuarios con ese rol
- La eliminación es irreversible

---

## 7️⃣ Buscar Rol por Nombre

**Endpoint:** `GET /api/usuarios/roles/buscar/?nombre={nombre}`

**Autenticación:** ✅ Requerida (Bearer Token)

**Body:** ❌ No requiere

**Query Params:**

- `nombre` (string, requerido): Nombre exacto del rol a buscar

**Request:**

```http
GET http://localhost:8000/api/usuarios/roles/buscar/?nombre=Administrador
Authorization: Bearer {tu_token_jwt}
```

**Ejemplos de búsqueda:**

```http
# Buscar rol "Cliente"
GET /api/usuarios/roles/buscar/?nombre=Cliente

# Buscar rol "Vendedor"
GET /api/usuarios/roles/buscar/?nombre=Vendedor

# Buscar rol "Gerente"
GET /api/usuarios/roles/buscar/?nombre=Gerente
```

**Respuesta (200 OK):**

```json
{
  "idRol": 1,
  "nombre": "Administrador",
  "descripcion": "Usuario con permisos completos"
}
```

**Respuesta Error (400 Bad Request) - Falta parámetro:**

```json
{
  "error": "Debe proporcionar un nombre"
}
```

**Respuesta Error (404 Not Found):**

```json
{
  "error": "Rol no encontrado"
}
```

**Respuesta Error (500 Internal Server Error):**

```json
{
  "error": "Error al buscar rol: [mensaje de error]"
}
```

**Notas:**

- La búsqueda es **case-sensitive** (distingue mayúsculas/minúsculas)
- Debe coincidir **exactamente** con el nombre del rol
- Si necesitas búsqueda parcial, usa el endpoint de listar todos y filtra en el cliente

---

## 📊 Tabla Resumen de Endpoints

| Endpoint                              | Método | Body             | Autenticación | Descripción                  |
| ------------------------------------- | ------ | ---------------- | ------------- | ---------------------------- |
| `/api/usuarios/roles/`                | GET    | ❌ No            | ❌ No         | Lista todos los roles        |
| `/api/usuarios/roles/`                | POST   | ✅ Sí            | ❌ No         | Crea un nuevo rol            |
| `/api/usuarios/roles/{id}/`           | GET    | ❌ No            | ✅ Sí         | Obtiene un rol por ID        |
| `/api/usuarios/roles/{id}/`           | PUT    | ✅ Sí (completo) | ✅ Sí         | Actualiza todos los campos   |
| `/api/usuarios/roles/{id}/`           | PATCH  | ✅ Sí (parcial)  | ✅ Sí         | Actualiza campos específicos |
| `/api/usuarios/roles/{id}/`           | DELETE | ❌ No            | ✅ Sí         | Elimina rol (hard delete)    |
| `/api/usuarios/roles/buscar/?nombre=` | GET    | ❌ No            | ✅ Sí         | Busca rol por nombre exacto  |

---

## 🔐 Notas de Autenticación

### Endpoints Públicos (No requieren autenticación):

- ✅ `GET /api/usuarios/roles/` - Listar roles
- ✅ `POST /api/usuarios/roles/` - Crear rol

### Endpoints Protegidos (Requieren JWT):

- 🔒 `GET /api/usuarios/roles/{id}/` - Obtener rol
- 🔒 `PUT /api/usuarios/roles/{id}/` - Actualizar completo
- 🔒 `PATCH /api/usuarios/roles/{id}/` - Actualizar parcial
- 🔒 `DELETE /api/usuarios/roles/{id}/` - Eliminar rol
- 🔒 `GET /api/usuarios/roles/buscar/?nombre=` - Buscar rol

**Para endpoints protegidos, incluye el header:**

```http
Authorization: Bearer {tu_token_jwt}
```

---

## 🧪 Ejemplos con cURL

### Listar Roles (sin autenticación)

```bash
curl -X GET "http://localhost:8000/api/usuarios/roles/"
```

### Crear Rol (sin autenticación)

```bash
curl -X POST "http://localhost:8000/api/usuarios/roles/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Gerente",
    "descripcion": "Usuario gerente"
  }'
```

### Obtener Rol (con autenticación)

```bash
curl -X GET "http://localhost:8000/api/usuarios/roles/1/" \
  -H "Authorization: Bearer {tu_token_jwt}"
```

### Actualizar Parcial (PATCH)

```bash
curl -X PATCH "http://localhost:8000/api/usuarios/roles/1/" \
  -H "Authorization: Bearer {tu_token_jwt}" \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Nueva descripción"
  }'
```

### Eliminar Rol

```bash
curl -X DELETE "http://localhost:8000/api/usuarios/roles/3/" \
  -H "Authorization: Bearer {tu_token_jwt}"
```

### Buscar Rol por Nombre

```bash
curl -X GET "http://localhost:8000/api/usuarios/roles/buscar/?nombre=Administrador" \
  -H "Authorization: Bearer {tu_token_jwt}"
```

---

## 🚀 Ejemplos con JavaScript/Fetch

### Listar Roles

```javascript
const response = await fetch("http://localhost:8000/api/usuarios/roles/");
const roles = await response.json();
console.log(roles);
```

### Crear Rol

```javascript
const response = await fetch("http://localhost:8000/api/usuarios/roles/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    nombre: "Gerente",
    descripcion: "Usuario gerente del sistema",
  }),
});

const nuevoRol = await response.json();
console.log(nuevoRol);
```

### Obtener Rol (con token)

```javascript
const response = await fetch("http://localhost:8000/api/usuarios/roles/1/", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

const rol = await response.json();
console.log(rol);
```

### Actualizar Parcial con Axios

```javascript
const response = await axios.patch(
  "http://localhost:8000/api/usuarios/roles/1/",
  {
    descripcion: "Descripción actualizada",
  },
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

console.log(response.data);
```

### Eliminar Rol

```javascript
const response = await fetch("http://localhost:8000/api/usuarios/roles/3/", {
  method: "DELETE",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});

const result = await response.json();
console.log(result); // { "mensaje": "Rol eliminado exitosamente" }
```

### Buscar Rol

```javascript
const nombre = encodeURIComponent("Administrador");
const response = await fetch(
  `http://localhost:8000/api/usuarios/roles/buscar/?nombre=${nombre}`,
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

const rol = await response.json();
console.log(rol);
```

---

## ⚠️ Consideraciones Importantes

### 1. **Eliminación de Roles:**

- Solo se pueden eliminar roles sin usuarios asociados
- Es una eliminación permanente (hard delete)
- Verifica que no haya usuarios antes de eliminar

### 2. **Unicidad del Nombre:**

- El nombre del rol debe ser único en todo el sistema
- Si intentas crear o actualizar con un nombre existente, obtendrás error 400

### 3. **Autenticación:**

- `GET /roles/` y `POST /roles/` NO requieren autenticación (público)
- Todos los demás endpoints requieren token JWT válido

### 4. **Diferencia entre PUT y PATCH:**

- **PUT**: Requiere enviar todos los campos (reemplazo completo)
- **PATCH**: Solo envías los campos que quieres cambiar (actualización parcial)

### 5. **Búsqueda Exacta:**

- El endpoint de búsqueda busca el nombre **exacto**
- Case-sensitive (distingue mayúsculas/minúsculas)
- Para búsqueda flexible, lista todos y filtra en el cliente

---

## 📝 Códigos de Estado HTTP

| Código | Significado           | Cuándo ocurre                                         |
| ------ | --------------------- | ----------------------------------------------------- |
| 200    | OK                    | Operación exitosa (GET, PUT, PATCH, DELETE)           |
| 201    | Created               | Rol creado exitosamente (POST)                        |
| 400    | Bad Request           | Datos inválidos, nombre duplicado, validación fallida |
| 401    | Unauthorized          | Token JWT inválido o no proporcionado                 |
| 404    | Not Found             | Rol no encontrado                                     |
| 500    | Internal Server Error | Error del servidor                                    |

---

## 🎯 Flujo Típico de Uso

### 1. Listar roles disponibles

```javascript
GET /api/usuarios/roles/
```

### 2. Crear un nuevo rol

```javascript
POST /api/usuarios/roles/
Body: { "nombre": "Supervisor", "descripcion": "..." }
```

### 3. Obtener detalles de un rol

```javascript
GET /api/usuarios/roles/1/
Authorization: Bearer {token}
```

### 4. Actualizar el rol

```javascript
PATCH /api/usuarios/roles/1/
Body: { "descripcion": "Nueva descripción" }
Authorization: Bearer {token}
```

### 5. Eliminar el rol (si no tiene usuarios)

```javascript
DELETE /api/usuarios/roles/1/
Authorization: Bearer {token}
```
