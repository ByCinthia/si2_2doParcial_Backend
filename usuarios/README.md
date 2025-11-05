# Módulo de Usuarios - Documentación de API

## Estructura del Módulo

```
usuarios/
├── models.py           # Modelos Rol y Usuario
├── serializers.py      # Serializers para validación y transformación de datos
├── views.py            # Vistas API (APIView)
├── urls.py             # Rutas del módulo
├── admin.py            # Configuración del panel admin
├── services/
│   ├── __init__.py
│   ├── services_rol.py     # Lógica de negocio de Roles
│   └── services_usuario.py # Lógica de negocio de Usuarios
```

## Endpoints Disponibles

### Autenticación

#### Login

```http
POST /api/usuarios/login/
Content-Type: application/json

{
    "username": "tu_usuario",
    "password": "tu_contraseña"
}
```

**Respuesta exitosa (200):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "idUsuario": 1,
    "username": "tu_usuario",
    "email": "email@example.com",
    "fcmToken": null,
    "rol": {
      "idRol": 1,
      "nombre": "Admin",
      "descripcion": "Administrador del sistema"
    },
    "fecha_creacion": "2025-01-01T00:00:00Z",
    "fecha_actualizacion": "2025-01-01T00:00:00Z",
    "activo": true
  }
}
```

---

### Roles

#### Listar todos los roles

```http
GET /api/usuarios/roles/
Authorization: Bearer <access_token>
```

#### Crear un rol

```http
POST /api/usuarios/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "Admin",
    "descripcion": "Administrador del sistema"
}
```

#### Obtener un rol específico

```http
GET /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
```

#### Actualizar un rol

```http
PUT /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "SuperAdmin",
    "descripcion": "Super administrador"
}
```

#### Actualizar parcialmente un rol

```http
PATCH /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "descripcion": "Nueva descripción"
}
```

#### Eliminar un rol

```http
DELETE /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
```

#### Buscar rol por nombre

```http
GET /api/usuarios/roles/buscar/?nombre=Admin
Authorization: Bearer <access_token>
```

---

### Usuarios

#### Listar todos los usuarios

```http
GET /api/usuarios/
Authorization: Bearer <access_token>
```

#### Crear un usuario

```http
POST /api/usuarios/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "rol": 1,
    "fcmToken": "token_opcional"
}
```

#### Obtener un usuario específico

```http
GET /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
```

#### Actualizar un usuario

```http
PUT /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "usuario_actualizado",
    "email": "nuevo@example.com",
    "rol": 2,
    "activo": true
}
```

#### Actualizar parcialmente un usuario

```http
PATCH /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "email": "nuevo@example.com"
}
```

#### Desactivar un usuario (Soft Delete)

```http
DELETE /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
```

#### Eliminar permanentemente un usuario

```http
DELETE /api/usuarios/<id_usuario>/permanente/
Authorization: Bearer <access_token>
```

#### Cambiar contraseña

```http
POST /api/usuarios/cambiar-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "id_usuario": 1,
    "password_actual": "contraseña_actual",
    "password_nueva": "nueva_contraseña"
}
```

#### Buscar usuarios

```http
GET /api/usuarios/buscar/?q=juan
Authorization: Bearer <access_token>
```

#### Actualizar FCM Token

```http
PATCH /api/usuarios/<id_usuario>/fcm-token/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "fcmToken": "nuevo_token_fcm"
}
```

---

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos inválidos o error de validación
- **401 Unauthorized**: No autenticado o credenciales inválidas
- **403 Forbidden**: Sin permisos o usuario inactivo
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

---

## Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "error": "Descripción del error"
}
```

### Ejemplos de errores comunes:

**Usuario no encontrado:**

```json
{
  "error": "Usuario no encontrado"
}
```

**Credenciales inválidas:**

```json
{
  "error": "Credenciales inválidas"
}
```

**Email duplicado:**

```json
{
  "error": "El email ya está registrado"
}
```

**Rol con usuarios asociados:**

```json
{
  "error": "No se puede eliminar el rol porque tiene usuarios asociados"
}
```

---

## Modelos de Datos

### Rol

```python
{
    "idRol": int,
    "nombre": string (max 100, único),
    "descripcion": string (max 255, opcional)
}
```

### Usuario

```python
{
    "idUsuario": int,
    "username": string (max 150, único),
    "email": string (max 255, único),
    "password": string (max 255, write-only),
    "fcmToken": string (max 255, opcional),
    "rol": int (foreign key),
    "rol_nombre": string (read-only),
    "fecha_creacion": datetime (auto),
    "fecha_actualizacion": datetime (auto),
    "activo": boolean (default: true)
}
```

---

## Migraciones

Para aplicar las migraciones y crear las tablas en la base de datos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Crear Superusuario

Para acceder al panel de administración:

```bash
python manage.py createsuperuser
```

---

## Notas Importantes

1. **Encriptación de contraseñas**: Las contraseñas se encriptan automáticamente usando el sistema de hashing de Django.

2. **Soft Delete**: Al eliminar un usuario con `DELETE /api/usuarios/<id>/`, solo se desactiva (campo `activo = False`). Para eliminación permanente, usar el endpoint `/permanente/`.

3. **Protección de Roles**: No se puede eliminar un rol que tenga usuarios asociados.

4. **Tokens JWT**: El access token expira en 120 minutos y el refresh token en 7 días.

5. **Búsqueda**: La búsqueda de usuarios busca coincidencias parciales (case-insensitive) en `username` y `email`.
