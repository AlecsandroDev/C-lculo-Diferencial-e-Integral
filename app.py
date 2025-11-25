from flask import Flask, render_template, request
import json
import numpy as np
from sympy import symbols, sympify, diff, integrate, limit, solve, latex, lambdify, S, simplify, Abs

app = Flask(__name__)

def gerar_step_by_step(operacao, expr, params, x):
    """Gera o passo a passo detalhado da resolução"""
    steps = []
    
    if operacao == 'limite':
        ponto = float(params.get('ponto', 0))
        steps.append(f"\\textbf{{1. Analisar o ponto }} x = {ponto}")
        
        try:
            valor_ponto = expr.subs(x, ponto)
            if valor_ponto.is_finite and not valor_ponto.is_nan:
                steps.append(f"f({ponto}) = {latex(valor_ponto)} \\quad \\text{{(A função está definida neste ponto)}}")
            else:
                steps.append(f"f({ponto}) \\text{{ não está definido (indeterminação ou divisão por zero)}}")
        except:
            steps.append(f"f({ponto}) \\text{{ não pôde ser calculado diretamente.}}")
        
        steps.append(f"\\textbf{{2. Calcular Limites Laterais}}")
        l_esq = limit(expr, x, ponto, dir='-')
        l_dir = limit(expr, x, ponto, dir='+')
        steps.append(f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)}")
        steps.append(f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)}")
        
        steps.append(f"\\textbf{{3. Conclusão sobre o Limite}}")
        if l_esq == l_dir:
            steps.append(f"\\text{{Como }} \\lim_{{x \\to {ponto}^-}} = \\lim_{{x \\to {ponto}^+}}, \\text{{ o limite existe.}}")
            steps.append(f"\\lim_{{x \\to {ponto}}} f(x) = {latex(l_esq)}")
        else:
            steps.append(f"\\text{{Os limites laterais são diferentes, logo o limite global não existe.}}")
    
    elif operacao == 'derivada':
        steps.append(f"\\textbf{{1. Identificar a função}}")
        steps.append(f"f(x) = {latex(expr)}")
        
        steps.append(f"\\textbf{{2. Aplicar regras de derivação}}")
        derivada = diff(expr, x)
        # Tenta mostrar passo intermediário se não for muito complexo (simplificação)
        derivada_sem_simp = diff(expr, x, evaluate=False)
        if latex(derivada_sem_simp) != latex(derivada):
             steps.append(f"\\frac{{d}}{{dx}}[{latex(expr)}] = {latex(derivada_sem_simp)}")
        
        steps.append(f"\\textbf{{3. Resultado Simplificado}}")
        steps.append(f"f'(x) = {latex(derivada)}")
    
    elif operacao == 'pontos_criticos':
        steps.append(f"\\textbf{{1. Encontrar a Derivada }} f'(x)")
        derivada = diff(expr, x)
        steps.append(f"f'(x) = {latex(derivada)}")
        
        steps.append(f"\\textbf{{2. Igualar a zero }} (f'(x) = 0)")
        steps.append(f"{latex(derivada)} = 0")
        
        steps.append(f"\\textbf{{3. Resolver equação para x}}")
        try:
            solucoes = solve(derivada, x, domain=S.Reals)
            if solucoes:
                reais = [s for s in solucoes if s.is_real]
                if reais:
                    lista_x = ", ".join([latex(s) for s in reais])
                    steps.append(f"x \\in \\{{{lista_x}\\}}")
                    
                    steps.append(f"\\textbf{{4. Calcular coordenadas y}}")
                    for s in reais:
                        y_val = expr.subs(x, s)
                        steps.append(f"f({latex(s)}) = {latex(y_val)} \\implies P({latex(s)}, {latex(y_val)})")
                else:
                    steps.append(f"\\text{{Não foram encontradas raízes reais.}}")
            else:
                steps.append(f"\\text{{Sem solução para }} f'(x)=0")
        except:
            steps.append(f"\\text{{Erro ao resolver a equação algebricamente.}}")
    
    elif operacao == 'integral':
        a = float(params.get('int_a', 0))
        b = float(params.get('int_b', 5))
        n = int(params.get('int_n', 10))
        
        steps.append(f"\\textbf{{1. Integral Indefinida (Primitiva)}}")
        integral_indef = integrate(expr, x)
        steps.append(f"F(x) = \\int f(x)dx = {latex(integral_indef)} + C")
        
        steps.append(f"\\textbf{{2. Teorema Fundamental do Cálculo}}")
        steps.append(f"\\int_{{{a}}}^{{{b}}} f(x)dx = F({b}) - F({a})")
        
        val_b = integral_indef.subs(x, b)
        val_a = integral_indef.subs(x, a)
        area_exata = val_b - val_a
        
        steps.append(f"= ({latex(val_b.evalf(3))}) - ({latex(val_a.evalf(3))})")
        steps.append(f"= {latex(area_exata.evalf(4))}")
        
        steps.append(f"\\textbf{{3. Soma de Riemann (Aproximação)}}")
        delta_x = (b - a) / n
        steps.append(f"\\Delta x = \\frac{{{b} - {a}}}{{{n}}} = {delta_x:.4f}")
        steps.append(f"\\text{{Área}} \\approx \\sum_{{i=0}}^{{{n-1}}} f(x_i) \\cdot \\Delta x")
    
    return steps

