/**
 * Verifica si el usuario ya está autenticado.
 * Si el token JWT está presente y válido, redirige al dashboard.
 */
function checkAuthentication() {
    const token = localStorage.getItem("access_token");

    if (token) {
        // Verificar si el token es válido llamando al dashboard
        fetch("/dashboard", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        })
        .then((response) => {
            if (response.ok) {
                // Token válido, redirigir al dashboard
                window.location.href = "/dashboard";
            } else {
                // Token inválido, eliminar del localStorage
                localStorage.removeItem("access_token");
            }
        })
        .catch((error) => {
            console.error("Error al verificar el token:", error);
            localStorage.removeItem("access_token");
        });
    }
}

// Ejecutar al cargar la página para verificar autenticación
window.onload = checkAuthentication;

/**
 * Manejador del formulario de inicio de sesión
 */
document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevenir el comportamiento predeterminado del formulario

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const errorMessage = document.getElementById("error-message");
    errorMessage.textContent = ""; // Limpiar mensajes previos

    try {
        console.log("Enviando credenciales:", { username, password });

        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Respuesta del servidor:", data);

            const token = data.token || data.access_token;
            if (token) {
                // Guardar token JWT en localStorage
                localStorage.setItem("access_token", token);
                console.log("Token guardado correctamente:", token);

                // Redirigir directamente al dashboard
                window.location.href = "/dashboard";
            } else {
                console.error("No se recibió el token en la respuesta.");
                errorMessage.textContent = "Error: No se pudo obtener el token de autenticación.";
            }
        } else {
            const errorData = await response.json();
            errorMessage.textContent = errorData.message || "Error al iniciar sesión.";
        }
    } catch (error) {
        errorMessage.textContent = "No se pudo conectar al servidor.";
        console.error("Error:", error);
    }
});
