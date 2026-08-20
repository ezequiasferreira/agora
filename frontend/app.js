const API_BASE_URL = window.location.origin;
const API_ASK_URL = `${API_BASE_URL}/ask`;
const API_HEALTH_URL = `${API_BASE_URL}/health`;

const HEALTH_CHECK_INTERVAL_MS = 15000;

const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const submitButton = document.getElementById("submit-button");

const responseSection = document.getElementById("response-section");
const responseCard = document.querySelector(".response-card");
const loading = document.getElementById("loading");
const answer = document.getElementById("answer");
const error = document.getElementById("error");

const chartContainer = document.getElementById("chart-container");
const chartTitle = document.getElementById("chart-title");
const chartSummary = document.getElementById("chart-summary");
const resultChartCanvas = document.getElementById("result-chart");

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

let graficoAtual = null;


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


function normalizarTexto(valor) {
    return String(valor || "")
        .normalize("NFD")
        .replace(
            /[\u0300-\u036f]/g,
            ""
        )
        .toLowerCase()
        .trim();
}


function converterNumeroTexto(valor) {
    if (
        valor === null ||
        valor === undefined
    ) {
        return null;
    }

    let texto = String(valor)
        .trim()
        .replace(/\s/g, "")
        .replace(/^R\$/i, "")
        .replace(/^US\$/i, "")
        .replace(/%$/, "");

    if (!texto) {
        return null;
    }

    const possuiVirgula =
        texto.includes(",");

    const possuiPonto =
        texto.includes(".");

    if (
        possuiVirgula &&
        possuiPonto
    ) {
        texto = texto
            .replace(/\./g, "")
            .replace(",", ".");
    } else if (possuiVirgula) {
        texto = texto.replace(
            ",",
            "."
        );
    }

    texto = texto.replace(
        /[^0-9.+-]/g,
        ""
    );

    if (!texto) {
        return null;
    }

    const numero = Number(texto);

    if (Number.isNaN(numero)) {
        return null;
    }

    return numero;
}


function limparEstadoResposta() {
    responseCard.classList.remove(
        "response-state-answer",
        "response-state-not-answerable",
        "response-state-clarification",
        "response-state-error"
    );

    answer.classList.remove(
        "answer-normal",
        "answer-not-answerable",
        "answer-clarification"
    );
}


function aplicarEstadoResposta(status) {
    limparEstadoResposta();

    if (
        status === "ANSWER" ||
        status === "NO_DATA"
    ) {
        responseCard.classList.add(
            "response-state-answer"
        );

        answer.classList.add(
            "answer-normal"
        );

        return;
    }

    if (
        status ===
        "NOT_ANSWERABLE"
    ) {
        responseCard.classList.add(
            "response-state-not-answerable"
        );

        answer.classList.add(
            "answer-not-answerable"
        );

        return;
    }

    if (
        status ===
        "NEEDS_CLARIFICATION"
    ) {
        responseCard.classList.add(
            "response-state-clarification"
        );

        answer.classList.add(
            "answer-clarification"
        );

        return;
    }

    responseCard.classList.add(
        "response-state-error"
    );
}


function criarTituloResposta(titulo) {
    const elemento =
        document.createElement(
            "div"
        );

    elemento.className =
        "answer-state-title";

    elemento.textContent =
        titulo;

    return elemento;
}


function criarTextoResposta(texto) {
    const elemento =
        document.createElement(
            "div"
        );

    elemento.className =
        "answer-state-message";

    elemento.textContent =
        texto;

    return elemento;
}


function criarMensagemResposta(
    titulo,
    mensagem
) {
    answer.replaceChildren();

    answer.appendChild(
        criarTituloResposta(
            titulo
        )
    );

    answer.appendChild(
        criarTextoResposta(
            mensagem
        )
    );
}


function normalizarCelulasTabela(linha) {
    let texto = linha.trim();

    if (texto.startsWith("|")) {
        texto = texto.substring(1);
    }

    if (texto.endsWith("|")) {
        texto = texto.substring(
            0,
            texto.length - 1
        );
    }

    return texto
        .split("|")
        .map(
            (celula) =>
                celula.trim()
        );
}


function ehLinhaSeparadoraTabela(linha) {
    const celulas =
        normalizarCelulasTabela(
            linha
        );

    if (!celulas.length) {
        return false;
    }

    return celulas.every(
        (celula) =>
            /^:?-{3,}:?$/.test(
                celula
            )
    );
}


