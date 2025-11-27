from flask import Flask, render_template, request
import numpy as np
import sympy as sp
from sympy import (
    symbols, sympify, diff, integrate, limit, solve, latex,
    lambdify, simplify, Abs
)

app = Flask(__name__)


# -------------------------
# Helpers
# -------------------------
def to_float_safe(value):
    try:
        v = sp.N(value)
        if hasattr(v, "is_infinite") and v.is_infinite:
            return None
        if hasattr(v, "is_nan") and v.is_nan:
            return None
        if hasattr(v, "is_real") and not v.is_real:
            return None
        return float(v)
    except Exception:
        return None


def find_singularities(expr, x):
    """
    Retorna lista de singularidades reais (zeros do denominador) para expr.
    """
    try:
        frac = sp.together(expr)
        denom = sp.denom(frac)
        if denom == 1:
            return []
        sols = sp.solve(sp.simplify(denom), x)
        reais = []
        for s in sols:
            try:
                s_eval = sp.N(s)
                if s_eval.is_real:
                    reais.append(float(s_eval))
            except:
                continue
        return sorted(set(reais))
    except Exception:
        return []


def gerar_pontos_with_breaks(expr, xs, x, breaks=None):
    """
    Gera lista de y (float ou None) para xs.
    breaks: lista de x onde há singularidade -> gera None próximo desses pontos.
    """
    f_np = lambdify(x, expr, 'numpy')
    out = []
    tol = (xs[1] - xs[0]) / 2 if len(xs) > 1 else 1e-6

    for xv in xs:
        # próximo de singularidade?
        if breaks:
            near = any(abs(xv - bp) <= tol for bp in breaks)
            if near:
                out.append(None)
                continue

        try:
            val = f_np(xv)

            # arrays -> pegar escalar
            if isinstance(val, np.ndarray):
                try:
                    val = val.item()
                except:
                    val = val[0]

            # complex / nan / inf -> None
            if isinstance(val, complex) or not np.isfinite(val):
                out.append(None)
                continue

            out.append(float(val))
        except Exception:
            out.append(None)

    return out


def gerar_pontos_dual_auto(expr, xs, x):
    """
    Retorna (ys_esq, ys_dir). Detecta singularidades e separa ramos pelo primeiro breakpoint.
    """
    breaks = find_singularities(expr, x)
    if not breaks:
        ys = gerar_pontos_with_breaks(expr, xs, x, breaks=[])
        return [None if v is None else v for v in ys], ys

    bp = breaks[0]
    ys_esq = []
    ys_dir = []
    tol = (xs[1] - xs[0]) / 2 if len(xs) > 1 else 1e-6
    f_np = lambdify(x, expr, 'numpy')

    for xv in xs:
        if abs(xv - bp) <= tol:
            ys_esq.append(None)
            ys_dir.append(None)
            continue
        try:
            val = f_np(xv)
            if isinstance(val, np.ndarray):
                try:
                    val = val.item()
                except:
                    val = val[0]
            if isinstance(val, complex) or not np.isfinite(val):
                ys_esq.append(None); ys_dir.append(None); continue
            if xv < bp:
                ys_esq.append(float(val)); ys_dir.append(None)
            else:
                ys_esq.append(None); ys_dir.append(float(val))
        except:
            ys_esq.append(None); ys_dir.append(None)

    return ys_esq, ys_dir


