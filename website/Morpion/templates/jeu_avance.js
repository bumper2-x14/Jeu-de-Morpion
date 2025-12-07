// ==========================================================
// UTILITAIRE : récupérer l’élément carte le plus proche
// ==========================================================
function getCardRoot(elem) {
    return elem.closest(".card");
}

// ==========================================================
// Mise à jour des barres d’armurerie depuis le deck
// ==========================================================
function updateDeckArmoryBars(cardElem) {
    if (!cardElem) return;

    // Récupère la checkbox de ce label
    const inputElem = cardElem.closest("label")?.querySelector("input.deck-checkbox");
    if (!inputElem) return;

    // Détermine l’équipe
    const team = parseInt(inputElem.dataset.team);
    const team_prefix = team === 1 ? "p1" : "p2";

    // Statistiques de la carte
    const fireball = cardElem.dataset.fireball ?? 0;
    const heal = cardElem.dataset.heal ?? 0;
    const armageddon = cardElem.dataset.armageddon ?? 0;

    // Met à jour les barres CSS
    const f = document.getElementById(team_prefix + "_fireball_bar");
    const h = document.getElementById(team_prefix + "_heal_bar");
    const a = document.getElementById(team_prefix + "_armageddon_bar");

    if (f) f.style.setProperty('--fireball-percent', fireball + "%");
    if (h) h.style.setProperty('--heal-percent', heal + "%");
    if (a) a.style.setProperty('--armageddon-percent', armageddon + "%");
}

// ==========================================================
// Mise à jour de l’armurerie depuis une carte sur la grille
// ==========================================================
function updateGridArmoryBars(cardElem) {
    if (!cardElem) return;

    const cell = cardElem.closest(".cell-morpion");
    if (!cell) return;

    const team = parseInt(cell.dataset.team);
    if (!team) return;

    const team_prefix = team === 1 ? "p1" : "p2";

    const fireball = cell.dataset.fireball ?? 0;
    const heal = cell.dataset.heal ?? 0;
    const armageddon = cell.dataset.armageddon ?? 0;

    const f = document.getElementById(team_prefix + "_fireball_bar");
    const h = document.getElementById(team_prefix + "_heal_bar");
    const a = document.getElementById(team_prefix + "_armageddon_bar");

    if (f) f.style.setProperty('--fireball-percent', fireball + "%");
    if (h) h.style.setProperty('--heal-percent', heal + "%");
    if (a) a.style.setProperty('--armageddon-percent', armageddon + "%");
}

// ==========================================================
// Réinitialisation des barres d’armurerie
// ==========================================================
function clearArmoryBars() {
    const bars = [
        "p1_fireball_bar", "p1_heal_bar", "p1_armageddon_bar",
        "p2_fireball_bar", "p2_heal_bar", "p2_armageddon_bar"
    ];

    bars.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.setProperty("--fireball-percent", "0%");
            el.style.setProperty("--heal-percent", "0%");
            el.style.setProperty("--armageddon-percent", "0%");
        }
    });
}

// ==========================================================
// VARIABLES D’ÉTAT DU SYSTÈME D’ACTIONS
// ==========================================================
let selectedCardId = null;   // carte du deck sélectionnée
let chosenAbility = null;    // capacité choisie
let actingCard = null;       // carte qui déclenche l’action

let waitingForActor = true;      // attendre carte acteur
let waitingForAbility = false;   // attendre capacité
let waitingForTarget = false;    // attendre cible

const currentPlayer = parseInt(document.querySelector(".grid-container").dataset.turn);

// ==========================================================
// Sélection des cartes dans le deck
// ==========================================================
document.querySelectorAll(".deck-checkbox").forEach(cb => {
    cb.addEventListener("change", function () {

        // Autoriser une seule carte sélectionnée
        document.querySelectorAll(".deck-checkbox").forEach(c => {
            if (c !== cb) c.checked = false;
        });

        selectedCardId = cb.checked ? cb.value : null;

        // Mise à jour de l’armurerie
        const cardElem = cb.closest("label").querySelector(".card");
        if (cb.checked) updateDeckArmoryBars(cardElem);
        else clearArmoryBars();

        // Réinitialisation du système d’actions
        chosenAbility = null;
        actingCard = null;

        waitingForActor = true;
        waitingForAbility = false;
        waitingForTarget = false;

        document.querySelectorAll(".armory_checkbox").forEach(a => a.checked = false);
    });
});

