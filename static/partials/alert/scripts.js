let progressBarInterval = null;
let isAlertVisible = false;
let larguraAtual = 340;
let totalDuration = 10000; // 10s
let intervalTime = 100;
let startTime = 0;

function calcularLargura() {
    return window.matchMedia("(max-width: 600px)").matches ? 200 : 340;
}

function showAlert(message, type) {
    if (isAlertVisible) return;

    isAlertVisible = true;
    startTime = Date.now(); // marca o início
    const alertDiv = document.getElementById(type + 'Alert');
    const errorMessage = document.getElementById(type === 'error' ? 'errorMessage' : 'successMessage');
    
    errorMessage.innerText = message;
    alertDiv.style.display = "block";

    const progressBar = document.getElementById(type === 'error' ? 'errorProgressBar' : 'successProgressBar');

    larguraAtual = calcularLargura();

    function atualizarBarra() {
        const elapsed = Date.now() - startTime; // tempo real decorrido
        const progresso = Math.max(0, (totalDuration - elapsed) / totalDuration);
        progressBar.style.width = (larguraAtual * progresso) + "px";

        if (elapsed >= totalDuration) {
            clearInterval(progressBarInterval);
            closeAlert(type + 'Alert');
        }
    }

    if (progressBarInterval) clearInterval(progressBarInterval);
    progressBarInterval = setInterval(atualizarBarra, intervalTime);

    window.addEventListener("resize", () => {
        larguraAtual = calcularLargura();
        atualizarBarra(); // recalcula proporcionalmente
    });
}

function closeAlert(alertId) {
    const alertDiv = document.getElementById(alertId);
    alertDiv.style.display = "none";
    
    const progressBar = document.getElementById(alertId === 'errorAlert' ? 'errorProgressBar' : 'successProgressBar');
    progressBar.style.width = "0"; 

    if (progressBarInterval) {
        clearInterval(progressBarInterval);
        progressBarInterval = null;
    }

    isAlertVisible = false;
}
