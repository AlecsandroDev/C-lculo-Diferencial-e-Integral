# 📊 CalcTool Pro - Calculadora Visual de Cálculo

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-red?style=for-the-badge&logo=flask)
![SymPy](https://img.shields.io/badge/SymPy-Cálculo_Simbólico-green?style=for-the-badge)
![ECharts](https://img.shields.io/badge/Apache_ECharts-Visualização-orange?style=for-the-badge&logo=apache-echarts)

Uma aplicação web educacional desenvolvida para resolver e visualizar conceitos de **Cálculo Diferencial e Integral** de forma interativa. O projeto foca na precisão matemática visual (ex: descontinuidades) e na explicação passo a passo.

## 🚀 Funcionalidades Principais

O CalcTool Pro é dividido em 4 módulos principais, cada um com visualizações específicas:

### 1. Limites e Continuidade
* Cálculo de limites laterais ($\lim_{x \to p^-}$ e $\lim_{x \to p^+}$) e global.
* **Análise Visual de Continuidade:** O gráfico identifica automaticamente se o ponto deve ser representado com uma **Bolinha Fechada** (contínua) ou **Bolinha Aberta** (descontinuidade/indefinição).

### 2. Derivadas
* Cálculo simbólico da derivada $f'(x)$.
* Plotagem do gráfico da função derivada para análise de taxas de variação.
* Resolução passo a passo mostrando as regras de derivação aplicadas.

### 3. Pontos Críticos
* Identificação automática de máximos e mínimos locais.
* Resolução da equação $f'(x) = 0$.
* Marcadores visuais (`scatter`) nos pontos de interesse sobre o gráfico.

### 4. Integrais e Área (Soma de Riemann)
* **Integral Indefinida:** Exibição da primitiva $F(x) + C$.
* **Soma de Riemann Interativa:** Slider dinâmico para alterar o número de retângulos ($n$) em tempo real e visualizar a convergência da área.
* **Área Líquida vs. Geométrica:** Diferenciação visual e numérica entre:
    * *Integral Definida (Líquida):* Considera áreas abaixo do eixo X como negativas.
    * *Área Geométrica (Absoluta):* Soma todas as áreas como positivas ($\int |f(x)| dx$).

## 🛠️ Tecnologias Utilizadas

* **Backend:**
    * `Python 3`: Linguagem principal.
    * `Flask`: Framework web para roteamento e renderização de templates.
    * `SymPy`: Biblioteca core para manipulação simbólica e resolução algébrica.
    * `NumPy`: Geração de arrays numéricos para plotagem de alta performance.
* **Frontend:**
    * `HTML5` & `Jinja2`: Estrutura e templating dinâmico.
    * `Bootstrap 5`: Layout responsivo e componentes de UI.
    * `Apache ECharts`: Biblioteca JavaScript para gráficos interativos (Zoom, Pan, Tooltips).
    * `MathJax`: Renderização de equações LaTeX no navegador.

## 📦 Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/calctool-pro.git](https://github.com/seu-usuario/calctool-pro.git)
    cd calctool-pro
    ```

2.  **Crie um ambiente virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```

5.  **Acesse no navegador:**
    Abra `http://127.0.0.1:5000`

## 🧠 Desafios Técnicos Superados

* **Renderização Híbrida:** Integração do cálculo pesado no Python (Backend) com renderização leve no cliente (ECharts/Frontend) via JSON.
* **Tratamento de Singularidades:** Algoritmos para evitar que divisões por zero (ex: $1/x$) quebrem a geração do gráfico, permitindo visualização de assíntotas.
* **Interatividade Matemática:** Implementação de lógica para diferenciar visualmente áreas positivas (azul) e negativas (vermelho) na integração numérica.

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar e modificar para fins educacionais.

---