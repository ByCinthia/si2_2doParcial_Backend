# Ejemplos de Uso - API de Usuarios

## Usando cURL

### 1. Login

```bash
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 2. Crear un Rol

```bash
curl -X POST http://localhost:8000/api/usuarios/roles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "nombre": "Admin",
    "descripcion": "Administrador del sistema"
  }'
```

### 3. Listar Roles

```bash
curl -X GET http://localhost:8000/api/usuarios/roles/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 4. Crear un Usuario

```bash
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "password123",
    "rol": 1
  }'
```

### 5. Listar Usuarios

```bash
curl -X GET http://localhost:8000/api/usuarios/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 6. Actualizar Usuario

```bash
curl -X PATCH http://localhost:8000/api/usuarios/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "email": "nuevo_email@example.com"
  }'
```

### 7. Cambiar Contraseña

```bash
curl -X POST http://localhost:8000/api/usuarios/cambiar-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{
    "id_usuario": 1,
    "password_actual": "password123",
    "password_nueva": "nueva_password456"
  }'
```

### 8. Buscar Usuarios

```bash
curl -X GET "http://localhost:8000/api/usuarios/buscar/?q=juan" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 9. Refrescar Token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<REFRESH_TOKEN>"
  }'
```

---

## Usando Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Login
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/usuarios/login/",
        json={"username": username, "password": password}
    )
    data = response.json()
    return data.get("access"), data.get("refresh")

# 2. Crear Rol
def crear_rol(token, nombre, descripcion):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/usuarios/roles/",
        headers=headers,
        json={"nombre": nombre, "descripcion": descripcion}
    )
    return response.json()

# 3. Listar Roles
def listar_roles(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/usuarios/roles/", headers=headers)
    return response.json()

# 4. Crear Usuario
def crear_usuario(token, username, email, password, rol_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/usuarios/",
        headers=headers,
        json={
            "username": username,
            "email": email,
            "password": password,
            "rol": rol_id
        }
    )
    return response.json()

# 5. Listar Usuarios
def listar_usuarios(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/usuarios/", headers=headers)
    return response.json()

# 6. Obtener Usuario
def obtener_usuario(token, id_usuario):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/usuarios/{id_usuario}/", headers=headers)
    return response.json()

# 7. Actualizar Usuario
def actualizar_usuario(token, id_usuario, data):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/usuarios/{id_usuario}/",
        headers=headers,
        json=data
    )
    return response.json()

# 8. Cambiar Contraseña
def cambiar_password(token, id_usuario, password_actual, password_nueva):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/usuarios/cambiar-password/",
        headers=headers,
        json={
            "id_usuario": id_usuario,
            "password_actual": password_actual,
            "password_nueva": password_nueva
        }
    )
    return response.json()

# 9. Buscar Usuarios
def buscar_usuarios(token, query):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/usuarios/buscar/",
        headers=headers,
        params={"q": query}
    )
    return response.json()

# 10. Actualizar FCM Token
def actualizar_fcm_token(token, id_usuario, fcm_token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/usuarios/{id_usuario}/fcm-token/",
        headers=headers,
        json={"fcmToken": fcm_token}
    )
    return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    # Login
    access_token, refresh_token = login("admin", "admin123")
    print(f"Access Token: {access_token}")

    # Crear un rol
    rol = crear_rol(access_token, "Estudiante", "Rol para estudiantes")
    print(f"Rol creado: {rol}")

    # Listar roles
    roles = listar_roles(access_token)
    print(f"Roles: {roles}")

    # Crear un usuario
    usuario = crear_usuario(
        access_token,
        "estudiante1",
        "estudiante@example.com",
        "password123",
        rol['idRol']
    )
    print(f"Usuario creado: {usuario}")

    # Listar usuarios
    usuarios = listar_usuarios(access_token)
    print(f"Usuarios: {usuarios}")
```

---

## Usando JavaScript (Fetch API)

```javascript
const BASE_URL = "http://localhost:8000/api";

// 1. Login
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/usuarios/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  return data;
}

// 2. Crear Rol
async function crearRol(token, nombre, descripcion) {
  const response = await fetch(`${BASE_URL}/usuarios/roles/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ nombre, descripcion }),
  });
  return await response.json();
}

// 3. Listar Roles
async function listarRoles(token) {
  const response = await fetch(`${BASE_URL}/usuarios/roles/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await response.json();
}

// 4. Crear Usuario
async function crearUsuario(token, username, email, password, rol) {
  const response = await fetch(`${BASE_URL}/usuarios/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ username, email, password, rol }),
  });
  return await response.json();
}

// 5. Listar Usuarios
async function listarUsuarios(token) {
  const response = await fetch(`${BASE_URL}/usuarios/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await response.json();
}

// 6. Buscar Usuarios
async function buscarUsuarios(token, query) {
  const response = await fetch(`${BASE_URL}/usuarios/buscar/?q=${query}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await response.json();
}

// Ejemplo de uso
async function main() {
  try {
    // Login
    const loginData = await login("admin", "admin123");
    console.log("Login exitoso:", loginData);

    const token = loginData.access;

    // Crear rol
    const rol = await crearRol(token, "Estudiante", "Rol para estudiantes");
    console.log("Rol creado:", rol);

    // Listar roles
    const roles = await listarRoles(token);
    console.log("Roles:", roles);

    // Crear usuario
    const usuario = await crearUsuario(
      token,
      "estudiante1",
      "estudiante@example.com",
      "password123",
      rol.idRol
    );
    console.log("Usuario creado:", usuario);

    // Listar usuarios
    const usuarios = await listarUsuarios(token);
    console.log("Usuarios:", usuarios);
  } catch (error) {
    console.error("Error:", error);
  }
}

main();
```

---

## Postman Collection

Puedes importar esta colección en Postman:

```json
{
  "info": {
    "name": "API Usuarios",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/usuarios/login/",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"username\": \"admin\",\n  \"password\": \"admin123\"\n}"
        }
      }
    },
    {
      "name": "Listar Roles",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/usuarios/roles/",
        "auth": {
          "type": "bearer",
          "bearer": [{ "key": "token", "value": "{{access_token}}" }]
        }
      }
    }
  ],
  "variable": [{ "key": "base_url", "value": "http://localhost:8000/api" }]
}
```