def calcular_matematica(funcao_str, operacao, params):
    x = symbols('x')
    resultado_latex = ""
    dados_grafico = {}
    steps = []
    erro = None
    
    try:
        expr = sympify(funcao_str)
        # Gera os passos para QUALQUER operação
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
                except Exception:
                    y_vals.append(None)
            return y_vals

        if operacao == 'limite':
            ponto = float(params.get('ponto', 0))
            l_esq = limit(expr, x, ponto, dir='-')
            l_dir = limit(expr, x, ponto, dir='+')
            l_glob = limit(expr, x, ponto)
            
            # ESPAÇAMENTO AUMENTADO AQUI [1.5em]
            resultado_latex = (
                f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)} \\quad | \\quad "
                f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)} \\\\[1.5em]" 
                f"\\text{{Global: }} \\lim_{{x \\to {ponto}}} f(x) = {latex(l_glob)}"
            )

            tipo_ponto = "aberta"
            y_ponto = 0
            if l_glob.is_finite:
                y_ponto = float(l_glob)
                try:
                    valor_no_ponto = expr.subs(x, ponto)
                    if not valor_no_ponto.is_finite or valor_no_ponto is S.NaN:
                         tipo_ponto = "aberta"
                    else:
                        if abs(float(valor_no_ponto) - y_ponto) < 1e-6:
                            tipo_ponto = "fechada"
                        else:
                            tipo_ponto = "aberta"
                except:
                    tipo_ponto = "aberta"
            else:
                tipo_ponto = "aberta"

            x_vals = np.linspace(ponto - 5, ponto + 5, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            dados_grafico = {
                "tipo": "limite",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_destaque": {"x": float(ponto), "y": float(y_ponto), "estilo": tipo_ponto}
            }

        elif operacao == 'derivada':
            derivada_expr = diff(expr, x)
            resultado_latex = f"f'(x) = {latex(derivada_expr)}"
            x_vals = np.linspace(-10, 10, 500)
            y_vals = gerar_pontos_seguros(derivada_expr, x_vals)
            dados_grafico = {"tipo": "derivada", "eixo_x": x_vals.tolist(), "eixo_y": y_vals}

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
                        if val_y.is_finite:
                            pontos_map.append({"x": float(val_x), "y": float(val_y), "label": f"({float(val_x):.2f}, {float(val_y):.2f})"})
                    except: pass
            
            if pontos_map:
                latex_pts = ", \\quad ".join([f"P({p['x']:.2f}, {p['y']:.2f})" for p in pontos_map])
                resultado_latex = f"\\text{{Pontos Críticos: }} \\\\[1.0em] {latex_pts}"
            else:
                resultado_latex = "\\text{Nenhum ponto crítico real encontrado.}"

            x_vals = np.linspace(-10, 10, 500)
            if pontos_map:
                xs = [p['x'] for p in pontos_map]
                x_vals = np.linspace(min(xs)-5, max(xs)+5, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            dados_grafico = {"tipo": "pontos_criticos", "eixo_x": x_vals.tolist(), "eixo_y": y_vals, "pontos": pontos_map}

        elif operacao == 'integral':
            a = float(params.get('int_a', 0))
            b = float(params.get('int_b', 5))
            n = int(params.get('int_n', 10))
            
            integral_simb = integrate(expr, x)
            integral_liquida = float(integrate(expr, (x, a, b)).evalf())
            area_geometrica = float(integrate(Abs(expr), (x, a, b)).evalf())
            
            delta_x = (b - a) / n
            f_np = lambdify(x, expr, modules=['numpy', {'Abs': np.abs}])
            
            retangulos = []
            soma_liq = 0
            soma_abs = 0
            for i in range(n):
                x_esq = a + i * delta_x
                try:
                    altura = float(f_np(x_esq))
                    if np.isfinite(altura):
                        retangulos.append({"x": x_esq, "largura": delta_x, "altura": altura})
                        soma_liq += altura * delta_x
                        soma_abs += abs(altura * delta_x)
                except: pass
            
            # ESPAÇAMENTO AUMENTADO AQUI [1.5em]
            resultado_latex = (
                f"\\int f(x) \\, dx = {latex(integral_simb)} + C \\\\[1.5em]"
                f"\\text{{Integral Definida (Líquida): }} \\mathbf{{{integral_liquida:.4f}}} \\\\[0.8em]"
                f"\\text{{Área Geométrica (Total): }} \\mathbf{{{area_geometrica:.4f}}}"
            )
            x_vals = np.linspace(a - 1, b + 1, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            dados_grafico = {
                "tipo": "integral", 
                "eixo_x": x_vals.tolist(), 
                "eixo_y": y_vals, 
                "retangulos": retangulos, 
                "intervalo": [a, b],
                "integral_liquida": integral_liquida,
                "area_geometrica": area_geometrica
            }

    except Exception as e:
        erro = str(e)
        resultado_latex = f"\\text{{Erro: }} {str(e)}"

    return resultado_latex, dados_grafico, steps, erro

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    dados_grafico = None
    funcao_atual = ""
    aba_ativa = "limite"
    erro = None
    steps = []
    
    params = {'ponto': 0, 'int_a': 0, 'int_b': 5, 'int_n': 10}

    if request.method == 'POST':
        funcao_atual = request.form.get('funcao', '').strip()
        aba_ativa = request.form.get('aba_ativa', 'limite')
        
        params['ponto'] = request.form.get('ponto_limite', 0)
        params['int_a'] = request.form.get('int_a', 0)
        params['int_b'] = request.form.get('int_b', 5)
        params['int_n'] = request.form.get('int_n', 10)
        
        if funcao_atual:
            resultado, dados_grafico, steps, erro = calcular_matematica(funcao_atual, aba_ativa, params)

    return render_template('index.html', resultado=resultado, dados_grafico=json.dumps(dados_grafico) if dados_grafico else None, steps=steps, funcao=funcao_atual, aba_ativa=aba_ativa, params=params, erro=erro)

if __name__ == '__main__':
     app.run(host="0.0.0.0", debug=True, port=5000)
