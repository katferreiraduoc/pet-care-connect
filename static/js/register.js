const togglePasswords = document.getElementById("togglePasswords");
const password1 = document.getElementById("id_password1");
const password2 = document.getElementById("id_password2");

if (togglePasswords && password1 && password2) {
    togglePasswords.addEventListener("change", () => {
        const nextType = togglePasswords.checked ? "text" : "password";
        password1.type = nextType;
        password2.type = nextType;
    });
}
