import base64, os

FIG_DIR = "figures"

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

IMG = {
    # só o gráfico 05 continua embutido — os gráficos 01-04 saíram do apoio visual
    # quando o "caminho até a decisão" virou a linha do tempo de 9 momentos.
    "05": b64(os.path.join(FIG_DIR, "05_divergencia_proxies.png")),
}

def img_tag(key, alt):
    return f'<img src="data:image/png;base64,{IMG[key]}" alt="{alt}" loading="lazy">'

TIMELINE = [
    {
        "n": 1, "type": "checagem", "tag": "Checagem",
        "title": "Só 22,6% da base tem preço — e não por acaso",
        "text": "Antes de recortar, fomos checar o porquê: anúncios com 6+ reviews têm 56-80% de chance de ter preço capturado, contra 1-6% pros com poucos reviews. A cobertura não é aleatória — decidimos deixar isso explícito desde o início.",
    },
    {
        "n": 2, "type": "correcao", "tag": "Correção",
        "title": "R$ 10-29 mil/noite: antes de descartar, fomos ver o que era",
        "text": "Podia ser luxo de verdade. Abrimos os anúncios: preço fixo de R$10.000 em TODAS as datas do calendário é bloqueio, não tarifa real; outro caso era um pico isolado de um único dia. Confirmado como artefato de captura — só então excluímos.",
    },
    {
        "n": 3, "type": "achado", "tag": "Achado",
        "title": "Os dois proxies de ocupação não concordam entre si",
        "text": "Um proxy por taxa de review, outro por datas que somem no calendário — Spearman ≈ -0,03. Verificamos se era bug (não era) e reportamos a divergência como limitação real, sem esconder.",
    },
    {
        "n": 4, "type": "achado", "tag": "Achado",
        "title": "Primeiro sinal parece dar razão à tese",
        "text": "1-quarto no Centro precifica 25-31% mais caro por noite que em Meia Praia (p<0,01). Só olhando preço, dava pra concluir que a tese estava confirmada.",
    },
    {
        "n": 5, "type": "virada", "tag": "Virada",
        "title": "A segmentação inverte o sinal",
        "text": "Preço mais alto não virou mais receita: Centro · 1 quarto rende R$6.382/ano, o pior número entre os 8 segmentos elegíveis — atrás até de Meia Praia no mesmo tipo de imóvel.",
    },
    {
        "n": 6, "type": "virada", "tag": "Virada",
        "title": "Cruzar com preço de compra muda tudo",
        "text": "Ao dividir receita pelo preço de compra do VivaReal, 1-quarto perde em qualquer bairro (yield líquido negativo). E um bairro fora do roteiro original, Morretes, aparece disparado na frente com 2 quartos.",
    },
    {
        "n": 7, "type": "correcao", "tag": "Correção",
        "title": "“Maior amostra” estava errada — tinha duplicata inflando o N",
        "text": "Mesmo anúncio, mesmo preço, mesma área, mesmo anunciante — só o ID mudava. Dedupe forte no Morretes/2-quartos: 1.037 → 915. E a alegação de que era “a maior amostra do cruzamento” era simplesmente falsa — corrigida antes de virar argumento no relatório.",
    },
    {
        "n": 8, "type": "correcao", "tag": "Correção da correção",
        "title": "A limpeza só cobriu um segmento — não era comparação justa",
        "text": "O mesmo padrão de duplicata podia afetar os outros 7 segmentos também. Refizemos o dedupe na base VivaReal inteira, antes de segmentar: 8.293 → 7.908 linhas. Só aí o ranking de N ficou correto pros 8 segmentos.",
    },
    {
        "n": 9, "type": "final", "tag": "Posição final",
        "title": "2 quartos em Morretes — yield líquido 1,69% a.a.",
        "text": "Quase 2× o 2º colocado, amostra robusta (914, dedupe correto), preço mediano R$790 mil. Tese dos compactos no Centro: refutada no tipo de imóvel, empate técnico na localização.",
    },
]

