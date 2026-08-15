const API_BASE_URL = "http://localhost:8000";
const API_ASK_URL = `${API_BASE_URL}/ask`;
const API_HEALTH_URL = `${API_BASE_URL}/health`;

const HEALTH_CHECK_INTERVAL_MS = 15000;

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

const technicalModel = document.getElementById("technical-model");
const technicalTotalTokens = document.getElementById(
    "technical-total-tokens"
);
const technicalInputTokens = document.getElementById(
    "technical-input-tokens"
);
const technicalCachedTokens = document.getElementById(
    "technical-cached-tokens"
);
const technicalOutputTokens = document.getElementById(
    "technical-output-tokens"
);
const technicalCost = document.getElementById(
    "technical-cost"
);

const technicalUsageBreakdown = document.getElementById(
    "technical-usage-breakdown"
);
const technicalUsage = document.getElementById(
    "technical-usage"
);

const exampleButtons = document.querySelectorAll(".example");

const systemStatus = document.querySelector(".status");
const systemStatusDot = document.querySelector(".status-dot");


function mostrar(elemento) {
    elemento.classList.remove("hidden");
}


function esconder(elemento) {
    elemento.classList.add("hidden");
}


function formatarNumero(valor) {
    if (
        valor === null ||
        valor === undefined
    ) {
        return "—";
    }

    return Number(valor).toLocaleString("pt-BR");
}


function formatarCusto(valor) {
    if (
        valor === null ||
        valor === undefined
    ) {
        return "—";
    }

    const numero = Number(valor);

    if (Number.isNaN(numero)) {
        return "—";
    }

    return `US$ ${numero.toFixed(8)}`;
}


function limparDetalhesDeUso() {
    technicalModel.textContent = "—";
    technicalTotalTokens.textContent = "—";
    technicalInputTokens.textContent = "—";
    technicalCachedTokens.textContent = "—";
    technicalOutputTokens.textContent = "—";
    technicalCost.textContent = "—";

    technicalUsage.textContent = "—";

    esconder(
        technicalUsageBreakdown
    );
}


function limparResposta() {
    answer.textContent = "";
    error.textContent = "";

    technicalStatus.textContent = "—";
    technicalTime.textContent = "—";
    technicalSql.textContent = "—";

    limparDetalhesDeUso();

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


function preencherUso(resultado) {
    const usage = resultado.usage;

    if (!usage) {
        limparDetalhesDeUso();
        return;
    }

    technicalModel.textContent =
        usage.model || "—";

    technicalTotalTokens.textContent =
        formatarNumero(
            usage.total_tokens
        );

    technicalInputTokens.textContent =
        formatarNumero(
            usage.input_tokens
        );

    technicalCachedTokens.textContent =
        formatarNumero(
            usage.cached_input_tokens
        );

    technicalOutputTokens.textContent =
        formatarNumero(
            usage.output_tokens
        );

    if (
        usage.cost &&
        usage.cost.total_cost_usd !== null &&
        usage.cost.total_cost_usd !== undefined
    ) {
        technicalCost.textContent =
            formatarCusto(
                usage.cost.total_cost_usd
            );
    } else {
        technicalCost.textContent = "—";
    }

    const steps = usage.steps;

    if (
        !steps ||
        (
            !steps.sql_generation &&
            !steps.final_answer
        )
    ) {
        esconder(
            technicalUsageBreakdown
        );

        technicalUsage.textContent = "—";

        return;
    }

    const sqlGeneration =
        steps.sql_generation || {};

    const finalAnswer =
        steps.final_answer || {};

    const detalhamento = [
        "Geração do SQL",
        `  Entrada: ${formatarNumero(
            sqlGeneration.input_tokens
        )}`,
        `  Cache: ${formatarNumero(
            sqlGeneration.cached_input_tokens
        )}`,
        `  Saída: ${formatarNumero(
            sqlGeneration.output_tokens
        )}`,
        `  Total: ${formatarNumero(
            sqlGeneration.total_tokens
        )}`,
        "",
        "Resposta final",
        `  Entrada: ${formatarNumero(
            finalAnswer.input_tokens
        )}`,
        `  Cache: ${formatarNumero(
            finalAnswer.cached_input_tokens
        )}`,
        `  Saída: ${formatarNumero(
            finalAnswer.output_tokens
        )}`,
        `  Total: ${formatarNumero(
            finalAnswer.total_tokens
        )}`,
    ];

    technicalUsage.textContent =
        detalhamento.join("\n");

    mostrar(
        technicalUsageBreakdown
    );
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

    preencherUso(resultado);

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


function obterElementoTextoStatus() {
    let statusText =
        systemStatus.querySelector(".status-text");

    if (!statusText) {
        statusText = document.createElement("span");
        statusText.className = "status-text";

        const textosSoltos = Array.from(
            systemStatus.childNodes
        ).filter(
            (node) => node.nodeType === Node.TEXT_NODE
        );

        textosSoltos.forEach(
            (node) => node.remove()
        );

        systemStatus.appendChild(statusText);
    }

    return statusText;
}


function atualizarStatusSistema(
    estado,
    texto
) {
    const statusText =
        obterElementoTextoStatus();

    systemStatus.dataset.state = estado;
    statusText.textContent = texto;

    systemStatusDot.classList.remove(
        "status-dot-available",
        "status-dot-degraded",
        "status-dot-unavailable",
        "status-dot-checking"
    );

    if (estado === "available") {
        systemStatusDot.classList.add(
            "status-dot-available"
        );
        return;
    }

    if (estado === "degraded") {
        systemStatusDot.classList.add(
            "status-dot-degraded"
        );
        return;
    }

    if (estado === "checking") {
        systemStatusDot.classList.add(
            "status-dot-checking"
        );
        return;
    }

    systemStatusDot.classList.add(
        "status-dot-unavailable"
    );
}


async function verificarSaude() {
    atualizarStatusSistema(
        "checking",
        "Verificando sistema..."
    );

    try {
        const response = await fetch(
            API_HEALTH_URL,
            {
                method: "GET",
                cache: "no-store",
            }
        );

        let resultado;

        try {
            resultado = await response.json();
        } catch {
            atualizarStatusSistema(
                "unavailable",
                "Sistema indisponível"
            );
            return;
        }

        if (
            response.ok &&
            resultado.status === "ok" &&
            resultado.database === "ok"
        ) {
            atualizarStatusSistema(
                "available",
                "Sistema disponível"
            );
            return;
        }

        if (
            resultado.status === "degraded" ||
            resultado.database === "error"
        ) {
            atualizarStatusSistema(
                "degraded",
                "Sistema degradado"
            );
            return;
        }

        atualizarStatusSistema(
            "unavailable",
            "Sistema indisponível"
        );

    } catch (erroHealth) {
        atualizarStatusSistema(
            "unavailable",
            "Sistema indisponível"
        );

        console.error(
            "Erro no health check:",
            erroHealth
        );
    }
}


async function enviarPergunta(pergunta) {
    iniciarCarregamento();

    try {
        const response = await fetch(
            API_ASK_URL,
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
            preencherDetalhesTecnicos(
                resultado
            );

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

        await verificarSaude();

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


verificarSaude();

setInterval(
    verificarSaude,
    HEALTH_CHECK_INTERVAL_MS
);
