// --- FUNZIONI PER LA GESTIONE DELLE DATE ---
function addDateInput() {
    const container = document.getElementById('date-container');
    const newRow = document.createElement('div');
    newRow.className = 'date-input-row flex items-center space-x-2';
    newRow.innerHTML = `
        <input type="date" name="date_prenotazioni[]" required
               onchange="checkDisponibilita()"
               class="date-input flex-1 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md border">
        <button type="button" onclick="removeDate(this)" class="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded">
            <i class="fas fa-trash"></i>
        </button>
    `;
    container.appendChild(newRow);
    updateRemoveButtons();
}
function updateRemoveButtons() {
    const container = document.getElementById('date-container');
    const removeButtons = document.querySelectorAll('.date-input-row button[onclick="removeDate(this)"]');
    
    if (container.children.length > 1) {
        removeButtons.forEach(btn => btn.classList.remove('hidden'));
    } else {
        removeButtons.forEach(btn => btn.classList.add('hidden'));
    }
}
function removeDate(button) {
    const row = button.closest('.date-input-row');
    const container = document.getElementById('date-container');
    
    if (container.children.length > 1) {
        row.remove();
        checkDisponibilita();
        updateRemoveButtons();
    } else {
        alert('Devi mantenere almeno una data!');
    }
}

// FUNZIONE PER VERIFICA DISPONIBILITÀ (Implementa l'AND Booleano)
async function checkDisponibilita() {
    const aulaSelect = document.getElementById('id_aula');
    const dateInputs = document.querySelectorAll('.date-input');
    const fasciaSelect = document.getElementById('fascia_oraria');
    
    // 1. Reset selezione e classi
    Array.from(fasciaSelect.options).forEach(opt => {
        opt.classList.remove('occupata', 'disponibile');
        opt.text = opt.text.replace(/ [✓✗]$/, ''); 
        opt.disabled = false;
        opt.selected = false;
    });

    const idAula = aulaSelect.value;
    const dateSelezionate = Array.from(dateInputs)
        .map(input => input.value)
        .filter(val => val);
    
    // Interrompe se mancano dati essenziali (controllo frontend)
    if (!idAula || dateSelezionate.length === 0) {
        return;
    }

    // 2. Determina le fasce occupate su TUTTE le date (OR booleano sull'occupazione)
    const fasceTotalmenteOccupate = new Set();
    
    for (const data of dateSelezionate) {
        try {
            // Chiamata: /fasce-occupate
            const response = await fetch(`/fasce-occupate?data=${data}&id_aula=${idAula}`);
            
            if (!response.ok) {
                // In caso di errore , disabilita tutto e termina
                Array.from(fasciaSelect.options).forEach(opt => opt.disabled = true);
                console.error(`Errore nel caricamento della disponibilità per ${data}.`);
                return;
            }
            
            const dataJSON = await response.json();
            
            dataJSON.fasce_occupate.forEach(fascia => {
                // Una fascia è occupata se è prenotata in ALMENO UNA delle date
                fasceTotalmenteOccupate.add(fascia);
            });
        } catch (error) {
            console.error("Errore di rete/server:", error);
            Array.from(fasciaSelect.options).forEach(opt => opt.disabled = true);
            return;
        }
    }

    // 3. Aggiorna la select finale in base al set delle fasce occupate (AND booleano sulla disponibilità)
    Array.from(fasciaSelect.options).forEach(opt => {
        const fasciaValue = opt.value;
        const baseText = opt.text.split(' ')[0] + ' ' + opt.text.split(' ')[1] + ' ' + opt.text.split(' ')[2];
        
        if (fasceTotalmenteOccupate.has(fasciaValue)) {
            opt.classList.add('occupata');
            opt.text = baseText + ' ✗';
            opt.disabled = true;
        } else {
            opt.classList.add('disponibile');
            opt.text = baseText + ' ✓';
            opt.disabled = false;
        }
    });
}
// --- FUNZIONE PER MOSTRARE IL LOADER AL SUBMIT ---
function showLoader() {
    const form = document.querySelector('form');
    const loader = document.getElementById('loader-overlay');
    
    form.addEventListener('submit', (e) => {
        if (form.checkValidity()) {
            loader.classList.remove('hidden');
        }
    });
}
// Inizializzazione all'avvio
document.addEventListener('DOMContentLoaded', () => {
    updateRemoveButtons();
    checkDisponibilita();
    showLoader(); // new: loader
});