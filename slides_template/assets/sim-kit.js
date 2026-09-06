/*
  Robot Rockstars sim kit -- the shared JavaScript behind every interactive
  simulation in the decks under slides/.

  Generalized from the `NM` helper that name-your-moves.qmd already proved out.
  It replaces, across ~48 sims: 63 unnamespaced window globals, 47 hand-rolled
  requestAnimationFrame loops (each re-implementing the same dt clamp, fixed
  substep and restart guard), 410 bare setAttribute calls and ~20 copies of the
  same hand-drawn robot.

  Loaded into <head> for every deck via include-in-header in _quarto.yml, so it
  MUST only define functions here; the one thing it touches is document.body,
  and only on DOMContentLoaded. Styling lives in rockstars-sims.scss.
*/
(function () {
  "use strict";

  var actions = {};   // name -> handler, registered with SIM.def
  var running = {};   // loop key -> requestAnimationFrame id

  var SIM = {

    /* -- DOM ----------------------------------------------------------
       All are null-safe: a sim on a slide that was cut should go quiet,
       not throw and take the rest of the deck's scripts down with it. */

    el: function (id) { return document.getElementById(id); },

    set: function (id, attr, val) {
      var e = SIM.el(id);
      if (e) e.setAttribute(attr, val);
      return e;
    },

    tf: function (id, transform) { return SIM.set(id, 'transform', transform); },

    text: function (id, s) {
      var e = SIM.el(id);
      if (e) e.textContent = s;
      return e;
    },

    html: function (id, s) {
      var e = SIM.el(id);
      if (e) e.innerHTML = s;
      return e;
    },

    /* The coach message line. Tone is a class -- 'good', 'bad' or 'note' --
       so no sim has to know a brand colour. */
    msg: function (id, s, tone) {
      var e = SIM.el(id);
      if (!e) return null;
      e.innerHTML = s;
      e.classList.remove('good', 'bad', 'note');
      if (tone) e.classList.add(tone);
      return e;
    },

    /* Recolour an SVG label by swapping its tone class -- see .label.teal /
       .coral / .purple / .navy / .dim in rockstars-sims.scss. Use this rather
       than setAttribute('fill', '#...'): the stylesheet's `fill` wins over a
       presentation attribute, so setting the attribute would do nothing. */
    tone: function (id, t) {
      var e = SIM.el(id);
      if (!e) return null;
      e.classList.remove('teal', 'coral', 'purple', 'navy', 'dim');
      if (t) e.classList.add(t);
      return e;
    },

    /* -- Geometry -----------------------------------------------------
       Dial maths, lifted from name-your-moves. 0 degrees is up and angles
       run clockwise, matching both the gyro and the field map. */

    polar: function (deg, R) {
      var r = deg * Math.PI / 180;
      return (R * Math.sin(r)).toFixed(1) + ' ' + (-R * Math.cos(r)).toFixed(1);
    },

    arcD: function (a1, a2, R) {
      if (a2 - a1 < 0.5) return '';
      return 'M ' + SIM.polar(a1, R) +
             ' A ' + R + ' ' + R + ' 0 ' + ((a2 - a1) > 180 ? 1 : 0) + ' 1 ' +
             SIM.polar(a2, R);
    },

    /* A growing polyline, for the speed and error traces:
         var t = SIM.trace('wsTrace');
         t.clear(); t.push(x, y); */
    trace: function (id) {
      var pts = [];
      return {
        clear: function () { pts = []; SIM.set(id, 'points', ''); return this; },
        push: function (x, y) {
          pts.push(x.toFixed(1) + ',' + y.toFixed(1));
          SIM.set(id, 'points', pts.join(' '));
          return this;
        },
        points: function () { return pts; }
      };
    },

    /* -- The animation driver -----------------------------------------

         SIM.loop('ws', {
           dt:   0.008,                 // fixed physics substep, in seconds
           step: function (dt) { ... }, // one substep; return true when finished
           draw: function () { ... },   // once per frame, after the substeps
           done: function () { ... }    // once, after step returns true
         });

       Physics advances in fixed `dt` substeps while drawing stays on the
       frame, so a sim behaves the same on a 60 Hz laptop and a 144 Hz monitor.
       The frame delta is clamped at 50 ms so a tab that was backgrounded
       resumes instead of teleporting.

       `key` identifies the sim. Calling loop again with a key already running
       cancels the old run first, so a second click restarts cleanly rather
       than racing two loops against each other -- the guard every sim used to
       spell out as `if (raf) cancelAnimationFrame(raf)`. */

    loop: function (key, opts) {
      SIM.stop(key);
      var sd = opts.dt || 0.016;
      var last = null, finished = false;

      function frame(now) {
        var elapsed = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
        last = now;
        var n = Math.max(1, Math.round(elapsed / sd));
        for (var i = 0; i < n && !finished; i++) {
          if (opts.step(sd)) finished = true;
        }
        if (opts.draw) opts.draw();
        if (finished) {
          delete running[key];
          if (opts.done) opts.done();
          return;
        }
        running[key] = requestAnimationFrame(frame);
      }

      running[key] = requestAnimationFrame(frame);
    },

    stop: function (key) {
      if (running[key]) {
        cancelAnimationFrame(running[key]);
        delete running[key];
      }
    },

    /* -- Actions ------------------------------------------------------
       SIM.def('wsRun', fn) registers the handler behind data-sim="wsRun".
       One delegated listener (below) then serves every button in every deck,
       so no sim needs a window global. Pass a value with data-sim-arg:

         <button class="sim-btn" data-sim="ptRun" data-sim-arg="loop">

       The handler is called (arg, buttonElement), so a row of preset buttons
       can mark the one that was pressed:  SIM.def('setSides', function (n, btn) {…})

       Sliders use data-sim-input and receive the value. A slider that also
       carries data-sim-arg names a channel, and its handler is called
       (channel, value) -- the shape a panel of sliders sharing one setter
       already had:

         <input type="range" data-sim-input="ggSet">                  -> ggSet(value)
         <input type="range" data-sim-input="lfSet" data-sim-arg="kp"> -> lfSet('kp', value) */

    def: function (name, fn) { actions[name] = fn; return fn; },

    /* True when a name has a handler. A button whose data-sim points at nothing
       is silently dead, so this is what a check can assert on. */
    has: function (name) { return Object.prototype.hasOwnProperty.call(actions, name); },

    run: function (name, arg, el) {
      if (!actions[name]) return;
      /* data-* attributes are always strings, but most handlers were written
         against a numeric literal (setDial(90), lfSet(3)). Coerce anything
         fully numeric so they still get a number; real words pass through. */
      if (typeof arg === 'string' && arg !== '' && !isNaN(arg)) arg = Number(arg);
      /* The control that fired is passed through as the second argument --
         the handlers that used to be written `onclick="setPiSides(4, this)"`
         need it to mark themselves selected. */
      return actions[name](arg, el);
    }
  };

  /* One click listener for the whole deck. `closest` lets a label, an emoji
     or a <code> span inside a button carry the click. */
  document.addEventListener('click', function (ev) {
    var t = ev.target && ev.target.closest && ev.target.closest('[data-sim]');
    if (!t) return;
    SIM.run(t.getAttribute('data-sim'), t.getAttribute('data-sim-arg'), t);
  });

  document.addEventListener('input', function (ev) {
    var t = ev.target;
    if (!t || !t.getAttribute) return;
    var name = t.getAttribute('data-sim-input');
    if (!name || !actions[name]) return;
    var channel = t.getAttribute('data-sim-arg');
    if (channel === null) SIM.run(name, t.value);
    else actions[name](channel, t.value);
  });

  /* -- The shared robot -----------------------------------------------
     Drawn once here instead of ~20 times across six decks. Both glyphs point
     up (-y) and rotate about their own origin, so a sim positions one with
     translate() and steers it with rotate(). Tint the body per sim with the
     --bot custom property:

       <g id="ptBot"><use href="#sim-bot-mini" style="--bot:#FF7A5C"/></g>

     #sim-bot carries wheels and is for close-ups; #sim-bot-mini drops them and
     stays legible when scaled down onto a field or a track. */

  var DEFS =
    '<svg id="sim-defs" width="0" height="0" aria-hidden="true" style="position:absolute">' +
      '<defs>' +
        '<g id="sim-bot">' +
          '<rect x="-14" y="-30" width="28" height="54" rx="8" fill="var(--bot,#1C355E)"/>' +
          '<rect x="-19" y="-21" width="6" height="14" rx="3" fill="#1C355E"/>' +
          '<rect x="13" y="-21" width="6" height="14" rx="3" fill="#1C355E"/>' +
          '<rect x="-19" y="6" width="6" height="14" rx="3" fill="#1C355E"/>' +
          '<rect x="13" y="6" width="6" height="14" rx="3" fill="#1C355E"/>' +
          '<path d="M -8 -12 L 0 -23 L 8 -12 Z" fill="#fff" opacity="0.9"/>' +
          '<circle cy="-30" r="4" fill="#FFD500"/>' +
        '</g>' +
        '<g id="sim-bot-mini">' +
          '<rect x="-14" y="-30" width="28" height="54" rx="8" fill="var(--bot,#1C355E)"/>' +
          '<path d="M -8 -12 L 0 -23 L 8 -12 Z" fill="#fff" opacity="0.9"/>' +
          '<circle cy="-30" r="4" fill="#FFD500"/>' +
        '</g>' +
        '<marker id="sim-arrow" viewBox="0 0 10 10" refX="9" refY="5" ' +
                'markerWidth="6" markerHeight="6" orient="auto-start-reverse">' +
          '<path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/>' +
        '</marker>' +
      '</defs>' +
    '</svg>';

  function install() {
    if (!document.getElementById('sim-defs')) {
      document.body.insertAdjacentHTML('afterbegin', DEFS);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }

  window.SIM = SIM;
})();