function linhaPareceTabela(linha) {
    const texto =
        linha.trim();

    if (!texto.includes("|")) {
        return false;
    }

    return (
        normalizarCelulasTabela(
            texto
        ).length >= 2
    );
}


function extrairTabelaMarkdown(texto) {
    const linhas =
        String(texto)
            .replace(/\r\n/g, "\n")
            .split("\n");

    for (
        let indice = 0;
        indice < linhas.length - 1;
        indice += 1
    ) {
        const linhaCabecalho =
            linhas[indice];

        const linhaSeparadora =
            linhas[indice + 1];

        if (
            !linhaPareceTabela(
                linhaCabecalho
            )
        ) {
            continue;
        }

        if (
            !ehLinhaSeparadoraTabela(
                linhaSeparadora
            )
        ) {
            continue;
        }

        const cabecalho =
            normalizarCelulasTabela(
                linhaCabecalho
            );

        const linhasDados = [];

        let proximoIndice =
            indice + 2;

        while (
            proximoIndice <
            linhas.length
        ) {
            const linhaAtual =
                linhas[
                    proximoIndice
                ];

            if (
                !linhaPareceTabela(
                    linhaAtual
                )
            ) {
                break;
            }

            const celulas =
                normalizarCelulasTabela(
                    linhaAtual
                );

            if (
                celulas.length !==
                cabecalho.length
            ) {
                break;
            }

            linhasDados.push(
                celulas
            );

            proximoIndice += 1;
        }

        if (
            linhasDados.length === 0
        ) {
            continue;
        }

        return {
            cabecalho,
            linhas: linhasDados,
            textoAntes:
                linhas
                    .slice(
                        0,
                        indice
                    )
                    .join("\n")
                    .trim(),
            textoDepois:
                linhas
                    .slice(
                        proximoIndice
                    )
                    .join("\n")
                    .trim(),
        };
    }

    return null;
}


function valorPareceNumerico(valor) {
    return (
        converterNumeroTexto(
            valor
        ) !== null
    );
}


function criarTabelaVisual(
    cabecalho,
    linhas
) {
    const container =
        document.createElement(
            "div"
        );

    container.className =
        "agora-table-container";

    const table =
        document.createElement(
            "table"
        );

    table.className =
        "agora-table";

    const thead =
        document.createElement(
            "thead"
        );

    const linhaCabecalho =
        document.createElement(
            "tr"
        );

    cabecalho.forEach(
        (titulo, indice) => {
            const th =
                document.createElement(
                    "th"
                );

            th.textContent =
                titulo;

            const colunaNumerica =
                linhas.length > 0 &&
                linhas.every(
                    (linha) =>
                        valorPareceNumerico(
                            linha[
                                indice
                            ]
                        )
                );

            if (colunaNumerica) {
                th.classList.add(
                    "agora-cell-number"
                );
            }

            linhaCabecalho.appendChild(
                th
            );
        }
    );

    thead.appendChild(
        linhaCabecalho
    );

    table.appendChild(
        thead
    );

    const tbody =
        document.createElement(
            "tbody"
        );

    linhas.forEach(
        (linha) => {
            const tr =
                document.createElement(
                    "tr"
                );

            linha.forEach(
                (valor, indice) => {
                    const td =
                        document.createElement(
                            "td"
                        );

                    td.textContent =
                        valor;

                    const colunaNumerica =
                        linhas.every(
                            (linhaTeste) =>
                                valorPareceNumerico(
                                    linhaTeste[
                                        indice
                                    ]
                                )
                        );

                    if (
                        colunaNumerica
                    ) {
                        td.classList.add(
                            "agora-cell-number"
                        );
                    }

                    tr.appendChild(
                        td
                    );
                }
            );

            tbody.appendChild(
                tr
            );
        }
    );

    table.appendChild(
        tbody
    );

    container.appendChild(
        table
    );

    return container;
}


function criarResumoTabela(
    quantidadeLinhas
) {
    const resumo =
        document.createElement(
            "div"
        );

    resumo.className =
        "agora-table-summary";

    resumo.textContent =
        quantidadeLinhas === 1
            ? "1 registro"
            : `${quantidadeLinhas} registros`;

    return resumo;
}


