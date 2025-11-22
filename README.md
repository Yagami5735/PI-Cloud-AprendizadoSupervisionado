# Sistema de Processamento e Predição via Regressão Linear

**Projeto Final — Disciplina: Computação em Nuvem** **Pontifícia Universidade Católica de Campinas (PUC-Campinas)**

## Equipe
Edson Eduardo Ferreira — 23908965 — [edson.ef@puccampinas.edu.br](mailto:edson.ef@puccampinas.edu.br)

Gabriel Batista Chiezo — 23028678 — [gabriel.bc@puccampinas.edu.br](mailto:gabriel.bc@puccampinas.edu.br)

Yan Yoshida Luz — 23911118 — [yan.yl@puccampinas.edu.br](mailto:yan.yl@puccampinas.edu.br)

## Descrição Geral
A aplicação desenvolvida consiste em uma plataforma web de treinamento, avaliação e predição de modelos de Machine Learning Linear Regressor diretamente na nuvem, permitindo que qualquer usuário envie seus próprios datasets e realize todo o fluxo de análise sem necessidade de ambientes locais, bibliotecas instaladas ou notebooks de código.

O sistema nasce do problema central: a falta de ferramentas simples e acessíveis que democratizem o uso de IA, facilitando o treinamento e a validação de modelos sem conhecimento avançado de infraestrutura ou configuração. Para isso, a solução automatiza etapas como pré-processamento, divisão de dados, treinamento (via Regressão Linear), validação cruzada, avaliação de métricas e geração de gráficos.

Os principais objetivos do sistema são:

- Permitir o upload dinâmico de datasets (.csv) enviados pelo usuário.
- Automatizar tratamento, transformação e normalização dos dados.
- Realizar o treinamento de modelos supervisionados, com foco inicial em Regressão Linear.
- Exibir métricas de desempenho (R², RMSE) e gráficos gerados automaticamente.
- Possibilitar avaliação com novos dados e predição final.
- Integrar todo o fluxo em um ambiente 100% em nuvem, utilizando Docker, FastAPI, Azure Blob Storage e CI/CD.

O sistema se posiciona como uma ferramenta educacional e prática que integra conceitos de Computação em Nuvem, Aprendizado Supervisionado, Transformação de Dados, Séries Temporais e DevOps, oferecendo uma solução completa e modular para experimentação de modelos de Machine Learning.

## Dataset

O sistema é agnóstico em relação aos dados.
* **Fonte:** Arquivos `.csv` enviados dinamicamente pelo usuário (não fixos).
* **Requisitos:** O arquivo deve conter colunas numéricas para as variáveis independentes e uma coluna alvo. O sistema trata a separação automática.

## Arquitetura da Solução
<img width="877" height="423" alt="image" src="https://github.com/user-attachments/assets/adfcb941-3f12-4616-b998-73dc3a6bc214" />

**Componentes Principais:**
1.  **Cliente:** Interage via aplicação web.
2.  **Aplicação Web:** Interface frontend hospedada.
3.  **Blob Storage:** Armazena os CSVs de entrada e as imagens (plots) geradas.
4.  **Backend:** API Python/FastAPI rodando em container.
5.  **Docker:** Empacotamento da aplicação.
6.  **GitHub Actions:** Pipeline de CI/CD para deploy automático.

## Demonstração
<img width="796" height="3553" alt="pi-backend-ml azurewebsites net_" src="https://github.com/user-attachments/assets/d54b7f21-7115-4d1e-95ba-2eb610ab8e15" />

## Referências

* **FastAPI Documentation:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
* **Scikit-Learn (Linear Regression):** [https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
* **Azure Blob Storage Docs:** [https://learn.microsoft.com/en-us/azure/storage/blobs/](https://learn.microsoft.com/en-us/azure/storage/blobs/)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **GitHub Actions for Azure:** [https://github.com/Azure/actions](https://github.com/Azure/actions)
