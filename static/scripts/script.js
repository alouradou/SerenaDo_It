document.addEventListener("DOMContentLoaded", function () {
    const btnsWithLoader = document.querySelectorAll(".btn-with-loader");

    btnsWithLoader.forEach(function (btn) {
        const loaderId = btn.closest(".button-container").getAttribute("data-loader-id");
        const loader = document.getElementById(loaderId);

        btn.addEventListener("click", function () {
            loader.style.display = "block";

            // Ici, vous pouvez ajouter votre logique pour effectuer des requêtes et des calculs

            // Simule une attente de 3 secondes (vous devrez remplacer cela par votre logique réelle)
            setTimeout(function () {
                loader.style.display = "none";
                // Ajoutez ici le code pour rediriger vers la page spécifique
                // window.location.href = btn.getAttribute("href");
            }, 6000);
        });
    });
});