# -------------------------
# Step-by-step (latex)
# -------------------------
def gerar_step_by_step(operacao, expr, params, x):
    steps = []

    if operacao == 'limite':
        ponto = float(params.get('ponto', 0))
        steps.append("\\textbf{Passo 1: Identificar o ponto}")
        steps.append(f"\\text{{Analisando }} x = {ponto}")

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

        try:
            l_glob = limit(expr, x, ponto)
            steps.append(f"\\text{{Limite bilateral (quando aplicável): }} {latex(l_glob)}")
        except:
            l_glob = None

    elif operacao == 'derivada':
        deriv = diff(expr, x)
        deriv_simp = simplify(deriv)
        steps.append("\\textbf{Passo 1: Função}")
        steps.append(f"f(x) = {latex(expr)}")
        steps.append("\\textbf{Passo 2: Derivada}")
        steps.append(f"f'(x) = {latex(deriv_simp)}")
        p = float(params.get('ponto_tangente', 0))
        steps.append(f"\\textbf{{Passo 3: Reta tangente em x = {p}}}")

    elif operacao == 'pontos_criticos':
        deriv = diff(expr, x)
        deriv2 = diff(deriv, x)
        steps.append("\\textbf{Derivada}")
        steps.append(f"f'(x) = {latex(deriv)}")

        try:
            sols = solve(deriv, x)
        except:
            sols = []
        if sols:
            steps.append("\\textbf{Pontos críticos}")
            for s in sols:
                try:
                    if s.is_real:
                        steps.append(f"x = {latex(s)}, f(x) = {latex(expr.subs(x, s))}")
                except:
                    continue
        else:
            steps.append("\\text{Nenhum ponto crítico encontrado}")

    elif operacao == 'integral':
        a = float(params.get('int_a', 0))
        b = float(params.get('int_b', 5))
        prim = integrate(expr, x)
        steps.append("F(x) = " + latex(prim))
        try:
            val = prim.subs(x, b) - prim.subs(x, a)
            steps.append(f"\\int_{{{a}}}^{{{b}}} f(x) dx = {latex(val)}")
        except:
            steps.append("\\text{Não foi possível calcular a integral}")

    return steps


