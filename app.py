from flask import Flask, render_template, request
import json
import numpy as np
import sympy as sp
from sympy import (
    symbols, sympify, diff, integrate, limit, solve, latex,
    lambdify, S, simplify, Abs
)

app = Flask(__name__)


# ================================================================
# FUNÇÃO SEGURA PARA CONVERTER VALORES SYMPY → FLOAT
# ================================================================
def to_float_safe(value):
    """
    Converte valores SymPy para float somente quando seguro.
    Evita erros como: 'Zero' object has no attribute 'is_nan'
    Retorna None quando:
        - é infinito
        - é NaN
        - é simbólico
        - é complexo
    """
    try:
        val = sp.N(value)

        if hasattr(val, "is_infinite") and val.is_infinite:
            return None

        if hasattr(val, "is_nan") and val.is_nan:
            return None

        if hasattr(val, "is_real") and not val.is_real:
            return None

        return float(val)

    except Exception:
        return None


# ================================================================
# GERAÇÃO DE PASSO A PASSO (LATEX)
# ================================================================
def gerar_step_by_step(operacao, expr, params, x):
    steps = []

    # ---------------------- LIMITE ----------------------
    if operacao == 'limite':
        ponto = float(params.get('ponto', 0))
        steps.append(f"\\textbf{{Passo 1: Identificar o ponto}}")
        steps.append(f"\\text{{Analisando }} x = {ponto}")

        # limites laterais
        try:
            l_esq = limit(expr, x, ponto, dir='-')
            steps.append(f"\\text{{Limite pela esquerda: }} {latex(l_esq)}")
        except:
            l_esq = None
            steps.append("\\text{Erro ao calcular limite pela esquerda}")

        try:
            l_dir = limit(expr, x, ponto, dir='+')
            steps.append(f"\\text{{Limite pela direita: }} {latex(l_dir)}")
        except:
            l_dir = None
            steps.append("\\text{Erro ao calcular limite pela direita}")

        # limite global
        try:
            l_glob = limit(expr, x, ponto)
        except:
            l_glob = None

        steps.append("\\textbf{Passo 3: Verificar limite}")

        if l_esq is not None and l_dir is not None:
            if to_float_safe(l_esq) is not None and to_float_safe(l_dir) is not None:
                if abs(to_float_safe(l_esq) - to_float_safe(l_dir)) < 1e-6:
                    steps.append("\\text{Os limites laterais são iguais → limite existe.}")
                    steps.append(f"\\lim_{{x\\to{ponto}}} f(x) = {latex(l_glob)}")
                else:
                    steps.append("\\text{Limites diferentes → limite NÃO existe}")
            else:
                steps.append("\\text{Limite infinito ou indefinido}")
        else:
            steps.append("\\text{Não foi possível calcular os limites laterais}")

        # continuidade
        steps.append("\\textbf{Passo 4: Verificar continuidade}")
        try:
            f_val = expr.subs(x, ponto)
            f_val_safe = to_float_safe(f_val)
            l_glob_safe = to_float_safe(l_glob)

            if f_val_safe is not None and l_glob_safe is not None:
                if abs(f_val_safe - l_glob_safe) < 1e-6:
                    steps.append("\\text{A função é CONTÍNUA no ponto}")
                else:
                    steps.append("\\text{DESCONTINUIDADE removível}")
            else:
                steps.append("\\text{DESCONTINUIDADE (função indefinida)}")

        except:
            steps.append("\\text{Erro ao testar continuidade}")

    # ---------------------- DERIVADA ----------------------
    elif operacao == 'derivada':
        derivada = diff(expr, x)
        derivada_simp = simplify(derivada)

        steps.append("\\textbf{Passo 1: Função Original}")
        steps.append(f"f(x) = {latex(expr)}")

        steps.append("\\textbf{Passo 2: Derivada}")
        steps.append(f"f'(x) = {latex(derivada_simp)}")

        p = float(params.get('ponto_tangente', 0))
        steps.append(f"\\textbf{{Passo 3: Reta Tangente em x = {p}}}")

        try:
            y0 = float(expr.subs(x, p))
            m = float(derivada_simp.subs(x, p))
            steps.append(f"P({p}, {y0:.4f}),\\; m = {m:.4f}")
        except:
            steps.append("\\text{Erro ao calcular reta tangente}")

    # ---------------------- PONTOS CRÍTICOS ----------------------
    elif operacao == 'pontos_criticos':
        derivada = diff(expr, x)
        derivada2 = diff(derivada, x)

        steps.append("\\textbf{Derivada}")
        steps.append(f"f'(x) = {latex(derivada)}")

        try:
            solucoes = solve(derivada, x)
        except:
            solucoes = []

        if solucoes:
            steps.append("\\textbf{Pontos Críticos:}")
            for s in solucoes:
                if s.is_real:
                    y_val = expr.subs(x, s)
                    steps.append(f"x = {latex(s)},\\; f(x) = {latex(y_val)}")
        else:
            steps.append("\\text{Nenhum ponto crítico encontrado}")

    # ---------------------- INTEGRAL ----------------------
    elif operacao == 'integral':
        a = float(params.get('int_a', 0))
        b = float(params.get('int_b', 5))

        prim = integrate(expr, x)
        steps.append("F(x) = " + latex(prim))

        val = prim.subs(x, b) - prim.subs(x, a)
        steps.append(f"\\int_{{{a}}}^{{{b}}} f(x) dx = {latex(val)}")

    return steps


