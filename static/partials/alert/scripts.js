let progressBarInterval = null;
let isAlertVisible = false;
let larguraAtual = 340;
let totalDuration = 10000;
let intervalTime = 100;
let startTime = 0;

function calcularLargura() {
    return window.matchMedia("(max-width: 600px)").matches ? 200 : 340;
}

function showAlert(message, type) {
    if (isAlertVisible) return;

    isAlertVisible = true;
    startTime = Date.now();

    const alertDiv = document.getElementById(type + 'Alert');
    const messageSpan = document.getElementById(type + 'Message');
    const progressBar = document.getElementById(type + 'ProgressBar');

    if (!alertDiv || !messageSpan || !progressBar) {
        console.error("IDs não encontrados para o tipo:", type);
        return;
    }

    messageSpan.innerText = message;
    alertDiv.style.display = "block";

    larguraAtual = calcularLargura();

    function atualizarBarra() {
        const elapsed = Date.now() - startTime;
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
        atualizarBarra();
    });
}

function closeAlert(alertId) {
    const alertDiv = document.getElementById(alertId);
    if (!alertDiv) return;

    alertDiv.style.display = "none";

    const type = alertId.replace("Alert", "");
    const progressBar = document.getElementById(type + 'ProgressBar');
    if (progressBar) progressBar.style.width = "0";

    if (progressBarInterval) {
        clearInterval(progressBarInterval);
        progressBarInterval = null;
    }

    isAlertVisible = false;
}