# -------------------------
# Core: cálculo e dados pro gráfico
# -------------------------
def calcular_matematica(funcao_str, operacao, params):
    x = symbols('x')
    erro = None
    resultado_latex = ""
    dados_grafico = {}
    steps = []

    try:
        # converte ^ => ** e cria expressão SymPy
        expr = sympify(funcao_str.replace("^", "**"))
        steps = gerar_step_by_step(operacao, expr, params, x)

        # para cálculos numéricos vamos usar expr_simplified onde fizer sentido,
        # mas evitamos simplificar demais que possa causar perda da forma original
        expr_simpl = simplify(expr)

        # LIMITE (usa série dual)
        if operacao == "limite":
            ponto = float(params.get("ponto", 0))
            try:
                l_esq = limit(expr_simpl, x, ponto, dir='-')
            except:
                l_esq = None
            try:
                l_dir = limit(expr_simpl, x, ponto, dir='+')
            except:
                l_dir = None
            try:
                l_glob = limit(expr_simpl, x, ponto)
            except:
                l_glob = None

            y_limite = to_float_safe(l_glob)

            xs = np.linspace(ponto - 5, ponto + 5, 800)
            ys_esq, ys_dir = gerar_pontos_dual_auto(expr_simpl, xs, x)

            dados_grafico = {
                "tipo": "limite",
                "eixo_x": xs.tolist(),
                "y_esquerda": ys_esq,
                "y_direita": ys_dir,
                "ponto_destaque": {"x": ponto, "y": y_limite}
            }

            resultado_latex = f"\\lim_{{x\\to{ponto}}} = {latex(l_glob) if l_glob is not None else 'Indeterminado'}"

        # DERIVADA
        elif operacao == "derivada":
            deriv = diff(expr_simpl, x)
            p = float(params.get("ponto_tangente", 0) or 0)
            y0 = to_float_safe(expr_simpl.subs(x, p))
            m = to_float_safe(deriv.subs(x, p))

            xs = np.linspace(-10, 10, 800)
            # detecta singularidades e gera com breaks (não dual)
            breaks = find_singularities(expr_simpl, x)
            ys = gerar_pontos_with_breaks(expr_simpl, xs, x, breaks=breaks if breaks else None)

            dados_grafico = {
                "tipo": "derivada",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "ponto_tangente": {"x": p, "y": y0, "inclinacao": m},
                "derivada_expr": latex(deriv)
            }

            resultado_latex = f"f'(x) = {latex(deriv)}"

        # PONTOS_CRÍTICOS
        elif operacao == "pontos_criticos":
            deriv = diff(expr_simpl, x)
            deriv2 = diff(deriv, x)
            try:
                roots = solve(deriv, x)
            except:
                roots = []

            pontos = []
            for r in roots:
                try:
                    if r.is_real:
                        yval = to_float_safe(expr_simpl.subs(x, r))
                        if yval is None:
                            continue
                        d2 = deriv2.subs(x, r)
                        tipo = "Inflexão"
                        try:
                            if d2.is_real:
                                if d2 > 0:
                                    tipo = "Mínimo"
                                elif d2 < 0:
                                    tipo = "Máximo"
                                else:
                                    tipo = "Inflexão"
                        except:
                            tipo = "Indefinido"
                        pontos.append({"x": float(r), "y": float(yval), "tipo": tipo})
                except:
                    continue

            xs = np.linspace(-10, 10, 800)
            breaks = find_singularities(expr_simpl, x)
            ys = gerar_pontos_with_breaks(expr_simpl, xs, x, breaks=breaks if breaks else None)

            dados_grafico = {
                "tipo": "pontos_criticos",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "pontos": pontos
            }

            resultado_latex = "\\text{Pontos críticos calculados.}"

        # INTEGRAL
        elif operacao == "integral":
            a = float(params.get("int_a", 0))
            b = float(params.get("int_b", 5))

            prim = integrate(expr_simpl, x)

            # verificar singularidades no intervalo (a,b)
            breaks = find_singularities(expr_simpl, x)
            tem_sing = any((min(a, b) < s < max(a, b)) for s in breaks) if breaks else False

            if tem_sing:
                liquida = None
                area = None
            else:
                try:
                    liquida = float(integrate(expr_simpl, (x, a, b)).evalf())
                except:
                    liquida = None
                try:
                    area = float(integrate(Abs(expr_simpl), (x, a, b)).evalf())
                except:
                    area = None

            xs = np.linspace(a - 1, b + 1, 800)
            ys = gerar_pontos_with_breaks(expr_simpl, xs, x, breaks=breaks if breaks else None)

            dados_grafico = {
                "tipo": "integral",
                "eixo_x": xs.tolist(),
                "eixo_y": ys,
                "intervalo": [a, b],
                "integral_liquida": liquida,
                "area_geometrica": area
            }

            resultado_latex = f"F(x) = {latex(prim)}"

    except Exception as e:
        erro = str(e)
        resultado_latex = f"\\text{{Erro: {erro}}}"

    # Debug prints (ajuda ao testar)
    try:
        print("DEBUG calcular_matematica:", funcao_str := funcao_str if 'funcao_str' in locals() else "<unknown>", "oper:", operacao)
        if dados_grafico:
            print("DEBUG keys:", list(dados_grafico.keys()))
            if "eixo_x" in dados_grafico:
                print("eixo_x[:5]:", dados_grafico["eixo_x"][:5])
            if "eixo_y" in dados_grafico:
                print("eixo_y[:10]:", dados_grafico["eixo_y"][:10])
            if "y_esquerda" in dados_grafico:
                print("y_esquerda[:10]:", dados_grafico["y_esquerda"][:10])
                print("y_direita[:10]:", dados_grafico["y_direita"][:10])
    except Exception:
        pass

    return resultado_latex, dados_grafico, steps, erro


# -------------------------
# ROTA
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    dados_grafico = None
    steps = []
    aba_ativa = "limite"
    funcao_atual = ""
    erro = None

    params = {"ponto": 0, "ponto_tangente": 0, "int_a": 0, "int_b": 5}

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
        "index.html",
        resultado=resultado,
        dados_grafico=dados_grafico,
        steps=steps,
        funcao=funcao_atual,
        aba_ativa=aba_ativa,
        params=params,
        erro=erro,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
