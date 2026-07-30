{% extends "base.html" %}
{% block body %}
<section class="cinema-hero">
  <canvas id="grid-canvas" class="grid-canvas" aria-hidden="true"></canvas>
  <div id="particles-container" aria-hidden="true"></div>

  <nav class="top-nav glass-nav" data-aos="fade-down">
    <div class="brand">
      <img src="{{ url_for('static', filename='img/logo.svg') }}" alt="NEET Analytics logo">
      <div class="brand-name">NEET Protest Analytics</div>
    </div>
    <div class="nav-actions">
      <a class="nav-link" href="#">About</a>
      <a class="nav-link" href="#">Docs</a>
      <a class="nav-link" href="#">GitHub</a>
    </div>
  </nav>

  <div class="hero-inner">
    <div class="hero-left" data-aos="fade-up" data-aos-delay="120">
      <h1 class="hero-title">Data Behind the Movement.</h1>
      <p class="hero-sub">
        <span id="typed-line" class="typed-line">AI-powered intelligence platform analysing the NEET Protest 2026.</span>
      </p>

      <div class="hero-counters" aria-hidden="true">
        <div class="counter card-glass">
          <div class="counter-label">Posts Analysed</div>
          <div class="counter-value" id="cnt-posts">—</div>
        </div>
        <div class="counter card-glass">
          <div class="counter-label">AI Insights</div>
          <div class="counter-value" id="cnt-ai">—</div>
        </div>
        <div class="counter card-glass">
          <div class="counter-label">States Monitored</div>
          <div class="counter-value" id="cnt-states">—</div>
        </div>
        <div class="counter card-glass">
          <div class="counter-label">Live Trends</div>
          <div class="counter-value" id="cnt-trends">—</div>
        </div>
      </div>

      <div class="hero-ctas">
        <button id="enter-btn" class="btn-primary btn-glow">Enter Command Centre <i class="bi bi-arrow-right-short"></i></button>
        <a href="#learn" class="btn-ghost">Learn more</a>
      </div>
    </div>

    <div class="hero-right" data-aos="fade-up" data-aos-delay="220">
      <div class="card-glow-panel floating" id="hero-panel">
        <div class="panel-top">
          <div class="chip">Live Sentiment</div>
          <div class="chip subtle">Realtime</div>
        </div>
        <div class="sentiment-chart" id="hero-spark" role="img" aria-label="Sentiment sparkline"></div>
        <div class="panel-footer">Updated <span id="hero-update">just now</span></div>
      </div>
    </div>
  </div>

  <footer class="landing-footer">
    <div>© 2026 NEET Protest Analytics</div>
    <div>Built for clarity • Privacy-first</div>
  </footer>
</section>
{% endblock %}

{% block body_extra %}
<script>
  // Particle and grid already initialized in main.js; we only add smaller per-page logic here.

  // Hero typing (improved with cursor)
  (function typing(){
    const el = document.getElementById('typed-line');
    const text = el.innerText;
    el.innerText = '';
    const cursor = document.createElement('span');
    cursor.className = 'typed-cursor';
    cursor.innerText = '|';
    el.parentNode.appendChild(cursor);
    let i = 0;
    const speed = 14;
    function step(){
      if(i < text.length){
        el.innerText += text.charAt(i);
        i++;
        setTimeout(step, speed + (Math.random()*6));
      } else {
        setTimeout(()=> cursor.remove(), 400);
      }
    }
    setTimeout(step, 200);
  })();

  // Enter logic: show AI scanning overlay, play Lottie, then GSAP transition to dashboard
  document.getElementById('enter-btn').addEventListener('click', async (e)=>{
    e.preventDefault();
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
    // initialize lottie scanning animation (only once)
    if(!window._lottieScanner){
      window._lottieScanner = lottie.loadAnimation({
        container: document.getElementById('lottie-scanner'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '{{ url_for("static", filename="lottie/scanner.json") }}'
      });
    } else {
      window._lottieScanner.play();
    }
    // small simulated scan duration
    await new Promise(r => setTimeout(r, 1600));
    // page transition
    gsap.to('.hero-inner', { opacity: 0, scale: 0.96, duration: 0.8, ease: 'power3.inOut' });
    gsap.to('.top-nav', { opacity: 0, duration: 0.6 });
    await new Promise(r => setTimeout(r, 700));
    window.location.href = '/dashboard/';
  });

  // If auto navigation is desired after a delay, you may enable below:
  // setTimeout(()=> document.getElementById('enter-btn').click(), 3000);
</script>
{% endblock %}