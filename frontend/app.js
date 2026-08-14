const API_URL = "http://localhost:8000/ask";

const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const submitButton = document.getElementById("submit-button");

const responseSection = document.getElementById("response-section");
const loading = document.getElementById("loading");
const answer = document.getElementById("answer");
const error = document.getElementById("error");

const technicalDetails = document.getElementById("technical-details");
const technicalStatus = document.getElementById("technical-status");
const technicalTime = document.getElementById("technical-time");
const technicalSql = document.getElementById("technical-sql");

const exampleButtons = document.querySelectorAll(".example");


function mostrar(elemento) {
    elemento.classList.remove("hidden");
}


function esconder(elemento) {
    elemento.classList.add("hidden");
}


function limparResposta() {
    answer.textContent = "";
    error.textContent = "";

    technicalStatus.textContent = "—";
    technicalTime.textContent = "—";
    technicalSql.textContent = "—";

    esconder(answer);
    esconder(error);
    esconder(technicalDetails);
}


function iniciarCarregamento() {
    limparResposta();

    mostrar(responseSection);
    mostrar(loading);

    submitButton.disabled = true;
    submitButton.textContent = "Processando...";
}


function finalizarCarregamento() {
    esconder(loading);

    submitButton.disabled = false;
    submitButton.textContent = "Perguntar";
}


function preencherDetalhesTecnicos(resultado) {
    technicalStatus.textContent =
        resultado.status || "—";

    if (
        resultado.execution_time_ms !== null &&
        resultado.execution_time_ms !== undefined
    ) {
        technicalTime.textContent =
            `${resultado.execution_time_ms} ms`;
    } else {
        technicalTime.textContent = "—";
    }

    technicalSql.textContent =
        resultado.generated_sql || "—";

    mostrar(technicalDetails);
}


function exibirResposta(resultado) {
    preencherDetalhesTecnicos(resultado);

    if (resultado.answer) {
        answer.textContent = resultado.answer;
        mostrar(answer);
        return;
    }

    error.textContent =
        "O Ágora não retornou uma resposta.";
    mostrar(error);
}


function exibirErro(mensagem) {
    error.textContent = mensagem;
    mostrar(error);
}


async function enviarPergunta(pergunta) {
    iniciarCarregamento();

    try {
        const response = await fetch(
            API_URL,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    question: pergunta,
                }),
            }
        );

        let resultado;

        try {
            resultado = await response.json();
        } catch {
            throw new Error(
                "A API retornou uma resposta inválida."
            );
        }

        if (!response.ok) {
            preencherDetalhesTecnicos(resultado);

            exibirErro(
                resultado.answer ||
                "Não foi possível processar a pergunta."
            );

            return;
        }

        exibirResposta(resultado);

    } catch (erroRequisicao) {
        exibirErro(
            "Não foi possível conectar ao Ágora. " +
            "Verifique se a API está em execução."
        );

        console.error(
            "Erro ao consultar o Ágora:",
            erroRequisicao
        );

    } finally {
        finalizarCarregamento();
    }
}


form.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const pergunta =
            questionInput.value.trim();

        if (!pergunta) {
            return;
        }

        await enviarPergunta(pergunta);
    }
);


questionInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            form.requestSubmit();
        }
    }
);


exampleButtons.forEach(
    (button) => {
        button.addEventListener(
            "click",
            () => {
                const pergunta =
                    button.dataset.question;

                questionInput.value =
                    pergunta;

                questionInput.focus();
            }
        );
    }
);