function exibirRespostaComTabela(
    titulo,
    tabela
) {
    answer.replaceChildren();

    answer.appendChild(
        criarTituloResposta(
            titulo
        )
    );

    if (tabela.textoAntes) {
        answer.appendChild(
            criarTextoResposta(
                tabela.textoAntes
            )
        );
    }

    const blocoTabela =
        document.createElement(
            "div"
        );

    blocoTabela.className =
        "agora-table-block";

    blocoTabela.appendChild(
        criarResumoTabela(
            tabela.linhas.length
        )
    );

    blocoTabela.appendChild(
        criarTabelaVisual(
            tabela.cabecalho,
            tabela.linhas
        )
    );

    answer.appendChild(
        blocoTabela
    );

    if (tabela.textoDepois) {
        answer.appendChild(
            criarTextoResposta(
                tabela.textoDepois
            )
        );
    }
}


function exibirConteudoResposta(
    titulo,
    mensagem
) {
    const tabela =
        extrairTabelaMarkdown(
            mensagem
        );

    if (tabela) {
        exibirRespostaComTabela(
            titulo,
            tabela
        );

        return tabela;
    }

    criarMensagemResposta(
        titulo,
        mensagem
    );

    return null;
}


function limparGrafico() {
    if (graficoAtual) {
        graficoAtual.destroy();
        graficoAtual = null;
    }

    chartTitle.textContent =
        "Evolução";

    chartSummary.textContent =
        "";

    esconder(
        chartContainer
    );
}


function colunaEhTemporal(
    titulo
) {
    const texto =
        normalizarTexto(
            titulo
        );

    const termos = [
        "mes",
        "referencia",
        "competencia",
        "periodo",
        "data",
        "ano mes",
        "ano/mes",
    ];

    return termos.some(
        (termo) =>
            texto.includes(
                termo
            )
    );
}


function obterIndiceColunaTemporal(
    tabela
) {
    return tabela.cabecalho.findIndex(
        (titulo) =>
            colunaEhTemporal(
                titulo
            )
    );
}


function obterIndicesColunasNumericas(
    tabela,
    indiceTemporal
) {
    const indices = [];

    tabela.cabecalho.forEach(
        (titulo, indice) => {
            if (
                indice ===
                indiceTemporal
            ) {
                return;
            }

            const valores =
                tabela.linhas.map(
                    (linha) =>
                        converterNumeroTexto(
                            linha[
                                indice
                            ]
                        )
                );

            const validos =
                valores.filter(
                    (valor) =>
                        valor !== null
                );

            if (
                validos.length ===
                tabela.linhas.length
            ) {
                indices.push(
                    indice
                );
            }
        }
    );

    return indices;
}


function tituloPareceMonetario(
    titulo
) {
    const texto =
        normalizarTexto(
            titulo
        );

    const termos = [
        "remuneracao",
        "rendimento",
        "credito",
        "debito",
        "indenizacao",
        "vantagem",
        "gratificacao",
        "subsidio",
        "valor",
        "liquido",
        "salario",
    ];

    return termos.some(
        (termo) =>
            texto.includes(
                termo
            )
    );
}


function tituloParecePercentual(
    titulo
) {
    const texto =
        normalizarTexto(
            titulo
        );

    return (
        texto.includes("%") ||
        texto.includes(
            "percent"
        )
    );
}


function formatarValorGrafico(
    valor,
    tituloSerie
) {
    if (
        valor === null ||
        valor === undefined
    ) {
        return "—";
    }

    if (
        tituloParecePercentual(
            tituloSerie
        )
    ) {
        return (
            Number(valor)
                .toLocaleString(
                    "pt-BR",
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                    }
                )
            + "%"
        );
    }

    if (
        tituloPareceMonetario(
            tituloSerie
        )
    ) {
        return Number(valor)
            .toLocaleString(
                "pt-BR",
                {
                    style: "currency",
                    currency: "BRL",
                }
            );
    }

    return Number(valor)
        .toLocaleString(
            "pt-BR",
            {
                maximumFractionDigits: 2,
            }
        );
}


function criarDatasetsGrafico(
    tabela,
    indicesNumericos
) {
    const cores = [
        {
            borda: "#203a63",
            fundo: "rgba(32, 58, 99, 0.12)",
        },
        {
            borda: "#2f855a",
            fundo: "rgba(47, 133, 90, 0.10)",
        },
        {
            borda: "#b7791f",
            fundo: "rgba(183, 121, 31, 0.10)",
        },
    ];

    return indicesNumericos
        .slice(
            0,
            3
        )
        .map(
            (indice, posicao) => {
                const titulo =
                    tabela.cabecalho[
                        indice
                    ];

                const cor =
                    cores[
                        posicao %
                        cores.length
                    ];

                return {
                    label: titulo,
                    data:
                        tabela.linhas.map(
                            (linha) =>
                                converterNumeroTexto(
                                    linha[
                                        indice
                                    ]
                                )
                        ),
                    borderColor:
                        cor.borda,
                    backgroundColor:
                        cor.fundo,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBorderWidth: 2,
                    tension: 0.32,
                    fill:
                        indicesNumericos.length === 1,
                };
            }
        );
}


