from flask import Flask, render_template, request
import json
import numpy as np
from sympy import symbols, sympify, diff, integrate, limit, solve, latex, lambdify, S, simplify, Abs, oo

app = Flask(__name__)

def gerar_step_by_step(operacao, expr, params, x):
    steps = []
    if operacao == 'limite':
        ponto = float(params.get('ponto', 0))
        steps.append(f"\\textbf{{Passo 1: Identificar o ponto}}")
        steps.append(f"\\text{{Analisando }} x \\to {ponto}")
        
        try:
            l_esq = limit(expr, x, ponto, dir='-')
            l_dir = limit(expr, x, ponto, dir='+')
            steps.append(f"\\text{{Limites Laterais:}}")
            steps.append(f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)}")
            steps.append(f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)}")
            
            if l_esq == l_dir and l_esq.is_finite:
                steps.append(f"\\text{{Como os laterais são iguais e finitos, o limite existe:}}")
                steps.append(f"\\lim_{{x \\to {ponto}}} f(x) = {latex(l_esq)}")
            else:
                steps.append(f"\\text{{Os limites são diferentes ou infinitos.}}")
        except:
            steps.append("\\text{Erro ao calcular limites laterais.}")

    elif operacao == 'derivada':
        steps.append(f"f(x) = {latex(expr)}")
        derivada = diff(expr, x)
        steps.append(f"\\text{{Aplicando regras de derivação:}}")
        steps.append(f"f'(x) = {latex(derivada)}")
        
    elif operacao == 'pontos_criticos':
        derivada = diff(expr, x)
        steps.append(f"f'(x) = {latex(derivada)}")
        steps.append(f"\\text{{Igualando a zero: }} {latex(derivada)} = 0")
        
    elif operacao == 'integral':
        a = float(params.get('int_a', 0))
        b = float(params.get('int_b', 5))
        primitive = integrate(expr, x)
        steps.append(f"\\int f(x)dx = {latex(primitive)} + C")
        steps.append(f"\\text{{Aplicando T.F.C de }} {a} \\text{{ a }} {b}")
        
    return steps

