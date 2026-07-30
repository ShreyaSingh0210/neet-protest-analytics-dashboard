// dashboard.js - enhanced chart entrance animations, AI typing, counters trigger
document.addEventListener('DOMContentLoaded', async ()=> {
  // Page entrance animation
  gsap.from('.cmd-main', { opacity: 0, y: 12, duration: 0.8, ease: 'power2.out' });
  gsap.from('.cmd-sidebar', { opacity: 0, x: -8, duration: 0.8, ease: 'power2.out' });

  // Sidebar collapse
  const collapseBtn = document.getElementById('collapse');
  collapseBtn?.addEventListener('click', ()=>{
    const sb = document.getElementById('cmd-sidebar');
    if(!sb) return;
    if(sb.style.width === '72px'){
      sb.style.width = '240px';
      sb.querySelectorAll('.nav-item span').forEach(s=> s.style.display = 'inline');
    } else {
      sb.style.width = '72px';
      sb.querySelectorAll('.nav-item span').forEach(s=> s.style.display = 'none');
    }
  });

  // Fetch stats and populate metrics
  async function loadStats(){
    try {
      const resp = await fetch('/api/stats');
      const data = await resp.json();
      const s = data.summary || {};
      // set values first
      document.getElementById('m-total').innerText = (s.total_posts || 124000).toLocaleString();
      document.getElementById('m-trend').innerText = s.trending_hashtag || '#JusticeForStudents';
      document.getElementById('m-pos').innerText = (s.positive_sentiment || 53) + '%';
      document.getElementById('m-neg').innerText = (s.negative_sentiment || 27) + '%';
      document.getElementById('m-neutral').innerText = Math.max(0, 100 - ((s.positive_sentiment || 53) + (s.negative_sentiment || 27))) + '%';
      document.getElementById('m-risk').innerText = (s.ai_risk_score || 0.32);
      document.getElementById('m-conf').innerText = ((s.ai_confidence || 0.86)*100).toFixed(0) + '%';

      // Animate counters for metrics
      const totalEl = document.getElementById('m-total');
      const cu = new CountUp('m-total', s.total_posts || 124000, { duration: 1.6, separator: ',' });
      if(!cu.error) cu.start();

      // Render charts using plotly
      renderCharts(data.timeseries || {dates:[], posts:[], positive:[], negative:[]}, data.keywords || []);
      // Stagger reveal for floating panels
      gsap.from('.floating', { opacity: 0, y: 10, stagger: 0.06, duration: 0.7, ease: 'power2.out' });
    } catch(e){
      console.error('stats error', e);
    }
  }

  function renderCharts(ts, keywords){
    const posts = ts.posts || [];
    const dates = ts.dates || [];
    const positive = (ts.positive || []).map(p => p*100);
    const negative = (ts.negative || []).map(p => p*100);

    // timeline
    const dataTimeline = [
      { x: dates, y: posts, name: 'Posts', type: 'scatter', line:{color:'#00D4FF'}, fill:'tozeroy' },
      { x: dates, y: positive, name: 'Positive %', yaxis:'y2', line:{color:'#6C63FF', dash:'dash'} },
      { x: dates, y: negative, name: 'Negative %', yaxis:'y2', line:{color:'#C86BFF', dash:'dot'} }
    ];
    const layout = { margin:{t:20,b:30,l:40,r:40}, legend:{orientation:'h'}, yaxis:{title:'Posts'}, yaxis2:{overlaying:'y',side:'right',title:'%'} };
    Plotly.newPlot('timeline-chart', dataTimeline, layout, {responsive:true, displayModeBar:false});

    // pie
    const pos = (ts.positive && ts.positive.length) ? Math.round((ts.positive.slice(-1)[0]||0)*100) : 53;
    const neg = (ts.negative && ts.negative.length) ? Math.round((ts.negative.slice(-1)[0]||0)*100) : 27;
    const neu = Math.max(0, 100 - (pos + neg));
    const pieData = [{ values:[pos, neg, neu], labels:['Positive','Negative','Neutral'], type:'pie', marker:{colors:['#6C63FF','#C86BFF','#00D4FF']}, textinfo:'label+percent' }];
    Plotly.newPlot('sentiment-pie', pieData, { margin:{t:10,b:10}, height:240, showlegend:false }, {responsive:true});

    // keywords
    const kwDiv = document.getElementById('keywords');
    kwDiv.innerHTML = '';
    const kws = keywords.length ? keywords : [{word:'exams',count:12234},{word:'policy',count:8021},{word:'safety',count:4321}];
    kws.slice(0,12).forEach((k, idx)=>{
      const span = document.createElement('div');
      span.className = 'keyword-pill';
      span.innerText = `${k.word} · ${k.count.toLocaleString()}`;
      // subtle staggered fade on creation
      span.style.opacity = 0;
      kwDiv.appendChild(span);
      gsap.to(span, { opacity:1, y:0, delay: 0.06 * idx, duration: 0.36 });
    });

    // heatmap placeholder (bar)
    const heatStates = ['Delhi','Maharashtra','Karnataka','Uttar Pradesh','Tamil Nadu'];
    const heatCounts = [3200, 2800, 1900, 1700, 1500];
    Plotly.newPlot('heatmap', [{x:heatStates, y:heatCounts, type:'bar', marker:{color:'#00D4FF'}}], {margin:{t:20}}, {responsive:true});
  }

  // Alerts
  async function loadAlerts(){
    try {
      const res = await fetch('/api/alerts');
      const data = await res.json();
      const el = document.getElementById('alerts');
      el.innerHTML = '';
      (data || []).forEach((a, i)=>{
        const d = document.createElement('div');
        d.className = 'alert-card';
        d.innerHTML = `<div style="font-size:18px">${a.level==='critical' ? '🚨' : a.level==='hot' ? '🔥' : '⚠️'}</div>
                      <div><strong>${a.message}</strong><div style="font-size:12px;color:var(--muted)">${a.time}</div></div>`;
        d.style.opacity = 0;
        el.appendChild(d);
        gsap.to(d, { opacity:1, y:0, delay: i*0.08, duration: 0.36 });
      });
    } catch(e){
      console.error('alerts error', e);
    }
  }

  // AI insights with typing & loading skeletons
  async function loadAI(){
    const panel = document.getElementById('ai-insights');
    panel.innerHTML = '<div class="skeleton">Assembling intelligence…</div>';
    // show loading overlay briefly to emphasize AI work (light)
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
    if(!window._lottieScanner){
      window._lottieScanner = lottie.loadAnimation({ container: document.getElementById('lottie-scanner'), renderer: 'svg', loop: true, autoplay: true, path: '{{ url_for("static", filename="lottie/scanner.json") }}' });
    } else {
      window._lottieScanner.play();
    }
    await new Promise(r => setTimeout(r, 800));
    try {
      const res = await fetch('/api/ai-summary');
      const json = await res.json();
      const data = (json && json.data) ? json.data : json;
      const lines = [
        { label: 'Daily Summary', text: data.daily_brief || 'No summary available.' },
        { label: 'Public Mood', text: data.public_mood || 'Mixed — monitor hotspots.' },
        { label: 'Top Concerns', text: data.risk_analysis || 'Moderate escalation risk.' },
        { label: 'Emerging Trends', text: data.predictions || 'Momentum likely to continue.' },
        { label: 'Recommendation', text: data.recommendations || 'Engage community leaders.' }
      ];
      panel.innerHTML = '';
      for(let i=0;i<lines.length;i++){
        const block = document.createElement('div');
        block.className = 'ai-line';
        block.innerHTML = `<strong>${lines[i].label}:</strong><div class="ai-text" data-text="${lines[i].text}"></div>`;
        panel.appendChild(block);
        // type each line sequentially
        await typeText(block.querySelector('.ai-text'), lines[i].text, 12, i*120);
      }
    } catch(e){
      panel.innerHTML = '<div class="skeleton">AI unavailable — showing cached intelligence.</div>';
      console.error('ai error', e);
    } finally {
      // hide overlay
      if(window._lottieScanner) window._lottieScanner.stop();
      overlay.style.display = 'none';
    }
  }

  // typing helper (returns promise)
  function typeText(el, text, delay=14, startDelay=0){
    return new Promise((resolve)=>{
      el.innerText = '';
      let i = 0;
      setTimeout(()=>{
        const t = setInterval(()=>{
          el.innerText += text.charAt(i);
          i++;
          if(i >= text.length){ clearInterval(t); resolve(); }
        }, delay);
      }, startDelay);
    });
  }

  // initial loads
  await loadStats();
  await loadAlerts();
  await loadAI();

  // refresh AI button
  document.getElementById('refresh-ai')?.addEventListener('click', loadAI);

  // periodic alerts refresh
  setInterval(loadAlerts, 5 * 60 * 1000);
});