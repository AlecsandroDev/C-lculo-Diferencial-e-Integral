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
        
        # Calcular limites laterais
        l_esq = limit(expr, x, ponto, dir='-')
        l_dir = limit(expr, x, ponto, dir='+')
        
        steps.append(f"\\textbf{{2. Calcular Limites Laterais}}")
        steps.append(f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)}")
        steps.append(f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)}")
        
        steps.append(f"\\textbf{{3. Verificar se os limites laterais coincidem}}")
        if l_esq == l_dir and l_esq.is_finite:
            steps.append(f"\\text{{Limites laterais são iguais: }} \\lim_{{x \\to {ponto}}} f(x) = {latex(l_esq)}")
            
            steps.append(f"\\textbf{{4. Análise de Continuidade}}")
            try:
                valor_ponto = expr.subs(x, ponto)
                if valor_ponto.is_finite and not valor_ponto.is_nan:
                    if abs(float(valor_ponto) - float(l_esq)) < 1e-6:
                        steps.append(f"f({ponto}) = {latex(valor_ponto)} = \\lim_{{x \\to {ponto}}} f(x)")
                        steps.append(f"\\Rightarrow \\textbf{{Função Contínua (Bolinha Fechada)}}")
                    else:
                        steps.append(f"f({ponto}) = {latex(valor_ponto)} \\neq {latex(l_esq)} = \\lim_{{x \\to {ponto}}} f(x)")
                        steps.append(f"\\Rightarrow \\textbf{{Descontinuidade Removível (Bolinha Aberta)}}")
                else:
                    steps.append(f"f({ponto}) \\text{{ é indefinido}}")
                    steps.append(f"\\Rightarrow \\textbf{{Descontinuidade (Bolinha Aberta)}}")
            except:
                steps.append(f"f({ponto}) \\text{{ não pode ser calculado}}")
                steps.append(f"\\Rightarrow \\textbf{{Descontinuidade (Bolinha Aberta)}}")
        else:
            steps.append(f"\\text{{Limites laterais diferentes ou infinitos}}")
            steps.append(f"\\Rightarrow \\textbf{{Limite não existe}}")
    
    elif operacao == 'derivada':
        steps.append(f"\\textbf{{1. Função Original}}")
        steps.append(f"f(x) = {latex(expr)}")
        
        steps.append(f"\\textbf{{2. Calcular a Primeira Derivada}}")
        derivada = diff(expr, x)
        steps.append(f"f'(x) = {latex(derivada)}")
        
        steps.append(f"\\textbf{{3. Calcular a Segunda Derivada}}")
        derivada2 = diff(derivada, x)
        derivada2_simp = simplify(derivada2)
        steps.append(f"f''(x) = {latex(derivada2_simp)}")
    
    elif operacao == 'pontos_criticos':
        steps.append(f"\\textbf{{1. Calcular a Primeira Derivada}}")
        derivada = diff(expr, x)
        steps.append(f"f'(x) = {latex(derivada)}")
        
        steps.append(f"\\textbf{{2. Encontrar Pontos Críticos (f'(x) = 0)}}")
        steps.append(f"{latex(derivada)} = 0")
        
        try:
            solucoes = solve(derivada, x, domain=S.Reals)
            if solucoes:
                reais = [s for s in solucoes if s.is_real and s.is_finite]
                if reais:
                    for sol in reais:
                        steps.append(f"x = {latex(sol)}")
                    
                    steps.append(f"\\textbf{{3. Calcular a Segunda Derivada para Classificação}}")
                    derivada2 = diff(derivada, x)
                    steps.append(f"f''(x) = {latex(derivada2)}")
                    
                    steps.append(f"\\textbf{{4. Teste da Segunda Derivada}}")
                    for sol in reais:
                        y_val = expr.subs(x, sol)
                        d2_val = derivada2.subs(x, sol)
                        
                        if d2_val > 0:
                            tipo = "\\text{Mínimo Local}"
                        elif d2_val < 0:
                            tipo = "\\text{Máximo Local}"
                        else:
                            tipo = "\\text{Ponto de Inflexão ou Inconclusivo}"
                        
                        steps.append(f"P({latex(sol)}, {latex(y_val)}): \\, f''({latex(sol)}) = {latex(d2_val)} \\Rightarrow {tipo}")
                else:
                    steps.append(f"\\text{{Sem raízes reais}}")
            else:
                steps.append(f"\\text{{Sem solução}}")
        except:
            steps.append(f"\\text{{Erro ao resolver}}")
    
    elif operacao == 'integral':
        a = float(params.get('int_a', 0))
        b = float(params.get('int_b', 5))
        
        steps.append(f"\\textbf{{1. Calcular a Integral Indefinida (Primitiva)}}")
        integral_indef = integrate(expr, x)
        steps.append(f"F(x) = \\int f(x) \\, dx = {latex(integral_indef)} + C")
        
        steps.append(f"\\textbf{{2. Aplicar o Teorema Fundamental do Cálculo}}")
        steps.append(f"\\int_{{{a}}}^{{{b}}} f(x) \\, dx = F({b}) - F({a})")
        
        val_b = integral_indef.subs(x, b)
        val_a = integral_indef.subs(x, a)
        resultado = val_b - val_a
        
        steps.append(f"= {latex(val_b)} - ({latex(val_a)})")
        steps.append(f"= {latex(resultado)}")
        
        steps.append(f"\\textbf{{3. Interpretação das Áreas}}")
        steps.append(f"\\text{{Integral Líquida: }} {float(resultado):.6f} \\text{{ (considera sinal)}}")
        
        area_geom = integrate(Abs(expr), (x, a, b))
        steps.append(f"\\text{{Área Geométrica: }} \\int_{{{a}}}^{{{b}}} |f(x)| \\, dx = {float(area_geom):.6f}")
    
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
            """Gera pontos do gráfico evitando NaN e Infinitos"""
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

        # LIMITES - Análise de Continuidade
        if operacao == 'limite':
            ponto = float(params.get('ponto', 0))
            
            l_esq = limit(expr, x, ponto, dir='-')
            l_dir = limit(expr, x, ponto, dir='+')
            l_glob = limit(expr, x, ponto)
            
            # Lógica CORRIGIDA de continuidade
            tipo_ponto = "aberta"
            y_ponto = 0
            
            if l_glob.is_finite and not l_glob.is_nan:
                y_ponto = float(l_glob)
                try:
                    valor_no_ponto = expr.subs(x, ponto)
                    if valor_no_ponto.is_finite and not valor_no_ponto.is_nan:
                        if abs(float(valor_no_ponto) - y_ponto) < 1e-6:
                            tipo_ponto = "fechada"  # Contínua
                        else:
                            tipo_ponto = "aberta"   # Descontinuidade removível
                    else:
                        tipo_ponto = "aberta"
                except:
                    tipo_ponto = "aberta"
            else:
                tipo_ponto = "aberta"
            
            continuidade_texto = "Contínua (Bolinha Fechada)" if tipo_ponto == "fechada" else "Descontinuidade (Bolinha Aberta)"
            
            resultado_latex = (
                f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)} \\\\[1.5em]"
                f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)} \\\\[1.5em]"
                f"\\lim_{{x \\to {ponto}}} f(x) = {latex(l_glob)} \\\\[2em]"
                f"\\textbf{{Análise: }} \\text{{{continuidade_texto}}}"
            )

            x_vals = np.linspace(ponto - 5, ponto + 5, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "limite",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_destaque": {
                    "x": float(ponto),
                    "y": float(y_ponto),
                    "estilo": tipo_ponto
                }
            }

        # DERIVADA
        elif operacao == 'derivada':
            derivada_expr = diff(expr, x)
            derivada2_expr = diff(derivada_expr, x)
            derivada2_simp = simplify(derivada2_expr)
            
            resultado_latex = (
                f"f'(x) = {latex(derivada_expr)} \\\\[2em]"
                f"f''(x) = {latex(derivada2_simp)}"
            )
            
            x_vals = np.linspace(-10, 10, 500)
            y_vals = gerar_pontos_seguros(derivada2_simp, x_vals)
            
            dados_grafico = {
                "tipo": "derivada",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals
            }

        # PONTOS CRÍTICOS
        elif operacao == 'pontos_criticos':
            derivada = diff(expr, x)
            derivada2 = diff(derivada, x)
            
            try:
                solucoes = solve(derivada, x, domain=S.Reals)
            except:
                solucoes = []
            
            pontos_map = []
            if isinstance(solucoes, (list, tuple)):
                reais = [s for s in solucoes if s.is_real and s.is_finite]
                for val_x in reais:
                    try:
                        val_y = expr.subs(x, val_x)
                        d2_val = derivada2.subs(x, val_x)
                        
                        if d2_val > 0:
                            tipo = "Mínimo"
                        elif d2_val < 0:
                            tipo = "Máximo"
                        else:
                            tipo = "Inflexão"
                        
                        if val_y.is_finite:
                            pontos_map.append({
                                "x": float(val_x),
                                "y": float(val_y),
                                "tipo": tipo,
                                "label": f"{tipo}: ({float(val_x):.2f}, {float(val_y):.2f})"
                            })
                    except:
                        pass
            
            if pontos_map:
                latex_pts = " \\\\[1.2em] ".join([
                    f"\\textbf{{{p['tipo']}}}: \\, P({p['x']:.2f}, {p['y']:.2f})" 
                    for p in pontos_map
                ])
                resultado_latex = f"\\text{{Pontos Críticos Encontrados:}} \\\\[1.5em] {latex_pts}"
            else:
                resultado_latex = "\\text{Nenhum ponto crítico real encontrado.}"

            if pontos_map:
                xs = [p['x'] for p in pontos_map]
                x_vals = np.linspace(min(xs) - 5, max(xs) + 5, 500)
            else:
                x_vals = np.linspace(-10, 10, 500)
            
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "pontos_criticos",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "pontos": pontos_map
            }

        # INTEGRAL
        elif operacao == 'integral':
            a = float(params.get('int_a', 0))
            b = float(params.get('int_b', 5))
            
            integral_simb = integrate(expr, x)
            integral_liquida = float(integrate(expr, (x, a, b)).evalf())
            area_geometrica = float(integrate(Abs(expr), (x, a, b)).evalf())
            
            resultado_latex = (
                f"\\int f(x) \\, dx = {latex(integral_simb)} + C \\\\[2em]"
                f"\\text{{Integral Líquida: }} \\int_{{{a}}}^{{{b}}} f(x) \\, dx = {integral_liquida:.6f} \\\\[2em]"
                f"\\text{{Área Geométrica: }} \\int_{{{a}}}^{{{b}}} |f(x)| \\, dx = {area_geometrica:.6f}"
            )

            x_vals = np.linspace(a - 1, b + 1, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            # Pré-calcular retângulos iniciais (n=10)
            n = 10
            delta_x = (b - a) / n
            f_np = lambdify(x, expr, modules=['numpy', {'Abs': np.abs}])
            
            retangulos = []
            for i in range(n):
                x_esq = a + i * delta_x
                try:
                    altura = float(f_np(x_esq))
                    if np.isfinite(altura):
                        retangulos.append({
                            "x": x_esq,
                            "largura": delta_x,
                            "altura": altura
                        })
                except:
                    pass
            
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
        print(f"Erro: {e}")

    return resultado_latex, dados_grafico, steps, erro

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    dados_grafico = None
    steps = []
    funcao_atual = ""
    aba_ativa = "limite"
    erro = None
    
    params = {'ponto': 0, 'int_a': 0, 'int_b': 5}

    if request.method == 'POST':
        funcao_atual = request.form.get('funcao', '').strip()
        aba_ativa = request.form.get('aba_ativa', 'limite')
        
        params['ponto'] = request.form.get('ponto_limite', 0)
        params['int_a'] = request.form.get('int_a', 0)
        params['int_b'] = request.form.get('int_b', 5)
        
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