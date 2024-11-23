document.getElementById("register-form").addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevenir comportamiento por defecto del formulario

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    const successMessage = document.getElementById("success-message");
    const errorMessage = document.getElementById("error-message");

    // Limpiar mensajes previos
    successMessage.textContent = "";
    errorMessage.textContent = "";

    // Validar campos vacíos
    if (!username || !email || !password) {
        errorMessage.textContent = "Por favor, completa todos los campos.";
        return; // Detener el proceso
    }

    try {
        // Mostrar datos enviados en la consola para depuración
        console.log("Datos enviados:", JSON.stringify({ username, email, password }));

        // Enviar solicitud al servidor
        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password }),
        });

        // Manejar la respuesta del servidor
        if (response.ok) {
            const result = await response.json();
            successMessage.textContent = result.message || "¡Registro exitoso!";
            setTimeout(() => {
                window.location.href = "/"; // Redirigir al login
            }, 2000); // Esperar 2 segundos antes de redirigir
        } else {
            // Manejar errores específicos del servidor
            const errorData = await response.json();
            errorMessage.textContent = errorData.message || "Error al registrar usuario.";
            console.error("Error en respuesta del servidor:", errorData);
        }
    } catch (error) {
        // Manejar errores de red o de conexión
        errorMessage.textContent = "No se pudo conectar al servidor.";
        console.error("Error:", error);
    }
});