# ================================================================
# FUNÇÃO PRINCIPAL DE CÁLCULO
# ================================================================
def calcular_matematica(funcao_str, operacao, params):
    x = symbols('x')
    erro = None
    resultado_latex = ""
    dados_grafico = {}
    steps = []

    try:
        expr = sympify(funcao_str.replace("^", "**"))
        steps = gerar_step_by_step(operacao, expr, params, x)

        expr = simplify(expr)

        # Para gerar y seguros
        def gerar_pontos(expr, xs):
            f_np = lambdify(x, expr, 'numpy')
            out = []

            last_val = None

            for xv in xs:
                try:
                    val = f_np(xv)

                    # quebra em inf e nan
                    if val is None or not np.isfinite(val):
                        out.append(None)
                        last_val = None
                        continue

                    # se o salto entre dois valores consecutivos é MUITO grande,
                    # quebra o gráfico (não deixa ligar os ramos)
                    if last_val is not None and abs(val - last_val) > 1e6:
                        out.append(None)
                        last_val = val
                        continue

                    out.append(float(val))
                    last_val = val

                except:
                    out.append(None)
                    last_val = None

            return out

        def gerar_pontos_dual(expr, xs):
            f_np = lambdify(x, expr, 'numpy')
            esquerda = []
            direita = []

            for xv in xs:
                try:
                    val = f_np(xv)

                    if val is None or not np.isfinite(val) or abs(val) > 1e6:
                        # não adiciona nada
                        esquerda.append(None)
                        direita.append(None)
                        continue

                    if xv < 0:
                        esquerda.append(float(val))
                        direita.append(None)
                    else:
                        esquerda.append(None)
                        direita.append(float(val))

                except:
                    esquerda.append(None)
                    direita.append(None)

            return esquerda, direita
        # ------------------------------------------------------------
        # LIMITE
        # ------------------------------------------------------------
        if operacao == "limite":
            ponto = float(params.get("ponto", 0))

            # simplificar antes é ESSENCIAL p/ limites com divisão
            expr_simp = simplify(expr)

            # cálculos laterais
            try:
                l_esq = limit(expr_simp, x, ponto, dir='-')
            except:
                l_esq = None

            try:
                l_dir = limit(expr_simp, x, ponto, dir='+')
            except:
                l_dir = None

            # limite principal (bilateral)
            try:
                l_glob = limit(expr_simp, x, ponto)
            except:
                l_glob = None

            # tentar fallback quando 0/0
            if (l_glob is None or str(l_glob) == "nan") and l_esq is not None and l_dir is not None:
                try:
                    l_glob = limit(expr_simp, x, ponto, dir='+')
                except:
                    pass

            # converter para float quando possível
            y_limite = to_float_safe(l_glob)

            # valor real da função no ponto
            try:
                f_p = to_float_safe(expr_simp.subs(x, ponto))
            except:
                f_p = None

            # tipo de ponto (fechado/aberto)
            if y_limite is not None and f_p is not None:
                tipo = "fechada" if abs(y_limite - f_p) < 1e-6 else "aberta"
            else:
                tipo = "aberta"

            # latex final
            resultado_latex = (
                f"\\lim_{{x\\to{ponto}^-}} = {latex(l_esq)}\\\\"
                f"\\lim_{{x\\to{ponto}^+}} = {latex(l_dir)}\\\\"
            )
            if y_limite is not None:
                resultado_latex += f"\\lim_{{x\\to{ponto}}} = {latex(l_glob)}"
            else:
                resultado_latex += "\\text{Limite não existe}"

            # gráfico
            xs = np.linspace(ponto - 5, ponto + 5, 500)
            ys_esq, ys_dir = gerar_pontos_dual(expr, xs)

            dados_grafico = {
                "tipo": "limite",
                "eixo_x": xs.tolist(),
                "y_esquerda": ys_esq,
                "y_direita": ys_dir,
                "ponto_destaque": {
                    "x": ponto,
                    "y": y_limite,
                    "estilo": tipo
                }
            }


        # ------------------------------------------------------------
        # DERIVADA
        # ------------------------------------------------------------
        elif operacao == "derivada":
            deriv = diff(expr, x)
            deriv_simp = simplify(deriv)
            p = float(params.get("ponto_tangente", 0) or 0)


            try:
                y0 = float(expr.subs(x, p))
                m = float(deriv_simp.subs(x, p))
            except:
                y0 = 0
                m = 0

            resultado_latex = (
                f"f'(x) = {latex(deriv_simp)}\\\\"
                f"P({p},{y0:.4f}), m={m:.4f}"
            )

            xs = np.linspace(-10, 10, 500)
            ys = gerar_pontos(expr, xs)

            dados_grafico = {
                "tipo": "derivada",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "ponto_tangente": {
                    "x": p,
                    "y": y0,
                    "inclinacao": m
                },
                "derivada_expr": str(deriv_simp)
            }

        # ------------------------------------------------------------
        # PONTOS CRÍTICOS
        # ------------------------------------------------------------
        elif operacao == "pontos_criticos":
            deriv = diff(expr, x)
            deriv2 = diff(deriv, x)

            try:
                roots = solve(deriv, x)
            except:
                roots = []

            pontos = []
            for r in roots:
                if not r.is_real:
                    continue

                # Coordenada Y
                y = expr.subs(x, r)
                if not (hasattr(y, "is_finite") and y.is_finite):
                    continue

                # Segunda derivada
                d2 = deriv2.subs(x, r)

                # Tipo do ponto
                if d2.is_real:
                    if d2 > 0:
                        tipo = "Mínimo Local"
                    elif d2 < 0:
                        tipo = "Máximo Local"
                    else:
                        tipo = "Ponto de Inflexão"
                else:
                    tipo = "Crítico (indefinido)"

                pontos.append({
                    "x": float(r),
                    "y": float(y),
                    "tipo": tipo
                })

            xs = np.linspace(-10, 10, 500)
            ys = gerar_pontos(expr, xs)

            dados_grafico = {
                "tipo": "pontos_criticos",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "pontos": pontos
            }

            resultado_latex = "\\text{Pontos críticos encontrados.}"

        # ------------------------------------------------------------
        # INTEGRAL
        # ------------------------------------------------------------
        elif operacao == "integral":
            a = float(params.get("int_a", 0))
            b = float(params.get("int_b", 5))

            prim = integrate(expr, x)
            liquida = float(integrate(expr, (x, a, b)).evalf())
            area = float(integrate(Abs(expr), (x, a, b)).evalf())

            resultado_latex = (
                f"F(x) = {latex(prim)} + C\\\\"
                f"\\int_{{{a}}}^{{{b}}} = {liquida:.6f}\\\\"
                f"\\text{{Área geométrica}} = {area:.6f}"
            )

            xs = np.linspace(a - 1, b + 1, 500)
            ys = gerar_pontos(expr, xs)

            dados_grafico = {
                "tipo": "integral",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "intervalo": [a, b],
                "integral_liquida": liquida,
                "area_geometrica": area
            }

    except Exception as e:
        erro = str(e)
        resultado_latex = f"\\text{{Erro: {erro}}}"

    return resultado_latex, dados_grafico, steps, erro


# ================================================================
# ROTA PRINCIPAL
# ================================================================
@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    dados_grafico = None
    steps = []
    aba_ativa = "limite"
    funcao_atual = ""
    erro = None

    params = {}

    if request.method == "POST":
        funcao_atual = request.form.get("funcao", "")
        aba_ativa = request.form.get("aba_ativa", "limite")

        params["ponto"] = request.form.get("ponto_limite", 0)
        params["ponto_tangente"] = request.form.get("ponto_tangente", 0)
        params["int_a"] = request.form.get("int_a", 0)
        params["int_b"] = request.form.get("int_b", 5)

        if funcao_atual:
            resultado, dados_grafico, steps, erro = calcular_matematica(funcao_atual, aba_ativa, params)

    return render_template(
        'index.html',
        resultado=resultado,
        dados_grafico=dados_grafico if dados_grafico else None,
        steps=steps,
        funcao=funcao_atual,
        aba_ativa=aba_ativa,
        params=params,
        erro=erro
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
