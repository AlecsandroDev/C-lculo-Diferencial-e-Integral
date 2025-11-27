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
        
        steps.append(f"\\textbf{{Passo 1: Identificar o ponto de análise}}")
        steps.append(f"\\text{{Queremos analisar }} x = {ponto}")
        
        steps.append(f"\\textbf{{Passo 2: Calcular os limites laterais}}")
        
        try:
            l_esq = limit(expr, x, ponto, dir='-')
            steps.append(f"\\text{{Limite pela esquerda: }} \\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)}")
        except:
            l_esq = None
            steps.append(f"\\text{{Limite pela esquerda: não calculável}}")
        
        try:
            l_dir = limit(expr, x, ponto, dir='+')
            steps.append(f"\\text{{Limite pela direita: }} \\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)}")
        except:
            l_dir = None
            steps.append(f"\\text{{Limite pela direita: não calculável}}")
        
        steps.append(f"\\textbf{{Passo 3: Verificar se o limite existe}}")
        
        if l_esq is not None and l_dir is not None:
            if l_esq.is_finite and l_dir.is_finite:
                if abs(float(l_esq) - float(l_dir)) < 1e-6:
                    steps.append(f"\\text{{Como }} \\lim_{{x \\to {ponto}^-}} = \\lim_{{x \\to {ponto}^+}} = {latex(l_esq)}")
                    steps.append(f"\\text{{O limite existe: }} \\lim_{{x \\to {ponto}}} f(x) = {latex(l_esq)}")
                    
                    steps.append(f"\\textbf{{Passo 4: Testar continuidade}}")
                    
                    try:
                        valor_funcao = expr.subs(x, ponto)
                        if valor_funcao.is_finite and not valor_funcao.is_nan:
                            steps.append(f"\\text{{Valor da função: }} f({ponto}) = {latex(valor_funcao)}")
                            
                            if abs(float(valor_funcao) - float(l_esq)) < 1e-6:
                                steps.append(f"\\text{{Como }} f({ponto}) = \\lim_{{x \\to {ponto}}} f(x)")
                                steps.append(f"\\Rightarrow \\textbf{{A função é CONTÍNUA em x = {ponto}}}")
                                steps.append(f"\\textbf{{Representação: Bolinha Fechada (●)}}")
                            else:
                                steps.append(f"\\text{{Como }} f({ponto}) \\neq \\lim_{{x \\to {ponto}}} f(x)")
                                steps.append(f"\\Rightarrow \\textbf{{DESCONTINUIDADE REMOVÍVEL em x = {ponto}}}")
                                steps.append(f"\\textbf{{Representação: Bolinha Aberta (○)}}")
                        else:
                            steps.append(f"\\text{{A função }} f({ponto}) \\text{{ não está definida}}")
                            steps.append(f"\\Rightarrow \\textbf{{DESCONTINUIDADE em x = {ponto}}}")
                            steps.append(f"\\textbf{{Representação: Bolinha Aberta (○)}}")
                    except:
                        steps.append(f"\\text{{Erro ao calcular }} f({ponto})")
                        steps.append(f"\\Rightarrow \\textbf{{DESCONTINUIDADE em x = {ponto}}}")
                        steps.append(f"\\textbf{{Representação: Bolinha Aberta (○)}}")
                else:
                    steps.append(f"\\text{{Os limites laterais são DIFERENTES}}")
                    steps.append(f"\\Rightarrow \\textbf{{O LIMITE NÃO EXISTE}}")
            else:
                steps.append(f"\\text{{Um ou ambos os limites são infinitos}}")
                steps.append(f"\\Rightarrow \\textbf{{Comportamento assintótico}}")
        else:
            steps.append(f"\\text{{Não foi possível calcular os limites laterais}}")
    
    # ============================================================
    # DERIVADA - REFEITO COM RETA TANGENTE
    # ============================================================
    elif operacao == 'derivada':
        steps.append(f"\\textbf{{Passo 1: Função Original}}")
        steps.append(f"f(x) = {latex(expr)}")
        
        steps.append(f"\\textbf{{Passo 2: Calcular a Derivada}}")
        derivada = diff(expr, x)
        derivada_simp = simplify(derivada)
        steps.append(f"f'(x) = {latex(derivada_simp)}")
        
        steps.append(f"\\textbf{{Passo 3: Interpretação Geométrica}}")
        steps.append(f"\\text{{A derivada }} f'(x) \\text{{ representa a inclinação da reta tangente}}")
        steps.append(f"\\text{{ao gráfico de }} f(x) \\text{{ em cada ponto}}")
        
        # Ponto inicial para a tangente
        ponto_tangente = float(params.get('ponto_tangente', 0))
        steps.append(f"\\textbf{{Passo 4: Reta Tangente em x = {ponto_tangente}}}")
        
        try:
            y0 = float(expr.subs(x, ponto_tangente))
            m = float(derivada_simp.subs(x, ponto_tangente))
            
            steps.append(f"\\text{{Ponto de tangência: }} P({ponto_tangente}, {y0:.4f})")
            steps.append(f"\\text{{Inclinação (coeficiente angular): }} m = f'({ponto_tangente}) = {m:.4f}")
            steps.append(f"\\text{{Equação da reta tangente: }} y - {y0:.4f} = {m:.4f}(x - {ponto_tangente})")
            steps.append(f"y = {m:.4f}x + {(y0 - m*ponto_tangente):.4f}")
        except:
            steps.append(f"\\text{{Erro ao calcular reta tangente em x = {ponto_tangente}}}")
    
    # ... (manter o restante: pontos_criticos e integral)
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
            
            # Calcular limites
            try:
                l_esq = limit(expr, x, ponto, dir='-')
                l_dir = limit(expr, x, ponto, dir='+')
                l_glob = limit(expr, x, ponto)
            except:
                l_esq = l_dir = l_glob = None
            
            # Determinar tipo de ponto (bolinha aberta ou fechada)
            tipo_ponto = "aberta"
            y_limite = 0
            
            if l_glob is not None and l_glob.is_finite and not l_glob.is_nan:
                y_limite = float(l_glob)
                
                try:
                    valor_funcao = expr.subs(x, ponto)
                    
                    if valor_funcao.is_finite and not valor_funcao.is_nan:
                        # Função está definida no ponto
                        if abs(float(valor_funcao) - y_limite) < 1e-6:
                            # f(p) = lim f(x) → CONTÍNUA → Bolinha Fechada
                            tipo_ponto = "fechada"
                        else:
                            # f(p) ≠ lim f(x) → DESCONTINUIDADE REMOVÍVEL → Bolinha Aberta
                            tipo_ponto = "aberta"
                    else:
                        # Função não definida → DESCONTINUIDADE → Bolinha Aberta
                        tipo_ponto = "aberta"
                except:
                    # Erro ao calcular → DESCONTINUIDADE → Bolinha Aberta
                    tipo_ponto = "aberta"
            
            # Montar resultado LaTeX
            if l_esq is not None and l_dir is not None:
                resultado_latex = (
                    f"\\lim_{{x \\to {ponto}^-}} f(x) = {latex(l_esq)} \\\\[1.5em]"
                    f"\\lim_{{x \\to {ponto}^+}} f(x) = {latex(l_dir)} \\\\[1.5em]"
                )
                
                if l_glob is not None and l_glob.is_finite:
                    resultado_latex += f"\\lim_{{x \\to {ponto}}} f(x) = {latex(l_glob)} \\\\[2em]"
                    
                    if tipo_ponto == "fechada":
                        resultado_latex += f"\\textbf{{Conclusão: CONTÍNUA }} \\text{{(Bolinha Fechada ●)}}"
                    else:
                        resultado_latex += f"\\textbf{{Conclusão: DESCONTINUIDADE }} \\text{{(Bolinha Aberta ○)}}"
                else:
                    resultado_latex += f"\\textbf{{O limite não existe ou é infinito}}"
            else:
                resultado_latex = f"\\text{{Erro ao calcular limites em x = {ponto}}}"
            
            # Gerar gráfico
            x_vals = np.linspace(ponto - 5, ponto + 5, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "limite",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_destaque": {
                    "x": float(ponto),
                    "y": float(y_limite),
                    "estilo": tipo_ponto  # "fechada" ou "aberta"
                }
            }

        # DERIVADA
        elif operacao == 'derivada':
            derivada_expr = diff(expr, x)
            derivada_simp = simplify(derivada_expr)
            
            # Ponto inicial da tangente
            ponto_tangente = float(params.get('ponto_tangente', 0))
            
            try:
                y0 = float(expr.subs(x, ponto_tangente))
                m = float(derivada_simp.subs(x, ponto_tangente))
                
                resultado_latex = (
                    f"f'(x) = {latex(derivada_simp)} \\\\[2em]"
                    f"\\text{{Reta tangente em }} x = {ponto_tangente}: \\\\[1em]"
                    f"\\text{{Ponto: }} ({ponto_tangente}, {y0:.4f}) \\\\[0.5em]"
                    f"\\text{{Inclinação: }} m = {m:.4f} \\\\[0.5em]"
                    f"\\text{{Equação: }} y = {m:.4f}x + {(y0 - m*ponto_tangente):.4f}"
                )
            except:
                resultado_latex = (
                    f"f'(x) = {latex(derivada_simp)} \\\\[2em]"
                    f"\\text{{Erro ao calcular reta tangente em x = {ponto_tangente}}}"
                )
                y0 = 0
                m = 0
            
            # Gerar gráfico da função original
            x_vals = np.linspace(-10, 10, 500)
            y_vals = gerar_pontos_seguros(expr, x_vals)
            
            dados_grafico = {
                "tipo": "derivada",
                "eixo_x": x_vals.tolist(),
                "eixo_y": y_vals,
                "ponto_tangente": {
                    "x": float(ponto_tangente),
                    "y": float(y0),
                    "inclinacao": float(m)
                },
                "derivada_expr": str(derivada_simp)  # Para recalcular dinamicamente
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
    
    params = {'ponto': 0, 'ponto_tangente': 0, 'int_a': 0, 'int_b': 5}

    if request.method == 'POST':
        funcao_atual = request.form.get('funcao', '').strip()
        aba_ativa = request.form.get('aba_ativa', 'limite')
        
        params['ponto'] = request.form.get('ponto_limite', 0)
        params['ponto_tangente'] = request.form.get('ponto_tangente', 0)
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