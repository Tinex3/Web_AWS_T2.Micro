document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorMessage = document.getElementById("error-message");

    errorMessage.textContent = "";

    try {
        console.log("Enviando credenciales:", { username, password });

        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
            credentials: "include", // Enviar cookies
        });

        if (response.ok) {
            const result = await response.json();
            console.log("Inicio de sesión exitoso:", result.message);
            window.location.href = "/dashboard";
        } else {
            const errorData = await response.json();
            errorMessage.textContent = errorData.message || "Error al iniciar sesión.";
            console.error("Error en el login:", errorData);
        }
    } catch (error) {
        errorMessage.textContent = "No se pudo conectar al servidor.";
        console.error("Error de red:", error);
    }
});
