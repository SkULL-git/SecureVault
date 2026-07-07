// ==========================
// Password Strength Meter
// ==========================

document.addEventListener("DOMContentLoaded", function () {

    const passwordInput = document.getElementById("password");

    const strengthText = document.getElementById("password-strength");

    if (!passwordInput || !strengthText) return;

    passwordInput.addEventListener("input", function () {

        const password = passwordInput.value;

        let score = 0;

        if (password.length >= 8) score++;

        if (/[A-Z]/.test(password)) score++;

        if (/[a-z]/.test(password)) score++;

        if (/[0-9]/.test(password)) score++;

        if (/[^A-Za-z0-9]/.test(password)) score++;

        if (password.length === 0) {

            strengthText.innerHTML = "";

            return;

        }

        if (score <= 2) {

            strengthText.innerHTML =
                "<span class='text-danger fw-bold'>🔴 Weak Password</span>";

        }

        else if (score == 3) {

            strengthText.innerHTML =
                "<span class='text-warning fw-bold'>🟡 Medium Password</span>";

        }

        else if (score == 4) {

            strengthText.innerHTML =
                "<span class='text-primary fw-bold'>🔵 Strong Password</span>";

        }

        else {

            strengthText.innerHTML =
                "<span class='text-success fw-bold'>🟢 Very Strong Password</span>";

        }

    });

});

// ==========================
// Login Password Toggle
// ==========================

const loginPassword = document.getElementById("loginPassword");
const toggleLoginPassword = document.getElementById("toggleLoginPassword");

if (loginPassword && toggleLoginPassword) {

    toggleLoginPassword.addEventListener("click", function () {

        const type = loginPassword.getAttribute("type") === "password"
            ? "text"
            : "password";

        loginPassword.setAttribute("type", type);

        this.innerHTML =
            type === "password"
                ? '<i class="fas fa-eye"></i>'
                : '<i class="fas fa-eye-slash"></i>';

    });

}