function exibirGraficoTemporal(
    tabela
) {
    if (
        typeof Chart ===
        "undefined"
    ) {
        console.warn(
            "Chart.js não está disponível."
        );

        return false;
    }

    const indiceTemporal =
        obterIndiceColunaTemporal(
            tabela
        );

    if (
        indiceTemporal < 0
    ) {
        return false;
    }

    const indicesNumericos =
        obterIndicesColunasNumericas(
            tabela,
            indiceTemporal
        );

    if (
        indicesNumericos.length ===
        0
    ) {
        return false;
    }

    limparGrafico();

    const labels =
        tabela.linhas.map(
            (linha) =>
                linha[
                    indiceTemporal
                ]
        );

    const datasets =
        criarDatasetsGrafico(
            tabela,
            indicesNumericos
        );

    if (!datasets.length) {
        return false;
    }

    const primeiraSerie =
        datasets[0].label;

    chartTitle.textContent =
        datasets.length === 1
            ? `Evolução — ${primeiraSerie}`
            : "Evolução dos indicadores";

    chartSummary.textContent =
        `${labels.length} períodos`;

    const contexto =
        resultChartCanvas.getContext(
            "2d"
        );

    graficoAtual =
        new Chart(
            contexto,
            {
                type: "line",

                data: {
                    labels,
                    datasets,
                },

                options: {
                    responsive: true,

                    maintainAspectRatio:
                        false,

                    interaction: {
                        mode: "index",
                        intersect: false,
                    },

                    plugins: {
                        legend: {
                            display:
                                datasets.length >
                                1,
                            position:
                                "top",
                            align:
                                "end",
                            labels: {
                                usePointStyle:
                                    true,
                                boxWidth: 8,
                                boxHeight: 8,
                                padding: 18,
                            },
                        },

                        tooltip: {
                            callbacks: {
                                label:
                                    (
                                        contextoTooltip
                                    ) => {
                                        const titulo =
                                            contextoTooltip
                                                .dataset
                                                .label;

                                        const valor =
                                            contextoTooltip
                                                .parsed
                                                .y;

                                        return (
                                            `${titulo}: ` +
                                            formatarValorGrafico(
                                                valor,
                                                titulo
                                            )
                                        );
                                    },
                            },
                        },
                    },

                    scales: {
                        x: {
                            grid: {
                                display:
                                    false,
                            },

                            ticks: {
                                color:
                                    "#667085",
                            },
                        },

                        y: {
                            beginAtZero:
                                false,

                            border: {
                                display:
                                    false,
                            },

                            grid: {
                                color:
                                    "rgba(102, 112, 133, 0.10)",
                            },

                            ticks: {
                                color:
                                    "#667085",

                                callback:
                                    (
                                        valor
                                    ) => {
                                        const titulo =
                                            datasets[
                                                0
                                            ].label;

                                        if (
                                            tituloPareceMonetario(
                                                titulo
                                            )
                                        ) {
                                            return Number(
                                                valor
                                            ).toLocaleString(
                                                "pt-BR",
                                                {
                                                    notation:
                                                        "compact",
                                                    maximumFractionDigits:
                                                        1,
                                                }
                                            );
                                        }

                                        return Number(
                                            valor
                                        ).toLocaleString(
                                            "pt-BR",
                                            {
                                                maximumFractionDigits:
                                                    1,
                                            }
                                        );
                                    },
                            },
                        },
                    },
                },
            }
        );

    mostrar(
        chartContainer
    );

    return true;
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
    answer.replaceChildren();
    error.textContent = "";

    technicalStatus.textContent = "—";
    technicalTime.textContent = "—";
    technicalSql.textContent = "—";

    limparGrafico();
    limparDetalhesDeUso();
    limparEstadoResposta();

    esconder(answer);
    esconder(error);
    esconder(technicalDetails);
}


function iniciarCarregamento() {
    limparResposta();

    mostrar(responseSection);
    mostrar(loading);

    submitButton.disabled = true;
    submitButton.textContent =
        "Processando...";
}


function finalizarCarregamento() {
    esconder(loading);

    submitButton.disabled = false;
    submitButton.textContent =
        "Perguntar";
}