def timeline_html():
    items = []
    for it in TIMELINE:
        items.append(f'''      <div class="tl-item {it['type']}">
        <div class="tl-node">{it['n']}</div>
        <div class="tl-card">
          <span class="tl-tag {it['type']}">{it['tag']}</span>
          <div class="tl-title">{it['title']}</div>
          <p class="tl-text">{it['text']}</p>
        </div>
      </div>''')
    return "\n".join(items)

HTML = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Apoio visual — Recomendação Itapema</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --surface: #fcfcfb;
    --plane: #f0efeb;
    --ink: #0b0b0b;
    --ink-2: #52514e;
    --muted: #898781;
    --grid: #e1e0d9;
    --blue: #2a78d6;
    --orange: #eb6834;
    --aqua: #1baf7a;
    --yellow: #eda100;
    --red: #e34948;
    --good: #0ca30c;
    --card: #ffffff;
    --shadow: 0 1px 2px rgba(11,11,11,0.06), 0 8px 24px rgba(11,11,11,0.06);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: var(--plane);
    color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    scroll-behavior: smooth;
  }}
  body {{
    scroll-snap-type: y mandatory;
    overflow-y: scroll;
    height: 100vh;
  }}
  .slide {{
    scroll-snap-align: start;
    min-height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 76px 6vw 36px;
    position: relative;
  }}
  .slide-inner {{
    width: 100%;
    max-width: 1080px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .cue {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    align-self: flex-start;
    background: var(--ink);
    color: #fff;
    font-variant-numeric: tabular-nums;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.02em;
    padding: 6px 12px 6px 10px;
    border-radius: 999px;
  }}
  .cue .dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--orange); }}
  h1 {{ font-size: clamp(28px, 4vw, 44px); line-height: 1.15; margin: 0; letter-spacing: -0.01em; }}
  h2 {{ font-size: clamp(24px, 3.4vw, 36px); line-height: 1.2; margin: 0; letter-spacing: -0.01em; }}
  .sub {{ color: var(--ink-2); font-size: clamp(15px, 1.6vw, 19px); line-height: 1.5; max-width: 760px; margin: 0; }}
  .frame {{
    background: var(--card);
    border: 1px solid var(--grid);
    border-radius: 14px;
    box-shadow: var(--shadow);
    padding: 14px;
  }}
  .frame img {{ display: block; max-width: 100%; max-height: 34vh; width: auto; height: auto; margin: 0 auto; border-radius: 6px; }}
  .frame-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .frame-row .frame {{ flex: 1 1 320px; }}
  .stat-row {{ display: flex; gap: 14px; flex-wrap: wrap; }}
  .stat {{
    background: var(--card);
    border: 1px solid var(--grid);
    border-radius: 12px;
    padding: 14px 18px;
    min-width: 150px;
    flex: 1 1 150px;
  }}
  .stat .n {{ font-size: clamp(22px, 2.6vw, 30px); font-weight: 700; font-variant-numeric: tabular-nums; }}
  .stat .l {{ font-size: 12.5px; color: var(--muted); margin-top: 2px; }}
  .stat.good .n {{ color: var(--good); }}
  .stat.warn .n {{ color: var(--red); }}
  .why {{
    border-left: 3px solid var(--blue);
    background: #eef4fc;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    font-size: 15px;
    color: var(--ink);
    max-width: 760px;
  }}
  .why b {{ color: var(--blue); }}
  ul.list {{ margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 10px; max-width: 720px; }}
  ul.list li {{
    display: flex; gap: 10px; align-items: flex-start;
    font-size: clamp(15px, 1.7vw, 18px); line-height: 1.5; color: var(--ink);
  }}
  ul.list li::before {{
    content: ""; flex: none; width: 8px; height: 8px; margin-top: 8px;
    border-radius: 2px; background: var(--orange);
  }}
  ul.list li > span {{ flex: 1 1 auto; min-width: 0; }}
  .tag {{
    display: inline-block; font-size: 12.5px; font-weight: 700; letter-spacing: 0.03em;
    text-transform: uppercase; padding: 4px 10px; border-radius: 999px;
  }}
  .tag.refutada {{ background: #fbeae9; color: var(--red); }}
  .tag.reco {{ background: #e6f6ee; color: var(--good); }}
  .title-slide {{ align-items: flex-start; text-align: left; }}
  .title-slide .slide-inner {{ align-items: flex-start; }}
  .kicker {{ color: var(--muted); font-size: 14px; letter-spacing: 0.04em; text-transform: uppercase; font-weight: 600; }}
  .closer {{ background: var(--ink); color: #fff; }}
  .closer .sub {{ color: #d8d6cf; }}
  .closer .frame {{ background: #1a1a19; border-color: #383835; }}
  .closer-line {{ font-size: clamp(24px, 3.4vw, 38px); font-weight: 700; line-height: 1.3; }}
  .closer-line .no {{ color: #ff9a86; }}
  .closer-line .yes {{ color: #63e6a5; }}

  /* nav rail */
  #rail {{
    position: fixed; top: 0; right: 0; height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 14px; padding-right: 22px; z-index: 20;
  }}
  .navdot {{
    width: 34px; height: 34px; border-radius: 50%;
    background: var(--card); border: 1px solid var(--grid);
    display: flex; align-items: center; justify-content: center;
    font-size: 10.5px; font-weight: 700; color: var(--muted);
    cursor: pointer; font-variant-numeric: tabular-nums;
    transition: all .15s ease;
  }}
  .navdot:hover {{ border-color: var(--blue); color: var(--blue); }}
  .navdot.active {{ background: var(--blue); border-color: var(--blue); color: #fff; transform: scale(1.12); }}
  .navdot.due {{ box-shadow: 0 0 0 3px rgba(235,104,52,0.35); }}

  /* timer bar */
  #timerbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 30;
    display: flex; align-items: center; gap: 12px;
    padding: 10px 18px; background: rgba(252,252,251,0.92);
    backdrop-filter: blur(6px); border-bottom: 1px solid var(--grid);
  }}
  #timerbar .clock {{
    font-variant-numeric: tabular-nums; font-weight: 700; font-size: 17px;
    background: var(--ink); color: #fff; padding: 5px 10px; border-radius: 8px;
  }}
  #timerbar .clock.over {{ background: var(--red); }}
  #timerbar button {{
    font: inherit; font-weight: 600; font-size: 13px; cursor: pointer;
    border: 1px solid var(--grid); background: var(--card); color: var(--ink);
    padding: 6px 12px; border-radius: 8px;
  }}
  #timerbar button:hover {{ border-color: var(--blue); color: var(--blue); }}
  #timerbar .hint {{ font-size: 12.5px; color: var(--muted); margin-left: auto; }}
  #timerbar .target {{ font-size: 12.5px; color: var(--ink-2); }}
  #timerbar .target b {{ color: var(--ink); }}

  @media (max-width: 720px) {{
    #rail {{ display: none; }}
    .slide {{ padding: 84px 5vw 48px; }}
    #timerbar .hint {{ display: none; }}
  }}

  /* vertical timeline — o caminho até a decisão */
  .process-slide {{ justify-content: flex-start; }}
  .process-slide .slide-inner {{ gap: 10px; height: calc(100vh - 112px); }}
  .timeline-scroll {{
    flex: 1 1 auto; min-height: 0; overflow-y: auto;
    padding: 4px 14px 4px 0; margin-top: 4px;
  }}
  .timeline-scroll::-webkit-scrollbar {{ width: 8px; }}
  .timeline-scroll::-webkit-scrollbar-track {{ background: transparent; }}
  .timeline-scroll::-webkit-scrollbar-thumb {{ background: var(--grid); border-radius: 4px; }}
  .timeline {{ position: relative; padding-left: 42px; }}
  .timeline::before {{
    content: ""; position: absolute; left: 15px; top: 4px; bottom: 4px;
    width: 2px; background: var(--grid);
  }}
  .tl-item {{ position: relative; padding-bottom: 16px; }}
  .tl-item:last-child {{ padding-bottom: 2px; }}
  .tl-node {{
    position: absolute; left: -42px; top: 0; width: 32px; height: 32px;
    border-radius: 50%; background: var(--card); border: 2px solid var(--grid);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 13px; color: var(--ink-2); z-index: 2;
  }}
  .tl-card {{
    border: 1px solid var(--grid); border-radius: 10px;
    padding: 9px 14px 11px; background: var(--card);
  }}
  .tl-tag {{
    display: inline-block; font-size: 10px; font-weight: 800; letter-spacing: 0.04em;
    text-transform: uppercase; padding: 2px 8px; border-radius: 999px; margin-bottom: 4px;
  }}
  .tl-tag.checagem {{ background: #eef4fc; color: var(--blue); }}
  .tl-tag.achado {{ background: #e6f6ee; color: #0f8a5f; }}
  .tl-tag.virada {{ background: #fff6e0; color: #a56a00; }}
  .tl-tag.correcao {{ background: #fbe7de; color: #c34f19; }}
  .tl-title {{ font-size: 15.5px; font-weight: 700; margin: 2px 0 4px; line-height: 1.3; }}
  .tl-text {{ font-size: 13.5px; line-height: 1.48; color: var(--ink-2); margin: 0; }}

  /* correção: destaque forte, bolha preenchida — não esconde */
  .tl-item.correcao .tl-node {{
    background: var(--orange); border-color: var(--orange); color: #fff;
    box-shadow: 0 0 0 4px rgba(235,104,52,0.20);
  }}
  .tl-item.correcao .tl-card {{ border: 1.5px solid var(--orange); background: #fff8f4; }}
  .tl-item.correcao .tl-tag {{ background: var(--orange); color: #fff; }}

  /* nó final: terminal da linha, estilo próprio */
  .tl-item.final .tl-node {{
    background: var(--ink); border-color: var(--ink); color: #fff;
    width: 36px; height: 36px; left: -44px; font-size: 15px;
  }}
  .tl-item.final .tl-card {{ background: var(--ink); border-color: var(--ink); }}
  .tl-item.final .tl-tag {{ background: #63e6a5; color: #0b3d24; }}
  .tl-item.final .tl-title {{ color: #fff; }}
  .tl-item.final .tl-text {{ color: #d8d6cf; }}

  @media (max-width: 720px) {{
    .process-slide .slide-inner {{ height: calc(100vh - 120px); }}
  }}
</style>
</head>
<body>

<div id="timerbar">
  <span class="clock" id="clock">0:00</span>
  <button id="btnToggle">Iniciar</button>
  <button id="btnReset">Zerar</button>
  <span class="target" id="target">Próxima deixa: <b>0:10</b> — caminho até a decisão</span>
  <span class="hint">setas ↑↓ ou clique nos pontos pra navegar</span>
</div>

<div id="rail"></div>

<section class="slide title-slide" data-t="0">
  <div class="slide-inner">
    <span class="cue"><span class="dot"></span>0:00</span>
    <span class="kicker">Hackathon Jovens Talentos AI Builder 2026 — Seazone</span>
    <h1>Recomendação de investimento imobiliário<br>Itapema, SC</h1>
    <p class="sub">Cruzando anúncios de Airbnb (receita) com anúncios de venda do VivaReal (custo de compra), bairro por bairro, tipologia por tipologia — pra responder: no que a Seazone investiria hoje?</p>
    <p class="sub" style="margin-top:8px">por Kaka</p>
  </div>
</section>

<section class="slide process-slide" data-t="10">
  <div class="slide-inner">
    <span class="cue"><span class="dot"></span>0:10</span>
    <h2>O caminho até a decisão</h2>
    <p class="sub" style="margin:0">9 momentos reais da investigação, em ordem — os em laranja são correções que mudaram o rumo da análise.</p>
    <div class="timeline-scroll">
      <div class="timeline">
{timeline_html()}
      </div>
    </div>
  </div>
</section>

<section class="slide" data-t="60">
  <div class="slide-inner">
    <span class="cue"><span class="dot"></span>1:00</span>
    <h2>Sendo honesta com os números</h2>
    <div class="stat-row">
      <div class="stat"><div class="n">~43 anos</div><div class="l">Payback simples (yield bruto)</div></div>
      <div class="stat"><div class="n">~59 anos</div><div class="l">Payback simples (yield líquido)</div></div>
    </div>
    <p class="sub">Não é o imóvel dos sonhos — é a <b>melhor opção relativa</b> dentro do que os dados mostram.</p>
    <ul class="list">
      <li><span>Preço do VivaReal é o <b>anunciado</b>, não o vendido — no Brasil costuma vender mais barato, então o retorno real tende a ser um pouco <b>melhor</b>.</span></li>
      <li><span>Yield líquido descontou só condomínio + IPTU — <b>não</b> descontou taxa de plataforma, limpeza nem gestão, então o retorno real tende a ser um pouco <b>pior</b>.</span></li>
    </ul>
  </div>
</section>

<section class="slide" data-t="78">
  <div class="slide-inner">
    <span class="cue"><span class="dot"></span>1:18</span>
    <h2>Como usei IA — não foi só pedir e aceitar</h2>
    <div class="frame">{img_tag("05", "Divergência entre os dois proxies de ocupação")}</div>
    <ul class="list">
      <li><span>Construí dois jeitos de estimar ocupação e eles <b>não bateram entre si</b> — investiguei se era erro de código, confirmei que não era, documentei como limitação real da análise.</span></li>
      <li><span>Peguei um erro dela: validou a amostra do Morretes de um jeito <b>injusto</b> comparado aos outros bairros. Pedi correção duas vezes até o critério ficar igual pros 8 segmentos.</span></li>
    </ul>
  </div>
</section>

<section class="slide" data-t="105">
  <div class="slide-inner">
    <span class="cue"><span class="dot"></span>1:45</span>
    <h2>Com mais uma semana</h2>
    <ul class="list">
      <li><span>Validaria o proxy de receita <b>contra ocupação real</b> — hoje ele é indireto, baseado em taxa de conversão de review.</span></li>
      <li><span>Estimaria o <b>desconto médio entre preço anunciado e preço de venda</b> em Itapema, pra fechar a conta do retorno com mais precisão.</span></li>
    </ul>
  </div>
</section>

<section class="slide closer" data-t="120">
  <div class="slide-inner">
    <span class="cue" style="background:#fff;color:#0b0b0b"><span class="dot"></span>2:00</span>
    <h2 style="color:#fff">Recomendação final</h2>
    <p class="closer-line"><span class="no">Compacto no Centro não é a aposta certa.</span><br><span class="yes">Dois quartos em Morretes é.</span></p>
    <div class="stat-row">
      <div class="stat" style="background:#242422;border-color:#383835"><div class="n" style="color:#63e6a5">1,69% a.a.</div><div class="l" style="color:#c3c2b7">Yield líquido estimado</div></div>
      <div class="stat" style="background:#242422;border-color:#383835"><div class="n" style="color:#fff">R$ 790 mil</div><div class="l" style="color:#c3c2b7">Preço mediano — Morretes, 2 quartos</div></div>
    </div>
    <p class="sub">Obrigada.</p>
  </div>
</section>

<script>
  const slides = Array.from(document.querySelectorAll('.slide'));
  const rail = document.getElementById('rail');
  const clockEl = document.getElementById('clock');
  const targetEl = document.getElementById('target');
  const btnToggle = document.getElementById('btnToggle');
  const btnReset = document.getElementById('btnReset');

  const cues = slides.map(s => parseInt(s.dataset.t, 10));
  const labels = ['início','caminho até a decisão','honestidade','gráf. 05 (uso de IA)','+1 semana','fechamento'];

  slides.forEach((s, i) => {{
    const d = document.createElement('div');
    d.className = 'navdot';
    const t = cues[i];
    d.textContent = (Math.floor(t/60)) + ':' + String(t%60).padStart(2,'0');
    d.title = labels[i];
    d.addEventListener('click', () => s.scrollIntoView({{behavior:'smooth'}}));
    rail.appendChild(d);
  }});
  const dots = Array.from(rail.children);

  function fmt(s) {{
    const m = Math.floor(s/60), r = s%60;
    return m + ':' + String(r).padStart(2,'0');
  }}

  function nextCue(elapsed) {{
    for (let i=0;i<cues.length;i++) {{
      if (cues[i] > elapsed) return {{i, t: cues[i]}};
    }}
    return null;
  }}

  function updateTarget(elapsed) {{
    const nc = nextCue(elapsed);
    if (nc) {{
      targetEl.innerHTML = 'Próxima deixa: <b>' + fmt(nc.t) + '</b> — ' + labels[nc.i];
    }} else {{
      targetEl.innerHTML = 'Última deixa concluída — fechamento';
    }}
    dots.forEach((d,i) => {{
      d.classList.toggle('due', nc && i === nc.i);
    }});
  }}

  let running = false, elapsed = 0, timer = null;
  function tick() {{
    elapsed += 1;
    clockEl.textContent = fmt(elapsed);
    clockEl.classList.toggle('over', elapsed > 180);
    updateTarget(elapsed);
  }}
  btnToggle.addEventListener('click', () => {{
    running = !running;
    btnToggle.textContent = running ? 'Pausar' : 'Continuar';
    if (running) timer = setInterval(tick, 1000);
    else clearInterval(timer);
  }});
  btnReset.addEventListener('click', () => {{
    running = false; elapsed = 0;
    clearInterval(timer);
    btnToggle.textContent = 'Iniciar';
    clockEl.textContent = '0:00';
    clockEl.classList.remove('over');
    updateTarget(0);
  }});
  updateTarget(0);

  // active-slide highlighting via scroll
  const io = new IntersectionObserver((entries) => {{
    entries.forEach(e => {{
      const idx = slides.indexOf(e.target);
      if (e.isIntersecting && e.intersectionRatio > 0.6) {{
        dots.forEach(d => d.classList.remove('active'));
        if (dots[idx]) dots[idx].classList.add('active');
      }}
    }});
  }}, {{ threshold: [0.6] }});
  slides.forEach(s => io.observe(s));

  // keyboard nav
  document.addEventListener('keydown', (e) => {{
    const activeIdx = dots.findIndex(d => d.classList.contains('active'));
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'PageDown') {{
      e.preventDefault();
      const next = slides[Math.min(activeIdx+1, slides.length-1)];
      next.scrollIntoView({{behavior:'smooth'}});
    }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'PageUp') {{
      e.preventDefault();
      const prev = slides[Math.max(activeIdx-1, 0)];
      prev.scrollIntoView({{behavior:'smooth'}});
    }}
  }});
</script>

</body>
</html>
"""

with open("apoio_visual.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("apoio_visual.html gerado,", len(HTML), "bytes de HTML (antes de contar que as imagens já estão embutidas no tamanho acima)")
import os as _os
print("tamanho final do arquivo:", _os.path.getsize("apoio_visual.html"), "bytes")