def calcular_matematica(funcao_str, operacao, params):
    x = symbols('x')
    resultado_latex = ""
    dados_grafico = {}
    steps = []
    erro = None
    
    try:
        expr = sympify(funcao_str)
        steps = gerar_step_by_step(operacao, expr, params, x)

        def gerar_pontos_seguros(expressao, x_vals):
            f_np = lambdify(x, expressao, modules=['numpy', {'Abs': np.abs}])
            y_vals = []
            for xv in x_vals:
                try:
                    val = f_np(xv)
                    if np.isfinite(val):
                        y_vals.append(float(val))
                    else:
                        y_vals.append(None)
                except:
                    y_vals.append(None)
            return y_vals

        if operacao == 'limite':
            ponto = float(params.get('ponto', 0))
            
            try:
                l_esq = limit(expr, x, ponto, dir='-')
                l_dir = limit(expr, x, ponto, dir='+')
            except:
                l_esq = S.NaN
                l_dir = S.NaN
            
            try:
                l_glob = limit(expr, x, ponto)
            except:
                l_glob = S.NaN

            ponto_existe = False
            y_limite = 0
            tipo_ponto = "aberta"
            
            resultado_latex = (
                f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)} \\\\[1em]"
                f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)} \\\\[1em]"
            )

            if l_glob is not None and l_glob.is_finite:
                resultado_latex += f"\\text{{Global: }} {latex(l_glob)}"
                ponto_existe = True
                y_limite = float(l_glob)
                
                try:
                    valor_funcao = expr.subs(x, ponto)
                    if valor_funcao.is_finite and abs(float(valor_funcao) - y_limite) < 1e-6:
                        tipo_ponto = "fechada"
                    else:
                        tipo_ponto = "aberta"
                except:
                    tipo_ponto = "aberta"
            else:
                resultado_latex += "\\text{O limite não existe ou é infinito.}"
                ponto_existe = False
            
            x_vals = np.linspace(ponto - 5, ponto + 5, 400)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "limite",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_destaque": {
                    "mostrar": ponto_existe,
                    "x": float(ponto),
                    "y": float(y_limite),
                    "estilo": tipo_ponto
                }
            }

        elif operacao == 'derivada':
            derivada_expr = diff(expr, x)
            derivada_simp = simplify(derivada_expr)
            resultado_latex = f"f'(x) = {latex(derivada_simp)}"
            ponto_tangente = float(params.get('ponto_tangente', 0))
            x_vals = np.linspace(-10, 10, 400)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "derivada",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_inicial": ponto_tangente 
            }

        elif operacao == 'pontos_criticos':
            derivada = diff(expr, x)
            try:
                solucoes = solve(derivada, x, domain=S.Reals)
            except:
                solucoes = []
            
            pontos_map = []
            if isinstance(solucoes, list):
                reais = [s for s in solucoes if s.is_real and s.is_finite]
                for val_x in reais:
                    try:
                        val_y = expr.subs(x, val_x)
                        d2 = diff(derivada, x).subs(x, val_x)
                        tipo = "Mínimo" if d2 > 0 else "Máximo" if d2 < 0 else "Inflexão"
                        if val_y.is_finite:
                            pontos_map.append({
                                "x": float(val_x), "y": float(val_y), 
                                "tipo": tipo, "label": f"{tipo}"
                            })
                    except: pass

            if pontos_map:
                latex_txt = ", ".join([f"x={p['x']:.2f}" for p in pontos_map])
                resultado_latex = f"\\text{{Pontos em: }} {latex_txt}"
            else:
                resultado_latex = "\\text{Nenhum ponto crítico encontrado.}"
            
            if pontos_map:
                xs = [p['x'] for p in pontos_map]
                x_vals = np.linspace(min(xs)-5, max(xs)+5, 400)
            else:
                x_vals = np.linspace(-10, 10, 400)
            
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "pontos_criticos",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "pontos": pontos_map
            }

        elif operacao == 'integral':
            a = float(params.get('int_a', 0))
            b = float(params.get('int_b', 5))
            
            int_simb = integrate(expr, x)
            int_def = float(integrate(expr, (x, a, b)).evalf())
            area_geo = float(integrate(Abs(expr), (x, a, b)).evalf())
            
            resultado_latex = (
                f"\\int f(x)dx = {latex(int_simb)} + C \\\\[1em]"
                f"\\text{{Líquida: }} {int_def:.4f} \\quad | \\quad \\text{{Área: }} {area_geo:.4f}"
            )
            
            x_vals = np.linspace(a - 1, b + 1, 400)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            retangulos = []
            delta = (b-a)/10
            f_np = lambdify(x, expr, modules=['numpy', {'Abs': np.abs}])
            for i in range(10):
                xi = a + i*delta
                try:
                    h = float(f_np(xi))
                    if np.isfinite(h):
                        retangulos.append({'x': xi, 'largura': delta, 'altura': h})
                except: pass
                
            dados_grafico = {
                "tipo": "integral",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "retangulos": retangulos,
                "intervalo": [a, b],
                "int_liq": int_def,
                "area_geo": area_geo
            }

    except Exception as e:
        erro = str(e)
        resultado_latex = f"\\text{{Erro: }} {str(e)}"

    return resultado_latex, dados_grafico, steps, erro

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    dados_grafico = None
    steps = []
    funcao_atual = ""
    aba_ativa = "limite"
    erro = None
    params = {'ponto': 0, 'ponto_tangente': 0, 'int_a': 0, 'int_b': 5}

    if request.method == 'POST':
        funcao_atual = request.form.get('funcao', '').strip()
        aba_ativa = request.form.get('aba_ativa', 'limite')
        
        try: params['ponto'] = float(request.form.get('ponto_limite', 0))
        except: pass
        try: params['ponto_tangente'] = float(request.form.get('ponto_tangente', 0))
        except: pass
        try: params['int_a'] = float(request.form.get('int_a', 0))
        except: pass
        try: params['int_b'] = float(request.form.get('int_b', 5))
        except: pass
        
        if funcao_atual:
            resultado, dados_grafico, steps, erro = calcular_matematica(
                funcao_atual, aba_ativa, params
            )

    return render_template(
        'index.html',
        resultado=resultado,
        dados_grafico=json.dumps(dados_grafico) if dados_grafico else None,
        steps=steps,
        funcao=funcao_atual,
        aba_ativa=aba_ativa,
        params=params,
        erro=erro
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)