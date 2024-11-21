document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevenir comportamiento predeterminado del formulario

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const errorMessage = document.getElementById("error-message");
    errorMessage.textContent = ""; // Limpiar mensajes de error

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token); // Guardar el token JWT
            window.location.href = "/dashboard"; // Redirigir al dashboard
        } else {
            const errorData = await response.json();
            errorMessage.textContent = errorData.message || "Error al iniciar sesión.";
        }
    } catch (error) {
        errorMessage.textContent = "No se pudo conectar al servidor.";
        console.error("Error:", error);
    }
});
