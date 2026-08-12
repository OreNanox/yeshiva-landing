(function () {
  "use strict";

  /* ============================================================
     חיבור הטופס
     ------------------------------------------------------------
     הדביקו כאן כתובת שמקבלת POST עם JSON — Google Apps Script,
     Make, Zapier או שרת משלכם. כל עוד השדה ריק, הטופס נופל
     חזרה לפתיחת דוא״ל מהמכשיר של הנרשם.
     ============================================================ */
  var SUBMIT_ENDPOINT = "";
  var FALLBACK_EMAIL  = "info@yarenunissim.com";

  var form       = document.getElementById("applyForm");
  if (!form) { return; }

  var status     = document.getElementById("status");
  var done       = document.getElementById("done");
  var submitBtn  = document.getElementById("submitBtn");
  var about      = document.getElementById("about");
  var aboutCount = document.getElementById("aboutCount");
  var source     = document.getElementById("source");
  var otherField = document.getElementById("sourceOtherField");
  var otherInput = document.getElementById("sourceOther");

  var LABELS = {
    fullName: "שם ושם משפחה",
    phone: "טלפון",
    age: "גיל",
    occupation: "עיסוק היום",
    address: "כתובת",
    about: "ספר על עצמך",
    why: "למה מעניין אותך להיכנס לישיבה",
    source: "איך הגעת אלינו"
  };

  function countWords(text) {
    var t = text.trim();
    return t ? t.split(/\s+/).length : 0;
  }

  about.addEventListener("input", function () {
    var n = countWords(about.value);
    aboutCount.textContent = n + (n === 1 ? " מילה" : " מילים");
    aboutCount.classList.toggle("over", n > 200);
  });

  source.addEventListener("change", function () {
    var isOther = source.value === "אחר";
    otherField.hidden = !isOther;
    otherInput.required = isOther;
    if (isOther) { otherInput.focus(); }
  });

  function say(message) {
    status.textContent = message;
    status.classList.add("show");
  }

  function firstInvalid() {
    var keys = ["fullName", "phone", "age", "occupation", "address", "about", "why", "source"];
    for (var i = 0; i < keys.length; i++) {
      if (!form[keys[i]].value.trim()) { return form[keys[i]]; }
    }
    if (source.value === "אחר" && !otherInput.value.trim()) { return otherInput; }
    if (form.phone.value.replace(/\D/g, "").length < 9) { return form.phone; }
    return null;
  }

  function collect() {
    var data = {};
    Object.keys(LABELS).forEach(function (k) { data[k] = form[k].value.trim(); });
    if (data.source === "אחר") { data.source = "אחר — " + otherInput.value.trim(); }
    return data;
  }

  function asText(data) {
    return Object.keys(data).map(function (k) { return LABELS[k] + ": " + data[k]; }).join("\n\n");
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    status.classList.remove("show");

    var bad = firstInvalid();
    if (bad) {
      if (bad === form.phone && bad.value.trim()) {
        say("מספר הטלפון קצר מדי. בדקו אותו שוב.");
      } else if (bad === otherInput) {
        say("כתבו לנו איך הגעתם אלינו.");
      } else {
        say("חסר למלא: " + (LABELS[bad.name] || "אחד השדות") + ".");
      }
      bad.focus();
      return;
    }

    var data = collect();
    submitBtn.disabled = true;
    submitBtn.textContent = "שולח…";

    function succeed() {
      form.style.display = "none";
      done.classList.add("show");
      done.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function fallbackToEmail() {
      var href = "mailto:" + FALLBACK_EMAIL +
                 "?subject=" + encodeURIComponent("מועמדות לישיבה — " + data.fullName) +
                 "&body=" + encodeURIComponent(asText(data));
      window.location.href = href;
      submitBtn.disabled = false;
      submitBtn.textContent = "שליחת המועמדות";
      say("נפתח אצלך חלון דוא״ל עם הפרטים. שלחו אותו ונקבל את הבקשה.");
    }

    if (!SUBMIT_ENDPOINT) { fallbackToEmail(); return; }

    fetch(SUBMIT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (res) {
      if (!res.ok) { throw new Error("bad status"); }
      succeed();
    }).catch(fallbackToEmail);
  });
})();
