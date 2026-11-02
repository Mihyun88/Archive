/* 🧪 실거래 랩 (테스트) — 국토부 실거래 + 서울시 정비사업 통계 + 브이월드 토지 정보
   브이월드 키는 mihyun88.github.io 도메인에 묶여 있어 다른 사이트에서는 동작하지 않음 */
(function(){
  const VW_KEY = "7708EC8A-2B5C-43F7-A078-A497EE9AADBE", VW_DOMAIN = "https://mihyun88.github.io";
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const won = m => { if (m == null) return "–"; const e = Math.floor(m/10000), r = Math.round(m%10000); return e ? `${e}억${r ? " " + r.toLocaleString() : ""}` : `${r.toLocaleString()}만`; };
  let D = null, loading = null;

  // ---------- 브이월드 호출: fetch → 안 되면 JSONP ----------
  let jsn = 0;
  function jsonp(url){
    return new Promise((res, rej) => {
      const cb = "__vw" + (++jsn) + Date.now(), s = document.createElement("script");
      const t = setTimeout(() => { cleanup(); rej(new Error("응답 없음(시간 초과)")); }, 12000);
      function cleanup(){ clearTimeout(t); delete window[cb]; s.remove(); }
      window[cb] = d => { cleanup(); res(d); };
      s.onerror = () => { cleanup(); rej(new Error("불러오기 실패")); };
      s.src = url + "&callback=" + cb; document.head.appendChild(s);
    });
  }
  async function vw(path, params){
    const q = new URLSearchParams({ ...params, format: "json", key: VW_KEY, domain: VW_DOMAIN });
    const url = `https://api.vworld.kr/${path}?${q}`;
    try { const r = await fetch(url); if (!r.ok) throw 0; return await r.json(); }
    catch { return jsonp(url); }
  }

  // ---------- 주소 조회 ----------
  const HOT = { UQQ600: "토지거래허가구역", UDT100: "정비구역", UDJ100: "정비예정구역", UDJ200: "정비계획 수립 중", UDA100: "재정비촉진지구", UDK200: "소규모주택정비 관리지역", UDK300: "소규모주택정비 사업시행구역", UQQ300: "지구단위계획구역" };
  async function lookup(addr){
    const out = $("lab-res"); out.innerHTML = `<p class="sub">조회 중이에요…</p>`;
    try {
      const s = await vw("req/search", { service: "search", request: "search", version: "2.0", size: "1", query: addr, type: "address", category: "parcel", errorformat: "json" });
      const it = s?.response?.result?.items?.[0];
      if (!it) { out.innerHTML = `<p class="note">주소를 찾지 못했어요. "서대문구 북아현동 3-66"처럼 동과 번지까지 넣어주세요. (상태: ${esc(s?.response?.status || "알 수 없음")})</p>`; return; }
      const pnu = it.id, y = new Date().getFullYear();
      const [lu, pr, ch] = await Promise.all([
        vw("ned/data/getLandUseAttr", { pnu, numOfRows: "100", pageNo: "1" }).catch(e => ({ err: e.message })),
        vw("ned/data/getIndvdLandPriceAttr", { pnu, stdrYear: String(y), numOfRows: "10", pageNo: "1" }).catch(e => ({ err: e.message })),
        vw("ned/data/getLandCharacteristics", { pnu, stdrYear: String(y), numOfRows: "10", pageNo: "1" }).catch(e => ({ err: e.message }))
      ]);
      render(it, lu?.landUses?.field || [], pr?.indvdLandPrices?.field?.[0], ch?.landCharacteristicss?.field?.[0], [lu, pr, ch].filter(x => x?.err).map(x => x.err));
    } catch (e) {
      out.innerHTML = `<p class="note">브이월드에 연결하지 못했어요 (${esc(e.message)}). 잠시 뒤 다시 눌러보고, 계속 안 되면 이 문구를 캡처해서 알려주세요.</p>`;
    }
  }
  function render(it, uses, price, chr, errs){
    const pick = c => uses.filter(u => u.prposAreaDstrcCode === c);
    const zone = uses.filter(u => /^UQA\d{3}$/.test(u.prposAreaDstrcCode) && u.cnflcAtNm !== "접함").map(u => u.prposAreaDstrcCodeNm);
    const touch = uses.filter(u => /^UQA\d{3}$/.test(u.prposAreaDstrcCode) && u.cnflcAtNm === "접함").map(u => u.prposAreaDstrcCodeNm);
    const p = price ? +price.pblntfPclnd : chr ? +chr.pblntfPclnd : null;
    const ar = chr ? +chr.lndpclAr : null;
    const flags = Object.entries(HOT).map(([c, nm]) => { const f = pick(c); return f.length ? `<div class="lab-flag hot"><b>${esc(nm)} ${esc(f[0].cnflcAtNm)}</b><span>${f.map(x => esc(x.registDt)).join(" · ")} 등록</span></div>` : ""; }).join("");
    const isZone = ["UDT100","UDJ100","UDJ200","UDA100","UDK200","UDK300"].some(c => pick(c).length);
    const rest = uses.filter(u => !HOT[u.prposAreaDstrcCode] && !/^UQA/.test(u.prposAreaDstrcCode)).map(u => `${esc(u.prposAreaDstrcCodeNm)}(${esc(u.cnflcAtNm)})`);
    // 같은 지번 빌라 거래
    const par = it.address.parcel || "", m = par.match(/([가-힣0-9]+(?:동\d*가|동|가))\s+(?:산\s*)?(\d+(?:-\d+)?)$/);
    const same = m && D ? D.trades.filter(t => t[1] === m[1] && t[2] === m[2]) : [];
    $("lab-res").innerHTML = `
      <div class="lab-card">
        <div class="lab-addr"><b>${esc(par)}</b><span>${esc(it.address.road || "")} · 필지번호 ${esc(it.id)}</span></div>
        <div class="lab-kpi">
          <div><span>용도지역</span><b>${esc(zone.join(", ") || "확인 안 됨")}</b><small>${touch.length ? esc(touch.join(", ")) + "과 접함" : "&nbsp;"}</small></div>
          <div><span>${price ? esc(price.stdrYear) : ""} 공시지가</span><b>${p ? Math.round(p/10000).toLocaleString() + "만 원/㎡" : "–"}</b><small>${p ? "평당 약 " + Math.round(p*3.3058/10000).toLocaleString() + "만 원" + (price?.stdLandAt === "Y" ? " · 표준지" : "") : "올해 자료가 아직 없을 수 있어요"}</small></div>
          <div><span>면적 · 지목</span><b>${ar ? ar.toLocaleString() + "㎡ · " + esc(chr.lndcgrCodeNm) : "–"}</b><small>${ar ? "약 " + Math.round(ar/3.3058).toLocaleString() + "평 · " + esc(chr.tpgrphHgCodeNm) + " · " + esc(chr.tpgrphFrmCodeNm) : "&nbsp;"}</small></div>
          <div><span>도로 · 이용</span><b>${chr ? esc(chr.roadSideCodeNm) : "–"}</b><small>${chr ? esc(chr.ladUseSittnNm) : "&nbsp;"}</small></div>
        </div>
        <div class="lab-flags">${flags || ""}${isZone ? "" : `<div class="lab-flag"><b>정비구역 아님</b><span>정비구역·정비예정구역 표시가 없어요</span></div>`}</div>
        ${rest.length ? `<p class="sub">그 밖에: ${rest.join(" · ")}</p>` : ""}
        ${errs.length ? `<p class="note">일부 정보를 못 불러왔어요: ${esc(errs.join(", "))}</p>` : ""}
        <h3 class="lab-h3">이 지번 빌라 거래 (최근 13개월)</h3>
        ${same.length ? `<div class="tw"><table><thead><tr><th>날짜</th><th>건물</th><th class="num">금액</th><th class="num">전용</th><th class="num">대지권</th><th class="num">층</th><th class="num">준공</th></tr></thead><tbody>${same.map(t => `<tr><td>${esc(t[4])}</td><td>${esc(t[3])}</td><td class="num">${won(t[5])}</td><td class="num">${t[6]}㎡</td><td class="num">${t[7]}㎡</td><td class="num">${esc(t[8])}</td><td class="num">${esc(t[9])}</td></tr>`).join("")}</tbody></table></div>` : `<p class="sub">이 지번의 연립·다세대 거래는 없어요. (서대문·마포 빌라만 담겨 있어요)</p>`}
      </div>`;
  }

  // ---------- 표 그리기 ----------
  function seg(el, onPick){
    const opts = ["전체","서대문구","마포구"]; let cur = "전체";
    const draw = () => { el.innerHTML = opts.map(o => `<button type="button" class="${o===cur?"on":""}">${o}</button>`).join(""); };
    el.addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; cur = b.textContent; draw(); onPick(cur); });
    draw(); onPick(cur);
  }
  const chips = zs => zs.length ? zs.map(z => `<span class="lab-z">${esc(z.name)}<i>${esc(z.stage)}</i></span>`).join("") : `<span class="meta">정비구역 없음</span>`;
  function tables(){
    $("lab-kpis").innerHTML = [[D.zones,"마포·서대문 정비구역"],[D.rh_n,"빌라 거래"],[D.sh_n,"단독·다가구 거래"],[D.sv_n,"분양권·입주권 거래"]]
      .map(([n,l]) => `<div class="kpi"><div class="l">${l}</div><div class="v">${n.toLocaleString()}</div></div>`).join("");
    $("lab-period").textContent = `거래 기간 ${D.period[0].replace("-",".")} ~ ${D.period[1].replace("-",".")} · 해제 거래 제외 · 최근 1~2개월은 신고가 더 들어올 수 있어요`;
    seg($("lab-seg1"), g => {
      $("lab-rh").innerHTML = D.rh.filter(r => g==="전체" || r.gu===g).slice(0, 25).map(r => `<tr><td><b>${esc(r.dong)}</b><div class="meta">${esc(r.gu)}</div></td><td>${chips(r.zones)}</td><td class="num">${r.n}</td><td class="num">${won(r.med)}</td><td class="num">${r.land ? won(r.land) : "–"}</td><td class="num">${r.old}%</td></tr>`).join("");
    });
    const ORDER = ["구역지정","추진위","조합설립","건축심의","사업시행","관리처분","착공"];
    seg($("lab-seg2"), g => {
      const zs = D.zlist.filter(z => g==="전체" || z.gu===g).sort((a,b) => ORDER.indexOf(b.stage)-ORDER.indexOf(a.stage) || (b.units||0)-(a.units||0));
      $("lab-zones").innerHTML = zs.map(z => { const k = ORDER.indexOf(z.stage); return `<div class="lab-zrow"><span><b>${esc(z.name)}</b><small>${esc(z.gu)} ${esc(z.dong)} · ${esc(z.stage)}</small></span><span class="lab-track">${ORDER.map((_,i) => `<i class="${i<k?"on":i===k?"cur":""}"></i>`).join("")}</span><span class="meta">${z.units ? z.units.toLocaleString()+"세대" : "–"}</span></div>`; }).join("");
    });
    $("lab-apt").innerHTML = D.apt.map(a => `<tr><td><b>${esc(a.apt)}</b><div class="meta">${esc(a.gu)} ${esc(a.dong)}</div></td><td class="num">${a.n}</td><td class="num">${a.ip||"–"}</td><td class="num">${a.m59 ? won(a.m59[0]) : "–"}</td><td class="num">${a.m84 ? won(a.m84[0]) : "–"}</td><td>${esc(a.last)} · ${won(a.lastAmt)}</td></tr>`).join("");
  }

  function init(){
    if (loading) return loading;
    loading = fetch("data/realtrade/lab.json").then(r => r.json()).then(d => { D = d; tables(); })
      .catch(() => { $("lab-kpis").innerHTML = `<p class="note">데이터 파일을 불러오지 못했어요.</p>`; });
    return loading;
  }
  $("lab-form").addEventListener("submit", e => { e.preventDefault(); const v = $("lab-addr").value.trim(); if (v) init().then(() => lookup(v)); });
  document.querySelectorAll("[data-lab-ex]").forEach(b => b.addEventListener("click", () => { $("lab-addr").value = b.dataset.labEx; init().then(() => lookup(b.dataset.labEx)); }));
  window.GS_labInit = init;
  const pane = document.getElementById("pane-lab"); if (pane && pane.classList.contains("on")) init();
})();
