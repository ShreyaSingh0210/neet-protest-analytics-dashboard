// main.js - enhanced animations & micro-interactions (landing + global)
// Uses GSAP, CountUp, tsParticles, lottie (already loaded in base)

(function(){
  // performant cursor glow using requestAnimationFrame
  const glow = document.getElementById('cursor-glow');
  let mouseX = window.innerWidth/2, mouseY = window.innerHeight/2;
  let cx = mouseX, cy = mouseY;
  function onMove(e){ mouseX = e.clientX; mouseY = e.clientY; }
  window.addEventListener('mousemove', onMove, {passive:true});
  function animLoop(){
    cx += (mouseX - cx) * 0.18;
    cy += (mouseY - cy) * 0.18;
    if(glow){
      glow.style.transform = `translate(${cx}px, ${cy}px)`;
    }
    requestAnimationFrame(animLoop);
  }
  animLoop();

  // tsParticles background for all pages (if element present)
  if(document.getElementById('particles-container')){
    tsParticles.load("particles-container", {
      fullScreen: { zIndex: 0 },
      particles: {
        number: { value: 45 },
        color: { value: ["#00D4FF", "#6C63FF", "#C86BFF"] },
        opacity: { value: 0.12 },
        size: { value: { min: 1, max: 6 } },
        links: { enable: true, color: "#6C63FF", distance: 140, opacity: 0.04 },
        move: { speed: 0.5 }
      },
      interactivity: { events: { onHover: { enable: true, mode: "repulse" } } }
    });
  }

  // grid canvas for landing (already lightweight)
  (function gridInit(){
    const canvas = document.getElementById('grid-canvas');
    if(!canvas) return;
    const ctx = canvas.getContext('2d');
    function resize(){ canvas.width = innerWidth; canvas.height = innerHeight; }
    resize(); window.addEventListener('resize', resize);
    let t = 0;
    function frame(){
      t += 0.32;
      ctx.clearRect(0,0,canvas.width,canvas.height);
      const spacing = 84;
      ctx.strokeStyle = 'rgba(108,99,255,0.04)';
      ctx.lineWidth = 1;
      for(let x=0; x<canvas.width; x+=spacing){
        const offset = Math.sin((x/220)+t) * 6;
        ctx.beginPath(); ctx.moveTo(x, 0 + offset); ctx.lineTo(x, canvas.height + offset); ctx.stroke();
      }
      for(let y=0; y<canvas.height; y+=spacing){
        const offset = Math.cos((y/220)+t) * 6;
        ctx.beginPath(); ctx.moveTo(0 + offset, y); ctx.lineTo(canvas.width + offset, y); ctx.stroke();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  })();

  // small stagger entrance for glass cards to avoid initial heavy paint
  gsap.from('.card-glass', { opacity: 0, y: 10, stagger: 0.04, duration: 0.7, ease:'power2.out' });

  // initialize hero sparkline if present (data fetched by landing script)
  // Setup lazy counters that start when visible
  const counters = document.querySelectorAll('.counter .counter-value, .m-value');
  const counterObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
      if(!entry.isIntersecting) return;
      const el = entry.target;
      if(el.dataset.counted) return;
      el.dataset.counted = '1';
      // pick numeric from text, default fallback
      let value = parseInt(el.textContent.replace(/[^\d]/g,'')) || 0;
      // decide target from dataset or data fetched values will replace later
      // Use CountUp for fancy effect
      const opts = { duration: 1.4, separator: ',' };
      const c = new CountUp(el.id || el, value, opts);
      // if element already has digits replaced by JS, CountUp will run; else we simply fade in
      try { if(c.error) { el.style.opacity=1; } else c.start(); } catch(e){ el.style.opacity=1; }
    });
  }, { threshold: 0.35 });
  counters.forEach(c => counterObserver.observe(c));

  // small micro-interaction: button glows
  document.querySelectorAll('.btn-primary, .btn-ghost, .icon-btn').forEach(btn=>{
    btn.addEventListener('mouseenter', ()=> gsap.to(btn, { boxShadow: "0 20px 60px rgba(108,99,255,0.12)", scale:1.02, duration:0.16 }));
    btn.addEventListener('mouseleave', ()=> gsap.to(btn, { boxShadow: "0 8px 30px rgba(2,6,23,0.55)", scale:1, duration:0.16 }));
  });

  // setup the loading overlay lottie without playing (prefetch)
  try {
    window._lottieScannerPrefetch = lottie.loadAnimation({
      container: document.createElement('div'), // dummy container just to cache
      renderer: 'svg',
      loop: true,
      autoplay: false,
      path: '{{ url_for("static", filename="lottie/scanner.json") }}'
    });
    window._lottieScannerPrefetch.stop();
  } catch(e){ /* ignore */ }

})();