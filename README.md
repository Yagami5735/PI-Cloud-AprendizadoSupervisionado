# Sistema de Processamento e Predição via Regressão Linear

**Projeto Final — Disciplina: Computação em Nuvem** **Pontifícia Universidade Católica de Campinas (PUC-Campinas)**

## 👥 Equipe

| Nome | RA | E-mail |
|------|----|--------|
| **Edson Eduardo Ferreira** | 23908965 | [edson.ef@puccampinas.edu.br](mailto:edson.ef@puccampinas.edu.br) |
| **Gabriel Batista Chiezo** | 23028678 | [gabriel.bc@puccampinas.edu.br](mailto:gabriel.bc@puccampinas.edu.br) |
| **Yan Yoshida Luz** | 23911118 | [yan.yl@puccampinas.edu.br](mailto:yan.yl@puccampinas.edu.br) |

---

## 📝 Descrição Geral

A aplicação foi desenvolvida de forma modular, separando frontend, backend e lógica de aprendizado de máquina. Seu objetivo é democratizar o acesso a treinos de modelos simples sem a necessidade de codificação local.

* **Backend (FastAPI):** O núcleo lógico gerencia o envio de arquivos CSV, identifica o campo alvo (*target*), separa as variáveis independentes ($X$) e dependente ($y$), e processa/transforma os dados. Ele executa o treinamento de um modelo de **Regressão Linear**. Após o treino, o sistema gera um gráfico com os resultados de validação cruzada e calcula métricas estatísticas essenciais, como **RMSE** (Raiz do Erro Quadrático Médio) e **R²** (Coeficiente de Determinação). O sistema também suporta a avaliação de desempenho com novos dados e a realização de predições futuras.
    
* **Frontend (HTML/CSS/JS):** A interface permite ao usuário enviar os arquivos, visualizar o modelo treinado e resetar o ambiente. O JavaScript realiza as requisições assíncronas ao backend e atualiza a interface de forma dinâmica e responsiva.

* **Infraestrutura e DevOps:** O uso do **Docker** garante portabilidade e isolamento do ambiente, permitindo que toda a aplicação rode de forma padronizada. O **CORS** foi configurado para permitir comunicação segura entre cliente e servidor. No ambiente em nuvem (via **Azure Blob Storage**), as credenciais e chaves de acesso são armazenadas de forma segura em variáveis de ambiente, e os arquivos recebidos são criptografados.

---

## 📊 Dataset

O sistema é agnóstico em relação aos dados.
* **Fonte:** Arquivos `.csv` enviados dinamicamente pelo usuário (não fixos).
* **Requisitos:** O arquivo deve conter colunas numéricas para as variáveis independentes e uma coluna alvo. O sistema trata a separação automática.

---

## 🏗️ Arquitetura da Solução

A solução utiliza uma arquitetura baseada em microsserviços e eventos, hospedada na nuvem Microsoft Azure.

![Diagrama da Arquitetura](arquitetura.png)
*(Certifique-se de que a imagem do diagrama esteja na pasta raiz com este nome ou ajuste o caminho)*

**Componentes Principais:**
1.  **Cliente:** Interage via navegador.
2.  **Aplicação Web:** Interface frontend hospedada (ex: Azure Static Web Apps).
3.  **Blob Storage:** Armazena os CSVs de entrada e as imagens (plots) geradas.
4.  **Backend:** API Python/FastAPI rodando em container.
5.  **Docker:** Empacotamento da aplicação.
6.  **GitHub Actions:** Pipeline de CI/CD para deploy automático.

---

## 💻 Demonstração

### Dashboard e Gráficos Gerados
![Tela de Upload](path/to/print_upload.png)
*Tela inicial de upload de arquivos*

![Gráfico de Regressão](path/to/print_grafico.png)
*Resultado do modelo de Regressão Linear (Real vs. Predito)*

### Vídeo de Demonstração
Confira o funcionamento completo da aplicação no link abaixo:
[▶️ Assistir Vídeo de Demonstração](https://youtube.com/link_do_seu_video)

---

## 📚 Referências

* **FastAPI Documentation:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
* **Scikit-Learn (Linear Regression):** [https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
* **Azure Blob Storage Docs:** [https://learn.microsoft.com/en-us/azure/storage/blobs/](https://learn.microsoft.com/en-us/azure/storage/blobs/)
* **Docker Documentation:** [https://docs.docker.com/](https://docs.docker.com/)
* **GitHub Actions for Azure:** [https://github.com/Azure/actions](https://github.com/Azure/actions)