function preencherUso(resultado) {
    const usage =
        resultado.usage;

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
        technicalCost.textContent =
            "—";
    }

    const steps =
        usage.steps;

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

        technicalUsage.textContent =
            "—";

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


function preencherDetalhesTecnicos(
    resultado
) {
    technicalStatus.textContent =
        resultado.status || "—";

    if (
        resultado.execution_time_ms !== null &&
        resultado.execution_time_ms !== undefined
    ) {
        technicalTime.textContent =
            `${resultado.execution_time_ms} ms`;
    } else {
        technicalTime.textContent =
            "—";
    }

    technicalSql.textContent =
        resultado.generated_sql ||
        "—";

    preencherUso(
        resultado
    );

    mostrar(
        technicalDetails
    );
}


function exibirResposta(resultado) {
    preencherDetalhesTecnicos(
        resultado
    );

    aplicarEstadoResposta(
        resultado.status
    );

    const mensagem =
        resultado.answer ||
        "O Ágora não retornou uma resposta.";

    if (
        resultado.status ===
        "NOT_ANSWERABLE"
    ) {
        criarMensagemResposta(
            "Informação não disponível nos dados",
            mensagem
        );

        mostrar(answer);

        return;
    }

    if (
        resultado.status ===
        "NEEDS_CLARIFICATION"
    ) {
        criarMensagemResposta(
            "Preciso de mais detalhes",
            mensagem
        );

        mostrar(answer);

        return;
    }

    if (
        resultado.status ===
        "NO_DATA"
    ) {
        criarMensagemResposta(
            "Nenhum resultado encontrado",
            mensagem
        );

        mostrar(answer);

        return;
    }

    const tabela =
        exibirConteudoResposta(
            "Resposta",
            mensagem
        );

    mostrar(answer);

    if (tabela) {
        exibirGraficoTemporal(
            tabela
        );
    }
}


function exibirErro(
    mensagem,
    resultado = null
) {
    limparGrafico();

    aplicarEstadoResposta(
        resultado?.status ||
        "ERROR"
    );

    error.textContent =
        mensagem;

    mostrar(error);
}


function obterElementoTextoStatus() {
    let statusText =
        systemStatus.querySelector(
            ".status-text"
        );

    if (!statusText) {
        statusText =
            document.createElement(
                "span"
            );

        statusText.className =
            "status-text";

        const textosSoltos =
            Array.from(
                systemStatus.childNodes
            ).filter(
                (node) =>
                    node.nodeType ===
                    Node.TEXT_NODE
            );

        textosSoltos.forEach(
            (node) =>
                node.remove()
        );

        systemStatus.appendChild(
            statusText
        );
    }

    return statusText;
}


function atualizarStatusSistema(
    estado,
    texto
) {
    const statusText =
        obterElementoTextoStatus();

    systemStatus.dataset.state =
        estado;

    statusText.textContent =
        texto;

    systemStatusDot.classList.remove(
        "status-dot-available",
        "status-dot-degraded",
        "status-dot-unavailable",
        "status-dot-checking"
    );

    if (
        estado ===
        "available"
    ) {
        systemStatusDot.classList.add(
            "status-dot-available"
        );

        return;
    }

    if (
        estado ===
        "degraded"
    ) {
        systemStatusDot.classList.add(
            "status-dot-degraded"
        );

        return;
    }

    if (
        estado ===
        "checking"
    ) {
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
        const response =
            await fetch(
                API_HEALTH_URL,
                {
                    method: "GET",
                    cache: "no-store",
                }
            );

        let resultado;

        try {
            resultado =
                await response.json();
        } catch {
            atualizarStatusSistema(
                "unavailable",
                "Sistema indisponível"
            );

            return;
        }

        if (
            response.ok &&
            resultado.status ===
                "ok" &&
            resultado.database ===
                "ok"
        ) {
            atualizarStatusSistema(
                "available",
                "Sistema disponível"
            );

            return;
        }

        if (
            resultado.status ===
                "degraded" ||
            resultado.database ===
                "error"
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


async function enviarPergunta(
    pergunta
) {
    iniciarCarregamento();

    try {
        const response =
            await fetch(
                API_ASK_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body:
                        JSON.stringify({
                            question:
                                pergunta,
                        }),
                }
            );

        let resultado;

        try {
            resultado =
                await response.json();
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
                "Não foi possível processar a pergunta.",
                resultado
            );

            return;
        }

        exibirResposta(
            resultado
        );

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

        await enviarPergunta(
            pergunta
        );
    }
);


questionInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key ===
                "Enter" &&
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