// ==========================================================
// Sélection des capacités dans l’armurerie
// ==========================================================
document.querySelectorAll(".armory_checkbox").forEach(ab => {
    ab.addEventListener("change", function () {

        // Une seule capacité à la fois
        document.querySelectorAll(".armory_checkbox").forEach(x => {
            if (x !== ab) x.checked = false;
        });

        chosenAbility = ab.checked ? ab.value : null;

        if (!chosenAbility) {
            waitingForAbility = false;
            waitingForTarget = false;
            return;
        }

        // On doit d’abord choisir la carte acteur
        if (!actingCard) {
            alert("Sélectionne d’abord une de tes cartes sur la grille avant de choisir une capacité.");
            ab.checked = false;
            chosenAbility = null;
            return;
        }

        waitingForAbility = false;
        waitingForTarget = true;

    });
});

// ==========================================================
// Gestion du clic sur une case vide (placement simple)
// ==========================================================
document.querySelectorAll(".cell-morpion").forEach(cell => {
    cell.addEventListener("click", function (ev) {

        // Case détruite
        if (cell.classList.contains("armageddon-locked")) {
            ev.stopPropagation();
            alert("Cette case est détruite par Armageddon. Impossible de jouer ici.");
            return;
        }

        // Placement normal sans capacité
        if (!chosenAbility) {

            if (!selectedCardId) return;

            if (cell.querySelector(".card")) {
                alert("Impossible : cette case est déjà occupée.");
                return;
            }

            // Remplir le formulaire
            document.getElementById("action_type").value = "place";
            document.getElementById("selected_card").value = selectedCardId;
            document.getElementById("selected_move").value = cell.dataset.pos;

            document.getElementById("game_form").submit();
        }
    });
});

// ==========================================================
// Gestion du clic sur une carte de la grille (acteur / cible)
// ==========================================================
document.querySelectorAll(".cell-morpion .card").forEach(card => {
    card.addEventListener("click", function (ev) {
        ev.stopPropagation();

        const cell = card.closest(".cell-morpion");

        // Carte détruite
        if (cell.classList.contains("armageddon-locked")) {
            alert("Cette carte est détruite par Armageddon.");
            return;
        }

        const clickedTeam = parseInt(cell.dataset.team);

        // Highlight de sélection + possibilité de désélection
        const parentCell = card.closest(".cell-morpion");
        if (parentCell) {
            if (parentCell.classList.contains("selected")) {
                parentCell.classList.remove("selected");
            } else {
                document.querySelectorAll(".cell-morpion").forEach(c => c.classList.remove("selected"));
                parentCell.classList.add("selected");
            }
        }

        // ---------- Phase 1 : choisir l’acteur ----------
        if (waitingForActor) {

            if (clickedTeam !== currentPlayer) {
                alert("Tu dois choisir une carte qui t’appartient !");
                return;
            }

            updateGridArmoryBars(card);

            actingCard = cell.dataset.id;
            waitingForActor = false;
            waitingForAbility = true;

            // Highlight de l’armurerie du joueur actif
            document.querySelector(".player1_armory").classList.toggle("highlight-armory", clickedTeam === 1);
            document.querySelector(".player2_armory").classList.toggle("highlight-armory", clickedTeam === 2);

            return;
        }

        // ---------- Phase 2 : capacité non choisie ----------
        if (waitingForAbility) {
            return;
        }

        // ---------- Phase 3 : choisir la cible ----------
        if (waitingForTarget) {

            if (chosenAbility !== "heal" && clickedTeam === currentPlayer) {
                alert("Cette capacité ne peut pas cibler tes propres cartes.");
                return;
            }

            // Envoie de l'action au backend
            document.getElementById("action_type").value = "ability";
            document.getElementById("acting_card").value = actingCard;
            document.getElementById("ability").value = chosenAbility;
            document.getElementById("ability_target").value = cell.dataset.id;

            // Réinitialisation
            actingCard = null;
            chosenAbility = null;

            waitingForActor = true;
            waitingForAbility = false;
            waitingForTarget = false;

            document.querySelectorAll(".armory_checkbox").forEach(a => a.checked = false);

            document.querySelector(".player1_armory").classList.remove("highlight-armory");
            document.querySelector(".player2_armory").classList.remove("highlight-armory");

            document.getElementById("game_form").submit();
        }
    });
});

// ==========================================================
// Highlight simple sur les cases (clic sur case vide)
// ==========================================================
document.querySelectorAll(".cell-morpion").forEach(cell => {
    cell.addEventListener("click", function () {

        if (cell.classList.contains("armageddon-locked")) return;

        const team = parseInt(this.dataset.team || 0);

        // Le joueur ne peut sélectionner que ses cases ou des cases vides
        if (team !== currentPlayer && team !== 0) return;

        // Permettre désélection
        if (this.classList.contains("selected")) {
            this.classList.remove("selected");
            return;
        }

        document.querySelectorAll(".cell-morpion").forEach(c => c.classList.remove("selected"));
        this.classList.add("selected");
    });
});
