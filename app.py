<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CalcTool - Visual e Detalhado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 2rem 0; font-family: sans-serif; }
        .main-card { background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; margin-bottom: 50px; }
        .header-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }
        .nav-tabs .nav-link.active { color: #667eea; border-bottom: 3px solid #667eea; }
        .resultado-card { background: #f8f9fa; border-radius: 15px; padding: 2rem; margin-top: 2rem; border: 1px solid #e9ecef; }
        .resultado-math { background: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; font-size: 1.2rem; line-height: 2.0; }
        
        .step-by-step { margin-top: 2rem; }
        .step-by-step h5 { color: #667eea; font-weight: 700; margin-bottom: 1.5rem; text-transform: uppercase; font-size: 0.9rem; }
        .step-item { background: white; padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid #667eea; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        
        #main-chart { background: white; border-radius: 10px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 2rem; }
        .area-info { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .area-box { padding: 1.5rem; border-radius: 12px; text-align: center; }
        .area-box .valor { font-size: 1.5rem; font-weight: 800; margin: 0.5rem 0; }
        .config-aba { animation: fadeIn 0.3s; margin-top: 15px;}
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

<div class="container">
    <div class="main-card">
        <div class="header-section">
            <h1>📊 CalcTool Pro</h1>
            <p>Limites, Derivadas, Integrais e Gráficos Interativos</p>
        </div>

        <ul class="nav nav-tabs px-3" role="tablist">
            <li class="nav-item"><button class="nav-link {% if aba_ativa == 'limite' %}active{% endif %}" onclick="mudarAba('limite')">Limites</button></li>
            <li class="nav-item"><button class="nav-link {% if aba_ativa == 'derivada' %}active{% endif %}" onclick="mudarAba('derivada')">Derivada</button></li>
            <li class="nav-item"><button class="nav-link {% if aba_ativa == 'pontos_criticos' %}active{% endif %}" onclick="mudarAba('pontos_criticos')">Pontos Críticos</button></li>
            <li class="nav-item"><button class="nav-link {% if aba_ativa == 'integral' %}active{% endif %}" onclick="mudarAba('integral')">Integral</button></li>
        </ul>

        <div class="p-4">
            <form method="POST" action="/">
                <input type="hidden" name="aba_ativa" id="input_aba_ativa" value="{{ aba_ativa }}">
                
                <div class="mb-4">
                    <label class="form-label fw-bold">Função f(x):</label>
                    <input type="text" class="form-control form-control-lg" name="funcao" value="{{ funcao }}" placeholder="Ex: x**3 - 2*x" required>
                </div>

                <div class="config-aba" id="div-limite" {% if aba_ativa != 'limite' %}style="display:none"{% endif %}>
                    <label class="form-label">Ponto (x → p):</label>
                    <input type="number" step="any" class="form-control" name="ponto_limite" value="{{ params.ponto }}">
                </div>

                <div class="config-aba" id="div-derivada" {% if aba_ativa != 'derivada' %}style="display:none"{% endif %}>
                    <label>Mover Reta Tangente (x): <span id="label_tg_form">{{ params.ponto_tangente }}</span></label>
                    <input type="range" class="form-range" min="-10" max="10" step="0.1" name="ponto_tangente" id="slider_tangente_form" value="{{ params.ponto_tangente }}" oninput="document.getElementById('label_tg_form').innerText = this.value">
                </div>

                <div class="config-aba" id="div-integral" {% if aba_ativa != 'integral' %}style="display:none"{% endif %}>
                    <div class="row g-3">
                        <div class="col-md-6"><label class="form-label">Início (a):</label><input type="number" step="any" class="form-control" name="int_a" value="{{ params.int_a }}"></div>
                        <div class="col-md-6"><label class="form-label">Fim (b):</label><input type="number" step="any" class="form-control" name="int_b" value="{{ params.int_b }}"></div>
                    </div>
                    <div class="mt-3">
                        <label class="form-label">N Retângulos Inicial: {{ params.int_n }}</label>
                        <input type="range" class="form-range" min="1" max="100" name="int_n" value="{{ params.int_n }}">
                    </div>
                </div>

                <button type="submit" class="btn btn-primary w-100 btn-lg mt-4">Calcular e Detalhar</button>
            </form>
        </div>

        {% if resultado %}
        <div class="resultado-card mx-4 mb-4">
            <h4 class="text-center mb-4" style="color: #667eea;">Resultado Final</h4>
            <div class="resultado-math">$$ {{ resultado | safe }} $$</div>

            {% if steps %}
            <div class="step-by-step">
                <h5>📝 Passo a Passo</h5>
                {% for step in steps %}
                <div class="step-item">$$ {{ step | safe }} $$</div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if dados_grafico %}
            <hr class="my-5">
            <h4 class="text-center mb-3">Visualização Gráfica</h4>
            
            <div id="controles-integral" style="display: none;">
                <div class="area-info">
                    <div class="area-box" style="background: #f8f9fa; border: 1px solid #dee2e6;">
                        <h6 style="color: #666;">Integral Definida (Líquida)</h6>
                        <div class="valor" id="integral_liquida_display">-</div>
                        <small class="text-muted">Riemann: <span id="soma_liquida_display">-</span></small>
                    </div>
                    <div class="area-box" style="background: #e8f4fc; border: 1px solid #b6e1fc;">
                        <h6 style="color: #2c3e50;">Área Geométrica (Total)</h6>
                        <div class="valor" id="area_geometrica_display">-</div>
                        <small class="text-muted">Riemann: <span id="soma_absoluta_display">-</span></small>
                    </div>
                </div>
                <div class="mb-3">
                    <label>Ajuste Dinâmico de Retângulos: <span id="val_n_dinamico"></span></label>
                    <input type="range" class="form-range" min="1" max="100" id="slider_riemann">
                </div>
            </div>

            <div id="controles-derivada" style="display: none;" class="mb-3 text-center">
                <label>Posição da Tangente (x): <span id="val_x_tg"></span></label>
                <input type="range" class="form-range" min="-10" max="10" step="0.1" id="slider_tangente_grafico">
            </div>
            
            <div id="main-chart" style="width: 100%; height: 600px;"></div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>

<script>
    function mudarAba(aba) {
        document.getElementById('input_aba_ativa').value = aba;
        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
        event.target.classList.add('active');
        document.querySelectorAll('.config-aba').forEach(el => el.style.display = 'none');
        if (aba === 'limite') document.getElementById('div-limite').style.display = 'block';
        if (aba === 'derivada') document.getElementById('div-derivada').style.display = 'block';
        if (aba === 'integral') document.getElementById('div-integral').style.display = 'block';
    }

    {% if dados_grafico %}
    (function() {
        const dados = {{ dados_grafico | safe }};
        const myChart = echarts.init(document.getElementById('main-chart'));
        
        const commonConfig = {
            toolbox: { feature: { dataZoom: {}, restore: {}, saveAsImage: {} }, right: 20 },
            tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
            grid: { left: '8%', right: '8%', bottom: '15%', top: '15%' },
            dataZoom: [{ type: 'inside' }, { type: 'slider' }],
            xAxis: { type: 'value', minInterval: 1 },
            yAxis: { type: 'value', minInterval: 1 }
        };

        let option = {};

        // --- 1. LIMITE (Corrigido mostrar/ocultar bolinha) ---
        if (dados.tipo === 'limite') {
            const series = [{
                name: 'f(x)', type: 'line', smooth: true, showSymbol: false,
                data: dados.eixo_x.map((x, i) => [x, dados.eixo_y[i]])
            }];
            
            if (dados.ponto_destaque.mostrar) {
                const isAberta = dados.ponto_destaque.estilo === 'aberta';
                series.push({
                    name: 'Limite', type: 'scatter', symbolSize: 15,
                    itemStyle: { color: isAberta ? 'white' : 'red', borderColor: 'red', borderWidth: 3 },
                    data: [[dados.ponto_destaque.x, dados.ponto_destaque.y]], z: 10
                });
            }
            option = { ...commonConfig, title: { text: 'Limite', left: 'center' }, series: series };
        } 
        
        // --- 2. DERIVADA (Corrigido Tangente Dinâmica) ---
        else if (dados.tipo === 'derivada') {
            document.getElementById('controles-derivada').style.display = 'block';
            
            function updateTangente(xTg) {
                document.getElementById('val_x_tg').innerText = xTg;
                
                // Encontrar vizinhos para calcular inclinação (m)
                let idx = dados.eixo_x.findIndex(v => v >= xTg);
                if(idx < 1) idx = 1;
                if(idx >= dados.eixo_x.length-1) idx = dados.eixo_x.length-2;
                
                let y0 = dados.eixo_y[idx];
                let p1 = {x: dados.eixo_x[idx-1], y: dados.eixo_y[idx-1]};
                let p2 = {x: dados.eixo_x[idx+1], y: dados.eixo_y[idx+1]};
                let m = (p2.y - p1.y) / (p2.x - p1.x); // Derivada numérica
                
                // Reta: y = m(x - x0) + y0
                let lineData = [];
                let range = 5; 
                lineData.push([xTg - range, m * (-range) + y0]);
                lineData.push([xTg + range, m * (range) + y0]);

                myChart.setOption({
                    title: { text: 'Derivada e Tangente', left: 'center' },
                    series: [
                        { name: 'f(x)', type: 'line', smooth: true, data: dados.eixo_x.map((x, i) => [x, dados.eixo_y[i]]) },
                        { name: 'Tangente', type: 'line', data: lineData, lineStyle: {type: 'dashed', color: 'red'}, showSymbol: false },
                        { name: 'Ponto', type: 'scatter', data: [[xTg, y0]], itemStyle: {color: 'red'} }
                    ]
                });
            }
            
            // Linkar sliders
            const s1 = document.getElementById('slider_tangente_grafico');
            const s2 = document.getElementById('slider_tangente_form'); // Do formulário
            
            function onSlider(val) { updateTangente(parseFloat(val)); }
            
            s1.addEventListener('input', (e) => onSlider(e.target.value));
            // Inicia com valor do python
            s1.value = dados.ponto_inicial; 
            updateTangente(dados.ponto_inicial);
            
            option = commonConfig; 
        }

        // --- 3. PONTOS CRÍTICOS ---
        else if (dados.tipo === 'pontos_criticos') {
            option = {
                ...commonConfig, title: { text: 'Pontos Críticos', left: 'center' },
                series: [
                    { name: 'f(x)', type: 'line', smooth: true, data: dados.eixo_x.map((x, i) => [x, dados.eixo_y[i]]) },
                    { 
                        name: 'Pontos', type: 'scatter', symbolSize: 15, itemStyle: {color: 'orange'},
                        data: dados.pontos.map(p => [p.x, p.y]),
                        label: { show: true, formatter: '{b}', position: 'top' }
                    }
                ]
            };
        }

        // --- 4. INTEGRAL (Mantido: Área Geométrica vs Líquida) ---
        else if (dados.tipo === 'integral') {
            document.getElementById('controles-integral').style.display = 'block';
            
            function updateRiemann(n) {
                document.getElementById('val_n_dinamico').innerText = n;
                
                const a = dados.intervalo[0], b = dados.intervalo[1];
                const dx = (b - a) / n;
                const rects = [];
                let s_liq = 0, s_abs = 0;
                
                for(let i=0; i<n; i++) {
                    let xi = a + i*dx;
                    let idx = dados.eixo_x.findIndex(v => v >= xi);
                    let h = dados.eixo_y[idx] || 0;
                    rects.push({x: xi, w: dx, h: h});
                    s_liq += h*dx;
                    s_abs += Math.abs(h*dx);
                }

                // Atualiza Texto
                document.getElementById('integral_liquida_display').innerText = dados.integral_liquida.toFixed(4);
                document.getElementById('soma_liquida_display').innerText = s_liq.toFixed(4);
                document.getElementById('area_geometrica_display').innerText = dados.area_geometrica.toFixed(4);
                document.getElementById('soma_absoluta_display').innerText = s_abs.toFixed(4);

                myChart.setOption({
                    title: { text: `Soma de Riemann (n=${n})`, left: 'center' },
                    series: [
                        { name: 'f(x)', type: 'line', smooth: true, z: 10, data: dados.eixo_x.map((x, i) => [x, dados.eixo_y[i]]) },
                        {
                            type: 'custom',
                            renderItem: function(params, api) {
                                var r = rects[params.dataIndex];
                                var start = api.coord([r.x, 0]);
                                var size = api.size([r.w, r.h]);
                                return {
                                    type: 'rect',
                                    shape: { x: start[0], y: start[1] - (r.h>0 ? size[1] : 0), width: size[0], height: Math.abs(size[1]) },
                                    style: { fill: r.h>0 ? 'rgba(0,0,255,0.3)' : 'rgba(255,0,0,0.3)' }
                                };
                            },
                            data: rects
                        }
                    ]
                });
            }
            
            const slider = document.getElementById('slider_riemann');
            slider.addEventListener('input', (e) => updateRiemann(parseInt(e.target.value)));
            // Inicia com retângulos do python
            slider.value = dados.retangulos.length;
            updateRiemann(dados.retangulos.length);
            
            option = commonConfig;
        }

        if (dados.tipo !== 'derivada' && dados.tipo !== 'integral') {
            myChart.setOption(option);
        }
        window.addEventListener('resize', () => myChart.resize());
    })();
    {% endif %}
</script>
</body>
</html>